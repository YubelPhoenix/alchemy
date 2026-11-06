#!/usr/bin/env python3
"""Build Sarah's battle sheet from her supplied 64x64 poses (assets/sarah).

She has her own monster resource (SarahSprites, SPR_488, games/tbs/src/
graphics/monster/sarah.png), like Kegare.  Battle monsters are 64x64 frames at
8 bits per pixel, raw indices into the shared 224-colour sprite palette
(games/tbs/src/system/memory/basic.png); index 0 is transparent.  The sheet is
16 frames tall; spr_488.tsv steps through frames 0, 2, 4, 6, 8, 10, 12 and 14,
so every frame is stored twice.

  Each pose is dropped so its lowest row sits on the frame's bottom row.  Her
  idle, dash, cast and damage poses are drawn facing left, so they are
  mirrored to face the party on the right; the attack lunges right already.

  0, 2      idle (two drawn poses, looped)
  4         attack end (the follow-through after the thrust)
  6         dash
  8         attack
  10, 12    cast
  14        damage
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets" / "sarah"
DEST = ROOT / "games/tbs/src/graphics/monster/sarah.png"
SHARED_PALETTE = ROOT / "games/tbs/src/system/memory/basic.png"

FRAME = 64
FRAMES = 16
# Frame -> supplied pose; the other frame of each pair is a copy.
MIRROR = {"attack_end"}  # the game draws enemy sheets mirrored: rise and attack are used as drawn (facing left), attack end is flipped to match
STEPS = {0: "idle_new", 2: "idle2", 4: "attack_end", 6: "rise", 8: "attack_leap",
         10: "idle1", 12: "idle1", 14: "damage"}

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

CLEAN = {"dash", "damage", "rise", "attack_leap", "attack_end"}   # their drawings carry stray speckle


def despeckle(img):
    """Drops isolated pixels and recolours lone off-colour ones from their
    neighbours' median, leaving the drawing's edges alone."""
    a = np.asarray(img.convert("RGBA")).astype(np.int32).copy()
    h, w, _ = a.shape
    opaque = a[..., 3] >= 128
    out = a.copy()
    for y in range(h):
        for x in range(w):
            ys = slice(max(y - 1, 0), min(y + 2, h))
            xs = slice(max(x - 1, 0), min(x + 2, w))
            nb = opaque[ys, xs].copy()
            nb[y - ys.start, x - xs.start] = False
            count = int(nb.sum())
            if opaque[y, x]:
                if count <= 1:                    # a lone dot
                    out[y, x, 3] = 0
                    continue
                cols = a[ys, xs, :3][nb]
                med = np.median(cols, axis=0)
                if np.abs(a[y, x, :3] - med).sum() > 150:
                    near = (np.abs(cols - a[y, x, :3]).sum(axis=1) < 60).sum()
                    if near == 0:                 # nothing like it nearby
                        out[y, x, :3] = med
            elif count >= 7:                      # a pinhole
                cols = a[ys, xs, :3][nb]
                out[y, x, :3] = np.median(cols, axis=0)
                out[y, x, 3] = 255
    return Image.fromarray(out.astype(np.uint8), "RGBA")


sheet = Image.new("RGBA", (FRAME, FRAME * FRAMES), (0, 0, 0, 0))
for index in range(FRAMES):
    pose = STEPS[index - index % 2]
    src = Image.open(SOURCE / f"{pose}.png").convert("RGBA")
    if pose in CLEAN:
        src = despeckle(src)
    if pose in MIRROR:
        src = src.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if src.size != (FRAME, FRAME):
        raise ValueError(f"{pose} must be {FRAME}x{FRAME}")
    bottom = src.getchannel("A").getbbox()[3]
    if pose in ("idle1", "idle2", "idle3"):
        bottom = 60   # the three idle drawings keep their own heights (the bob)
    frame = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    frame.alpha_composite(src, (0, FRAME - bottom))
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

# Her mugshot: portrait icon ICON_68 (icons.tsv; numbered 128 + 52 in
# Portrait_GetForSpeaker). 32x32, sixteen colours, index 0 transparent, each
# channel a multiple of eight (GBA 5-bit colour).
portrait = Image.open(SOURCE / "mugshot_32.png").convert("RGBA")
if portrait.size != (32, 32):
    raise ValueError(f"Sarah mugshot is {portrait.size}, expected 32x32")
alpha = np.asarray(portrait.getchannel("A")) >= 128
small = portrait.convert("RGB").quantize(
    colors=15, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
small_palette = small.getpalette()[:45]
pixels = np.asarray(small, dtype=np.uint8) + 1
pixels[~alpha] = 0
icon = Image.fromarray(pixels, "P")
icon_palette = [0, 0, 0] + small_palette
icon_palette += [0] * (48 - len(icon_palette))
for i in range(len(icon_palette)):
    icon_palette[i] = (icon_palette[i] // 8) * 8
icon.putpalette(icon_palette)
icon_target = ROOT / "games/tbs/src/graphics/ui/icons/icon_68.png"
icon.save(icon_target)
print(f"Rebuilt {icon_target.relative_to(ROOT)} from the Sarah mugshot")
