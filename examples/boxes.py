import sys
import numpy as np
from colorsys import rgb_to_hls

from zline import (
  Weight,
  BorderStyle,
  TextStyle,
  TextWrapper,
  Canvas,
  Text,
  Box )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
with Canvas(shape=(20,20), alt = True) as app:

  app.content.append( Box(
    pos = (2, 2),
    shape = (8, 10),
    content = Text(
      shape = (6, 8),
      text = "hello",
      style = TextStyle(
        color = '#ffcf00')),
    border = BorderStyle(
      color = '#ff4500',
      weight = Weight.H ) ) )

  app.content.append( Box(
    pos = (5, 6),
    shape = (8, 8),
    content = Text(
      shape = (6, 6),
      text = "world",
      style = TextStyle(
        color = '#00c9ff') ),
    border = BorderStyle(
      color = ['#3300ff', '#f200ff', '#ebff00', '#00ff85'],
      weight = [Weight.D, Weight.S, Weight.D, Weight.S] ) ) )

  app.content.append( Box(
    pos = (7, 4),
    shape = (5, 5),
    border = BorderStyle(
      color = '#00ff8c',
      weight = Weight.S,
      rounded = True,
      intersect = True ) ) )

  # print(app.buf)
  app.render()
  app.flush()
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
