#!/usr/bin/env python3
"""Build the "???" commander's battle sheet from her supplied 64x64 art
(assets/mystery: idle0-7 and dash0-7 are the frames of her two GIFs; attack,
cast and damage are single poses).

She has her own monster resource (MysterySprites, SPR_489, games/tbs/src/
graphics/monster/mystery.png), like Kegare and Sarah.  Monster frames are
64x64 at 8 bits per pixel, raw indices into the shared 224-colour sprite
palette (games/tbs/src/system/memory/basic.png); index 0 is transparent.
Her sprite is kind 44, which reads a frame id straight as a row of this sheet,
so the frames are stored once each and the ids run one after another:

  0-7    idle (her breathing loop; 0 is also her standing pose)
  8-14   dash: stand, lean, three frames of the dark swirl, then (the GIF's
         blank sixth frame is a `blank` in spr_489.tsv) the reappearance
         and the standing frame
  15     attack (the thrust)
  16     cast
  17     damage

All the poses face right, toward the party.  Her cast is drawn facing left and
is mirrored.  Poses keep the places she was drawn at; each is lowered so that
her feet stand on the frame's bottom row.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "assets" / "mystery"
DEST = ROOT / "games/tbs/src/graphics/monster/mystery.png"
SHARED_PALETTE = ROOT / "games/tbs/src/system/memory/basic.png"

FRAME = 64
LAYOUT = ([f"idle{i}" for i in range(8)]
          + ["dash0", "dash1", "dash2", "dash3", "dash4", "dash6", "dash7"]
          + ["attack", "cast", "damage"])
FRAMES = len(LAYOUT)
MIRROR = {"cast"}
OWN_BASELINE = {"attack", "damage"}   # lowered by their own lowest row
SWIRL = {"dash2", "dash3", "dash4"}   # no feet: lowered like the idle pose

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


def load(name):
    img = Image.open(SOURCE / f"{name}.png").convert("RGBA")
    if img.size != (FRAME, FRAME):
        raise ValueError(f"{name} is {img.size}, expected {FRAME}x{FRAME}")
    return img


def feet_x(img):
    """Mean column of the lowest ten rows she occupies."""
    mask = np.asarray(img.getchannel("A")) >= 128
    rows = np.nonzero(mask.any(axis=1))[0]
    low = mask[max(rows[-1] - 9, 0):rows[-1] + 1]
    return np.nonzero(low)[1].mean()


idle = load("idle0")
idle_drop = FRAME - idle.getchannel("A").getbbox()[3]
idle_feet = feet_x(idle)

sheet = Image.new("RGBA", (FRAME, FRAME * FRAMES), (0, 0, 0, 0))
for index, name in enumerate(LAYOUT):
    img = load(name)
    dx = 0
    if name in MIRROR:
        img = img.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        dx = int(round(idle_feet - feet_x(img)))
    box = img.getchannel("A").getbbox()
    if box is None:
        raise ValueError(f"{name} is empty")
    drop = FRAME - box[3] if name in OWN_BASELINE else min(idle_drop, FRAME - box[3])
    frame = Image.new("RGBA", (FRAME, FRAME), (0, 0, 0, 0))
    frame.alpha_composite(img, (dx, drop))
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
