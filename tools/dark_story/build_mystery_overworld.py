#!/usr/bin/env python3
"""Build the "???" commander's overworld sprite (SPR_490) from Menardi's
(SPR_033), so she reads as a woman, has the look of the other characters (the
same size, shading and frames) and matches her own art (assets/mystery): long
silver hair, a black coat, a red band across the brow.

  - Menardi's yellow hair becomes silver: each hair colour goes to the grey of
    its brightness (60 to 255).
  - Her red and pink dress becomes the black coat: each to a dark grey of its
    brightness (10 to 120); her two brightest reds become a dark red trim.
  - Her face keeps its shading in the party's skin tones (Isaac's and Mia's
    palette entries); the red band across her brow stays red.

(Her walking sheet, assets/mystery/overworld, is drawn at four times the
game's scale and shrinks to mud at 32x32. An earlier sprite borrowed the
silver-haired man in black, SPR_167, and read as a man.)

Three frames make one pose, as for the villagers: front, side and back,
picked from the way an actor faces (games/tbs/src/field/facing.c).  She never
walks, so only the first pose, frames 0-2, is kept.
"""
import colorsys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "games/tbs/src/graphics/sprite/spr_033.png"
DEST = ROOT / "games/tbs/src/graphics/sprite/spr_490.png"
FRAME = 32
FRAMES = 3

# The shared sprite palette's greys, (brightness, index), and the party's
# skin tones.
GREYS = [(0, 1), (24, 217), (40, 218), (56, 13), (80, 219), (96, 220),
         (112, 87), (128, 222), (152, 14), (176, 130), (200, 223), (224, 173),
         (248, 15)]
SKIN = [(140, 88), (175, 95), (195, 131), (215, 138), (240, 180)]
TRIM = 12          # (112, 0, 0), dark red
BRIGHT_REDS = {(248, 0, 0), (224, 0, 0)}
BROW_REDS = {12, 31}

base = Image.open(BASE)
assert base.size[0] == FRAME
src = np.asarray(base)[:FRAME * FRAMES].copy()
raw = base.getpalette()
pal = [tuple(raw[3 * i:3 * i + 3]) for i in range(len(raw) // 3)]


def nearest(ramp, level):
    return min(ramp, key=lambda e: abs(e[0] - level))[1]


def recolour(index, x, y):
    if index in (0, 1):
        return index
    r, g, b = (c / 255 for c in pal[index])
    hue, sat, val = colorsys.rgb_to_hsv(r, g, b)
    hue *= 360
    light = (0.3 * r + 0.59 * g + 0.11 * b) * 255
    frame, row = divmod(y, FRAME)
    reddish = hue >= 290 or hue < 40
    # Her face (front frame): pinks keep their shading as skin.
    if (frame == 0 and 11 <= row <= 16 and 13 <= x <= 20
            and (hue >= 290 or hue < 15) and val > 0.5 and sat > 0.15):
        return nearest(SKIN, light)
    # The red band across her brow.
    if frame == 0 and 9 <= row <= 10 and 14 <= x <= 19 and index in BROW_REDS:
        return index
    if sat < 0.15:
        return index                      # whites and greys stay
    if not reddish or (15 <= hue < 40 and val > 0.8 and sat < 0.7):
        return nearest(GREYS, 60 + (255 - 60) * light / 255)   # hair
    if pal[index] in BRIGHT_REDS:
        return TRIM
    return nearest(GREYS, 10 + (120 - 10) * light / 255)       # coat


out = src.copy()
for y in range(src.shape[0]):
    for x in range(src.shape[1]):
        out[y, x] = recolour(int(src[y, x]), x, y)

sheet = Image.fromarray(out, "P")
sheet.putpalette(raw)
assert sheet.size == (FRAME, FRAME * FRAMES)
sheet.save(DEST, optimize=False)
print(f"Rebuilt {DEST.relative_to(ROOT)}: {FRAMES} frames")
