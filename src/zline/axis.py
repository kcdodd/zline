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
  LINES,
  Tl, Rl, Bl, Ll )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@dataclass
class AxisStyle:
  title : str = ''

  xtitle : str = ''
  xticks : list[float] = tuple()
  xlabels : list[str] = '{:g}'

  ytitle : str = ''
  yticks : list[float] = tuple()
  ylabels : list[str] = '{:g}'

  #-----------------------------------------------------------------------------
  def spc(self):
    h = 0 if self.x is None else self.x.spc()
    w = 0 if self.y is None else self.y.spc()

    return h, w

  #-----------------------------------------------------------------------------
  def ticks(self, nx, ny):
    yticks, ylabels = ticks(ny, self.yticks, self.ylabels)
    xticks, xlabels = ticks(nx, self.xticks, self.xlabels)

    return xticks, xlabels, yticks, ylabels

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Axis(Tile):
  #-----------------------------------------------------------------------------
  def __init__(self,*,
    graph = None,
    style = None,
    **kwargs):

    super().__init__(**kwargs)

    if style is None:
      style = AxisStyle()

    self._graph = graph
    self.style = style

  #-----------------------------------------------------------------------------
  @property
  def graph(self):
    return self._graph

  #-----------------------------------------------------------------------------
  @graph.setter
  def graph(self, graph):
    self._graph = graph

  #-----------------------------------------------------------------------------
  def min_shape(self,
    max_shape : Shape = None):

    if max_shape is None:
      max_shape = Shape(2**20, 2**20)

    if self._init_shape is None:

      if self.graph is None:
        return 4,4
      else:
        _max_shape = Shape(*[s-4 for s in max_shape])
        shape = self.graph.min_shape(_max_shape)
        return [s+4 for s in shape]

    return self._init_shape

  #-----------------------------------------------------------------------------
  def set_shape(self, max_shape):
    if self._init_shape is not None:
      max_shape = [min(s,m) for s,m in zip(self._init_shape, max_shape)]

    _max_shape = Shape(*[s-4 for s in max_shape])

    self.graph.set_shape(_max_shape)

    self.shape = max_shape

  #-----------------------------------------------------------------------------
  def render(self):
    self.buf[:] = '\0'

    self.graph.render()
    h,w = self.shape
    xticks, xlabels, yticks, ylabels = self.style.ticks(w-2, h-2)

    i0 = 1
    i1 = h-3

    j0 = 3
    j1 = w-1

    self.buf[i0:i1, j0:j1] = self.graph.buf
    self.fg[i0:i1, j0:j1] = self.graph.fg
    self.bg[i0:i1, j0:j1] = self.graph.bg

    for j in range(w-2):
      if j > 0 and j < w-3:
        self.lines[[0,-3], 2+j] = Ll|Rl

      if j in xticks:
        self.lines[[0,-3], 2+j] |= Tl|Bl


    for i in range(h-2):

      if i > 0 and i < h-3:
        self.lines[i, [2,-1]] = Tl|Bl

      if h-3-i in yticks:
        self.lines[i, [2,-1]] |= Ll|Rl


    self.lines[0, 2] |= Bl|Rl
    self.lines[0, -1] |= Ll|Bl
    self.lines[-3, -1] |= Tl|Ll
    self.lines[-3, 2] |= Tl|Rl

    for k, (tick, label) in enumerate(zip(xticks, xlabels)):
      if not label:
        continue

      j0, j1, label = pos_center_text(w-2, tick, label)
      self.buf[-2, (j0+2):(j1+2)] = label

    if self.style.xtitle:
      title = self.style.xtitle

      j0, j1, title = pos_center_text(w-2, (w-2)//2, title)
      self.buf[-1, (j0+2):(j1+2)] = title

    if self.style.ytitle:
      title = self.style.ytitle
      title = title.replace('-', '|')
      i0, i1, title = pos_center_text(h-2, (h-2)//2, title)
      self.buf[i0:i1, 0] = title

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def ticks(n, ticks, labels):

  if not ticks:
    return list(), list()

  hi = np.amax(ticks)
  lo = np.amin(ticks)
  f = (n-1) / (hi - lo)
  _ticks = np.minimum(n-1, np.round((np.array(ticks)-lo)*f).astype(np.uint32))

  if isinstance(labels, str):
    labels = [labels.format(x) for x in ticks]

  if labels is None:
    labels = list()

  return _ticks, labels

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def pos_center_text(n, pos, text):

  text = np.array(
    [str(text)],
    dtype = np.unicode_ ).view('U1').reshape(1,-1)[0]

  j0 = max(0, min(pos - len(text)//2, n-len(text)))
  j1 = min(n, j0+len(text))
  lw = j1-j0

  return j0, j1, text[:lw]
