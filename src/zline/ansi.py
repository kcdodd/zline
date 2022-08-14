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
def reset_style():
  return f"\u001b[0m"

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
def bg_standard(rgb):
  n = rgb_to_standard(rgb)
  return [
    f"\u001b[{40+_n}m"
    for _n in n ]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def bg_8bit(rgb, reset_rgb = None ):
  n = rgb_to_8bit(rgb)

  if reset_rgb is None:
    return [
      f"\u001b[48;5;{_n}m"
      for _n in n ]

  else:
    reset_n = rgb_to_8bit(reset_rgb)

    return [
      f"\u001b[48;5;{_n}m" if _n != reset_n else "\u001b[49m"
      for _n in n ]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def bg_24bit(rgb, reset_rgb = None ):
  rgb = np.atleast_2d(rgb)

  if reset_rgb is None:
    return [
      f"\u001b[48;2;{r};{g};{b}m"
      for r, g, b in rgb ]

  else:
    return [
      f"\u001b[48;2;{r};{g};{b}m" if (r,g,b) != reset_rgb else "\u001b[49m"
      for r, g, b in rgb ]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
FG = {
  4 : fg_standard,
  8 : fg_8bit,
  24 : fg_24bit }

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
BG = {
  4 : bg_standard,
  8 : bg_8bit,
  24 : bg_24bit }
