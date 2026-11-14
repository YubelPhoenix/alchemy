#!/usr/bin/env python3
"""Makes each boss's "breathing in" idle drawing: the standing pose with two
rows repeated, at the chest and the waist, and the feet left where they are, so
the head and shoulders rise about two pixels. The battle sheets loop the idle
between the two drawings (build_heart_art.py, build_ash_jenna_art.py,
build_kegare_art.py, build_sarah_art.py)."""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
JOBS = [("ash_jenna/v2/idle1.png", "ash_jenna/v2/idle_breath.png"),
        ("kegare/idle1.png", "kegare/idle_breath.png"),
        ("sarah/idle_new.png", "sarah/idle_breath.png"),
        ("heart/v2/idle1.png", "heart/v2/idle2.png")]
for source, dest in JOBS:
    src = Image.open(ROOT / "assets" / source).convert("RGBA")
    l, t, r, b = src.getchannel("A").getbbox()
    art = np.asarray(src.crop((l, t, r, b)))
    h = art.shape[0]
    rows = []
    for y in range(h):
        rows.append(art[y])
        if y in (int(h * 0.30), int(h * 0.82)):
            rows.append(art[y])
    new = np.stack(rows)
    assert t - 2 >= 0, (source, t)
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    out.alpha_composite(Image.fromarray(new), (l, b - new.shape[0]))
    if source.startswith("ash_jenna"):
        # her blade angles down to the left of the body: lift it a pixel with
        # the hips, so its tip moves too (rows 46 down, left of the body)
        o = np.asarray(src).copy()
        o[:, :] = o
        o2 = np.asarray(out).copy()
        o2[45:, :22] = 0
        o2[45:63, :22] = o[46:64, :22]
        out = Image.fromarray(o2)
    if source.startswith("sarah"):
        # Her pike runs from its butt at the upper left (8, 25) down to the
        # blade's tip at the lower right (54, 61). Above row 52 it already
        # rises a pixel with her hands; lift the blade below that a pixel
        # too, so the whole pike moves as one and its tip breathes with her.
        o = np.asarray(src)
        o2 = np.asarray(out).copy()
        for y in range(51, 64):
            edge = int(8 + (y - 25) * 46 / 36) - 2
            o2[y, edge:] = 0
            if y + 1 < 64:
                o2[y, edge:] = o[y + 1, edge:]
        out = Image.fromarray(o2)
    out.save(ROOT / "assets" / dest)
    print(dest, "rows", h, "->", new.shape[0], "bbox", out.getchannel("A").getbbox())
