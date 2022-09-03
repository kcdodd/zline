import numpy as np
from colorsys import rgb_to_hls
from collections import namedtuple

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Color = namedtuple('Color', [
  'r', 'g', 'b' ])

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
STD_PALETTE = np.array(
  [ [0,0,0],
    [0x80,0,0], [0,0x80,0], [0x80,0x80,0],
    [0,0,0x80], [0x80,0,0x80], [0,0x80,0x80],
    [0xc0,0xc0,0xc0] ],
  dtype = np.uint8 )

COLOR_LEVELS = np.array([0x00, 0x5f, 0x87, 0xaf, 0xd7, 0xff])
COLOR_THRESH = COLOR_LEVELS[:-1] + np.round(np.diff(COLOR_LEVELS)/2)

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def rgb_to_8bit(rgb):
  rgb = np.atleast_2d(rgb)
  shape = rgb.shape[:-1]
  rgb = rgb.reshape(-1, 3)

  # arrays to accumulate the 'best' color index by minimizing the max RGB error
  out = np.zeros(rgb.shape[:1], dtype = np.uint8)
  err = np.zeros(rgb.shape[:1], dtype = np.uint8)

  # find nearest standard color
  # the first 0-7 colors are combinations of RGB
  # use 0x80 as the threshold for setting each RGB to true/false
  # the next 8-15 are duplicated in the >15 'non-standard' colors
  out[:] = (rgb[:,0] >= 0x80) + 2*(rgb[:,1] >= 0x80) + 4*(rgb[:,2] >= 0x80)
  err[:] = np.amax( np.abs(STD_PALETTE[out] - rgb), axis = 1 )

  # Divide the 6x6x6 color block by thresholds 'centered' between each level
  # searchsorted returns which of these ranges the input falls into
  ilvl = np.searchsorted(COLOR_THRESH, rgb)
  # compute the resulting error using the actual levels
  color_err = np.amax( np.abs(COLOR_LEVELS[ilvl] - rgb), axis = 1 )

  out[:] = np.where(
    color_err <= err,
    # convert the individual RGB levels to the index into the 6x6x6 block,
    # offset by the starting index 16
    16 + ilvl[:,2] + 6*ilvl[:,1] + 36*ilvl[:,0],
    out )
  err[:] = np.minimum(color_err, err)

  # Divide the grayscale levels, and normalize the input value to a 'lightness'
  # defined by the average between the highest and lowest RGB value
  l = (np.amax(rgb, axis = 1) + np.amin(rgb, axis = 1)) // 2
  # threshold is 'centered' between each gray level, width of 10
  # the first gray level is 8, so will match any lightness from (8-5) to (8+4)
  idx = (l - 3)//10

  gray_err = np.amax(
    np.abs(np.where( l < 3, 0, 8 + 10*idx )[:,None] - rgb),
    axis = 1 )

  out[:] = np.where(
    gray_err <= err,
    # offset to output index in the gray levels >=232
    # lightness < 3 is mapped to output index 16 (black)
    np.where( l < 3, 16, 232 + idx ),
    out )
  err[:] = np.minimum(gray_err, err)

  return out.reshape(shape)

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
