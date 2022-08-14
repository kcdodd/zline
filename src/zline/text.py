import numpy as np
from textwrap import TextWrapper
from collections import namedtuple
from dataclasses import dataclass, field, asdict, fields
import sys

from .color import (
  Color,
  norm_rgb,
  rgb_to_8bit )

from .tile import Tile, Shape, Pos

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@dataclass
class TextStyle:
  color : tuple[int] = (255, 255, 255)

  #-----------------------------------------------------------------------------
  def __post_init__(self):
    self.color = norm_rgb(self.color)

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

    self._text = text
    self.wrapper = wrapper
    self.style = style

  #-----------------------------------------------------------------------------
  def min_shape(self,
    max_shape : Shape = None):

    if self._init_shape is not None:
      return self._init_shape

    if max_shape is None:
      max_shape = Shape(2**32, 2**32)

    self.wrapper.width = max_shape.w
    self.wrapper.max_lines = max_shape.h

    text = self.wrapper.wrap(self.text)

    shape = len(lines), max(len(l) for l in text)

    return shape

  #-----------------------------------------------------------------------------
  @property
  def text(self):
    return self._text

  #-----------------------------------------------------------------------------
  @text.setter
  def text(self, text):
    self._text = text

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
