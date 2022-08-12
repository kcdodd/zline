import numpy as np
from .color import (
  rgb_to_standard,
  rgb_to_8bit )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def goto(i, j):
  return f"\u001b[{i};{j}H"

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def move(di, dj):
  res = ''

  if di > 0:
    res += f"\u001b[{di}A"
  elif di < 0:
    res += f"\u001b[{di}B"

  if dj > 0:
    res += f"\u001b[{dj}C"
  elif dj < 0:
    res += f"\u001b[{dj}D"

  return res


#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def fg_standard(rgb):
  n = rgb_to_standard(rgb)
  return [
    f"\u001b[{30+_n}m"
    for _n in n ]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def fg_8bit(rgb):
  n = rgb_to_8bit(rgb)
  return [
    f"\u001b[38;5;{_n}m"
    for _n in n ]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def fg_24bit(rgb):
  rgb = np.atleast_2d(rgb)
  return [
    f"\u001b[38;2;{r};{g};{b}m"
    for r, g, b in rgb ]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
FG = {
  4 : fg_standard,
  8 : fg_8bit,
  24 : fg_24bit }
