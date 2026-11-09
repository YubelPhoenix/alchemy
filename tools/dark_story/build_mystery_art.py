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

All the poses are used as drawn (none mirrored).  Poses keep the places she was drawn at; each is lowered so that
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
MIRROR = set()   # cast was mirrored once and faced the wrong way in battle
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


EYE = (195, 54, 64)        # her eyes are single red pixels in the drawings
EYE_GLOW = (255, 104, 112)
EYE_SHINE = (255, 236, 240)


def add_eye_shine(img):
    """Brightens each red eye pixel in the head and lights the pixel above it,
    so the eyes catch the light.  The scarf and cloak, lower down, are not
    touched."""
    px = img.load()
    for y in range(0, 30):
        for x in range(FRAME):
            r, g, b, a = px[x, y]
            if a >= 128 and (r, g, b) == EYE:
                px[x, y] = EYE_GLOW + (255,)
                if y > 0 and px[x, y - 1][3] >= 128:
                    px[x, y - 1] = EYE_SHINE + (255,)
    return img


# How far the breath has swung her hair and cloak out on each idle frame (the
# drawings' left edge runs 18, 16, 12, 9, 5, 5, 8, 16).  Only the cloak's left
# side moves in the drawings, so the red lining on the right, beside the spear,
# and the patch under the coat sway with it here, a pixel at a time.
SWING = [0.0, 0.15, 0.46, 0.69, 1.0, 1.0, 0.77, 0.23]


def sway_cape(img, frame):
    import math
    px = img.load()

    def is_red(x, y):
        r, g, b, a = px[x, y]
        return a >= 128 and r > g + 45 and r > b + 45

    def shift_run(y, x0, x1, dx):
        """Moves the red run x0..x1 of row y by dx (-1), the pixel it leaves
        taking its right-hand neighbour's colour and the one it covers red."""
        red = px[x0, y]
        leave = px[x1 + 1, y]
        for x in range(x0, x1 + 1):
            if x + dx < x0:
                px[x + dx, y] = red
        px[x1, y] = leave

    swing = SWING[frame]
    for y in range(40, 54):
        # the lining on the right, columns 39-43
        wave = math.sin(0.8 * y + 1.3 * frame)
        if swing * wave > 0.35:
            x = 39
            while x < 44 and not is_red(x, y):
                x += 1
            x1 = x
            while x1 < 45 and is_red(x1 + 1, y):
                x1 += 1
            if x < 44 and is_red(x, y) and not is_red(x - 1, y):
                shift_run(y, x, x1, -1)
    for y in range(53, 56):
        # the patch of lining under the coat, between the legs
        wave = math.sin(1.1 * y + 0.9 * frame)
        if swing * wave > 0.3:
            x = 29
            while x < 36 and not is_red(x, y):
                x += 1
            if x < 36:
                x1 = x
                while x1 < 36 and is_red(x1 + 1, y):
                    x1 += 1
                shift_run(y, x, x1, -1)
    # The hem at the cloak's lower left (rows 50-54, columns 20-27) is the same
    # in every drawing: draw it swinging out with the rest of the left side.
    hem = {}
    for y in range(50, 55):
        hem[y] = [px[x, y] for x in range(20, 28)]
    for y in range(50, 55):
        d = round(swing * (1.0 + 0.7 * math.sin(0.9 * y + 1.3 * frame)) * 1.5)
        d = max(0, min(d, 2))
        for k in range(d):
            px[27 - k, y] = px[28, y]
        for k, colour in enumerate(hem[y]):
            if colour[3] >= 128 or d == 0:
                if 20 + k - d >= 0:
                    px[20 + k - d, y] = colour
    return img


def load(name):
    img = Image.open(SOURCE / f"{name}.png").convert("RGBA")
    if img.size != (FRAME, FRAME):
        raise ValueError(f"{name} is {img.size}, expected {FRAME}x{FRAME}")
    if name.startswith("idle"):
        img = sway_cape(img, int(name[4:]))
    return add_eye_shine(img)


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
