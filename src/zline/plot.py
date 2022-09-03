import numpy as np
from textwrap import TextWrapper
from collections import namedtuple
from dataclasses import dataclass, field, asdict, fields
import sys

from .color import (
  Color,
  norm_rgb,
  rgb_to_8bit )

from .tile import Tile, Shape, Pos, Flags

from .line import (
  QUADS,
  Qa, Qb, Qc, Qd )

from .graphic import Graphic, GraphicStyle

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@dataclass
class PlotStyle(GraphicStyle):
  color : tuple[int] = (255, 255, 255)

  #-----------------------------------------------------------------------------
  def __post_init__(self):
    self.color = norm_rgb(self.color)
    self.cmap = self.color
    self.pattern = 'dot'
    super().__post_init__()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Plot(Graphic):
  #-----------------------------------------------------------------------------
  def __init__(self,*,
    xy = None,
    style = None,
    **kwargs):

    if style is None:
      style = PlotStyle()

    super().__init__(style = style, **kwargs)


    self._xy = xy

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
    # self.buf[:] = '\0'

    h, w = self.shape
    #
    # mask4 = _interp_mask(4*w, 4*h, *self.xy)
    # scale = mask4.astype(np.float32)
    #
    # scale_max = coarsen(scale, (2, 2), op = 'max')
    # mean = (1/16) * coarsen(scale, (4, 4))
    #
    # mask2 = scale_max > 0
    #
    # count = coarsen(mask2, (2, 2), op = 'sum')
    # mask, quads = _mask_quads(mask2)
    #
    # self.buf[mask] = quads[mask]
    #
    # self.fg[:] = np.where(
    #   mask[:,:,np.newaxis],
    #   np.minimum(255, (((mask/(0.95+0.05*count))[:,:,np.newaxis]) * np.array(self.style.color))).astype(np.uint8),
    #   self.fg )
    #
    # self.bg[:] = np.where(
    #   mask[:,:,np.newaxis],
    #   ((mean[:,:,np.newaxis]) * np.array(self.style.color)).astype(np.uint8),
    #   self.bg )

    x, y = self.xy

    z = _plot(
      x0 = np.amin(x),
      x1 = np.amax(x),
      nx = 2*w,
      ny = 4*h,
      y0 = np.amin(y),
      y1 = np.amax(y),
      _x = x,
      _y = y )

    self.arr = z
    self.flags[:] = Flags.B.value

    super().render()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def _plot(x0, x1, nx, y0, y1, ny, _x, _y):

  lx = x1 - x0
  dx = lx / nx

  ly = y1 - y0
  dy = ly / ny

  xi = np.arange(nx)
  x = x0 + dx * xi
  y = np.interp(x, _x, _y)

  m = (y >= y0) & (y <= y1)
  xi = xi[m]
  x = x[m]
  y = y[m]

  yi = ny-1 - np.minimum(ny-1, np.round((y-y0)/dy).astype(np.int16) )

  z = np.zeros((ny, nx), dtype = np.float32)
  z[yi,xi] = 1.0

  return z

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def _draw(x0, x1, nx, y0, y1, ny, _x, _y):

  _ds = np.zeros_like(_x)
  _ds[1:] = ( np.diff(_x)**2 + np.diff(_y)**2 )**0.5
  _s = np.cumsum(_ds)
  ls = _s[-1]

  lx = x1 - x0
  dx = lx / nx

  ly = y1 - y0
  dy = ly / ny

  ds = 4*(dx**2 + dy**2)**0.5

  ns = max(1, int(ls / ds))

  s = ds * np.arange(ns+1)

  x = np.interp(s, _s, _x)
  y = np.interp(s, _s, _y)

  mx = (x >= x0) & (x <= x1)
  my = (y >= y0) & (y <= y1)

  x = x[mx]
  y = y[my]

  yi = ny-1 - np.minimum(ny-1, np.round((y-y0)/dy).astype(np.int16) )
  xi = np.minimum(nx-1, np.round((x-x0)/dx).astype(np.int16) )

  z = np.zeros((ny, nx), dtype = np.float32)

  from skimage.draw import line_aa

  for i in range(ns):
    rr, cc, val = line_aa(
      yi[i], xi[i],
      yi[i+1], xi[i+1] )

    z[rr, cc] = np.maximum(z[rr, cc], val)

  z = np.minimum(1.0, 2*z)

  # import matplotlib.pyplot as plt
  # plt.plot(xi,yi)
  # plt.show()
  # plt.imshow(z)
  # plt.show()

  return z
