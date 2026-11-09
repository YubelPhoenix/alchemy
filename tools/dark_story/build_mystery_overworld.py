#!/usr/bin/env python3
"""Build the "???" commander's overworld sprite (SPR_490) from her walking
sheet (assets/mystery/overworld: front, back and side, her standing poses
cut from the sheet; the side faces east).

An overworld sprite is 32x32 frames in the shared 224-colour palette (index 0
transparent).  Her sprite draws like the other villagers: three frames per
pose, front, side (facing east; the engine mirrors it for west) and back,
picked from the way an actor faces (games/tbs/src/field/facing.c).  She never
walks, so there is only the one pose.  The drawings are about four times the
size of the game's characters, so each is averaged down to the same scale
and her feet put on row 31.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets" / "mystery" / "overworld"
DEST = ROOT / "games/tbs/src/graphics/sprite/spr_490.png"
SHARED_PALETTE = ROOT / "games/tbs/src/system/memory/basic.png"
FRAME = 32
HEIGHT = 28           # her tallest drawing, spear tip to boots, in game pixels
FEET = 31             # the row her boots end on
POSES = ["front", "side", "back"]

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
images = [Image.open(SOURCE / f"{n}.png").convert("RGBA") for n in POSES]
scale = HEIGHT / max(i.height for i in images)

sheet = np.zeros((FRAME * len(POSES), FRAME), dtype=np.uint8)
for index, img in enumerate(images):
    w = max(1, round(img.width * scale))
    h = max(1, round(img.height * scale))
    # Average in premultiplied colour so the edges keep their dark outline.
    arr = np.asarray(img).astype(np.float64)
    alpha = arr[..., 3:4] / 255.0
    pre = Image.fromarray(
        np.dstack([arr[..., :3] * alpha, arr[..., 3:4]]).astype("uint8"), "RGBA")
    small = np.asarray(pre.resize((w, h), Image.Resampling.BOX)).astype(np.float64)
    cover = small[..., 3] / 255.0
    rgb = np.where(cover[..., None] > 0, small[..., :3] / np.maximum(cover[..., None], 1e-6), 0)
    visible = cover >= 0.5
    frame = np.zeros((FRAME, FRAME), dtype=np.uint8)
    lab = to_lab(rgb[visible])
    distance = ((lab[:, None, :] - palette_lab[None, 1:, :]) ** 2).sum(axis=2)
    pixels = np.zeros((h, w), dtype=np.uint8)
    pixels[visible] = distance.argmin(axis=1).astype(np.uint8) + 1
    x0 = (FRAME - w) // 2
    y0 = FEET + 1 - h
    assert x0 >= 0 and y0 >= 0, (POSES[index], w, h)
    frame[y0:y0 + h, x0:x0 + w] = pixels
    sheet[index * FRAME:(index + 1) * FRAME] = frame

indexed = Image.fromarray(sheet, "P")
indexed.putpalette(palette)
assert indexed.size == (FRAME, FRAME * len(POSES))
assert sheet.max() <= 223
for n in range(len(POSES)):
    assert sheet[n * FRAME:(n + 1) * FRAME].any()
indexed.save(DEST, optimize=False)
print(f"Rebuilt {DEST.relative_to(ROOT)}: {len(POSES)} frames")
