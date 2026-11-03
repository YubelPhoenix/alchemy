#!/usr/bin/env python3
"""Build Ash Jenna's battle sheet from her original 64x64 poses.

She borrows the unused Slime sprite slot (SPR_477, games/tbs/src/graphics/
monster/slime.png).  Battle monsters are 64x64 frames at 8 bits per pixel,
raw indices into the shared 224-colour sprite palette
(games/tbs/src/system/memory/basic.png); index 0 is transparent.  The sheet is
16 frames tall; spr_477.tsv steps through frames 0, 2, 4, 6, 8, 10, 12 and 14,
so every frame is stored twice.

  0, 2, 4   idle (the same pose, bobbing one row)
  6, 8      dash / leap
  10, 12    cast
  14        damage
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets" / "ash_jenna"
DEST = ROOT / "games/tbs/src/graphics/monster/slime.png"
SHARED_PALETTE = ROOT / "games/tbs/src/system/memory/basic.png"

FRAME = 64
FRAMES = 16
# Source pose number, mirror (so she faces the party on the right), rise (rows).
STEPS = {
    0: (1, False, 0), 2: (1, False, 1), 4: (1, False, 0),
    6: (2, False, 0), 8: (4, False, 0),
    10: (3, True, 0), 12: (6, False, 0),
    14: (5, True, 0),
}

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

sheet = Image.new("RGBA", (FRAME, FRAME * FRAMES), (0, 0, 0, 0))
for index in range(FRAMES):
    number, mirror, rise = STEPS[index - index % 2]
    src = Image.open(SOURCE / f"pose_64_{number}.png").convert("RGBA")
    if src.size != (FRAME, FRAME):
        raise ValueError(f"pose {number} must be {FRAME}x{FRAME}, got {src.size}")
    if mirror:
        src = src.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    frame = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    frame.alpha_composite(src, (0, -rise))
    sheet.alpha_composite(frame, (0, index * FRAME))

data = np.asarray(sheet)
visible = data[..., 3] >= 128
lab = to_lab(data[..., :3][visible])
distance = ((lab[:, None, :] - palette_lab[None, 1:, :]) ** 2).sum(axis=2)
indices = np.zeros(visible.shape, dtype=np.uint8)
indices[visible] = distance.argmin(axis=1).astype(np.uint8) + 1
indexed = Image.fromarray(indices, "P")
indexed.putpalette(palette)

assert indexed.size == (FRAME, FRAME * FRAMES), indexed.size
assert indexed.getpalette()[:224 * 3] == palette
assert indices.max() <= 223, "pixel outside the shared 224-colour palette"
assert indices.max() > 15, "sheet only uses the first 16 colours"
assert (indices[~visible] == 0).all() and (indices[visible] != 0).all()
for n in range(FRAMES):
    assert indices[n * FRAME:(n + 1) * FRAME].any(), f"frame {n} is empty"
indexed.save(DEST, optimize=False)
print(f"Rebuilt {DEST.relative_to(ROOT)}: {FRAMES} frames, "
      f"{len(set(indices[visible].tolist()))} colours from the shared palette")
