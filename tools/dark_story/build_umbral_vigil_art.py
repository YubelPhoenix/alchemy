#!/usr/bin/env python3
"""Build the Vigil's weeping statue (SPR_507) from the wreathed maiden statue
(SPR_258).

The statue is turned to dark, damp grey stone (her wreath and flowers too, dead),
her eyes become dark sockets and two dark streaks run from them down her
cheeks, as if the stone has been weeping. Frame 0 is her at rest; frame 1,
the pose she is found in once she has moved, has the sockets wider and her
mouth open. The Vigil (scene/umbral_rift.c) swaps to frame 1 when she first
moves while the leader's back is turned.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPR = ROOT / "games/tbs/src/graphics/sprite"
STONE = [(40, 218), (56, 13), (80, 219), (96, 220), (128, 222), (152, 14)]
SOCKET, STREAK = 1, 218

base = Image.open(SPR / "spr_258.png")
pal = base.getpalette()
src = np.asarray(base)
assert src.shape == (64, 32), src.shape


def stone(frame):
    out = frame.copy()
    for y in range(64):
        for x in range(32):
            v = int(frame[y, x])
            if v:
                r, g, b = pal[3 * v:3 * v + 3]
                # Damp, dark stone: her lights at two thirds.
                light = (0.3 * r + 0.59 * g + 0.11 * b) * 0.62
                out[y, x] = min(STONE, key=lambda s: abs(s[0] - light))[1]
    return out


def weep(frame, screaming):
    out = frame.copy()
    for y in (29, 30):                       # the sockets
        for x in ((12, 13, 17, 18) if not screaming else
                  (11, 12, 13, 17, 18, 19)):
            out[y, x] = SOCKET
    for y in range(31, 38):                  # the streaks
        out[y, 12 if y % 3 else 13] = STREAK
        out[y, 18 if y % 3 else 17] = STREAK
    if screaming:                            # the open mouth
        for y in (32, 33, 34):
            out[y, 15] = SOCKET
            out[y, 16] = SOCKET
    return out


rest = weep(stone(src), False)
moved = weep(stone(src), True)
sheet = Image.fromarray(np.vstack([rest, moved]), "P")
sheet.putpalette(pal)
sheet.save(SPR / "spr_507.png", optimize=False)
(SPR / "spr_507.tsv").write_text(
    "anim\tframe 0 6, hold\n"
    "anim\tframe 0 90, loop\n"
    "anim\tframe 1 6, hold\n")
print("Built spr_507.png: the weeping statue, at rest and moved")
