import numpy as np
from textwrap import TextWrapper
from collections import namedtuple
from dataclasses import dataclass, field, asdict, fields
import sys
from .ansi import (
  goto,
  move,
  reset_style,
  FG,
  BG )

from .color import (
  Color,
  norm_rgb )

from .line import (
  LINES )

from .box import Box

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Canvas(Box):
  #-----------------------------------------------------------------------------
  def __init__(self,
    shape,
    fp = sys.stdout,
    alt = True ):

    super().__init__(shape = shape)

    self.fp = fp
    self.alt = alt

  #-----------------------------------------------------------------------------
  def __enter__(self):
    if self.alt:
      self.fp.write('\u001b[?1049h' + '\u001b[?25l')

    return self

  #-----------------------------------------------------------------------------
  def __exit__(self, type, value, traceback):
    if self.alt:
      self.fp.write('\u001b[?25h' + '\u001b[?1049l')

    return False

  #-----------------------------------------------------------------------------
  def render(self):
    super().render()

    buf = LINES[self.lines]
    mask = (buf != '\0')

    self.buf[:] = np.where(mask, buf, self.buf)

    mask = (self.buf == '\0')
    self.buf[:] = np.where(mask, ' ', self.buf)

  #-----------------------------------------------------------------------------
  def flush(self):
    row_shape = self.buf.shape[-1:]
    mask = np.ones(row_shape, dtype = bool)

    if self.alt:
      self.fp.write('\u001b[2j')
      self.fp.write(goto(1,1))
      cr = move(-1, -self.shape[1])

    else:
      cr = '\n'

    fg_color = FG[8]
    bg_color = BG[8]
    reset = reset_style()

    for i in range(self.shape[0]):
      buf = self.buf[i]

      mask[1:] = np.logical_or.reduce(
        self.fg[i, 1:] != self.fg[i, :-1],
        axis = 1 )

      fg = np.chararray(row_shape, itemsize = 20, unicode = True)
      fg[mask] = fg_color(self.fg[i, mask])
      # print(self.fg[i])
      # print(mask)
      # print(fg)

      mask[1:] = np.logical_or.reduce(
        self.bg[i, 1:] != self.bg[i, :-1],
        axis = 1 )

      bg = np.chararray(row_shape, itemsize = 20, unicode = True)
      bg[mask] = bg_color(self.bg[i, mask], reset_rgb = None)

      row = [_fg+_bg+t for _fg, _bg, t in zip(fg, bg, buf) ]
      # print(row)
      # input('')
      self.fp.write(''.join(row) + reset + cr)
