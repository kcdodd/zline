import sys
import numpy as np
import time
from zline.line import (
  QUADS,
  SQUADS,
  Qa, Qb, Qc, Qd )

from zline import (
  Weight,
  BorderStyle,
  TextStyle,
  TextWrapper,
  Canvas,
  Plot )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
with Canvas(shape=(20,80), alt = False) as app:
  x = np.linspace(0, 4*np.pi, 100)
  y = np.sin(x)

  app.content.append( Plot(
    xy = (x, y) ))

  app.set_shape(app.min_shape())
  app.render()
  app.flush()

# buf = np.zeros(
#   (20, 80),
#   dtype = np.unicode_ )
#
# buf[:] = ' '
#
# lx = 2.0
# nx = 2*buf.shape[1]
# ny = 2*buf.shape[0]
# dx = lx / nx
#
# x = dx * (0.5 + np.arange(nx))
#
# y = x**2
#
# ly = np.amax(y)
# dy = ly / nx
#
# yq = y/dy
# yi = ny-1 - np.minimum(ny-1, np.round(yq).astype(np.int16) )
# # yi = yi[::-1]
#
# xi = np.arange(nx)
#
# mask = np.zeros((ny,nx), dtype = np.uint8)
#
# mask[yi, xi] = True
#
# n = np.zeros((ny,nx), dtype = np.uint8)
# n[::2,::2] = Qa
# n[::2,1::2] = Qb
# n[1::2,1::2] = Qc
# n[1::2,::2] = Qd
# n = np.where(mask, n, 0)
# n = n[::2,::2] | n[::2,1::2] | n[1::2,1::2] | n[1::2,::2]
#
# print(yi)
# print('\n'.join([''.join(['1' if m else ' ' for m in mr]) for mr in mask[:10,:40] ]))
#
#
# buf[:] = QUADS[n]
#
# print('\n'.join([''.join(l) for l in buf]))
