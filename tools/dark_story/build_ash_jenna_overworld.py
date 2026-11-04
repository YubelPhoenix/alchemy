#!/usr/bin/env python3
"""Build Ash Jenna's overworld sprite from her four original standing poses.

She takes over SPR_094 (sprite id 0x5e, SPRITE_ASH_JENNA), one of the sprite table's
empty rows, so no other actor shares it. (SPR_090 to SPR_093 are the four
elements' Djinn; never reuse those.)  An overworld sprite of draw kind 3 is a stack of 32x32
frames at 8 bits per pixel (raw indices into the shared 224-colour palette,
index 0 transparent); each animation step is three frames: front, side
(facing right; the engine mirrors it for left) and back.  Her sheet follows
SPR_042's layout: eleven steps, 33 frames.  spr_094.tsv is a copy of
spr_042.tsv, so the animation scripts match.

  assets/ash_jenna/overworld_1.png  facing left   (mirrored for the side frame)
  assets/ash_jenna/overworld_2.png  front
  assets/ash_jenna/overworld_3.png  back
  assets/ash_jenna/overworld_4.png  facing right

Her walk (steps 15 to 30) bobs her one row on alternate frames.
"""
from pathlib import Path
import shutil

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets" / "ash_jenna"
SPRITES = ROOT / "games/tbs/src/graphics/sprite"
SHARED_PALETTE = ROOT / "games/tbs/src/system/memory/basic.png"

FRAME = 32
STEPS = 11
FOOT_ROW = 31  # the last row her feet may touch, as in SPR_042
WALK_BOB = {15: 1, 18: 0, 21: 1, 24: 0, 27: 1, 30: 0}

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


def pose(name):
    return Image.open(SOURCE / name).convert("RGBA")


FRONT, BACK = pose("overworld_2.png"), pose("overworld_3.png")
SIDE = pose("overworld_4.png")  # faces right, like SPR_042's side frames


def place(src, rise):
    frame = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    x = (FRAME - src.width) // 2
    y = FOOT_ROW + 1 - src.height - rise
    frame.alpha_composite(src, (x, y))
    return frame


sheet = Image.new("RGBA", (FRAME, FRAME * STEPS * 3), (0, 0, 0, 0))
for step in range(STEPS):
    base = step * 3
    rise = WALK_BOB.get(base, 0)
    for offset, src in enumerate((FRONT, SIDE, BACK)):
        sheet.alpha_composite(place(src, rise), (0, (base + offset) * FRAME))

data = np.asarray(sheet)
visible = data[..., 3] >= 128
lab = to_lab(data[..., :3][visible])
distance = ((lab[:, None, :] - palette_lab[None, 1:, :]) ** 2).sum(axis=2)
indices = np.zeros(visible.shape, dtype=np.uint8)
indices[visible] = distance.argmin(axis=1).astype(np.uint8) + 1
indexed = Image.fromarray(indices, "P")
indexed.putpalette(palette)

assert indexed.size == (FRAME, FRAME * 33), indexed.size
assert indices.max() <= 223 and indices.max() > 15
assert (indices[~visible] == 0).all() and (indices[visible] != 0).all()
for n in range(33):
    assert indices[n * FRAME:(n + 1) * FRAME].any(), f"frame {n} is empty"
indexed.save(SPRITES / "spr_094.png", optimize=False)
shutil.copyfile(SPRITES / "spr_042.tsv", SPRITES / "spr_094.tsv")
print(f"Rebuilt spr_094.png: 33 frames, "
      f"{len(set(indices[visible].tolist()))} colours from the shared palette")
