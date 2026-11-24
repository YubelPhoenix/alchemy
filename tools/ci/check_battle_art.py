#!/usr/bin/env python3
"""Fails early, with a plain message, when battle art would break the build or
the game: a backdrop palette the graphics encoder rejects, a boss sheet whose
size doesn't match its builder, or an animation that names a missing frame.
Run from the repository root."""
import re
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
GFX = ROOT / "games/tbs/src/graphics"
problems = []


def fail(message):
    problems.append(message)


# Heart's backdrop: 256x120, a palette of exact RGB555 colours, the four glowing
# tile-seam entries (120-123) in use and nothing above them.
backdrop = Image.open(GFX / "battle_bg/heart_floor.png")
if backdrop.mode != "P" or backdrop.size != (256, 120):
    fail(f"heart_floor.png must be 256x120 palette art, is {backdrop.mode} {backdrop.size}")
else:
    palette = backdrop.getpalette()[:128 * 3]
    odd = [i // 3 for i, v in enumerate(palette) if v % 8]
    if odd:
        fail("heart_floor.png palette entries are not exact RGB555 (each "
             f"channel a multiple of 8), e.g. entry {odd[0]}; the graphics encoder rejects them")
    used = set(backdrop.tobytes())
    if max(used) > 127:
        fail(f"heart_floor.png uses palette entry {max(used)}; battle backdrops have 128")
    missing = [e for e in range(120, 124) if e not in used]
    if missing:
        fail(f"heart_floor.png does not use seam entries {missing}; background.c pulses 120-123")

# Boss sheets: (picture, builder script, sprite animation table)
SHEETS = [
    ("monster/purple_beast.png", "tools/dark_story/build_heart_art.py", "sprite/spr_484.tsv"),
    ("monster/slime.png", "tools/dark_story/build_ash_jenna_art.py", "sprite/spr_477.tsv"),
    ("monster/kegare.png", "tools/dark_story/build_kegare_art.py", "sprite/spr_487.tsv"),
    ("monster/sarah.png", "tools/dark_story/build_sarah_art.py", "sprite/spr_488.tsv"),
]
for picture, builder, animations in SHEETS:
    sheet = Image.open(GFX / picture)
    frames = int(re.search(r"^FRAMES = (\d+)", (ROOT / builder).read_text(), re.M).group(1))
    if sheet.size != (64, frames * 64):
        fail(f"{picture} is {sheet.size} but {builder} makes {frames} frames of 64x64 "
             f"({64}, {frames * 64})")
        continue
    rgba = sheet.convert("RGBA")
    for pair in range(frames // 2):
        top = rgba.crop((0, pair * 128, 64, pair * 128 + 64)).tobytes()
        bottom = rgba.crop((0, pair * 128 + 64, 64, pair * 128 + 128)).tobytes()
        if top != bottom:
            fail(f"{picture}: frames {pair * 2} and {pair * 2 + 1} differ; each pose is stored twice")
    for number in re.findall(r"frame (\d+)", (GFX / animations).read_text()):
        n = int(number)
        if n >= frames or n % 2:
            fail(f"{animations} names frame {n}, but {picture} has frames 0-{frames - 1} "
                 "and poses sit on even frames")

if problems:
    print("Battle art check failed:")
    for line in problems:
        print(" -", line)
    sys.exit(1)
print("Battle art check passed: backdrop palette and 4 boss sheets are consistent.")
