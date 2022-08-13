import numpy as np
from textwrap import TextWrapper
from collections import namedtuple
from dataclasses import dataclass, field, asdict, fields
import sys

from .color import (
  Color,
  norm_rgb,
  rgb_to_8bit )

from .line import (
  LINES )

from .border import BorderStyle

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@dataclass
class TextStyle:
  color : tuple[int] = (255, 255, 255)

  #-----------------------------------------------------------------------------
  def __post_init__(self):
    self.color = norm_rgb(self.color)


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Tile:
  #-----------------------------------------------------------------------------
  def __init__(self,*,
    pos = None,
    shape = None ):

    if pos is None:
      pos = (0,0)

    if shape is None:
      shape = (1,1)

    self.pos = pos
    self.shape = shape
    self.buf = np.zeros(self.shape, dtype = np.unicode_)
    self.lines = np.zeros( self.shape, dtype = np.uint16 )
    self.exterior = np.zeros( self.shape, dtype = np.uint16 )

    self.fg = 255*np.ones( self.shape + (3,), dtype = np.uint8 )
    # self.fg_num = np.ones( self.shape, dtype = np.uint32 )
    self.bg = np.zeros( self.shape + (3,), dtype = np.uint8 )

  #-----------------------------------------------------------------------------
  def render(self):
    pass

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Box(Tile):
  #-----------------------------------------------------------------------------
  def __init__(self,*,
    content = None,
    border = None,
    **kwargs):

    super().__init__(**kwargs)

    if border is None:
      border = BorderStyle()

    if content is None:
      content = list()

    elif not isinstance(content, (tuple, list)):
      content = [content]

    self.content = content
    self.border = border

  #-----------------------------------------------------------------------------
  def render(self):
    self.buf[:] = '\0'
    self.lines[:] = 0
    self.exterior[:] = 0

    h, w = self.shape

    spc = self.border.spc()
    h -= sum(spc[::2])
    w -= sum(spc[1::2])

    _fg = self.fg.astype(dtype = np.uint32)
    _fg_num = np.ones( self.shape, dtype = np.uint32 )

    for cell in self.content:
      cell.render()

      s = tuple(slice(o+i, o+i+d) for o,i,d in zip(spc[::3], cell.pos, cell.shape))

      self.lines[s] &= cell.exterior
      existing = self.lines[s] != 0

      self.lines[s] |= cell.lines

      fg = _fg[s]
      fg_num = _fg_num[s]

      interior = cell.exterior == 0
      border = cell.lines != 0
      mask = interior | border

      mono = ~existing & mask
      blend = existing & mask

      fg[mono] = cell.fg[mono]
      fg_num[mono] = 1

      fg[blend] += cell.fg[blend]
      fg_num[blend] += 1

    self.fg[:] = np.round(_fg / _fg_num[:,:, np.newaxis])

    for cell in self.content:

      mask = (cell.buf != '\0')
      s = tuple(slice(o+i, o+i+d) for o,i,d in zip(spc[::3], cell.pos, cell.shape))

      for attr in ['buf', 'fg', 'bg']:
        view = getattr(self, attr)[s]
        _mask = mask
        if view.ndim == 3:
          _mask = _mask[:, :, np.newaxis]

        view[...] = np.where(_mask, getattr(cell, attr), view)

    #...........................................................................
    b = self.border.interior()

    if spc.top and spc.left:
      self.lines[0,0] = b[0,0]

    if spc.top:
      self.lines[0,1:-1] = b[0,1]

    if spc.top and spc.right:
      self.lines[0,-1] = b[0,2]

    if spc.left:
      self.lines[1:-1, 0] = b[1,0]

    if spc.right:
      self.lines[1:-1, -1] = b[1,2]

    if spc.bottom and spc.left:
      self.lines[-1,0] = b[2,0]

    if spc.bottom:
      self.lines[-1,1:-1] = b[2,1]

    if spc.bottom and spc.right:
      self.lines[-1,-1] = b[2,2]

    #...........................................................................
    e = self.border.exterior()

    self.exterior[0,0] = e[0,0]
    self.exterior[0,1:-1] = e[0,1]
    self.exterior[0,-1] = e[0,2]

    self.exterior[1:-1, 0] = e[1,0]
    self.exterior[1:-1, -1] = e[1,2]

    self.exterior[-1,0] = e[2,0]
    self.exterior[-1,1:-1] = e[2,1]
    self.exterior[-1,-1] = e[2,2]

    #...........................................................................

    self.fg[:,0] = self.border.color.left
    self.fg[:,-1] = self.border.color.right
    self.fg[0,:] = self.border.color.top
    self.fg[-1,:] = self.border.color.bottom


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Text(Tile):
  #-----------------------------------------------------------------------------
  def __init__(self,*,
    text = None,
    wrapper = None,
    style = None,
    **kwargs):

    super().__init__(**kwargs)

    if text is None:
      text = ''

    if wrapper is None:
      wrapper = TextWrapper(
        placeholder = '')

    if style is None:
      style = TextStyle()

    self.text = text
    self.wrapper = wrapper
    self.style = style

  #-----------------------------------------------------------------------------
  def render(self):
    self.buf[:] = '\0'

    h, w = self.shape

    self.wrapper.width = w
    self.wrapper.max_lines = h

    text = self.wrapper.wrap(self.text)
    nlines = len(text)

    text = np.array(
      text,
      dtype = np.unicode_ ).view('U1')

    if text.size > 0:
      text = text.reshape((nlines, -1))
    else:
      text = text.reshape((0, 0))

    for i, l in enumerate(text):

      n = min(w, len(l))
      _buf = self.buf[i, :n]
      _l = l[:n]

      _buf[:] = _l

    self.fg[:] = self.style.color
