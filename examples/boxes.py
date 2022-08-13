import sys
import numpy as np
from colorsys import rgb_to_hls

from zline import (
  Weight,
  BorderStyle,
  TextStyle,
  TextWrapper,
  Canvas,
  TextBox )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
with Canvas(shape=(20,20)) as app:

  app.cells.append( TextBox(
    pos = (2, 2),
    shape = (8, 10),
    text = "hello",
    style = TextStyle(
      color = '#ffcf00'),
    border = BorderStyle(
      color = '#ff4500',
      weight = Weight.H ) ) )

  app.cells.append( TextBox(
    pos = (5, 6),
    shape = (8, 8),
    text = "world",
    style = TextStyle(
      color = '#00c9ff'),
    border = BorderStyle(
      color = ['#3300ff', '#f200ff', '#ebff00', '#00ff85'],
      weight = [Weight.D, Weight.S, Weight.D, Weight.S] ) ) )

  app.cells.append( TextBox(
    pos = (7, 4),
    shape = (5, 5),
    border = BorderStyle(
      color = '#00ff8c',
      weight = Weight.S,
      rounded = True,
      intersect = True ) ) )

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
