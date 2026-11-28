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

# Approved directional frames are checked against the exact indexed source,
# rather than weakening the original duplicate-pose checks for other frames.
REAR_PAIRS = {
    "monster/purple_beast.png": {0: "heart_idle", 5: "heart_idle"},
    "monster/slime.png": {2: "ash_jenna_slash"},
    "monster/kegare.png": {2: "kegare_slash"},
    "monster/wraith.png": {3: "wraith_cast"},
    "monster/menardi_atropos.png": {5: "atropos_cast"},
}


def check_rear_pair(picture, sheet, pair, asset):
    rear = Image.open(ROOT / "assets/rear_battle" / (asset + ".png"))
    frame = sheet.crop((0, pair * 128 + 64, 64, pair * 128 + 128))
    if (sheet.mode != "P" or rear.mode != "P" or rear.size != (64, 64)
            or rear.getpalette()[:672] != sheet.getpalette()[:672]
            or not any(rear.tobytes()) or max(rear.tobytes()) > 223
            or frame.tobytes() != rear.tobytes()):
        fail(f"{picture}: rear pose pair {pair} differs from approved indexed asset {asset}")


# Boss sheets: (picture, builder script, sprite animation table)
SHEETS = [
    ("monster/purple_beast.png", "tools/dark_story/build_heart_art.py", "sprite/spr_484.tsv"),
    ("monster/slime.png", "tools/dark_story/build_ash_jenna_art.py", "sprite/spr_477.tsv"),
    ("monster/kegare.png", "tools/dark_story/build_kegare_art.py", "sprite/spr_487.tsv"),
    ("monster/sarah.png", "tools/dark_story/build_sarah_art.py", "sprite/spr_488.tsv"),
    ("monster/wraith.png", "tools/dark_story/build_wraith_art.py", "sprite/spr_491.tsv"),
]
for picture, builder, animations in SHEETS:
    sheet = Image.open(GFX / picture)
    frames = int(re.search(r"^FRAMES = (\d+)", (ROOT / builder).read_text(), re.M).group(1))
    if sheet.size != (64, frames * 64):
        fail(f"{picture} is {sheet.size} but {builder} makes {frames} frames of 64x64 "
             f"({64}, {frames * 64})")
        continue
    # Retain the indexed-palette guarantees from the retired standalone
    # Heart artwork workflow, alongside the general animation checks.
    if picture in ("monster/purple_beast.png", "monster/slime.png"):
        if sheet.mode != "P":
            fail(f"{picture} must be indexed palette art")
        else:
            shared = Image.open(ROOT / "games/tbs/src/system/memory/basic.png").getpalette()[:224 * 3]
            palette = sheet.getpalette()[:224 * 3]
            used = set(sheet.tobytes())
            if palette != shared:
                fail(f"{picture}: palette differs from basic.png")
            if max(used) > 223 or max(used) <= 15:
                fail(f"{picture}: invalid shared palette indices")
            if picture == "monster/purple_beast.png":
                if min(used) != 0 or any(c % 8 for c in palette):
                    fail(f"{picture}: missing transparency or non-RGB555 palette")
                for pair in range(frames // 2):
                    top = sheet.crop((0, pair * 128, 64, pair * 128 + 64)).tobytes()
                    bottom = sheet.crop((0, pair * 128 + 64, 64, pair * 128 + 128)).tobytes()
                    if pair not in REAR_PAIRS.get(picture, {}) and top != bottom:
                        fail(f"{picture}: indexed pose pair {pair} differs")
    rgba = sheet.convert("RGBA")
    for pair in range(frames // 2):
        top = rgba.crop((0, pair * 128, 64, pair * 128 + 64)).tobytes()
        bottom = rgba.crop((0, pair * 128 + 64, 64, pair * 128 + 128)).tobytes()
        asset = REAR_PAIRS.get(picture, {}).get(pair)
        if asset is not None:
            check_rear_pair(picture, sheet, pair, asset)
        elif top != bottom:
            fail(f"{picture}: frames {pair * 2} and {pair * 2 + 1} differ; each pose is stored twice")
    for number in re.findall(r"frame (\d+)", (GFX / animations).read_text()):
        n = int(number)
        if n >= frames or n % 2:
            fail(f"{animations} names frame {n}, but {picture} has frames 0-{frames - 1} "
                 "and poses sit on even frames")

# Atropos is a committed sheet, not rebuilt by the art generators.
atropos_picture = "monster/menardi_atropos.png"
atropos = Image.open(GFX / atropos_picture)
if atropos.mode != "P" or atropos.size != (64, 16 * 64):
    fail("Atropos must retain its 16 indexed 64x64 frames")
else:
    for pair in range(8):
        asset = REAR_PAIRS[atropos_picture].get(pair)
        if asset is not None:
            check_rear_pair(atropos_picture, atropos, pair, asset)
        elif (atropos.crop((0, pair * 128, 64, pair * 128 + 64)).tobytes()
              != atropos.crop((0, pair * 128 + 64, 64, pair * 128 + 128)).tobytes()):
            fail(f"Atropos: unsupported pose pair {pair} differs")

# Wraith assets are deliberately not rebuilt from the battle poses by CI.
# Check the committed sheet and the regenerated portrait independently.
wraith = Image.open(GFX / "monster/wraith.png")
if wraith.mode != "P":
    fail("wraith.png must be indexed palette art")
elif wraith.size == (64, 12 * 64):
    for n in range(0, 12, 2):
        frame = wraith.crop((0, n * 64, 64, (n + 1) * 64))
        if not any(frame.tobytes()):
            fail(f"wraith.png: frame {n} is entirely transparent")
        if max(frame.tobytes()) >= 224:
            fail(f"wraith.png: frame {n} exceeds the shared sprite palette")
portrait = Image.open(GFX / "ui/icons/icon_69.png")
if portrait.mode != "P" or portrait.size != (32, 32):
    fail("icon_69.png must be 32x32 indexed portrait art")
elif not any(portrait.tobytes()) or max(portrait.tobytes()) > 15:
    fail("icon_69.png is empty or exceeds the 4-bit palette")
icons = (GFX / "ui/icons/icons.tsv").read_text().splitlines()
if len(icons) <= 69 or icons[69] != "ICON_69":
    fail("Wraith portrait is missing from icon table slot 69")

if problems:
    print("Battle art check failed:")
    for line in problems:
        print(" -", line)
    sys.exit(1)
print("Battle art check passed: backdrop palette, 6 boss sheets, approved rear poses and Wraith portrait are consistent.")
