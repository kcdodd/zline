import numpy as np
from textwrap import TextWrapper
from collections import namedtuple
from dataclasses import dataclass, field, asdict, fields
import sys
from .ansi import (
  goto,
  move,
  FG )

from .color import (
  Color,
  norm_rgb )

from .line import (
  LINES )

from .tile import Box

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
