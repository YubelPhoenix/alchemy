#!/usr/bin/env python3
"""Moves the cliff of Sarah's background further back so the battlers fit.

assets/backgrounds/sarah_original.png has its ledge and two graves in the
middle of the lower half, where the characters stand. This shrinks that
cluster, sets it back on a plateau of the picture's own foreground rock, fills
the gap it leaves from the surrounding scenery and writes
assets/backgrounds/sarah.png (build_battle_backgrounds.py turns that into the
256x120 battle picture).
"""
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "assets/backgrounds/sarah_original.png"
DEST = ROOT / "assets/backgrounds/sarah.png"

SCALE = 0.55        # how much smaller the cliff becomes (further back)
PLATEAU_TOP = 840   # where the foreground rock now starts
REGION = (430, 690, 1340, 990)  # x0, y0, x1, y1 around the cliff

img = np.asarray(Image.open(SRC).convert("RGB")).astype(np.int16)
h, w, _ = img.shape
x0, y0, x1, y1 = REGION
r, g, b = img[..., 0], img[..., 1], img[..., 2]

# Cliff = grey rock (r ~ g ~ b) or the graves (warm: r well above b).
grey = (np.abs(r - g) < 22) & (np.abs(g - b) < 28)
warm = (r - b) > 25
mask = (grey | warm)
region = np.zeros_like(mask)
region[y0:y1, x0:x1] = True
mask &= region
mask = mask.astype(np.uint8)
mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
count, labels, stats, _ = cv2.connectedComponentsWithStats(mask)
biggest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
mask = (labels == biggest).astype(np.uint8)
mask = cv2.dilate(mask, np.ones((5, 5), np.uint8))
# The old foreground band (grey, full width, from y ~ 975) stays out of it.
mask[975:, :] = 0

bx, by, bw, bh = cv2.boundingRect(mask)
cliff = img[by:by + bh, bx:bx + bw].astype(np.uint8)
cliff_mask = mask[by:by + bh, bx:bx + bw] * 255

# Fill what the cliff leaves behind from the scenery around it.
scenery = cv2.inpaint(img.astype(np.uint8), mask * 255, 9, cv2.INPAINT_TELEA)
canvas = scenery.copy()

# Plateau: the foreground rock (rows 985 to 1080) stretched up to PLATEAU_TOP,
# its top edge gently uneven.
band = canvas[985:1080]
need = 1080 - PLATEAU_TOP + 30
plateau = cv2.resize(band, (w, need), interpolation=cv2.INTER_CUBIC)
xs = np.arange(w)
edge = (6 * np.sin(xs / 140.0) + 4 * np.sin(xs / 53.0 + 1.0)).astype(int)
for x in range(w):
    top_y = PLATEAU_TOP + edge[x]
    column = plateau[top_y - PLATEAU_TOP + 30:, x] if False else None
    ys = np.arange(top_y, 1080)
    canvas[ys, x] = plateau[np.clip(ys - PLATEAU_TOP + 15, 0, need - 1), x]
    for k in range(6):  # a short blend into the scenery above the edge
        yy = top_y - 6 + k
        t = (k + 1) / 7
        canvas[yy, x] = (scenery[yy, x] * (1 - t)
                         + canvas[top_y, x] * t).astype(np.uint8)

# The shrunken cliff, resting on the plateau's top edge, same centre.
new_w, new_h = round(bw * SCALE), round(bh * SCALE)
small = cv2.resize(cliff, (new_w, new_h), interpolation=cv2.INTER_AREA)
small_mask = cv2.resize(cliff_mask, (new_w, new_h), interpolation=cv2.INTER_AREA)
cx = bx + bw // 2
left = cx - new_w // 2
top = PLATEAU_TOP + 6 - new_h
alpha = (small_mask[..., None] / 255.0)
roi = canvas[top:top + new_h, left:left + new_w].astype(np.float64)
canvas[top:top + new_h, left:left + new_w] = (
    roi * (1 - alpha) + small * alpha).astype(np.uint8)

Image.fromarray(canvas).save(DEST)
print(f"Wrote {DEST.relative_to(ROOT)}")
