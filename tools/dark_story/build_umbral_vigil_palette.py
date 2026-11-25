#!/usr/bin/env python3
"""Vale's colours as the Rift remembers them (pal_umbral_vigil.png, from
tileset set_02's palette): the night of the storm that never ended.

Every colour keeps its place and its brightness order, so Vale's plaza reads
at a glance, but: the grass is dead olive-grey; the thatch and timber are ash;
the water of the pond is black with a violet sheen; the Psynergy Stone is the
Rift's black crystal; and the autumn reds of the trees go to the brown of old
blood.
"""
import colorsys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "games/tbs/src/graphics/tileset/set_02/palette.png"
DST = ROOT / "games/tbs/src/graphics/tileset/palettes/pal_umbral_vigil.png"

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
        if sat < 0.12:                       # greys and whites: dimmed
            nh, ns, nv = 0.70, 0.05, 0.12 + val * 0.62
        elif 0.17 <= hue < 0.47:             # grass, leaves: dead olive
            nh, ns, nv = 0.17, sat * 0.28, 0.08 + val * 0.42
        elif 0.47 <= hue < 0.68:             # water, sky: black, violet sheen
            nh, ns, nv = 0.74, 0.30, 0.04 + val * 0.30
        elif 0.68 <= hue < 0.90:             # the Psynergy Stone: black crystal
            nh, ns, nv = 0.78, sat * 0.55, 0.05 + val * 0.30
        elif 0.07 <= hue < 0.17:             # thatch, timber, paths: ash
            nh, ns, nv = 0.09, sat * 0.22, 0.10 + val * 0.55
        else:                                # reds, oranges: old blood
            nh, ns, nv = 0.99, min(1.0, sat * 0.75), 0.07 + val * 0.40
        rgb = colorsys.hsv_to_rgb(nh, ns, nv)
        out[3 * i:3 * i + 3] = [int(round(c * 255)) // 8 * 8 for c in rgb]
im.putpalette(out)
im.save(DST)
print(f"Built {DST.relative_to(ROOT)}")
