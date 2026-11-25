#!/usr/bin/env python3
"""Pack the Vengeful Wraith's battle art (assets/wraith, drawn by the
author on 128x128 canvases at the game's scale) into her monster sheet,
SPR_491.

Each pose is cut from its canvas through one shared 64x64 window, so the
poses keep the places they were drawn in relative to each other (two are
moved: SHIFT). The leap and the attack's end were drawn larger than the
rest (her hood 22 and 21 pixels wide against 18), so they are first shrunk to
their size (SCALE) about her feet. Colours
go to the nearest entries of the shared sprite palette
(games/tbs/src/system/memory/basic.png); half-transparent edge pixels are
kept if at least half opaque.

The sheet is 64x768, twelve frames, each pose stored twice as the sprite
engine steps frames by two (as Heart's, build_heart_art.py):

  0-1   idle             2-3   leap (the attack's run-up)   4-5   attack end
  6-7   cast
  8-9   damage           10-11 idle, breathing in
    (assets/wraith/idle2.png when drawn; until then made from the idle:
    everything above her feet, cloak, sword and the tops of her boots too,
    sinks a pixel, and the trailing wisps of her cloak sway further
    (flutter), so she rises and falls as the game swaps the two)
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets/wraith"
DEST = ROOT / "games/tbs/src/graphics/monster/wraith.png"
SHARED_PALETTE = ROOT / "games/tbs/src/system/memory/basic.png"
FRAME = 64
WINDOW = (36, 43)              # top left of the 64x64 window on each canvas
# Poses whose window is moved (dx, dy): the cast and the damage were drawn
# 26 and 10 pixels higher on their canvases than the idle, so they move down
# to stand where she stands (the damage floated above her shadow).
SHIFT = {"cast": (0, -26), "damage": (0, -10)}
# Poses shrunk to the others' size (her hood 18 pixels wide): factor, and the
# canvas point kept still (her feet). Shrunk, the attack's end fits the
# window whole.
SCALE = {"leap": (18 / 22, (72, 91)), "attack_end": (18 / 21, (68, 106))}
LAYOUT = ["idle", "leap", "attack_end", "cast", "damage", "idle2"]
WAIST = 101                    # canvas row: all above it breathes, the tops of
                               # her boots too; only her feet stay planted


def to_lab(rgb):
    rgb = rgb / 255.0
    rgb = np.where(rgb > 0.04045, ((rgb + 0.055) / 1.055) ** 2.4, rgb / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722],
                  [0.0193, 0.1192, 0.9505]])
    xyz = rgb @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]),
                     200 * (f[..., 1] - f[..., 2])], -1)


# The cloak's trailing wisps right of her sword hand (canvas box, after the
# breath): in battle she is drawn at 0xb8/0x100 scale, where a one-pixel sink
# is lost in that thin region and the tail looked frozen while she breathed.
# In the breathing frame its dark pixels sway on by TAIL_SWAY more, never over
# the sword or her hand.
TAIL_BOX = (80, 76, 100, 100)  # x0, y0, x1, y1 on the canvas
TAIL_SWAY = (1, 2)             # dx, dy


def flutter(canvas):
    out = canvas.copy()
    x0, y0, x1, y1 = TAIL_BOX
    dx, dy = TAIL_SWAY
    rgb = canvas[..., :3].astype(int)
    light = 0.3 * rgb[..., 0] + 0.59 * rgb[..., 1] + 0.11 * rgb[..., 2]
    cloak = (canvas[..., 3] > 127) & (light < 90)
    moved = []
    for y in range(y0, y1):
        for x in range(x0, x1):
            if cloak[y, x]:
                moved.append((y, x, canvas[y, x].copy()))
                out[y, x] = 0
    for y, x, value in moved:
        ty, tx = y + dy, x + dx
        if ty < out.shape[0] and tx < out.shape[1] and (
                out[ty, tx, 3] <= 127 or (cloak[ty, tx] and (ty, tx) != (y, x))):
            out[ty, tx] = value
    return out


palette = Image.open(SHARED_PALETTE).getpalette()[:224 * 3]
colors = np.array(palette, dtype=float).reshape(-1, 3)
lab_colors = to_lab(colors[1:])

sheet = np.zeros((FRAME * 2 * len(LAYOUT), FRAME), np.uint8)
for i, name in enumerate(LAYOUT):
    path = SOURCE / f"{name}.png"
    if name == "idle2" and not path.exists():
        canvas = np.asarray(Image.open(SOURCE / "idle.png").convert("RGBA"))
        breath = canvas.copy()
        breath[1:WAIST + 1] = canvas[0:WAIST]   # all but her feet sink 1px
        canvas = flutter(breath)
    else:
        canvas = np.asarray(Image.open(path).convert("RGBA"))
    if name in SCALE:
        factor, (ax, ay) = SCALE[name]
        size = round(canvas.shape[1] * factor), round(canvas.shape[0] * factor)
        small = Image.fromarray(canvas).resize(size, Image.Resampling.BOX)
        scaled = Image.new("RGBA", (canvas.shape[1], canvas.shape[0]))
        scaled.paste(small, (round(ax - ax * factor), round(ay - ay * factor)))
        canvas = np.asarray(scaled)
    dx, dy = SHIFT.get(name, (0, 0))
    x0, y0 = WINDOW[0] + dx, WINDOW[1] + dy
    src = canvas[y0:y0 + FRAME, x0:x0 + FRAME]
    assert src.shape[:2] == (FRAME, FRAME), name
    vis = src[..., 3] >= 128
    d = ((to_lab(src[vis][:, :3].astype(float))[:, None, :]
          - lab_colors[None]) ** 2).sum(2)
    frame = np.zeros((FRAME, FRAME), np.uint8)
    frame[vis] = d.argmin(1) + 1
    for k in range(2):
        sheet[(2 * i + k) * FRAME:(2 * i + k + 1) * FRAME] = frame

out = Image.fromarray(sheet, "P")
out.putpalette(palette + [0] * (256 - 224) * 3)
out.save(DEST, optimize=False)
print(f"Packed {DEST.relative_to(ROOT)}: {2 * len(LAYOUT)} frames")

# Her mugshot: portrait icon ICON_69 (icons.tsv; numbered 128 + 53 in
# Portrait_GetForSpeaker). assets/wraith/mugshot_32.png is the supplied 32x32
# portrait (cut out of a screenshot's window frame) with the pink
# backdrop made black and the smile closed to a flat mouth. Sixteen colours,
# all opaque, each channel a multiple of eight (GBA 5-bit colour).
portrait = Image.open(SOURCE / "mugshot_32.png").convert("RGB")
assert portrait.size == (32, 32), portrait.size
# Fifteen colours (palette index 0 is see-through in a portrait and stays
# unused, so every pixel is index 1 to 15). Her face keeps fixed shades (FACE: the light, the mid
# tones that shape her nose and jaw, and the mouth), or the cut merges them
# all into one flat skin colour; the other ten are picked by k-means in Lab
# (seeded farthest-first) for her hair, eyes and collar, not by median cut,
# which loses her purple eyes.
FACE = [(248, 232, 208), (248, 216, 184), (232, 192, 152), (216, 176, 128),
        (200, 136, 88)]
MOUTH = len(FACE) - 1
rgb = np.asarray(portrait, dtype=float).reshape(-1, 3)
lab = to_lab(rgb)
fixed = to_lab(np.array(FACE, dtype=float))
centres = list(fixed)
while len(centres) < 15:
    gap = np.min([((lab - c) ** 2).sum(1) for c in centres], 0)
    centres.append(lab[gap.argmax()])
centres = np.array(centres)
for _ in range(40):
    label = ((lab[:, None] - centres[None]) ** 2).sum(2).argmin(1)
    for k in range(len(FACE), 15):
        if (label == k).any():
            centres[k] = lab[label == k].mean(0)
icon_palette = []
for k in range(15):
    if k < len(FACE):
        mean = np.array(FACE[k], dtype=float)
    else:
        mean = rgb[label == k].mean(0) if (label == k).any() else np.zeros(3)
    icon_palette += [int(round(v)) // 8 * 8 for v in mean]
# A lone pixel of the mouth's shade elsewhere reads as a mark on her face:
# it takes its next-nearest colour.
grid = label.reshape(32, 32)
dist = ((lab[:, None] - centres[None]) ** 2).sum(2).reshape(32, 32, 15)
for y, x in zip(*np.nonzero(grid == MOUTH)):
    near = grid[max(y - 1, 0):y + 2, max(x - 1, 0):x + 2]
    if (near == MOUTH).sum() == 1:
        d = dist[y, x].copy()
        d[MOUTH] = np.inf
        grid[y, x] = d.argmin()
icon = Image.fromarray(grid.astype(np.uint8) + 1, "P")
icon.putpalette([0, 0, 0] + icon_palette)
icon_target = ROOT / "games/tbs/src/graphics/ui/icons/icon_69.png"
icon.save(icon_target)
print(f"Rebuilt {icon_target.relative_to(ROOT)} from her mugshot")
