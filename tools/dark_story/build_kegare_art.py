#!/usr/bin/env python3
"""Build Kegare's battle sheet from her supplied 64x64 poses (assets/kegare).

She has her own monster resource (KegareSprites, SPR_487, games/tbs/src/
graphics/monster/kegare.png); the damage frame is Mia's (SPR_303 frame 12).  Battle monsters are 64x64 frames at 8 bits per pixel,
raw indices into the shared 224-colour sprite palette
(games/tbs/src/system/memory/basic.png); index 0 is transparent.  The sheet is
16 frames tall; spr_477.tsv steps through frames 0, 2, 4, 6, 8, 10, 12 and 14,
so every frame is stored twice.

  The poses already carry her sword; each is dropped so its lowest row sits on
  the frame's bottom row (her feet on the ground, never floating).

  0, 2, 4   idle
  6         dash
  8         attack
  10, 12    cast
  14        damage (Mia's)
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets" / "kegare"
MIA = ROOT / "games/tbs/src/graphics/sprite/spr_303.png"
DEST = ROOT / "games/tbs/src/graphics/monster/kegare.png"
SHARED_PALETTE = ROOT / "games/tbs/src/system/memory/basic.png"

FRAME = 64
FRAMES = 16
# Frame -> supplied pose; the other frame of each pair is a copy.
# The supplied poses are drawn at full size (about 57 rows tall); the size on
# screen comes from SPR_477's scale column in sprites.tsv (0xb6, which puts her
# idle pose at Menardi's 40 or so rows), so the art itself is not resampled.
SCALE = 1.0
STEPS_MIA = {"damage": 12}
STEPS = {0: "idle", 2: "idle", 4: "idle", 6: "dash", 8: "attack",
         10: "cast", 12: "cast", 14: "damage"}

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
    pose = STEPS[index - index % 2]
    if pose in STEPS_MIA:
        mia = Image.open(MIA)
        px = mia.convert("RGBA")
        alpha = np.asarray(mia)[STEPS_MIA[pose] * 64:(STEPS_MIA[pose] + 1) * 64] != 0
        src = px.crop((0, STEPS_MIA[pose] * 64, 64, (STEPS_MIA[pose] + 1) * 64))
        src.putalpha(Image.fromarray((alpha * 255).astype(np.uint8)))
    else:
        src = Image.open(SOURCE / f"{pose}.png").convert("RGBA")
    if src.size != (FRAME, FRAME):
        raise ValueError(f"{pose} must be {FRAME}x{FRAME}")
    bottom = src.getchannel("A").getbbox()[3]
    frame = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    frame.alpha_composite(src, (0, FRAME - bottom))
    side = round(FRAME * SCALE)
    small = frame.resize((side, side), Image.Resampling.LANCZOS)
    frame = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    frame.alpha_composite(small, ((FRAME - side) // 2, FRAME - side))
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
