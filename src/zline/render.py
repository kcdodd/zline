import numpy as np
import sys
from .ansi import (
  goto,
  move,
  FG )

from .color import (
  norm_rgb )

from .line import (
  L, R, T, B,
  Lh, Rh, Th, Bh,
  Ld, Rd, Td, Bd,
  LINES )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Tile:
  #-----------------------------------------------------------------------------
  def __init__(self,*,
    pos,
    shape ):

    self.pos = pos
    self.shape = shape
    self.buf = np.zeros(self.shape, dtype = np.unicode_)
    self.fg = 255*np.ones( self.shape + (3,), dtype = np.uint8 )
    self.bg = np.zeros( self.shape + (3,), dtype = np.uint8 )
    self.lines = np.zeros( self.shape, dtype = np.uint16 )
    self.exterior = np.zeros( self.shape, dtype = np.uint16 )

  #-----------------------------------------------------------------------------
  def render(self):
    pass

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Box(Tile):
  #-----------------------------------------------------------------------------
  def __init__(self,*,
    text = '',
    ctext = '#fff',
    cborder = '#fff',
    nborder = 0,
    rborder = False,
    jborder = False,
    **kwargs):

    super().__init__(**kwargs)

    self.text = text
    # print(self.text)
    self.ctext = norm_rgb(ctext)
    self.cborder = norm_rgb(cborder)
    self.nborder = nborder
    self.rborder = rborder
    self.jborder = jborder

  #-----------------------------------------------------------------------------
  def render(self):
    h, w = self.shape

    text = [
      np.array(list(l), dtype = np.unicode_)
      for l in (self.text.splitlines() if self.text else [''])]

    for i, l in enumerate(text):
      if i >= h-2:
        break

      n = min(w-2, len(l))
      _buf = self.buf[i+1, 1:(n+1)]
      _l = l[:n]

      _buf[:] = _l

    if self.nborder == 0:
      _L, _R, _T, _B = L, R, T, B
    elif self.nborder == 1:
      _L, _R, _T, _B = Lh, Rh, Th, Bh
    else:
      _L, _R, _T, _B = Ld, Rd, Td, Bd

    if self.rborder:
      _L += 4096
      _R += 4096
      _T += 4096
      _B += 4096

    self.lines[:] = 0
    self.lines[0,0] = _R|_B # '╭'
    self.lines[0,-1] = _L|_B # '╮'
    self.lines[-1,0] = _T|_R # '╰'
    self.lines[-1,-1] = _L|_T# '╯'
    self.lines[[0, -1],1:-1] = _L|_R # '─'
    self.lines[1:-1,[0, -1]] = _T|_B # '│'

    self.exterior[:] = 0

    if self.jborder:
      self.exterior[:,0] = Ld|Td|Bd
      self.exterior[:,-1] = Rd|Td|Bd
      self.exterior[0,:] |= Td|Ld|Rd
      self.exterior[-1,:] |= Bd|Ld|Rd

    self.fg[:] = self.ctext
    self.fg[:,[0, -1]] = self.cborder
    self.fg[[0, -1],:] = self.cborder

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Canvas:
  #-----------------------------------------------------------------------------
  def __init__(self,
    shape,
    fp = sys.stdout ):

    self.shape = shape
    self.buf = np.full(self.shape, dtype = np.unicode_, fill_value = ' ')
    self.lines = np.zeros( self.shape, dtype = np.uint16 )

    self.fg = np.ones( self.shape + (3,), dtype = np.uint32 )
    self.fg_num = np.ones( self.shape, dtype = np.uint32 )

    self.bg = np.zeros( self.shape + (3,), dtype = np.uint32 )

    # self.buf[...] = ' '
    self.fp = fp
    self.cells = list()

  #-----------------------------------------------------------------------------
  def __enter__(self):
    self.fp.write('\u001b[?1049h' + '\u001b[?25l')
    return self

  #-----------------------------------------------------------------------------
  def __exit__(self, type, value, traceback):
    self.fp.write('\u001b[?25h' + '\u001b[?1049l')
    return False

  #-----------------------------------------------------------------------------
  def render(self):
    self.lines[:] = 0

    for cell in self.cells:
      cell.render()
      s = tuple(slice(i, i+d) for i,d in zip(cell.pos, cell.shape))

      self.lines[s] &= cell.exterior
      existing = self.lines[s] != 0

      self.lines[s] |= cell.lines

      fg = self.fg[s]
      fg_num = self.fg_num[s]

      interior = cell.exterior == 0
      border = cell.lines != 0
      mask = interior | border

      mono = ~existing & mask
      blend = existing & mask

      fg[mono] = cell.fg[mono]
      fg_num[mono] = 1

      fg[blend] += cell.fg[blend]
      fg_num[blend] += 1

    self.fg[:] = np.round(self.fg / self.fg_num[:,:, np.newaxis])
    self.buf[:] = LINES[self.lines]
    # print(self.lines)
    # print(self.fg)
    # print(self.buf)

    for cell in self.cells:
      mask = (cell.buf != '\0')
      s = tuple(slice(i, i+d) for i,d in zip(cell.pos, cell.shape))

      for attr in ['buf', 'fg', 'bg']:
        view = getattr(self, attr)[s]
        _mask = mask
        if view.ndim == 3:
          _mask = _mask[:, :, np.newaxis]

        view[...] = np.where(_mask, getattr(cell, attr), view)

    # print(rgb_to_standard(self.fg))
    # print(self.buf)
    self.flush()

  #-----------------------------------------------------------------------------
  def flush(self):
    row_shape = self.buf.shape[-1:]
    mask = np.ones(row_shape, dtype = bool)

    self.fp.write('\u001b[2j')

    self.fp.write(goto(0,0))
    cr = move(-1, -self.shape[1])

    fg_color = FG[8]

    for i in range(self.shape[0]):
      mask[1:] = np.logical_or.reduce(
        self.fg[i, 1:] != self.fg[i, :-1],
        axis = 1 )

      fg = np.chararray(row_shape, itemsize = 20, unicode = True)
      fg[mask] = fg_color(self.fg[i, mask])

      row = [_fg+t for _fg, t in zip(fg, self.buf[i]) ]
      # print(row)
      self.fp.write(''.join(row) + cr)
