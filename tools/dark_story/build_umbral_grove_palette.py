#!/usr/bin/env python3
"""Kolima's colours as the Rift remembers them (pal_umbral_grove.png, from
tileset set_29's palette): a village where wood and skin are one thing.

Every colour keeps its place and brightness order, so Kolima's great stumps
read at a glance, but: the bark of the stumps and roots is the colour of
skin, pink-grey and bruised in its shadows; the grass is bone-pale; the
leaves of the forest around are dead grey; and the village's red doors and
autumn reds go to the dark red of meat.
"""
import colorsys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "games/tbs/src/graphics/tileset/set_29/palette.png"
DST = ROOT / "games/tbs/src/graphics/tileset/palettes/pal_umbral_grove.png"

im = Image.open(SRC)
pal = im.getpalette()
out = list(pal)
w, h = im.size
px = im.load()
for y in range(h):
    for x in range(w):
        i = px[x, y]
        r, g, b = (v / 255 for v in pal[3 * i:3 * i + 3])
        hue, sat, val = colorsys.rgb_to_hsv(r, g, b)
        if x == 0 or val < 0.06:
            continue
        if sat < 0.12:                       # greys, whites
            nh, ns, nv = 0.05, 0.06, 0.10 + val * 0.70
        elif 0.24 <= hue < 0.47:             # grass, leaves
            if val > 0.6:                    # light grass: bone
                nh, ns, nv = 0.12, 0.10, 0.32 + val * 0.45
            else:                            # dark foliage: dead grey
                nh, ns, nv = 0.62, 0.07, 0.04 + val * 0.36
        elif 0.47 <= hue < 0.75:             # water, sky: grey murk
            nh, ns, nv = 0.95, 0.12, 0.06 + val * 0.35
        elif 0.05 <= hue < 0.24:             # bark, roots, paths: skin
            nh, ns, nv = 0.03, 0.18 + sat * 0.20, 0.12 + val * 0.78
        else:                                # reds, purples: meat
            nh, ns, nv = 0.99, min(1.0, sat * 0.85), 0.08 + val * 0.45
        rgb = colorsys.hsv_to_rgb(nh, ns, nv)
        out[3 * i:3 * i + 3] = [int(round(c * 255)) // 8 * 8 for c in rgb]
im.putpalette(out)
im.save(DST)
print(f"Built {DST.relative_to(ROOT)}")
