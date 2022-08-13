import numpy as np
from textwrap import TextWrapper
from collections import namedtuple
from dataclasses import dataclass, field, asdict, fields
import sys

from .color import (
  Color,
  norm_rgb )

from .line import (
  LINES )

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
    self.fg = 255*np.ones( self.shape + (3,), dtype = np.uint8 )
    self.bg = np.zeros( self.shape + (3,), dtype = np.uint8 )
    self.lines = np.zeros( self.shape, dtype = np.uint16 )
    self.exterior = np.zeros( self.shape, dtype = np.uint16 )

  #-----------------------------------------------------------------------------
  def render(self):
    pass

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class TextBox(Tile):
  #-----------------------------------------------------------------------------
  def __init__(self,*,
    text = None,
    wrapper = None,
    style = None,
    border = None,
    **kwargs):

    super().__init__(**kwargs)

    if text is None:
      text = ''

    if wrapper is None:
      wrapper = TextWrapper(
        placeholder = '')

    if style is None:
      style = TextStyle()

    if border is None:
      border = BorderStyle()

    self.text = text
    self.wrapper = wrapper
    self.style = style
    self.border = border

  #-----------------------------------------------------------------------------
  def render(self):
    h, w = self.shape

    spc = self.border.spc()
    h -= sum(min(1, _h) for _h in spc[::2])
    w -= sum(min(1, _w) for _w in spc[1::2])

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

    i0 = spc[0]
    j0 = spc[3]

    for i, l in enumerate(text):

      n = min(w, len(l))
      _buf = self.buf[i0+i, j0:(j0+n)]
      _l = l[:n]

      _buf[:] = _l

    #...........................................................................
    b = self.border.interior()

    self.lines[:] = 0

    self.lines[0,0] = b[0,0]
    self.lines[0,1:-1] = b[0,1]
    self.lines[0,-1] = b[0,2]

    self.lines[1:-1, 0] = b[1,0]
    self.lines[1:-1, -1] = b[1,2]

    self.lines[-1,0] = b[2,0]
    self.lines[-1,1:-1] = b[2,1]
    self.lines[-1,-1] = b[2,2]

    #...........................................................................
    e = self.border.exterior()

    self.exterior[:] = 0

    self.exterior[0,0] = e[0,0]
    self.exterior[0,1:-1] = e[0,1]
    self.exterior[0,-1] = e[0,2]

    self.exterior[1:-1, 0] = e[1,0]
    self.exterior[1:-1, -1] = e[1,2]

    self.exterior[-1,0] = e[2,0]
    self.exterior[-1,1:-1] = e[2,1]
    self.exterior[-1,-1] = e[2,2]

    #...........................................................................
    self.fg[:] = self.style.color

    self.fg[:,0] = self.border.color.left
    self.fg[:,-1] = self.border.color.right
    self.fg[0,:] = self.border.color.top
    self.fg[-1,:] = self.border.color.bottom
