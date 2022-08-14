import numpy as np
from collections import namedtuple
from dataclasses import dataclass, field, asdict, fields
import sys

from .color import (
  Color,
  norm_rgb )

from .line import (
  T, R, B, L,
  LINES,
  Weight )

BORDER_WEIGHTS = list(zip(T,R,B,L))

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
BorderSpec = namedtuple('BorderSpec', [
  'top', 'right', 'bottom', 'left'])

# margin
# border
# padding
# content

#+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
@dataclass
class BorderStyle:
  # top, right, bottom, left
  weight : BorderSpec[Weight] = BorderSpec(*[Weight.N]*4)
  margin : BorderSpec[int] = BorderSpec(*[0]*4)
  padding : BorderSpec[int] = BorderSpec(*[0]*4)
  color : BorderSpec[Color] = BorderSpec(*[Color(255, 255, 255)]*4)
  intersect : BorderSpec[bool] = BorderSpec(*[False]*4)
  # NOTE: Only supported if all weights are 'S' (single) or 'N' (none)
  rounded : bool = False

  #-----------------------------------------------------------------------------
  def __post_init__(self):
    for attr in ['weight', 'margin', 'padding', 'color', 'intersect']:
      v = getattr(self, attr)

      if not isinstance(v, (list,tuple)):
        v = [v]*4

      setattr(self, attr, BorderSpec(*v))

    self.color = BorderSpec(*[Color(*norm_rgb(c)) for c in self.color])

    assert not self.rounded or all(w.value <= Weight.S.value for w in self.weight)

  #-----------------------------------------------------------------------------
  def borders(self):
    return BorderSpec(*[ w != Weight.N for w in self.weight ])

  #-----------------------------------------------------------------------------
  def spc(self):
    return BorderSpec(*(
      min(1, w.value) + m + p
      for w, m, p in zip(self.weight, self.margin, self.padding) ))

  #-----------------------------------------------------------------------------
  def interior(self):
    tT, tR, tB, tL = BORDER_WEIGHTS[self.weight.top.value]
    rT, rR, rB, rL = BORDER_WEIGHTS[self.weight.right.value]
    bT, bR, bB, bL = BORDER_WEIGHTS[self.weight.bottom.value]
    lT, lR, lB, lL = BORDER_WEIGHTS[self.weight.left.value]

    idx = np.array([
      [lB|tR, tL|tR, tL|rB],
      [lT|lB, 0o000, rT|rB],
      [lT|bR, bL|bR, bL|rT] ],
      dtype = np.uint16 )

    if self.rounded:
      idx += 0o10000

    return idx

  #-----------------------------------------------------------------------------
  def exterior(self):
    idx = np.zeros((3,3), dtype = np.uint16)

    Td, Rd, Bd, Ld = BORDER_WEIGHTS[Weight.D.value]

    if self.intersect.top:
      idx[0,:] |= Td|Ld|Rd

    if self.intersect.right:
      idx[:,-1] |= Rd|Td|Bd

    if self.intersect.bottom:
      idx[-1,:] |= Bd|Ld|Rd

    if self.intersect.left:
      idx[:,0] |= Ld|Td|Bd

    return idx
