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

  xtitle : str = ''
  xticks : list[float] = tuple()
  xlabels : list[str] = '{:g}'

  ytitle : str = ''
  yticks : list[float] = tuple()
  ylabels : list[str] = '{:g}'

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
        h,w = max_shape

        xticks, xlabels, yticks, ylabels = self.style.ticks(w-2, h-2)
        aw = max(len(l) for l in ylabels) if ylabels else 1
        aw += 2
        _max_shape = Shape(*[s-d for s,d in zip(max_shape, (4, aw))])

        shape = self.graph.min_shape(_max_shape)
        return [s+d for s,d in zip(shape, (4, aw))]

    return self._init_shape

  #-----------------------------------------------------------------------------
  def set_shape(self, max_shape):
    if self._init_shape is not None:
      max_shape = [min(s,m) for s,m in zip(self._init_shape, max_shape)]

    h,w = max_shape
    xticks, xlabels, yticks, ylabels = self.style.ticks(w-2, h-2)
    aw = max(len(l) for l in ylabels) if ylabels else 1
    aw += 2
    _max_shape = Shape(*[s-d for s,d in zip(max_shape, (4, aw))])

    self.graph.set_shape(_max_shape)

    self.shape = max_shape

  #-----------------------------------------------------------------------------
  def render(self):
    self.buf[:] = '\0'

    self.graph.render()
    h,w = self.shape
    xticks, xlabels, yticks, ylabels = self.style.ticks(self.graph.shape[1]+2, h-2)
    al = max(len(l) for l in ylabels) if ylabels else 1

    i0 = 2
    i1 = h-2

    j0 = 1 + al
    j1 = w-1

    self.buf[i0:i1, j0:j1] = self.graph.buf
    self.fg[i0:i1, j0:j1] = self.graph.fg
    self.bg[i0:i1, j0:j1] = self.graph.bg
    self.flags[i0:i1, j0:j1] = self.graph.flags

    for j in range(w-j0+1):
      if j > 0 and j < w-j0:
        self.lines[[1,-2], j0-1+j] = Ll|Rl

      if j in xticks:
        self.lines[[1,-2], j0-1+j] |= Tl|Bl


    for i in range(h-2):

      if i > 0 and i < h-3:
        self.lines[i+1, [j0-1, -1]] = Tl|Bl

      if h-3-i in yticks:
        self.lines[i+1, [j0-1, -1]] |= Ll|Rl


    self.lines[1, j0-1] |= Bl|Rl
    self.lines[1, -1] |= Ll|Bl
    self.lines[-2, -1] |= Tl|Ll
    self.lines[-2, j0-1] |= Tl|Rl

    for k, (tick, label) in enumerate(zip(xticks, xlabels)):
      if not label:
        continue

      k0, k1, label = pos_center_text(w-j0+1, tick, label)
      self.buf[-1, (j0-1+k0):(j0-1+k1)] = label

    for k, (tick, label) in enumerate(zip(yticks, ylabels)):
      if not label:
        continue

      self.buf[h-2-tick, (j0-1-len(label)):(j0-1)] = text_array(label)

    title = self.style.ytitle + ' / ' + self.style.xtitle

    k0, k1, title = pos_center_text(w, w//2, title)
    self.buf[0, k0:k1] = title

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def ticks(n, ticks, labels):

  if ticks is None or len(ticks) == 0:
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
def text_array(text):
  return np.array(
    [str(text)],
    dtype = np.unicode_ ).view('U1').reshape(1,-1)[0]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def pos_center_text(n, pos, text):

  text = text_array(text)

  j0 = max(0, min(pos - len(text)//2, n-len(text)))
  j1 = min(n, j0+len(text))
  lw = j1-j0

  return j0, j1, text[:lw]
