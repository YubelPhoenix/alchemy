#!/usr/bin/env python3
"""Build Ash Jenna's battle sheet from her supplied 64x64 poses (assets/ash_jenna/v2).

She borrows the unused Slime sprite slot (SPR_477, games/tbs/src/graphics/
monster/slime.png).  Battle monsters are 64x64 frames at 8 bits per pixel,
raw indices into the shared 224-colour sprite palette
(games/tbs/src/system/memory/basic.png); index 0 is transparent.  The sheet is
10 frames tall; spr_477.tsv steps through frames 0, 2, 4, 6 and 8,
so every frame is stored twice.

  The poses already carry her sword; each is dropped so its lowest row sits on
  the frame's bottom row (her feet on the ground, never floating).

  0, 2, 4   idle
  6         dash
  8         attack
  10, 12    cast
  14        damage
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets" / "ash_jenna" / "v2"
DEST = ROOT / "games/tbs/src/graphics/monster/slime.png"
SHARED_PALETTE = ROOT / "games/tbs/src/system/memory/basic.png"

FRAME = 64
FRAMES = 14
# Frame -> supplied pose; the other frame of each pair is a copy.
# The supplied poses are drawn at full size (about 57 rows tall); the size on
# screen comes from SPR_477's scale column in sprites.tsv (0xb6, which puts her
# idle pose at Menardi's 40 or so rows), so the art itself is not resampled.
SCALE = 1.0
STEPS = {0: "idle1", 2: "dash", 4: "attack", 6: "cast", 8: "damage",
         10: "idle_glint",   # idle with the red eye flared
         12: "idle_breath"}  # breathing in (make_breath_frames.py)

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
    src = Image.open(SOURCE / f"{STEPS[index - index % 2]}.png").convert("RGBA")
    if src.size != (FRAME, FRAME):
        raise ValueError(f"{STEPS[index - index % 2]} must be {FRAME}x{FRAME}")
    bottom = src.getchannel("A").getbbox()[3]
    if STEPS[index - index % 2].startswith("idle"):
        # the three idle drawings keep their own heights (the breathing bob)
        bottom = Image.open(SOURCE / "idle1.png").getchannel("A").getbbox()[3]
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

# Her mugshot, a new portrait icon (ICON_67 in icons.tsv, numbered 128 + 51 in
# Portrait_GetForSpeaker). Icons are 32x32 with at most 16 colours, each
# channel a multiple of eight (GBA 5-bit colour).
portrait = Image.open(SOURCE / "mugshot.png").convert("RGB")
if portrait.size != (32, 32):
    portrait = portrait.resize((32, 32), Image.Resampling.LANCZOS)
# Palette index 0 is the portrait's transparent colour (the other mugshots never
# use it), so the picture takes fifteen colours, numbered from 1, with no dither.
small = portrait.quantize(colors=15, method=Image.Quantize.MEDIANCUT,
                          dither=Image.Dither.NONE)
small_palette = small.getpalette()[:45]
pixels = np.asarray(small, dtype=np.uint8) + 1
icon = Image.fromarray(pixels, "P")
icon_palette = [0, 0, 0] + small_palette
icon_palette += [0] * (48 - len(icon_palette))  # exactly sixteen colours
for i in range(0, len(icon_palette), 3):
    for channel in range(3):
        icon_palette[i + channel] = (icon_palette[i + channel] // 8) * 8
icon.putpalette(icon_palette)
icon_target = ROOT / "games/tbs/src/graphics/ui/icons/icon_67.png"
icon.save(icon_target)
print(f"Rebuilt {icon_target.relative_to(ROOT)} from mugshot.png")
