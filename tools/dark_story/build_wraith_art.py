#!/usr/bin/env python3
"""Pack the Vengeful Wraith's battle art (assets/wraith, drawn by the
author on 128x128 canvases at the game's scale) into her monster sheet,
SPR_491.

Each pose is cut from its canvas through one shared 64x64 window, so the
poses keep the places they were drawn in relative to each other (two are
moved a little: SHIFT). Colours
go to the nearest entries of the shared sprite palette
(games/tbs/src/system/memory/basic.png); half-transparent edge pixels are
kept if at least half opaque.

The sheet is 64x768, twelve frames, each pose stored twice as the sprite
engine steps frames by two (as Heart's, build_heart_art.py):

  0-1   idle             2-3   leap (the attack's run-up)   4-5   attack end
  6-7   cast (the leap's raised sword, until a cast pose is drawn)
  8-9   damage           10-11 idle, breathing in
    (assets/wraith/idle2.png when drawn; until then made from the idle:
    everything above her boots, cloak and sword too, sinks a pixel, so she
    rises and falls as the game swaps the two)
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
# Poses whose window is moved (dx, dy): the leap's raised sword reaches
# above the shared window; the attack's end is 70 pixels wide, so its window
# moves a pixel left and the last few pixels of the cloak's tail are cut.
SHIFT = {"leap": (0, -11), "attack_end": (-1, 0)}
LAYOUT = ["idle", "leap", "attack_end", "leap", "damage", "idle2"]
WAIST = 97                     # canvas row: all above it (not her boots) breathes


def to_lab(rgb):
    rgb = rgb / 255.0
    rgb = np.where(rgb > 0.04045, ((rgb + 0.055) / 1.055) ** 2.4, rgb / 12.92)
    m = np.array([[0.4124, 0.3576, 0.1805], [0.2126, 0.7152, 0.0722],
                  [0.0193, 0.1192, 0.9505]])
    xyz = rgb @ m.T / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > 0.008856, np.cbrt(xyz), 7.787 * xyz + 16 / 116)
    return np.stack([116 * f[..., 1] - 16, 500 * (f[..., 0] - f[..., 1]),
                     200 * (f[..., 1] - f[..., 2])], -1)


palette = Image.open(SHARED_PALETTE).getpalette()[:224 * 3]
colors = np.array(palette, dtype=float).reshape(-1, 3)
lab_colors = to_lab(colors[1:])

sheet = np.zeros((FRAME * 2 * len(LAYOUT), FRAME), np.uint8)
for i, name in enumerate(LAYOUT):
    path = SOURCE / f"{name}.png"
    if name == "idle2" and not path.exists():
        canvas = np.asarray(Image.open(SOURCE / "idle.png").convert("RGBA"))
        breath = canvas.copy()
        breath[1:WAIST + 1] = canvas[0:WAIST]   # all but her boots sink 1px
        canvas = breath
    else:
        canvas = np.asarray(Image.open(path).convert("RGBA"))
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
# portrait (mugshot_source.png, cut out of its window frame) with the pink
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
