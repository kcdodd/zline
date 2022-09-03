import numpy as np
from textwrap import TextWrapper
from collections import namedtuple
from dataclasses import dataclass, field, asdict, fields
import sys

from .color import (
  Color,
  norm_rgb,
  rgb_to_8bit )

from .cmap import get_cmap

from .tile import Tile, Shape, Pos

from .line import (
  QUADS,
  Qa, Qb, Qc, Qd )

import matplotlib.pyplot as plt

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@dataclass
class GraphicStyle:
  cmap : str = None
  pattern : str = 'quad'
  thresh : float = 0.5
  fg_scale : float = 1.0
  bg_scale : float = 0.0

  #-----------------------------------------------------------------------------
  def __post_init__(self):
    if callable(self.cmap):
      pass

    elif isinstance(self.cmap, str):

      self.cmap = get_cmap(self.cmap)

    else:
      cmap = self.cmap

      if cmap is None:
        cmap = (255,255,255)

      cmap = np.array(norm_rgb(cmap))

      self.cmap = lambda arr: np.clip(np.round( arr[:,:,np.newaxis] * cmap ), 0, 255).astype(np.uint8)

    assert self.pattern in ['quad', 'dot']

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
    self.fg[:] = 255
    self.bg[:] = 0

    h, w = self.shape

    if self.style.pattern == 'quad':
      shape = (2*h, 2*w)

    elif self.style.pattern == 'dot':
      shape = (4*h, 2*w)

    else:
      assert False

    arr = self.arr

    if arr.shape != shape:
      import skimage
      arr = skimage.transform.resize(arr, shape)

    if self.style.pattern == 'quad':
      mask, buf, avg_fg, avg_bg = _render_quads(
        arr = arr,
        thresh = self.style.thresh,
        fg_scale = self.style.fg_scale,
        bg_scale = self.style.bg_scale )

    elif self.style.pattern == 'dot':
      mask, buf, avg_fg, avg_bg = _render_dots(
        arr = arr,
        thresh = self.style.thresh,
        fg_scale = self.style.fg_scale,
        bg_scale = self.style.bg_scale )

    else:
      assert False


    self.buf[mask] = buf[mask]

    self.fg[:] = np.where(
      mask[:,:,np.newaxis],
      self.style.cmap(avg_fg),
      self.fg )

    self.bg[:] = np.where(
      mask[:,:,np.newaxis],
      self.style.cmap(avg_bg),
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
def _render_quads(arr, thresh, fg_scale, bg_scale):
  h, w = arr.shape
  h //= 2
  w //= 2
  shape = (h,w)

  _arr = _coarsen(arr, (2,2))

  _lo = np.amin(
    _arr,
    axis = (1,3) )

  _hi = np.amax(
    _arr,
    axis = (1,3) )

  lo = refine(_lo, (2,2))
  hi = refine(_hi, (2,2))

  mask = arr > lo + thresh*(hi - lo)

  delta = _hi - _lo
  avg_fg = _lo + fg_scale*delta
  avg_bg = _lo + bg_scale*delta

  qmask, quads = _mask_quads(mask)

  return qmask, quads, avg_fg, avg_bg

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def _mask_dots(mask):
  n = np.ones(mask.shape, dtype = np.uint32)

  # first column
  n[::4,::2] = 0x01
  n[1::4,::2] = 0x02
  n[2::4,::2] = 0x04
  n[3::4,::2] = 0x40

  # second column
  n[::4,1::2] = 0x08
  n[1::4,1::2] = 0x10
  n[2::4,1::2] = 0x20
  n[3::4,1::2] = 0x80

  n = np.where(mask, n, 0)
  n = coarsen(n, (4,2), 'sum').astype(dtype = n.dtype)
  mask = n != 0
  n += 0x2800

  chars = n.view('<U1')

  return mask, chars

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def _render_dots(arr, thresh, fg_scale, bg_scale):

  _arr = _coarsen(arr, (4,2))

  _lo = np.amin(
    _arr,
    axis = (1,3) )

  _hi = np.amax(
    _arr,
    axis = (1,3) )

  lo = refine(_lo, (4,2))
  hi = refine(_hi, (4,2))

  mask = arr > lo + thresh*(hi - lo)

  delta = _hi - _lo
  avg_fg = _lo + fg_scale*delta
  avg_bg = _lo + bg_scale*delta

  qmask, dots = _mask_dots(mask)

  return qmask, dots, avg_fg, avg_bg

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
