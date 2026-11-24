#!/usr/bin/env python3
"""Build Sarah's overworld sprite from The Lost Age's unfinished sprite 129.

The Lost Age left a 33-frame sheet of a blonde girl in a green skirt
(games/tla/src/graphics/sprite/spr_129.png), never used.  It takes the place
of the Broken Seal's spr_129 (sprite id 0x81, SPRITE_SARAH), whose one actor,
the lute player of the Bilibin cottage, now uses another sprite.  The sheet
is the same size on disk or smaller, so the sprite ROM region does not grow
(a new sprite there overflowed it).  Each animation step is three frames:
front, side and back; spr_129.tsv is The Lost Age's, so it matches the sheet.

Her frames are recoloured from The Lost Age's palette to the Broken Seal's
shared 224-colour sprite palette (games/tbs/src/system/memory/basic.png);
index 0 is transparent.
"""
from pathlib import Path
import shutil

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "games/tla/src/graphics/sprite"
SPRITES = ROOT / "games/tbs/src/graphics/sprite"
SHARED_PALETTE = ROOT / "games/tbs/src/system/memory/basic.png"
FRAME = 32

palette = Image.open(SHARED_PALETTE).getpalette()[:224 * 3]
colors = np.array(palette, dtype=np.float64).reshape(-1, 3)


def to_lab(rgb):
    rgb = np.asarray(rgb, dtype=np.float64) / 255.0
    rgb = np.where(rgb > 0.04045, ((rgb + 0.055) / 1.055) ** 2.4, rgb / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722],
                  [0.0193, 0.1192, 0.9505]])
    xyz = rgb @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]),
                     200 * (f[..., 1] - f[..., 2])], axis=-1)


palette_lab = to_lab(colors)

source = Image.open(SOURCE / "spr_129.png")
index0 = np.asarray(source) == 0
rgb = np.asarray(source.convert("RGB"))
visible = ~index0
assert source.size == (FRAME, FRAME * 33), source.size

lab = to_lab(rgb[visible])
distance = ((lab[:, None, :] - palette_lab[None, 1:, :]) ** 2).sum(axis=2)
indices = np.zeros(visible.shape, dtype=np.uint8)
indices[visible] = distance.argmin(axis=1).astype(np.uint8) + 1
indexed = Image.fromarray(indices, "P")
indexed.putpalette(palette)

assert indices.max() <= 223 and indices.max() > 15
assert (indices[~visible] == 0).all() and (indices[visible] != 0).all()
for n in range(33):
    assert indices[n * FRAME:(n + 1) * FRAME].any(), f"frame {n} is empty"
indexed.save(SPRITES / "spr_129.png", optimize=False)
shutil.copyfile(SOURCE / "spr_129.tsv", SPRITES / "spr_129.tsv")
print(f"Rebuilt spr_129.png: 33 frames, "
      f"{len(set(indices[visible].tolist()))} colours from the shared palette")
