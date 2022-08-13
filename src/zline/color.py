import numpy as np
from colorsys import rgb_to_hls
from collections import namedtuple

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Color = namedtuple('Color', [
  'r', 'g', 'b' ])

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def _rgb_ls(rgb):
  maxc = np.amax(rgb, axis = 1)
  minc = np.amin(rgb, axis = 1)
  sumc = maxc + minc
  rangec = maxc - minc
  l = 0.5 * sumc

  return l, np.where(
    rangec < 1e-6,
    0.0,
    np.where(
      sumc <= 1.0,
      rangec / np.maximum(1e-6, sumc),
      rangec / np.maximum(1e-6, 2.0 - sumc) ))

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def _rgb_to_hls(rgb):
  rgb = np.atleast_2d(rgb)

  maxc = np.amax(rgb, axis = 1)
  minc = np.amin(rgb, axis = 1)
  sumc = maxc + minc
  rangec = maxc - minc
  l = 0.5 * sumc

  s = np.where(
    rangec < 1e-6,
    0.0,
    np.where(
      sumc <= 1.0,
      rangec / sumc,
      rangec / (2.0 - sumc) ))

  r = rgb[:,0]
  rc = (maxc-r) / rangec

  g = rgb[:,1]
  gc = (maxc-g) / rangec

  b = rgb[:,2]
  bc = (maxc-b) / rangec

  h = (1./6.)*np.where(
    r == maxc,
    bc - gc,
    np.where(
      g == maxc,
      2.0+rc-bc,
      4.0+gc-rc ))

  h %= 1.0

  return h, l, s

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
STANDARD = np.array([
  (0, 0, 0),
  (170, 0, 0),
  (0, 170, 0),
  (170, 85, 0),
  (0, 0, 170),
  (170, 0, 170),
  (0, 170, 170),
  (170, 170, 170),
  (85, 85, 85),
  (255, 85, 85),
  (85, 255, 85),
  (255, 255, 85),
  (85, 85, 255),
  (255, 85, 255),
  (85, 255, 255),
  (255, 255, 255) ])

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
LEVELS_8BIT = np.array([0, 95, 135, 175, 215, 255])

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def rgb_from_4bit(n):
  return STANDARD[n]

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def rgb_from_8bit(n):
  if n < 16:
    return rgb_from_4bit(n)

  if n == 16:
    return 0, 0, 0

  if n == 231:
    return 255, 255, 255

  if n >= 232:
    l = 8 + round((230) * (n - 232) / (255 - 232))
    return l, l, l

  n -= 16
  r, n = divmod(n, 36)
  g, b = divmod(n, 6)

  r = LEVELS_8BIT[r]
  g = LEVELS_8BIT[g]
  b = LEVELS_8BIT[b]

  # ( 16 + 36 * round(r * 5.0) + 6 * round(g * 5.0) + round(b * 5.0) )
  return r, g, b

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def std_8bit_lookup():
  lookup = np.zeros((256,), dtype = np.uint8)

  for n in range(256):
    rgb = np.array(rgb_from_8bit(n))
    lookup[n] = np.argmin(np.linalg.norm( STANDARD - rgb, axis = 1 ))

  return lookup

STANDARD_8BIT = std_8bit_lookup()

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def rgb_to_8bit(rgb):
  """https://github.com/Textualize/rich/blob/master/rich/color.py
  """
  rgb = np.atleast_2d(rgb)
  shape = rgb.shape[:-1]
  rgb = rgb.reshape(-1, 3)

  rgb = rgb / 255.0
  r = rgb[:,0]
  g = rgb[:,1]
  b = rgb[:,2]

  l, s = _rgb_ls(rgb)

  gray = np.round( l * 25.0 ).astype(np.uint8)

  gray = np.where(
    gray == 0,
    16,
    np.where(
      gray == 25,
      231,
      231 + gray ) )

  color = (
    16
    + 36 * np.round( r * 5.0 ).astype(np.uint8)
    + 6 * np.round( g * 5.0 ).astype(np.uint8)
    + np.round( b * 5.0 ).astype(np.uint8) )

  return np.where(
    s < 0.1,
    gray,
    color ).reshape(shape)

  # if s < 0.1:
  #   gray = round(l * 25.0)
  #   if gray == 0:
  #     return 16
  #   elif gray == 25:
  #     return 231
  #   else:
  #     return 231 + gray
  #
  # return ( 16 + 36 * round(r * 5.0) + 6 * round(g * 5.0) + round(b * 5.0) )

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def rgb_to_standard(rgb):
  n = rgb_to_8bit(rgb)
  _n = STANDARD_8BIT[n]
  return _n

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def rgb_to_hex(rgb):
  return '#' + ''.join([f"{hex(c)[2:]:0>2}" for c in rgb])

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def hex_to_rgb(chex):
  chex = chex.lstrip('#')

  assert len(chex) in [3, 6]

  if len(chex) == 3:
    return int(chex[0]*2, 16), int(chex[1]*2, 16), int(chex[2]*2, 16)

  return int(chex[:2], 16), int(chex[2:4], 16), int(chex[4:6], 16)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def norm_rgb(rgb):
  if isinstance(rgb, str):
    return hex_to_rgb(rgb)

  rgb = Color(*(max(0, min(255, int(c))) for c in rgb))

  return rgb
