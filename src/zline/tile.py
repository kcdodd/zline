import numpy as np
from textwrap import TextWrapper
from collections import namedtuple
from dataclasses import dataclass, field, asdict, fields
import sys
from enum import Enum

from .color import (
  Color,
  norm_rgb,
  rgb_to_8bit )

from .line import (
  LINES )

from .border import BorderStyle

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Flags(Enum):
  B = 0b00001
  D = 0b00010
  I = 0b00100
  U = 0b01000
  K = 0b10000

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Shape = namedtuple('Shape', [
  'h', 'w'])

Pos = namedtuple('Pos', [
  'row', 'col'])

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Tile:
  #-----------------------------------------------------------------------------
  def __init__(self,*,
    pos = None,
    shape = None,
    transparent = (0,0,0) ):

    self._pos = None
    self.pos = pos
    self._init_shape = shape
    self._shape = None
    self._transparent = transparent

  #-----------------------------------------------------------------------------
  def min_shape(self,
    max_shape : Shape = None):

    if self._init_shape is None:
      return 0,0

    return self._init_shape

  #-----------------------------------------------------------------------------
  def set_shape(self, max_shape):
    if self._init_shape is not None:
      max_shape = [min(s,m) for s,m in zip(self._init_shape, max_shape)]

    self.shape = max_shape

  #-----------------------------------------------------------------------------
  @property
  def shape(self):
    return self._shape

  #-----------------------------------------------------------------------------
  @shape.setter
  def shape(self, shape):
    if self._shape == shape or shape is None:
      return

    self._shape = Shape(*shape)

    assert self.shape.h * self.shape.w < 2**20

    self.buf = np.zeros(self.shape, dtype = np.unicode_)
    self.lines = np.zeros( self.shape, dtype = np.uint16 )
    self.exterior = np.zeros( self.shape, dtype = np.uint16 )

    self.fg = 255*np.ones( self.shape + (3,), dtype = np.uint8 )
    self.bg = np.zeros( self.shape + (3,), dtype = np.uint8 )
    self.flags = np.zeros( self.shape, dtype = np.uint8 )

  #-----------------------------------------------------------------------------
  @property
  def pos(self):
    return self._pos

  #-----------------------------------------------------------------------------
  @pos.setter
  def pos(self, pos):
    if pos is None:
      pos = (0,0)

    self._pos = Pos(*pos)

  #-----------------------------------------------------------------------------
  @property
  def transparent(self):
    return self._transparent

  #-----------------------------------------------------------------------------
  def render(self):
    pass
