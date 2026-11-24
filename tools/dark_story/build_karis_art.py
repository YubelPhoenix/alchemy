#!/usr/bin/env python3
"""Pack Karis's battle poses (assets/karis, rendered from Dark Dawn's model by
dd_render/karis_frames.py) into her monster sheet, SPR_491.

The sheet is 64x768, twelve 64x64 frames, each pose stored twice as the
sprite engine steps frames by two (as Heart's, build_heart_art.py):

  0-1   idle (sword out at her hip)   2-3   wind-up     4-5   thrust
  6-7   cast (left hand raised)       8-9   damage      10-11 idle, breathing

Every pixel is a raw index into the shared sprite palette
(games/tbs/src/system/memory/basic.png); the poses are already in its colours,
so each maps to its exact entry.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets/karis"
DEST = ROOT / "games/tbs/src/graphics/monster/karis.png"
SHARED_PALETTE = ROOT / "games/tbs/src/system/memory/basic.png"
FRAME = 64
LAYOUT = ["idle", "dash", "lunge", "cast", "damage", "idle2"]

palette = Image.open(SHARED_PALETTE).getpalette()[:224 * 3]
colors = np.array(palette, dtype=np.int64).reshape(-1, 3)

sheet = np.zeros((FRAME * 2 * len(LAYOUT), FRAME), np.uint8)
for i, name in enumerate(LAYOUT):
    src = np.asarray(Image.open(SOURCE / f"{name}.png").convert("RGBA"))
    assert src.shape[:2] == (FRAME, FRAME), name
    vis = src[..., 3] >= 128
    d = ((src[vis][:, None, :3].astype(np.int64) - colors[None, 1:]) ** 2).sum(2)
    frame = np.zeros((FRAME, FRAME), np.uint8)
    frame[vis] = d.argmin(1) + 1
    for k in range(2):
        sheet[(2 * i + k) * FRAME:(2 * i + k + 1) * FRAME] = frame

out = Image.fromarray(sheet, "P")
out.putpalette(palette + [0] * (256 - 224) * 3)
out.save(DEST, optimize=False)
print(f"Packed {DEST.relative_to(ROOT)}: {2 * len(LAYOUT)} frames")
