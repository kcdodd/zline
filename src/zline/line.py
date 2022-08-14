import numpy as np
from enum import Enum

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class Weight(Enum):
  N = 0
  S = 1
  H = 2
  D = 3

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# The indexing for box drawing character lookup is constructed by forming
# connections between the four sides of a character cell.
# ┌--T──┐
# │     │
# L     R
# │     │
# └──B──┘
# Connections are formed by taking the bit-wise 'or' of the elemental constants
# Ll, Rl, Tl, B.
# Heavy and double lines are added using a 3-bit field for each of the four
# constants, resulting in a total of 12bits per character field to define the
# connections and the weight of the formed line(s).
# The constants are chosen so that a bit-wise 'or' will result in a line that
# maintains maximum line thickness.
# light | light -> light
# light | heavy -> heavy
# heavy | double -> double
# light | double -> double

# constants defined using 4x 'octal' (3-bit) number
# h: heavy, d: double

# top
Tn = 0o0000
Tl = 0o1000
Th = 0o3000
Td = 0o7000
T = [Tn, Tl, Th, Td]

# right
Rn = 0o0000
Rl = 0o0100
Rh = 0o0300
Rd = 0o0700
R = [Rn, Rl, Rh, Rd]

# bottom
Bn = 0o0000
Bl = 0o0010
Bh = 0o0030
Bd = 0o0070
B = [Bn, Bl, Bh, Bd]

# left
Ln = 0o0000
Ll = 0o0001
Lh = 0o0003
Ld = 0o0007
L = [Ln, Ll, Lh, Ld]

# arc
A = 0o10000

_LINES = [
  (Ll, '╴'),
  (Tl, '╵'),
  (Rl, '╶'),
  (Bl, '╷'),
  (Lh, '╸'),
  (Th, '╹'),
  (Rh, '╺'),
  (Bh, '╻'),
  (Ll|Rl, '─'),
  (Lh|Rh, '━'),
  (Tl|Bl, '│'),
  (Th|Bh, '┃'),
  (Ll|Rh, '╼'),
  (Tl|Bh, '╽'),
  (Lh|Rl, '╾'),
  (Th|Bl, '╿'),
  (Rl|Bl, '┌'),
  (Rh|Bl, '┍'),
  (Rl|Bh, '┎'),
  (Rh|Bh, '┏'),
  (Ll|Bl, '┐'),
  (Lh|Bl, '┑'),
  (Ll|Bh, '┒'),
  (Lh|Bh, '┓'),
  (Tl|Rl, '└'),
  (Tl|Rh, '┕'),
  (Th|Rl, '┖'),
  (Th|Rh, '┗'),
  (Ll|Tl, '┘'),
  (Lh|Tl, '┙'),
  (Ll|Th, '┚'),
  (Lh|Th, '┛'),
  (Tl|Rl|Bl, '├'),
  (Tl|Rh|Bl, '┝'),
  (Th|Rl|Bl, '┞'),
  (Tl|Rl|Bh, '┟'),
  (Th|Rl|Bh, '┠'),
  (Th|Rh|Bl, '┡'),
  (Tl|Rh|Bh, '┢'),
  (Th|Rh|Bh, '┣'),
  (Tl|Ll|Bl, '┤'),
  (Tl|Lh|Bl, '┥'),
  (Th|Ll|Bl, '┦'),
  (Tl|Ll|Bh, '┧'),
  (Th|Ll|Bh, '┨'),
  (Th|Lh|Bl, '┩'),
  (Tl|Lh|Bh, '┪'),
  (Th|Lh|Bh, '┫'),
  (Ll|Bl|Rl, '┬'),
  (Lh|Bl|Rl, '┭'),
  (Ll|Bl|Rh, '┮'),
  (Lh|Bl|Rh, '┯'),
  (Ll|Bh|Rl, '┰'),
  (Lh|Bh|Rl, '┱'),
  (Ll|Bh|Rh, '┲'),
  (Lh|Bh|Rh, '┳'),
  (Ll|Tl|Rl, '┴'),
  (Lh|Tl|Rl, '┵'),
  (Ll|Tl|Rh, '┶'),
  (Lh|Tl|Rh, '┷'),
  (Ll|Th|Rl, '┸'),
  (Lh|Th|Rl, '┹'),
  (Ll|Th|Rh, '┺'),
  (Lh|Th|Rh, '┻'),
  (Ll|Tl|Rl|Bl, '┼'),
  (Lh|Tl|Rl|Bl, '┽'),
  (Ll|Tl|Rh|Bl, '┾'),
  (Lh|Tl|Rh|Bl, '┿'),
  (Ll|Th|Rl|Bl, '╀'),
  (Ll|Tl|Rl|Bh, '╁'),
  (Ll|Th|Rl|Bh, '╂'),
  (Lh|Th|Rl|Bl, '╃'),
  (Ll|Th|Rh|Bl, '╄'),
  (Lh|Tl|Rl|Bh, '╅'),
  (Ll|Tl|Rh|Bh, '╆'),
  (Lh|Th|Rh|Bl, '╇'),
  (Lh|Tl|Rh|Bh, '╈'),
  (Lh|Th|Rl|Bh, '╉'),
  (Ll|Th|Rh|Bh, '╊'),
  (Lh|Th|Rh|Bh, '╋'),
  (Ld|Rd, '═'),
  (Td|Bd, '║'),
  (Rd|Bl, '╒'),
  (Rl|Bd, '╓'),
  (Rd|Bd, '╔'),
  (Ld|Bl, '╕'),
  (Ll|Bd, '╖'),
  (Ld|Bd, '╗'),
  (Tl|Rd, '╘'),
  (Td|Rl, '╙'),
  (Td|Rd, '╚'),
  (Ld|Tl, '╛'),
  (Ll|Td, '╜'),
  (Ld|Td, '╝'),
  (Tl|Rd|Bl, '╞'),
  (Td|Rl|Bd, '╟'),
  (Td|Rd|Bd, '╠'),
  (Ld|Tl|Bl, '╡'),
  (Ll|Td|Bd, '╢'),
  (Ld|Td|Bd, '╣'),
  (Ld|Rd|Bl, '╤'),
  (Ll|Rl|Bd, '╥'),
  (Ld|Rd|Bd, '╦'),
  (Ld|Tl|Rd, '╧'),
  (Ll|Td|Rl, '╨'),
  (Ld|Td|Rd, '╩'),
  (Ld|Tl|Rd|Bl, '╪'),
  (Ll|Td|Rl|Bd, '╫'),
  (Ld|Td|Rd|Bd, '╬') ]

_ARCS = [
  (A|Rl|Bl, '╭'),
  (A|Ll|Bl, '╮'),
  (A|Ll|Tl, '╯'),
  (A|Tl|Rl, '╰') ]

LINES = np.zeros((2*4096,), dtype = np.unicode_)
# LINES[:] = '�'
# LINES[:] = ' '
LINES[:] = '\0'

for i, c in _LINES:
  LINES[i] = c

# NOTE: the 'arc' flag doubles the space of lines, but re-uses 'non-arcs' for
# all but the four 'corners'
LINES[4096:] = LINES[:4096]

for i, c in _ARCS:
  LINES[i] = c

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
BLOCKS = [
  '▀',
  '▁',
  '▂',
  '▃',
  '▄',
  '▅',
  '▆',
  '▇',
  '█',
  '▉',
  '▊',
  '▋',
  '▌',
  '▍',
  '▎',
  '▏',
  '▐',
  '░',
  '▒',
  '▓',
  '▔',
  '▕', ]


Qa = 0b0001
Qb = 0b0010
Qc = 0b0100
Qd = 0b1000

_QUADS = [
  (Qa, '▘'),
  (Qb, '▝'),
  (Qc, '▗'),
  (Qd, '▖'),
  (Qa|Qb, '▀'),
  (Qc|Qb, '▐'),
  (Qc|Qd, '▄'),
  (Qa|Qd, '▌'),
  (Qa|Qc, '▚'),
  (Qd|Qb, '▞'),
  (Qa|Qb|Qc, '▜'),
  (Qd|Qb|Qc, '▟'),
  (Qa|Qd|Qc, '▙'),
  (Qa|Qb|Qd, '▛'),
  (Qa|Qb|Qc|Qd, '█') ]

QUADS = np.zeros((16,), dtype = np.unicode_)
QUADS[0] = ' '

SQUADS = np.zeros((16,), dtype = np.unicode_)
SQUADS[0] = ' '

for j, (i, c) in enumerate(_QUADS):
  SQUADS[j] = c
  QUADS[i] = c
