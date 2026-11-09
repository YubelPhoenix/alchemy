#!/usr/bin/env python3
"""Build the "???" commander's overworld sprite (SPR_490) from the game's own
silver-haired man in a black suit (SPR_167, SPRITE_MAN_IN_BLACK_SUIT), so she
has the look of the other characters: the same size, shading and animation
frames.  Only his gold buttons and his blue eyes are recoloured, red.

(Her walking sheet, assets/mystery/overworld, is drawn at four times the
game's scale and shrank to mud at 32x32; a hand-painted copy looked nothing
like Golden Sun.)

Three frames make one pose, as for the villagers: front, side and back,
picked from the way an actor faces (games/tbs/src/field/facing.c).  She never
walks, so only the first pose, frames 0-2, is kept.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "games/tbs/src/graphics/sprite/spr_167.png"
DEST = ROOT / "games/tbs/src/graphics/sprite/spr_490.png"
FRAME = 32
FRAMES = 3

# Palette indices of the shared sprite palette: his yellows and blues become
# the reds she wears (56,56,0 -> 56,0,0; 112,112,56 -> 112,0,0; ...).
RECOLOUR = {36: 18, 51: 12, 58: 31, 59: 44, 52: 46, 211: 12,
            37: 18, 80: 31, 123: 47}

base = Image.open(BASE)
assert base.size[0] == FRAME
indices = np.asarray(base)[:FRAME * FRAMES].copy()
for old, new in RECOLOUR.items():
    indices[indices == old] = new
sheet = Image.fromarray(indices, "P")
sheet.putpalette(base.getpalette())
assert sheet.size == (FRAME, FRAME * FRAMES)
sheet.save(DEST, optimize=False)
print(f"Rebuilt {DEST.relative_to(ROOT)}: {FRAMES} frames")
