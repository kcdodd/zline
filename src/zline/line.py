import numpy as np

L = 0b1000
R = 0b0001
T = 0b0100
B = 0b0010

# [ L,  '╴',
#   T,  '╵',
#   R,  '╶',
#   B,  '╷',
#   Lh, '╸',
#   Th, '╹',
#   Rh, '╺',
#   Bh, '╻'
#   L|R,   '─',
#   Lh|Rh, '━',
#   T|B,   '│',
#   Th|Bh, '┃',
#   L|Rh,  '╼',
#   T|Bh,  '╽',
#   Lh|R,  '╾',
#   Th|B,  '╿',

# '┌', '┍', '┎', '┏', '╒', '╓', '╔'
#
# '┐', '┑', '┒', '┓', '└', '┕', '┖', '┗', '┘', '┙', '┚', '┛', '├', '┝', '┞', '┟',
# '┠', '┡', '┢', '┣', '┤', '┥', '┦', '┧', '┨', '┩', '┪', '┫', '┬', '┭', '┮', '┯',
# '┰', '┱', '┲', '┳', '┴', '┵', '┶', '┷', '┸', '┹', '┺', '┻', '┼', '┽', '┾', '┿',
# '╀', '╁', '╂', '╃', '╄', '╅', '╆', '╇', '╈', '╉', '╊', '╋',
# '═', '║', '╕', '╖', '╗', '╘', '╙', '╚', '╛', '╜', '╝', '╞', '╟',
# '╠', '╡', '╢', '╣', '╤', '╥', '╦', '╧', '╨', '╩', '╪', '╫', '╬',
# '╭', '╮', '╯', '╰',

LINES = np.zeros((16,), dtype = np.unicode_)
LINES[:] = ' '

LINES[L]     = '╴'
LINES[R]     = '╶'
LINES[L|R]   = '─'

LINES[T]     = '╵'
LINES[B]     = '╷'
LINES[T|B]   = '│'

LINES[R|B] = '╭'
LINES[L|B] = '╮'
LINES[T|R] = '╰'
LINES[T|L] = '╯'

LINES[L|T|R]  = '┴'

LINES[T|R|B] = '├'
LINES[L|R|B] = '┬'
LINES[L|T|B] = '┤'

LINES[L|R|T|B] = '┼'