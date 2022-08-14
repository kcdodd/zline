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

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@dataclass
class PlotStyle:
  color : tuple[int] = (255, 255, 255)

  #-----------------------------------------------------------------------------
  def __post_init__(self):
    self.color = norm_rgb(self.color)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Plot(Tile):
  #-----------------------------------------------------------------------------
  def __init__(self,*,
    xy = None,
    wrapper = None,
    style = None,
    **kwargs):

    super().__init__(**kwargs)

    if style is None:
      style = PlotStyle()

    self._xy = xy
    self.style = style

  #-----------------------------------------------------------------------------
  @property
  def xy(self):
    return self._xy

  #-----------------------------------------------------------------------------
  @xy.setter
  def xy(self, xy):
    self._xy = xy

  #-----------------------------------------------------------------------------
  def render(self):
    self.buf[:] = '\0'

    h, w = self.shape

    mask4 = _interp_mask(4*w, 4*h, *self.xy)
    scale = mask4.astype(np.float32)

    scale_max = coarsen(scale, (2, 2), op = 'max')
    mean = (1/16) * coarsen(scale, (4, 4))

    mask2 = scale_max > 0

    count = coarsen(mask2, (2, 2), op = 'sum')
    mask, quads = _mask_quads(mask2)

    self.buf[mask] = quads[mask]

    self.fg[:] = np.where(
      mask[:,:,np.newaxis],
      np.minimum(255, (((mask/(0.95+0.05*count))[:,:,np.newaxis]) * np.array(self.style.color))).astype(np.uint8),
      self.fg )

    self.bg[:] = np.where(
      mask[:,:,np.newaxis],
      ((mean[:,:,np.newaxis]) * np.array(self.style.color)).astype(np.uint8),
      self.bg )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def _interp_mask(nx, ny, _x, _y):

  _ds = np.zeros_like(_x)
  _ds[1:] = np.sqrt(np.diff(_x)**2 + np.diff(_y)**2)
  _s = np.cumsum(_ds)

  x0 = np.amin(_x)
  lx = np.amax(_x) - x0
  dx = lx / nx

  ns = 2*_s[-1] / dx

  s = 0.5*dx * (0.5 + np.arange(ns))

  x = np.interp(s, _s, _x)
  y = np.interp(s, _s, _y)

  y0 = np.amin(y)
  ly = np.amax(y) - y0
  dy = ly / ny

  yi = ny-1 - np.minimum(ny-1, np.round((y-y0)/dy).astype(np.int16) )

  xi = np.minimum(nx-1, np.round((x-x0)/dx).astype(np.int16) )

  mask = np.zeros((ny,nx), dtype = bool)

  mask[yi, xi] = True

  return mask
#
# #+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# def _interp_quads(nx, ny, _x, _y):
#   nx *= 2
#   ny *= 2
#
#   mask = _interp_mask(nx, ny, _x, _y)
#
#   return _mask_quads(mask)
#
#   # n = np.zeros((ny,nx), dtype = np.uint8)
#   # n[::2,::2] = Qa
#   # n[::2,1::2] = Qb
#   # n[1::2,1::2] = Qc
#   # n[1::2,::2] = Qd
#   # n = np.where(mask, n, 0)
#   # n = n[::2,::2] | n[::2,1::2] | n[1::2,1::2] | n[1::2,::2]
#   #
#   # mask = n != 0
#   #
#   # return mask, QUADS[n[mask]]

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
def _coarsen(arr, factor):
  x_shape = np.empty( (4,), dtype = np.int32 )
  x_shape[::2] = arr.shape
  x_shape[::2] //= factor
  x_shape[1::2] = factor
  return arr.reshape(x_shape)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def coarsen(arr, factor, op = 'sum'):
  return getattr(_coarsen(arr, factor), op)(
    axis = tuple(range(1, 4, 2)) )
