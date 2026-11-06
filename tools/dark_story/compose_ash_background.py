#!/usr/bin/env python3
"""Raises the platform of Ash Jenna's background so the battlers stand on it.

assets/backgrounds/ash_original.png has its dark platform from row 860; the
party and Ash Jenna stand higher on the battle screen than that. This stretches
the platform up to PLATFORM_TOP (the burning town behind it loses its lowest
rows) and writes assets/backgrounds/ash.png.
"""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets/backgrounds/ash_original.png"
DEST = ROOT / "assets/backgrounds/ash.png"

OLD_TOP = 860
PLATFORM_TOP = 730

img = np.asarray(Image.open(SRC).convert("RGB"))
h, w, _ = img.shape
platform = img[OLD_TOP:h]
new_h = h - PLATFORM_TOP
stretched = cv2.resize(platform, (w, new_h), interpolation=cv2.INTER_CUBIC)
out = img.copy()
out[PLATFORM_TOP:h] = stretched
# The town's own base fades into the platform edge instead of ending abruptly.
for i in range(14):
    t = (i + 1) / 15
    y = PLATFORM_TOP - 14 + i
    out[y] = (img[y] * (1 - t) + stretched[0] * t).astype(np.uint8)
Image.fromarray(out).save(DEST)
print(f"Wrote {DEST.relative_to(ROOT)}")
