#!/usr/bin/env python3
"""Build the Umbral Rift's Vigil mother (SPR_507) from Dora (SPR_031).

The Rift rebuilt Vale's plaza from Isaac's memory of the stormy night, and
the only face it kept was his mother's; it kept it wrong. SPR_507 is Dora
with her face taken away: on every frame, between the line of her hair and
her chin and within the width of her hair (so never her sleeves), each eye,
brow, lid and mouth pixel (FEATURES) beside her skin becomes skin, so a smooth blank oval looks out of her hair.
Her clothes, hair and every frame and animation stay hers, so she turns,
blinks (now at nothing) and walks as Dora does.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPR = ROOT / "games/tbs/src/graphics/sprite"
SKIN = {138, 137, 144, 132, 131}           # her skin's tones
# Her eyes, lashes, brows, lids and mouth (blues, whites, greys, dark rose);
# her hair's golds and browns are never touched.
FEATURES = {122, 80, 15, 174, 215, 223, 222, 130, 14, 88, 89, 123, 81, 158,
            10, 95, 164, 165, 201, 207, 219, 220, 211, 115, 116, 173, 180,
            129}
FILL = 138                       # her face's middle tone
FACE_ROWS = range(10, 17)        # frame rows from her brow to her chin

base = Image.open(SPR / "spr_031.png")
pixels = np.asarray(base).copy()
frames = pixels.shape[0] // 32
HAIR = {11, 17, 23, 52, 53, 58, 59, 60, 66}
for f in range(frames):
    block = pixels[f * 32:(f + 1) * 32]
    # Her head's width: the columns her hair covers above her brow.
    cols = [x for x in range(32)
            if any(int(v) in HAIR for v in block[3:10, x])]
    if not cols:
        continue
    left, right = cols[0] + 1, cols[-1] - 1
    for _ in range(3):          # a feature beside a feature
        for row in FACE_ROWS:
            for x in range(left, right + 1):
                if int(block[row, x]) not in FEATURES:
                    continue
                near = block[row - 1:row + 2, max(x - 2, 0):x + 3]
                if any(int(v) in SKIN for v in near.flatten()):
                    block[row, x] = FILL
out = Image.fromarray(pixels, "P")
out.putpalette(base.getpalette())
out.save(SPR / "spr_507.png", optimize=False)
(SPR / "spr_507.tsv").write_text((SPR / "spr_031.tsv").read_text())
print(f"Built spr_507.png: {frames} frames of Dora, faceless")
