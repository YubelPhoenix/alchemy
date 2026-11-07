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
        if y in (int(h * 0.35), int(h * 0.62)):
            rows.append(art[y])
    new = np.stack(rows)
    # the lower body sways: from the waist down to just above the feet, the
    # rows shift one pixel (two near the hem), so the cloak, skirt and legs
    # move with the breath while the feet stay planted
    n = new.shape[0]
    for y in range(int(n * 0.62), n - 5):
        shift = 2 if y > n * 0.82 else 1
        row = np.zeros_like(new[y])
        row[shift:] = new[y][:-shift]       # no wrap-around at the edge
        new[y] = row
    assert t - 2 >= 0, (source, t)
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    out.alpha_composite(Image.fromarray(new), (l, b - new.shape[0]))
    out.save(ROOT / "assets" / dest)
    print(dest, "rows", h, "->", new.shape[0], "bbox", out.getchannel("A").getbbox())
