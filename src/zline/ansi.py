import numpy as np
from itertools import compress

from .color import (
  rgb_to_standard,
  rgb_to_8bit )

from .tile import Flags

FLAGS = [
  Flags.B.value,
  Flags.D.value,
  Flags.I.value,
  Flags.U.value,
  Flags.K.value ]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def goto(i, j):
  return f"\x1b[{i};{j}H"

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def move(di, dj):
  res = ''

  if di > 0:
    res += f"\x1b[{di}A"
  elif di < 0:
    res += f"\x1b[{di}B"

  if dj > 0:
    res += f"\x1b[{dj}C"
  elif dj < 0:
    res += f"\x1b[{dj}D"

  return res

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def reset_style():
  return f"\x1b[0m"

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def fg_reset():
  return "39"

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def fg_standard(rgb):
  n = rgb_to_standard(rgb)
  return [
    f"{30+_n}"
    for _n in n ]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def fg_8bit(rgb):
  n = rgb_to_8bit(rgb)
  return [
    f"38;5;{_n}"
    for _n in n ]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def fg_24bit(rgb):
  rgb = np.atleast_2d(rgb)
  return [
    f"38;2;{r};{g};{b}"
    for r, g, b in rgb ]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def bg_reset():
  return "49"

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def bg_standard(rgb):
  n = rgb_to_standard(rgb)
  return [
    f"{40+_n}"
    for _n in n ]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def bg_8bit(rgb):
  n = rgb_to_8bit(rgb)

  return [
    f"48;5;{_n}"
    for _n in n ]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def bg_24bit(rgb):
  rgb = np.atleast_2d(rgb)

  return [
    f"48;2;{r};{g};{b}"
    for r, g, b in rgb ]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def flags(flags):
  # TODO: generate lookup
  return [
    ';'.join([ str(i+(1 if (fl & f) else 22)) for i,fl in enumerate(FLAGS) ])
    for f in flags ]

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
