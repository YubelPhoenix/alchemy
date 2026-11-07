#!/usr/bin/env python3
"""Rebuild Heart's battle sheet and mugshot from her supplied 64x64 poses
(assets/heart/v2).

Golden Sun's battle engine draws monster frames as 64x64, 8 bits per pixel.
Every pixel is a raw index into the shared 224-colour sprite palette
(games/tbs/src/system/memory/basic.png), index 0 is transparent, and the
frames are packed one under another (64x640 = 10 frames) with no palette of
their own.  So the sheet must use that exact palette and nothing else; a
private 16-colour palette makes every index land on the wrong colour.

Frame layout (games/tbs/src/graphics/sprite/spr_484.tsv steps by two, each
frame is stored twice):
  0-1   idle            2-3   dash / leap (rise)     4-5  lunge (landing)
  6-7   cast            8-9   damage
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets" / "heart" / "v2"
DEST = ROOT / "games/tbs/src/graphics/monster/purple_beast.png"
SHARED_PALETTE = ROOT / "games/tbs/src/system/memory/basic.png"

FRAME = 64
FRAMES = 10
# The supplied poses are drawn at 64x64, the frame's own size, so they are not
# resampled: the size on screen comes from SPR_484's scale column in
# sprites.tsv (0xb8, which puts her idle pose, 56 rows, at Menardi's 40 or so).
# (pose, mirror so she faces the party on the right, rise)
LAYOUT = [
    ("idle1", True, 0), ("idle1", True, 0),
    ("dash", False, 0), ("dash", False, 0),
    ("lunge", False, 0), ("lunge", False, 0),
    ("cast", False, 0), ("cast", False, 0),
    ("damage", True, 0), ("damage", True, 0),
]

palette_image = Image.open(SHARED_PALETTE)
palette = palette_image.getpalette()[:224 * 3]
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


# Index 0 is transparent; every other entry of the shared palette may be used.
palette_lab = to_lab(colors)

sheet = Image.new("RGBA", (FRAME, FRAME * FRAMES), (0, 0, 0, 0))
for index, (name, mirror, rise) in enumerate(LAYOUT):
    src = Image.open(SOURCE / f"{name}.png").convert("RGBA")
    if src.size != (FRAME, FRAME):
        raise ValueError(f"Heart pose {name} is {src.size}, expected 64x64")
    bounds = src.getchannel("A").getbbox()
    if not bounds:
        raise ValueError(f"Heart pose {name} is empty")
    if name.startswith("idle"):
        # The three idle drawings keep their own heights (the breathing bob):
        # all are placed by where the first one lands.
        first = Image.open(SOURCE / "idle1.png").convert("RGBA")
        fb = first.getchannel("A").getbbox()
        fart = first.crop(fb)
        if mirror:
            fart = fart.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        fmask = np.asarray(fart)[..., 3] >= 128
        fcx = np.nonzero(fmask)[1].mean()
        fx = max(0, min(FRAME - fart.size[0], int(round(FRAME / 2 - fcx))))
        full = src.transpose(Image.Transpose.FLIP_LEFT_RIGHT) if mirror else src
        left = (FRAME - fb[2]) if mirror else fb[0]
        frame = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
        frame.alpha_composite(full, (fx - left, FRAME - fart.size[1] - fb[1]))
        sheet.alpha_composite(frame, (0, index * FRAME))
        continue
    art = src.crop(bounds)
    if mirror:
        art = art.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    width, height = art.size
    frame = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    # Feet (or the lowest row) on the bottom row, body centred on the frame.
    mask = np.asarray(art)[..., 3] >= 128
    cx = (np.nonzero(mask)[1].mean() if mask.any() else width / 2)
    x = int(round(FRAME / 2 - cx))
    x = max(0, min(FRAME - width, x))
    frame.alpha_composite(art, (x, FRAME - height - rise))
    sheet.alpha_composite(frame, (0, index * FRAME))

# Quantize each visible pixel to the nearest colour of the shared palette.
data = np.asarray(sheet)
visible = data[..., 3] >= 128
lab = to_lab(data[..., :3][visible])
distance = ((lab[:, None, :] - palette_lab[None, 1:, :]) ** 2).sum(axis=2)
indices = np.zeros(visible.shape, dtype=np.uint8)
indices[visible] = distance.argmin(axis=1).astype(np.uint8) + 1
indexed = Image.fromarray(indices, "P")
indexed.putpalette(palette)

# --- validation -----------------------------------------------------------
assert indexed.size == (FRAME, FRAME * FRAMES), indexed.size
assert indexed.getpalette()[:224 * 3] == palette
assert indices.max() <= 223, "pixel outside the shared 224-colour palette"
assert (indices[~visible] == 0).all(), "transparent pixels must be index 0"
assert (indices[visible] != 0).all(), "visible pixels must not be index 0"
assert indices.max() > 15, "sheet only uses the first 16 colours (4bpp bug)"
for n in range(FRAMES):
    f = indices[n * FRAME:(n + 1) * FRAME]
    assert f.any(), f"frame {n} is empty"
    ys, xs = np.nonzero(f)
    assert ys.max() <= FRAME - 1 and xs.min() >= 0 and xs.max() < FRAME
indexed.save(DEST, optimize=False)
print(f"Rebuilt {DEST.relative_to(ROOT)}: {FRAMES} frames, "
      f"{len(set(indices[visible].tolist()))} colours from the shared palette")

# Claude's portrait hook already points at ICON_66. Replace that placeholder
# with the supplied 32x32 Heart mugshot; no changes to Mia or other portraits.
# This icon atlas requires each entry to be 32x32 with at most 16 colours.
canvas = Image.open(SOURCE / "mugshot_32.png").convert("RGB")
if canvas.size != (32, 32):
    raise ValueError(f"Heart mugshot is {canvas.size}, expected 32x32")
portrait_target = ROOT / "games/tbs/src/graphics/ui/icons/icon_66.png"
# GBA icon palettes require opaque RGB channels aligned to eight.
# Quantize first, then snap palette entries to valid GBA levels.
icon = canvas.convert("RGB").quantize(colors=16, method=Image.Quantize.MEDIANCUT)
palette = icon.getpalette()[:48]
palette += [0] * (48 - len(palette))  # the icon atlas wants exactly sixteen colours
for i in range(0, len(palette), 3):
    for channel in range(3):
        palette[i + channel] = (palette[i + channel] // 8) * 8
icon.putpalette(palette)
icon.save(portrait_target)
print(f"Rebuilt {portrait_target.relative_to(ROOT)} from the Heart mugshot")
