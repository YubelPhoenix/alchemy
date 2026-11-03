#!/usr/bin/env python3
"""Build Ash Jenna's battle sheet from her original 64x64 poses.

She borrows the unused Slime sprite slot (SPR_477, games/tbs/src/graphics/
monster/slime.png).  Battle monsters are 64x64 frames at 8 bits per pixel,
raw indices into the shared 224-colour sprite palette
(games/tbs/src/system/memory/basic.png); index 0 is transparent.  The sheet is
16 frames tall; spr_477.tsv steps through frames 0, 2, 4, 6, 8, 10, 12 and 14,
so every frame is stored twice.

  Her sword is drawn over every pose (SWORD).

  0, 2, 4   idle (the same pose, bobbing one row)
  6, 8      dash / leap
  10, 12    cast
  14        damage
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

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

# Her sword, drawn over the poses: (hand x, hand y) -> (tip x, tip y) per step.
# Battle monsters cannot hold equipment, so the blade is part of the art.
SWORD = {
    0: ((40, 42), (52, 20)), 2: ((40, 42), (52, 20)), 4: ((40, 42), (52, 20)),
    6: ((50, 44), (63, 38)),
    8: ((45, 45), (58, 28)),
    10: ((42, 22), (47, 4)),
    12: ((38, 46), (57, 36)),
    14: ((45, 42), (56, 27)),
}


def draw_sword(frame, hand, tip, rise):
    """Blade, gold crossguard, grip and pommel from the hand to the tip."""
    draw = ImageDraw.Draw(frame)
    hx, hy = hand[0], hand[1] - rise
    tx, ty = tip[0], tip[1] - rise
    length = max(1.0, ((tx - hx) ** 2 + (ty - hy) ** 2) ** 0.5)
    ux, uy = (tx - hx) / length, (ty - hy) / length
    px, py = -uy, ux  # perpendicular
    steel, edge, gold, leather = ((214, 222, 236, 255), (250, 252, 255, 255),
                                  (232, 184, 72, 255), (104, 64, 40, 255))
    # grip and pommel behind the hand
    draw.line([(hx - ux * 4, hy - uy * 4), (hx, hy)], fill=leather, width=2)
    draw.ellipse([hx - ux * 5 - 1, hy - uy * 5 - 1, hx - ux * 5 + 1, hy - uy * 5 + 1], fill=gold)
    # blade, two pixels wide with a bright edge
    draw.line([(hx + ux * 2, hy + uy * 2), (tx, ty)], fill=steel, width=3)
    draw.line([(hx + ux * 3 + px * 0.7, hy + uy * 3 + py * 0.7),
               (tx + px * 0.7, ty + py * 0.7)], fill=edge, width=1)
    # crossguard
    draw.line([(hx + ux * 2 - px * 3, hy + uy * 2 - py * 3),
               (hx + ux * 2 + px * 3, hy + uy * 2 + py * 3)], fill=gold, width=2)

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
    hand, tip = SWORD[index - index % 2]
    draw_sword(frame, hand, tip, rise)
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

# Her mugshot, a new portrait icon (ICON_67 in icons.tsv, numbered 128 + 51 in
# Portrait_GetForSpeaker). Icons are 32x32 with at most 16 colours, each
# channel a multiple of eight (GBA 5-bit colour).
portrait = Image.open(SOURCE / "portrait_32.jpg").convert("RGB")
if portrait.size != (32, 32):
    portrait = portrait.resize((32, 32), Image.Resampling.LANCZOS)
icon = portrait.quantize(colors=16, method=Image.Quantize.MEDIANCUT)
icon_palette = icon.getpalette()
for i in range(0, len(icon_palette), 3):
    for channel in range(3):
        icon_palette[i + channel] = (icon_palette[i + channel] // 8) * 8
icon.putpalette(icon_palette)
icon_target = ROOT / "games/tbs/src/graphics/ui/icons/icon_67.png"
icon.save(icon_target)
print(f"Rebuilt {icon_target.relative_to(ROOT)} from portrait_32.jpg")
