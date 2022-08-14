import numpy as np
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
from .tile import Tile, Shape, Pos

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
  def min_shape(self,
      max_shape : Shape = None):

    if max_shape is None:
      max_shape = Shape(2**20, 2**20)

    if self._init_shape is not None:
      return Shape(*[min(s,m) for s,m in zip(self._init_shape, max_shape)])

    h, w = max_shape
    spc = self.border.spc()
    h -= sum(spc[::2])
    w -= sum(spc[1::2])
    _max_shape = Shape(h, w)

    h = 0
    w = 0

    for cell in self.content:
      hm = _max_shape.h - cell.pos.row
      wm = _max_shape.w - cell.pos.col

      _h, _w = cell.min_shape((hm, wm))

      h = max(h, cell.pos.row + _h )
      w = max(w, cell.pos.col + _w )

    return Shape(h, w)

  #-----------------------------------------------------------------------------
  def set_shape(self,
    max_shape : Shape ):

    if self._init_shape is not None:
      max_shape = [min(s,m) for s,m in zip(self._init_shape, max_shape)]

    h, w = max_shape
    spc = self.border.spc()
    h -= sum(spc[::2])
    w -= sum(spc[1::2])
    _max_shape = Shape(h, w)

    h = 0
    w = 0

    for cell in self.content:

      hm = _max_shape.h - cell.pos.row
      wm = _max_shape.w - cell.pos.col

      cell.set_shape((hm, wm))

      h = max(h, cell.pos.row + cell.shape.h )
      w = max(w, cell.pos.col + cell.shape.w )

    if self._init_shape is not None:
      self.shape = max_shape

    else:
      self.shape = (h, w)

  #-----------------------------------------------------------------------------
  def render(self):
    self.buf[:] = '\0'
    self.lines[:] = 0
    self.exterior[:] = 0

    h, w = self.shape

    spc = self.border.spc()
    h -= sum(spc[::2])
    w -= sum(spc[1::2])

    _fg = 255*np.ones( self.shape + (3,), dtype = np.uint32 )
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

    cmask = self.lines == 0

    for cell in self.content:

      s = tuple(slice(o+i, o+i+d) for o,i,d in zip(spc[::3], cell.pos, cell.shape))
      mask = (cell.buf != '\0') & cmask[s]

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