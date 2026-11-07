#!/usr/bin/env python3
"""Builds Heart's own battle backdrop (games/tbs/src/graphics/battle_bg/
heart_floor.png) from the dusk-clouds sky (assets/heart/dusk_clouds_sky.png):
the sky above a horizon, and below it a dark glassy floor that mirrors the
clouds, so the sprites have ground to stand on. The shared dusk clouds stay as
they are for the summon animations and the credits."""
import numpy as np
from PIL import Image, ImageFilter

SRC = "assets/heart/dusk_clouds_sky.png"
OUT = "games/tbs/src/graphics/battle_bg/heart_floor.png"
HORIZON = 74          # first floor row
W, H = 256, 120

sky = Image.open(SRC).convert("RGB")
a = np.asarray(sky).astype(float)
out = a.copy()

# the sky ends in a haze just above the horizon
for y in range(HORIZON - 6, HORIZON):
    t = (y - (HORIZON - 6)) / 6.0
    haze = np.array([74.0, 56.0, 92.0])
    out[y] = out[y] * (1 - 0.45 * t) + haze * 0.45 * t

rng = np.random.default_rng(7)
# horizontal streak noise, periodic in x so the backdrop wraps cleanly
def periodic_noise(rows, seed, bands):
    r = np.random.default_rng(seed)
    n = np.zeros((rows, W))
    xs = np.arange(W) / W * 2 * np.pi
    for k in bands:
        phase = r.uniform(0, 2 * np.pi, rows)[:, None]
        amp = r.uniform(0.4, 1.0)
        n += amp * np.sin(k * xs[None, :] + phase)
    return n / len(bands)

floor_rows = H - HORIZON
noise = periodic_noise(floor_rows, 3, [3, 5, 8, 13, 21, 34])
base = np.array([40.0, 27.0, 60.0])
xs_all = np.arange(W)
VANISH_Y = HORIZON - 34
for r in range(floor_rows):
    d = r + 1
    depth = r / floor_rows                    # 0 at the horizon, 1 at the bottom
    # the reflection is rippled sideways, more toward the viewer
    ripple = (np.sin(xs_all / W * 2 * np.pi * 9 + r * 0.9) * (1.0 + 3.5 * depth)
              + np.sin(xs_all / W * 2 * np.pi * 4 - r * 0.5) * 2.0)
    src_y = max(0, HORIZON - 2 - int(d * 0.85))
    src_x = (xs_all + ripple.astype(int)) % W
    refl = a[src_y][src_x] * (0.70 - 0.28 * depth)
    streak = noise[r][:, None] * (8 + 12 * depth)
    row = base * (0.85 + 0.45 * depth) + refl * (1.0 - 0.3 * depth) + streak
    # cracked-glass tiles: grout lines that converge toward the horizon
    for i in range(16):
        x_bottom = i * (W / 16)
        t = (HORIZON + r - VANISH_Y) / float(H - VANISH_Y)
        x_line = (W / 2) + (x_bottom - W / 2) * t
        dx = np.abs(((xs_all - x_line + W / 2) % W) - W / 2)
        row = row - (dx < 0.9)[:, None] * np.array([26.0, 18.0, 34.0])
    # horizontal grout rows, spaced wider toward the viewer
    for k in range(1, 6):
        yk = int(HORIZON + floor_rows * (k / 6.0) ** 1.7)
        if yk == HORIZON + r:
            row = row - np.array([22.0, 15.0, 30.0])
    # misty horizon instead of a hard rim
    if r < 7:
        m = (1 - r / 7.0) ** 1.5
        row = row * (1 - 0.55 * m) + np.array([120.0, 88.0, 150.0]) * 0.55 * m
    out[HORIZON + r] = row

# soft vertical vignette at the sides keeps the wrap seam invisible
img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
q = img.quantize(colors=128, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
pal = q.getpalette()[:384]
pal += [0] * (384 - len(pal))
q.putpalette(pal)
q.save(OUT)
print("wrote", OUT, q.size, len(q.getcolors()), "colours")
