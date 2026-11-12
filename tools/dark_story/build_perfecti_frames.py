#!/usr/bin/env python3
"""Draws the Mystery Leader's attack frames for the battle canvas.

Every frame is 64x48 canvas texels of brightness 0-63 (0 is see-through; the
violet ramp in perfecti.c colours the rest). The canvas is shown at twice its
width, so each picture is drawn at 128x48 screen pixels and then halved
across. Frames are packed with the same RLE as Gotterkanone
(gotterkanone_stream.c) into one stream:

  games/tbs/src/battle_anim/parts/perfecti_frames.rle
  games/tbs/src/battle_anim/parts/perfecti_frames.h   (offsets, move frame ranges)

Run from anywhere; --preview DIR also writes a PNG strip per move. The art is
original and procedural: change a drawing below and run it again.
"""
import argparse
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
PARTS = ROOT / "games/tbs/src/battle_anim/parts"
W, H = 64, 48          # canvas texels
SW, SH = 128, 48       # screen pixels
SS = 3                 # supersampling

# Screen-space sample grid, centre of each supersample.
ys, xs = np.mgrid[0:SH * SS, 0:SW * SS].astype(np.float64)
X = (xs + 0.5) / SS
Y = (ys + 0.5) / SS


def finish(img):
    """Screen image (0..1) -> 64x48 bytes 0..63, faint fringe removed."""
    img = np.clip(img, 0.0, 1.0)
    img = img.reshape(SH, SS, SW, SS).mean(axis=(1, 3))      # supersample
    img = img.reshape(SH, W, 2).mean(axis=2)                  # halve across
    out = np.round(img * 63).astype(np.int32)
    out[out < 7] = 0       # a faint value would draw as a dark violet haze
    return out.astype(np.uint8)


def noise(rng, scale, octaves=3):
    """Smooth periodic value noise in screen space (period SW across)."""
    total = np.zeros_like(X)
    amp, freq, norm = 1.0, scale, 0.0
    for _ in range(octaves):
        gx, gy = int(SW / freq), int(SH / freq) + 2
        grid = rng.random((gy + 1, gx))
        fx, fy = X / freq, Y / freq
        x0, y0 = np.floor(fx).astype(int), np.floor(fy).astype(int)
        tx, ty = fx - x0, fy - y0
        tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
        g = lambda yy, xx: grid[np.clip(yy, 0, gy), xx % gx]
        top = g(y0, x0) * (1 - tx) + g(y0, x0 + 1) * tx
        bot = g(y0 + 1, x0) * (1 - tx) + g(y0 + 1, x0 + 1) * tx
        total += amp * (top * (1 - ty) + bot * ty)
        norm += amp
        amp *= 0.5
        freq /= 2
    return total / norm


def orb(cx, cy, r, core=1.0, falloff=1.6):
    d = np.hypot(X - cx, Y - cy) / r
    return core * np.clip(1 - d, 0, 1) ** falloff


def ellipse_ring(cx, cy, rx, ry, width, strength):
    d = np.hypot((X - cx) / rx, (Y - cy) / ry)
    return strength * np.exp(-((d - 1) * min(rx, ry) / width) ** 2)


# ---------------------------------------------------------------- the moves

def ex_gotterkanone(rng):
    """A white-hot violet orb wreathed in flares, three motes orbiting it."""
    frames = []
    for f in range(8):
        n = noise(np.random.default_rng(100 + f), 10)
        ang = np.arctan2(Y - 24, (X - 64) / 1.3)
        flare = np.clip(np.sin(ang * 7 + f * 0.8) * 0.5 + n, 0, None)
        d = np.hypot((X - 64) / 1.3, Y - 24)
        img = orb(64, 24, 17, 1.0, 1.2) + 0.55 * np.clip(1 - d / (20 + 5 * flare), 0, 1)
        img = np.maximum(img, orb(64, 24, 7, 1.15, 0.8))
        for k in range(3):
            a = f / 8 * 2 * math.pi + k * 2 * math.pi / 3
            img = np.maximum(img, orb(64 + 34 * math.cos(a), 24 + 15 * math.sin(a), 3.5, 0.95, 1.0))
        frames.append(img)
    return frames


def ransnetz(rng):
    """A small homing mote with a turning four-point glint."""
    frames = []
    for f in range(8):
        a = f / 8 * math.pi / 2
        img = orb(64, 24, 10, 1.0, 1.2) + 0.35 * orb(64, 24, 16, 1.0, 2.0)
        rx, ry = X - 64, Y - 24
        u = rx * math.cos(a) + ry * math.sin(a)
        v = -rx * math.sin(a) + ry * math.cos(a)
        glint = np.exp(-(v / 1.1) ** 2) * np.clip(1 - np.abs(u) / 21, 0, 1) + \
            np.exp(-(u / 1.3) ** 2) * np.clip(1 - np.abs(v) / 21, 0, 1)
        flicker = 0.75 + 0.25 * (f % 2)
        frames.append(np.maximum(img, glint * flicker))
    return frames


def explosion(rng):
    """A core flash and a flattened shock ring, with sparks flung outward."""
    frames = []
    sparks = [(rng.random() * 2 * math.pi, 0.6 + 0.4 * rng.random()) for _ in range(14)]
    for f in range(12):
        t = f / 11
        core = orb(64, 24, 6 + 18 * t ** 0.5, max(0.0, 1.2 - 1.4 * t), 0.9)
        ring = ellipse_ring(64, 24, 10 + 50 * t, 5 + 18 * t, 2.5, max(0.0, 1.0 - t))
        img = core + ring
        for ang, speed in sparks:
            r = (8 + 52 * t) * speed
            img = np.maximum(img, orb(64 + r * math.cos(ang), 24 + r * 0.38 * math.sin(ang),
                                      2.5, max(0.0, 1.0 - t * 0.9), 1.0))
        frames.append(img)
    return frames


def p_vortex(rng):
    """Three spiral arms turning inward around a bright eye."""
    frames = []
    for f in range(8):
        rx, ry = (X - 64) / 1.9, Y - 24
        r = np.hypot(rx, ry) + 1e-6
        ang = np.arctan2(ry, rx)
        arms = np.cos(3 * ang + 5.0 * np.log(r) - f / 8 * 2 * math.pi) * 0.5 + 0.5
        env = np.clip(1 - r / 23, 0, 1) ** 0.8 * np.clip(r / 3, 0, 1)
        img = arms ** 3 * env * 1.1 + orb(64, 24, 4, 1.0, 1.0)
        frames.append(img)
    return frames


def glepnir(rng):
    """A full-width binding beam: it swells, its chain knots run, it fades.
    Period 32 across so two tiles meet seamlessly."""
    frames = []
    for f in range(12):
        if f < 3:
            half, phase = 2 + 2 * f, 0
        elif f < 9:
            half, phase = 8, (f - 3) / 6 * 32
        else:
            half, phase = 8 - 2.5 * (f - 8), 0
        dy = Y - 24
        band = np.exp(-(dy / half) ** 2)
        core = np.exp(-(dy / max(1.0, half * 0.35)) ** 2)
        xx = (X - phase) % 32 - 16
        knot = np.exp(-((np.hypot(xx / 9, dy / (half + 4)) - 1) * 6) ** 2) * (f >= 3) * (f < 9)
        frames.append(0.65 * band + 0.5 * core + 0.6 * knot)
    return frames


def ex_sternbrecher(rng):
    """Four frames of charge gathering at the user, then eight of a thick
    white-cored laser (period 64 across) with rippling edges."""
    frames = []
    for f in range(4):
        r = 5 + 3 * f
        img = orb(64, 24, r, 1.0, 1.0) + 0.4 * orb(64, 24, r + 8, 1.0, 2.0)
        for k in range(10):
            a = k * 2 * math.pi / 10 + f * 0.4
            dist = 30 - 6 * f
            img = np.maximum(img, orb(64 + dist * 1.8 * math.cos(a), 24 + dist * 0.7 * math.sin(a), 2.5, 0.9, 1.0))
        frames.append(img)
    for f in range(8):
        dy = Y - 24
        edge = 13 + 2.5 * np.sin(X / 64 * 2 * math.pi * 2 + f / 8 * 2 * math.pi)
        body = np.clip(1 - np.abs(dy) / edge, 0, 1) ** 0.7
        core = np.exp(-(dy / 4.5) ** 2) * (1.15 if f % 2 == 0 else 1.0)
        streak = (np.sin(X / 64 * 2 * math.pi * 4 - f / 8 * 2 * math.pi * 2) * 0.5 + 0.5) ** 6
        frames.append(0.7 * body + 0.6 * core + 0.25 * streak * body)
    return frames


def p_storm(rng):
    """A jagged violet bolt striking down, flaring where it lands."""
    frames = []
    for f in range(6):
        r = np.random.default_rng(300 + f)
        pts = [(64.0, -2.0)]
        for step in range(1, 9):
            pts.append((64 + r.normal(0, 4.5), step * 5.5))
        pts[-1] = (64.0, 44.0)
        bolt = np.zeros_like(X)
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            vx, vy = x1 - x0, y1 - y0
            t = np.clip(((X - x0) * vx + (Y - y0) * vy) / (vx * vx + vy * vy), 0, 1)
            d = np.hypot(X - (x0 + t * vx), Y - (y0 + t * vy))
            bolt = np.maximum(bolt, np.exp(-(d / 1.3) ** 2) + 0.35 * np.exp(-(d / 4) ** 2))
        flare = orb(64, 44, 6 + 3 * (f % 3), 1.0, 1.0) * (0.6 + 0.4 * ((f + 1) % 2))
        frames.append(np.maximum(bolt, flare))
    return frames


MOVES = [
    ("EX_GOTTERKANONE", ex_gotterkanone),
    ("RANSNETZ", ransnetz),
    ("EXPLOSION", explosion),
    ("P_VORTEX", p_vortex),
    ("GLEPNIR", glepnir),
    ("STERNBRECHER", ex_sternbrecher),
    ("P_STORM", p_storm),
]


def rle(frame):
    data = bytes(frame.flatten())
    out = bytearray()
    i = 0
    while i < len(data):
        run = 1
        while i + run < len(data) and run < 128 and data[i + run] == data[i]:
            run += 1
        if run >= 3:
            out += bytes([0x80 | (run - 1), data[i]])
            i += run
            continue
        start = i
        while i < len(data) and i - start < 128:
            if i + 2 < len(data) and data[i] == data[i + 1] == data[i + 2]:
                break
            i += 1
        out += bytes([i - start - 1]) + data[start:i]
    return bytes(out)


def unrle(src):
    out = bytearray()
    i = 0
    while i < len(src):
        c = src[i]
        i += 1
        n = (c & 127) + 1
        if c & 128:
            out += bytes([src[i]]) * n
            i += 1
        else:
            out += src[i:i + n]
            i += n
    return bytes(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", type=Path)
    args = ap.parse_args()

    stream = bytearray()
    offsets = []
    ranges = []
    all_frames = []
    for name, draw in MOVES:
        frames = [finish(f) for f in draw(np.random.default_rng(7))]
        ranges.append((name, len(all_frames), len(frames)))
        for frame in frames:
            packed = rle(frame)
            assert unrle(packed) == bytes(frame.flatten()) and len(unrle(packed)) == W * H
            offsets.append(len(stream))
            stream += packed
            all_frames.append(frame)
        if args.preview:
            from PIL import Image
            args.preview.mkdir(parents=True, exist_ok=True)
            strip = np.concatenate([np.pad(np.repeat(f, 2, axis=1), ((0, 0), (0, 4)))
                                    for f in frames], axis=1)
            rgb = np.stack(ramp(strip), axis=-1).astype(np.uint8)
            Image.fromarray(rgb).resize((rgb.shape[1] * 2, rgb.shape[0] * 2), Image.NEAREST) \
                .save(args.preview / f"{name.lower()}.png")
    offsets.append(len(stream))

    (PARTS / "perfecti_frames.rle").write_bytes(bytes(stream))
    lines = [
        "/* Generated by tools/dark_story/build_perfecti_frames.py: do not edit. */",
        "#ifndef PERFECTI_FRAMES_H",
        "#define PERFECTI_FRAMES_H",
        '#include "types.h"',
        f"#define PERFECTI_FRAME_COUNT {len(all_frames)}",
    ]
    for name, first, count in ranges:
        lines.append(f"#define PERFECTI_{name}_FIRST {first}")
        lines.append(f"#define PERFECTI_{name}_COUNT {count}")
    body = ", ".join(str(o) for o in offsets)
    lines.append(f"static const u16 sPerfectiFrameOffsets[{len(offsets)}] = {{{body}}};")
    if max(offsets) > 0xFFFF:
        raise SystemExit("frame stream exceeds 64 KB: widen the offsets to u32")
    lines.append("#endif")
    (PARTS / "perfecti_frames.h").write_text("\n".join(lines) + "\n")
    print(f"{len(all_frames)} frames, {len(stream)} bytes")


def ramp(levels):
    """The in-game violet ramp (perfecti.c / gotterkanone_native.c), as RGB."""
    lv = levels.astype(np.int32)
    lo = lv <= 31
    r = np.where(lo, lv * 24 // 31, 24 + (lv - 31) * 7 // 32)
    g = np.where(lo, lv * 3 // 31, 3 + (lv - 31) * 28 // 32)
    b = np.where(lo, lv * 25 // 31, 25 + (lv - 31) * 6 // 32)
    see = lv == 0
    return [np.where(see, 40, c * 255 // 31) for c in (r, g, b)]


if __name__ == "__main__":
    main()
