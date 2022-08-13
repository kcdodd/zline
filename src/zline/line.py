import numpy as np

L = 0o1000
Lh = 0o3000
Ld = 0o7000

R = 0o0001
Rh = 0o0003
Rd = 0o0007

T = 0o0100
Th = 0o0300
Td = 0o0700

B = 0o0010
Bh = 0o0030
Bd = 0o0070

_LINES = [
  (L,  '╴'),
  (T,  '╵'),
  (R,  '╶'),
  (B,  '╷'),
  (Lh, '╸'),
  (Th, '╹'),
  (Rh, '╺'),
  (Bh, '╻'),
  (L|R,   '─'),
  (Lh|Rh, '━'),
  (T|B,   '│'),
  (Th|Bh, '┃'),
  (L|Rh,  '╼'),
  (T|Bh,  '╽'),
  (Lh|R,  '╾'),
  (Th|B,  '╿'),
  (R|B, '┌'),
  (Rh|B, '┍'),
  (R|Bh, '┎'),
  (Rh|Bh, '┏'),
  (L|B, '┐'),
  (Lh|B, '┑'),
  (L|Bh, '┒'),
  (Lh|Bh, '┓'),
  (T|R, '└'),
  (T|Rh, '┕'),
  (Th|R, '┖'),
  (Th|Rh, '┗'),
  (L|T, '┘'),
  (Lh|T, '┙'),
  (L|Th, '┚'),
  (Lh|Th, '┛'),
  (T|R|B, '├'),
  (T|Rh|B, '┝'),
  (Th|R|B, '┞'),
  (T|R|Bh, '┟'),
  (Th|R|Bh, '┠'),
  (Th|Rh|B, '┡'),
  (T|Rh|Bh, '┢'),
  (Th|Rh|Bh, '┣'),
  (T|L|B, '┤'),
  (T|Lh|B, '┥'),
  (Th|L|B, '┦'),
  (T|L|Bh, '┧'),
  (Th|L|Bh, '┨'),
  (Th|Lh|B, '┩'),
  (T|Lh|Bh, '┪'),
  (Th|Lh|Bh, '┫'),
  (L|B|R, '┬'),
  (Lh|B|R, '┭'),
  (L|B|Rh, '┮'),
  (Lh|B|Rh, '┯'),
  (L|Bh|R, '┰'),
  (Lh|Bh|R, '┱'),
  (L|Bh|Rh, '┲'),
  (Lh|Bh|Rh, '┳'),
  (L|T|R, '┴'),
  (Lh|T|R, '┵'),
  (L|T|Rh, '┶'),
  (Lh|T|Rh, '┷'),
  (L|Th|R, '┸'),
  (Lh|Th|R, '┹'),
  (L|Th|Rh, '┺'),
  (Lh|Th|Rh, '┻'),
  (L|T|R|B, '┼'),
  (Lh|T|R|B, '┽'),
  (L|T|Rh|B, '┾'),
  (Lh|T|Rh|B, '┿'),
  (L|Th|R|B, '╀'),
  (L|T|R|Bh, '╁'),
  (L|Th|R|Bh, '╂'),
  (Lh|Th|R|B, '╃'),
  (L|Th|Rh|B, '╄'),
  (Lh|T|R|Bh, '╅'),
  (L|T|Rh|Bh, '╆'),
  (Lh|Th|Rh|B, '╇'),
  (Lh|T|Rh|Bh, '╈'),
  (Lh|Th|R|Bh, '╉'),
  (L|Th|Rh|Bh, '╊'),
  (Lh|Th|Rh|Bh, '╋'),
  (Ld|Rd, '═'),
  (Td|Bd, '║'),
  (Rd|B, '╒'),
  (R|Bd, '╓'),
  (Rd|Bd, '╔'),
  (Ld|B, '╕'),
  (L|Bd, '╖'),
  (Ld|Bd, '╗'),
  (T|Rd, '╘'),
  (Td|R, '╙'),
  (Td|Rd, '╚'),
  (Ld|T, '╛'),
  (L|Td, '╜'),
  (Ld|Td, '╝'),
  (T|Rd|B, '╞'),
  (Td|R|Bd, '╟'),
  (Td|Rd|Bd, '╠'),
  (Ld|T|B, '╡'),
  (L|Td|Bd, '╢'),
  (Ld|Td|Bd, '╣'),
  (Ld|Rd|B, '╤'),
  (L|R|Bd, '╥'),
  (Ld|Rd|Bd, '╦'),
  (Ld|T|Rd, '╧'),
  (L|Td|R, '╨'),
  (Ld|Td|Rd, '╩'),
  (Ld|T|Rd|B, '╪'),
  (L|Td|R|Bd, '╫'),
  (Ld|Td|Rd|Bd, '╬') ]

_ROUNDED = [
  (R|B, '╭'),
  (L|B, '╮'),
  (L|T, '╯'),
  (T|R, '╰') ]

LINES = np.zeros((2*4096,), dtype = np.unicode_)
# LINES[:] = '�'
LINES[:] = ' '

for i, c in _LINES:
  LINES[i] = c

LINES[4096:] = LINES[:4096]

for i, c in _ROUNDED:
  LINES[i + 4096] = c

# LINES[L]     = '╴'
# LINES[R]     = '╶'
# LINES[L|R]   = '─'
#
# LINES[T]     = '╵'
# LINES[B]     = '╷'
# LINES[T|B]   = '│'
#
# LINES[R|B] = '╭'
# LINES[L|B] = '╮'
# LINES[T|R] = '╰'
# LINES[T|L] = '╯'
#
# LINES[L|T|R]  = '┴'
#
# LINES[T|R|B] = '├'
# LINES[L|R|B] = '┬'
# LINES[L|T|B] = '┤'
#
# LINES[L|R|T|B] = '┼'
