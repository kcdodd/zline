import sys
import numpy as np
from colorsys import rgb_to_hls

from zline.render import (
  Canvas,
  Box )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
with Canvas(shape=(20,20)) as app:

  app.cells.append( Box(
        pos = (2, 2),
        shape = (8, 8),
        border_color = '#f00' ) )

  app.cells.append( Box(
        pos = (6, 6),
        shape = (8, 8),
        border_color = '#00f' ) )

  # print(app.buf)
  app.render()
  x = input('')

# print("\u001b[0m")
#
# for n in range(256):
#   rgb = rgb_from_8bit(n)
#   _n = STANDARD_8BIT[n]
#   _rgb = STANDARD[ _n ]
#
#   print(
#     fg_8bit(rgb)[0], n, rgb_to_8bit(rgb)[0], rgb, rgb_to_hex(*gb),
#     fg_8bit(_rgb)[0], _n, rgb_to_8bit(_rgb)[0], _rgb, rgb_to_hex(_rgb) )
