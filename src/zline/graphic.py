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

from .line import (
  QUADS,
  Qa, Qb, Qc, Qd )

import matplotlib.pyplot as plt

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@dataclass
class GraphicStyle:
  cmap : str = None

  #-----------------------------------------------------------------------------
  def __post_init__(self):
    if callable(self.cmap):
      pass
    elif isinstance(self.cmap, str):
      self.cmap = plt.get_cmap(self.cmap)

    else:
      cmap = self.cmap

      if cmap is None:
        cmap = (255,255,255)

      cmap = np.array(norm_rgb(cmap))

      self.cmap = lambda arr: ( arr[:,:,np.newaxis] * cmap ) / 255

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Graphic(Tile):
  #-----------------------------------------------------------------------------
  def __init__(self,*,
    arr = None,
    style = None,
    **kwargs):

    super().__init__(**kwargs)

    if style is None:
      style = GraphicStyle()

    self._arr = arr
    self.style = style

  #-----------------------------------------------------------------------------
  @property
  def arr(self):
    return self._arr

  #-----------------------------------------------------------------------------
  @arr.setter
  def arr(self, arr):
    self._arr = arr

  #-----------------------------------------------------------------------------
  def render(self):
    self.buf[:] = '\0'

    h, w = self.shape
    shape = (2*h, 2*w)

    arr = self.arr

    if arr.shape != shape:
      import skimage
      arr = skimage.transform.resize(arr, shape)

    mask, quads, avg_fg, avg_bg = _render_quads(arr)

    self.buf[mask] = quads[mask]

    self.fg[:] = np.where(
      mask[:,:,np.newaxis],
      np.clip(255*self.style.cmap(avg_fg)[:,:,:3], 0, 255).astype(np.uint8),
      self.fg )

    self.bg[:] = np.where(
      mask[:,:,np.newaxis],
      np.clip(255*self.style.cmap(avg_bg)[:,:,:3], 0, 255).astype(np.uint8),
      self.bg )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def _mask_quads(mask):

  n = np.zeros(mask.shape, dtype = np.uint8)
  n[::2,::2] = Qa
  n[::2,1::2] = Qb
  n[1::2,1::2] = Qc
  n[1::2,::2] = Qd
  n = np.where(mask, n, 0)
  n = n[::2,::2] | n[::2,1::2] | n[1::2,1::2] | n[1::2,::2]

  mask = n != 0

  return mask, QUADS[n]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def _render_quads(arr):
  h, w = arr.shape
  h //= 2
  w //= 2
  shape = (h,w)

  _arr = _coarsen(arr, (2,2))

  _mid = np.average(
    _arr,
    axis = (1,3) )

  _hi = np.amax(
    _arr,
    axis = (1,3) )

  mid = refine(_mid, (2,2))
  hi = refine(_hi, (2,2))

  mask = arr >= 0.75*hi + 0.25*mid

  avg_fg = 0.75*_hi + 0.25*_mid

  _lo = np.amin(
    _arr,
    axis = (1,3) )

  avg_bg = 0.75*_lo + 0.25*_mid

  import matplotlib.pyplot as plt

  qmask, quads = _mask_quads(mask)


  return qmask, quads, avg_fg, avg_bg

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def _coarsen(arr, factor):
  """Reshapes an array such that the first 'ndims' of original shape are reduced
  by 'factor', with all values are stacked into new dimensions
  """
  x_shape = np.empty( (2*arr.ndim,), dtype = np.int32 )
  x_shape[::2] = arr.shape
  x_shape[::2] //= factor
  x_shape[1::2] = factor
  assert np.all(x_shape[::2] * x_shape[1::2] == arr.shape)

  return arr.reshape(x_shape)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def coarsen(arr, factor, op = 'sum'):
  return getattr(_coarsen(arr, factor), op)(
    axis = tuple(range(1, 2 * arr.ndim, 2)) )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def refine(arr, factor):
  shape = np.array( arr.shape, dtype = np.int32 )
  shape *= factor
  _arr = np.empty(shape, dtype = arr.dtype)

  _coarsen(_arr, factor)[:] = arr[(slice(None), None)*2]

  return _arr
