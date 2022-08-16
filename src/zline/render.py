import numpy as np
from textwrap import TextWrapper
from collections import namedtuple
from dataclasses import dataclass, field, asdict, fields
import sys
from .ansi import (
  goto,
  move,
  reset_style,
  flags,
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
    esc = np.full(row_shape, dtype = np.object_, fill_value = '\x1b[')

    for i in range(self.shape[0]):
      buf = self.buf[i]
      fmt = np.full(row_shape, dtype = np.object_, fill_value = '')

      mask[1:] = np.logical_or.reduce(
        self.fg[i, 1:] != self.fg[i, :-1],
        axis = 1 )

      fmt[mask] = fg_color(self.fg[i, mask])

      if self.transparent is not None:
        bg_mask = (self.bg[i] != self.transparent).any(axis = 1)
      else:
        bg_mask = np.ones_like(mask)

      bg_mask[1:] &= np.logical_or.reduce(
        self.bg[i, 1:] != self.bg[i, :-1],
        axis = 1 )

      fmt[bg_mask & (fmt != '')] += ';'
      fmt[bg_mask] += bg_color(self.bg[i, bg_mask])


      mask[1:] = self.flags[i, 1:] != self.flags[i, :-1]
      fmt[mask & (fmt != '')] += ';'
      fmt[mask] += flags(self.flags[i, mask])

      m = fmt != ''
      fmt[m] = esc[m] + fmt[m] + 'm'

      row = fmt + buf
      # print(row)
      # input('')
      self.fp.write(''.join(row) + reset + cr)
