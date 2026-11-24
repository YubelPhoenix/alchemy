#!/usr/bin/env python3
"""Draws the Mystery Leader's battle backdrop (games/tbs/src/graphics/
battle_bg/mystery_citadel.png): a deep violet void above a dark steel deck,
thin charcoal gantries with crimson beacons on the horizon, and faint crimson
seams in the deck plates, after her greatcoat's lining. Everything repeats
every 256 pixels across, so the backdrop wraps as the battle camera pans.

Battle backdrops are 256x120 palette art of 128 exact RGB555 colours. The
art keeps 0 to 111; Mystery_StepBackdropGlow (battle/mystery_backdrop.c)
rewrites the rest every frame: 112 to 115 are each beacon's core and three
halo rings, which pulse, and 116 to 123 are eight groups of one-pixel stars,
which twinkle out of step. 124 to 127 are unused. The PNG stores each
animated entry at rest so the backdrop looks right before the task runs.

The art is original and procedural: change a drawing below and run it again.
--preview FILE also writes a 3x preview with her standing on it.
"""
import argparse
import math
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "games/tbs/src/graphics/battle_bg/mystery_citadel.png"
SPRITE = ROOT / "games/tbs/src/graphics/monster/mystery.png"
W, H = 256, 120
HORIZON = 74
STATIC = 112                 # entries the art keeps
BEACON_FIRST = 112           # core, then three halo rings
STAR_FIRST = 116             # eight twinkle groups
BEACONS = ((20, 40, 5), (84, 26, 3), (150, 46, 6), (214, 30, 4))

ys, xs = np.mgrid[0:H, 0:W].astype(float)
TAU = 2 * math.pi


def periodic_noise(seed, octaves, base):
    """Smooth noise that repeats every W pixels across."""
    r = np.random.default_rng(seed)
    out = np.zeros((H, W))
    amp, total = 1.0, 0.0
    for o in range(octaves):
        k = base * 2 ** o
        for _ in range(4):
            fx = r.integers(1, k + 1)
            fy = r.uniform(0.02, 0.12) * 2 ** o
            ph = r.uniform(0, TAU, 2)
            out += amp * np.sin(xs / W * TAU * fx + ph[0]) * np.sin(ys * fy + ph[1])
        total += amp * 4
        amp *= 0.5
    return out / total


def lerp(a, b, t):
    t = np.clip(t, 0, 1)[..., None]
    return np.asarray(a, float) * (1 - t) + np.asarray(b, float) * t


def draw():
    img = np.zeros((H, W, 3))

    # The void: near-black violet at the top, a lit violet haze at the horizon.
    t = ys / HORIZON
    sky = lerp((14, 6, 24), (92, 52, 128), t ** 1.6)
    ribbons = periodic_noise(3, 3, 1)
    band = np.exp(-((ys - 30 - 10 * np.sin(xs / W * TAU * 2)) / 9) ** 2)
    sky += (band * np.clip(ribbons * 2 + 0.4, 0, 1))[..., None] * np.array([70, 30, 100])
    img[:HORIZON] = sky[:HORIZON]

    # Gantries on the horizon: thin charcoal towers with a crimson beacon.
    beacon = np.zeros((H, W), int)              # 0, or 1 core to 4 outer ring
    tower = np.zeros((H, W), bool)
    for gx, gh, gw in BEACONS:
        top = HORIZON - gh
        body = (np.abs(((xs - gx + W / 2) % W) - W / 2) <= gw / 2) & (ys >= top) & (ys < HORIZON)
        img[body] = (34, 30, 40)
        tower |= body
        rim = body & (np.abs(((xs - gx + W / 2) % W) - W / 2 + gw / 2) < 1)
        img[rim] = (70, 56, 88)
        for strut in range(top + 6, HORIZON - 2, 8):   # cross struts
            arm = (np.abs(((xs - gx + W / 2) % W) - W / 2) <= gw / 2 + 3) & (np.abs(ys - strut) < 0.6)
            img[arm] = (40, 34, 48)
            tower |= arm
        d = np.hypot(((xs - gx + W / 2) % W) - W / 2, ys - (top - 2))
        for ring, radius in enumerate((1.3, 2.3, 3.4, 4.6)):
            beacon[(d < radius) & (beacon == 0)] = ring + 1

    # Haze where the deck meets the void.
    haze = np.exp(-((ys - HORIZON) / 3.0) ** 2)[..., None] * np.array([60, 36, 84])
    img += haze

    # The deck: dark steel plates, rows narrowing toward the horizon, faint
    # crimson light in the seams and the void's violet mirrored near it.
    floor = ys >= HORIZON
    depth = (ys - HORIZON + 1) / (H - HORIZON)
    steel = lerp((30, 26, 36), (46, 42, 52), depth)
    grain = periodic_noise(5, 2, 4) * 8
    deck = steel + grain[..., None]
    row = np.zeros_like(floor)                      # perspective rows
    for k in range(1, 8):
        row |= np.round(ys) == HORIZON + round((H - HORIZON) * (k / 7.5) ** 1.7)
    row &= floor
    col = (np.abs((xs % 32) - 16) < 0.6 + depth * 0.4) & floor
    seam = row | col
    deck[seam] = deck[seam] * 0.55 + np.array([110, 18, 22]) * 0.45 * depth[seam][..., None] ** 0.6
    mirror = np.exp(-(ys - HORIZON) / 9.0)[..., None] * np.array([46, 26, 66])
    deck += mirror
    img[floor] = deck[floor]

    # Stars: single pixels in the void, each in one of eight twinkle groups;
    # a few bright ones are crosses.
    stars = np.full((H, W), -1)
    r = np.random.default_rng(11)
    for _ in range(70):
        sx, sy = int(r.integers(0, W)), int(r.integers(2, HORIZON - 12))
        if beacon[sy, sx] or tower[sy, sx]:
            continue
        group = int(r.integers(0, 8))
        stars[sy, sx] = group
        if r.random() < 0.15:
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                stars[sy + dy, (sx + dx) % W] = group
    return np.clip(img, 0, 255), beacon, stars


def rest_colours():
    """The animated entries at rest (RGB, 0-255): beacons half lit, stars dim."""
    sky = np.array([40, 22, 62])
    red = np.array([248, 48, 40])
    beacon = [sky + (red - sky) * w * 0.6 for w in (1.0, 0.6, 0.35, 0.18)]
    stars = [np.array([120, 96, 160])] * 8
    return [np.clip(c, 0, 255) for c in beacon + stars]


def build(rgb, beacon, stars):
    im = Image.fromarray(rgb.astype(np.uint8), "RGB").quantize(STATIC, dither=Image.Dither.NONE)
    pal = np.array(im.getpalette()[:STATIC * 3]).reshape(-1, 3)
    pal = np.vstack([pal, rest_colours(), np.zeros((4, 3))])
    pal = (pal.astype(int) // 8) * 8           # exact RGB555
    index = np.asarray(im).astype(np.uint8).copy()
    index[beacon > 0] = BEACON_FIRST + beacon[beacon > 0] - 1
    index[stars >= 0] = STAR_FIRST + stars[stars >= 0]
    out = Image.fromarray(index, "P")
    out.putpalette(pal.flatten().tolist())     # exactly 128 entries
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", type=Path)
    args = ap.parse_args()
    im = build(*draw())
    used = len(set(im.tobytes()))
    assert im.size == (W, H) and len(im.getpalette()) == 128 * 3 and max(im.tobytes()) < 124
    im.save(OUT)
    print(f"{OUT.name}: {used} colours")
    if args.preview:
        view = im.convert("RGBA")
        wide = Image.new("RGBA", (W * 2, H))
        wide.paste(view, (0, 0))
        wide.paste(view, (W, 0))                 # shows the wrap seam
        sprite = Image.open(SPRITE).convert("RGBA").crop((0, 0, 64, 64))
        sprite.putdata([(0, 0, 0, 0) if p[:3] == (0, 0, 0) else p for p in sprite.get_flattened_data()])
        wide.alpha_composite(sprite, (W - 32 + 40, 96 - 64))
        wide.resize((W * 2 * 3, H * 3), Image.NEAREST).save(args.preview)


if __name__ == "__main__":
    main()
