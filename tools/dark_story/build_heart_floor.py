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
grout = np.zeros((H, W), bool)   # the tile seams, which glow in the game
noise = periodic_noise(floor_rows, 3, [3, 5, 8, 13, 21, 34])
base = np.array([40.0, 27.0, 60.0])
xs_all = np.arange(W)
VANISH_Y = HORIZON - 120   # a far vanishing point: seams reach both edges
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
        x_line = x_bottom   # parallel seams: they wrap and fill the whole width
        dx = np.abs(((xs_all - x_line + W / 2) % W) - W / 2)
        row = row - (dx < 0.9)[:, None] * np.array([26.0, 18.0, 34.0])
        grout[HORIZON + r] |= dx < 0.9
    # horizontal grout rows, spaced wider toward the viewer
    for k in range(1, 9):
        yk = int(HORIZON + floor_rows * (k / 9.0) ** 1.5)
        if yk == HORIZON + r:
            row = row - np.array([22.0, 15.0, 30.0])
            grout[HORIZON + r, :] = True
    # misty horizon instead of a hard rim
    if r < 7:
        m = (1 - r / 7.0) ** 1.5
        row = row * (1 - 0.55 * m) + np.array([120.0, 88.0, 150.0]) * 0.55 * m
    out[HORIZON + r] = row

# Glowing tile seams and three distant lightning bolts. They are painted after
# the floor is quantised, with palette entries reserved for them; the battle
# code (background.c, Heart_StepBackdropGlow) animates them:
#   120-123  the tile seams, four phases from the horizon outward
#   112-117  three bolts: entry 112+2b is bolt b, 113+2b the glare where it
#            strikes the floor. Their colours here are the "off" colours (the
#            cloud and floor they sit on); the game lights them during a flash.
NQ = 112
CORE = 120
img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
q = img.quantize(colors=NQ, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
idx = np.array(q)
pal = list(q.getpalette()[:NQ * 3])
pal += [0] * (384 - len(pal))
for y in range(HORIZON + 3, H):
    ph = ((y - HORIZON) // 4) % 4
    xs = np.nonzero(grout[y])[0]
    idx[y, xs] = CORE + ph
for k in range(4):
    pal[(CORE + k) * 3:(CORE + k) * 3 + 3] = [200, 72, 248]
rng2 = np.random.default_rng(5)
for b, bx in enumerate([44, 130, 214]):
    pts = []
    x, y = bx, 22
    while y < HORIZON:
        pts.append((x % W, y))
        y += 1
        if rng2.random() < 0.55:
            x += int(rng2.integers(-2, 3))
    bolt = list(pts) + [((px + 1) % W, py) for px, py in pts]   # two pixels wide
    # a short fork partway down
    fx, fy = pts[len(pts) // 2]
    for n in range(14):
        fx += 1 if b % 2 else -1
        fy += 1 if n % 2 else 0
        if fy < HORIZON:
            bolt.append((fx % W, fy))
    end_x = pts[-1][0]
    # off colour: the sky the bolt hides in
    under = np.array([out[y, x] for x, y in bolt])
    pal[(112 + 2 * b) * 3:(112 + 2 * b) * 3 + 3] = [int(v * 0.9) for v in under.mean(axis=0)]
    for x, y in bolt:
        idx[y, x] = 112 + 2 * b
    # the glare on the floor where it lands: a flat ellipse
    glare = []
    for gy in range(HORIZON, HORIZON + 6):
        half = 15 - 2 * (gy - HORIZON)
        for gx in range(-half, half + 1):
            glare.append(((end_x + gx) % W, gy))
    gunder = np.array([out[y, x] for x, y in glare])
    pal[(113 + 2 * b) * 3:(113 + 2 * b) * 3 + 3] = [int(v) for v in gunder.mean(axis=0)]
    for x, y in glare:
        idx[y, x] = 113 + 2 * b
q = Image.fromarray(idx.astype(np.uint8), "P")
# the graphics encoder only takes exact RGB555 colours (multiples of 8)
pal = [min(248, int(round(v / 8.0)) * 8) for v in pal]
q.putpalette(pal)
q.save(OUT)
print("wrote", OUT, q.size, len(set(idx.flatten().tolist())), "colours used")
