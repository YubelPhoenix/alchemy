#!/usr/bin/env python3
"""Build the Grove's figures (SPR_508, 32x64): Kolima's people, half become
trees.

Each figure is a villager's head and body (their own sprite, their own face,
drawn in one dead flesh-and-bark ramp) growing out of the trunk and roots of
Kolima's cursed tree (SPR_105) from the waist down, with a dead grey crown
grown from the head and both arms raised and gone to branches into it. The
mouth is open.

The sheet's three facings are three different people (the actor's facing
picks one: south the woman in the apron, SPR_106; east the young man,
SPR_108; north the man in orange, SPR_109), and frames 3-5 are the same three
breathing: everything above the roots sinks a pixel and the mouth opens
wider; the idle animation swaps them slowly.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPR = ROOT / "games/tbs/src/graphics/sprite"
FLESH = [(45, 45), (100, 88), (150, 131), (200, 131), (240, 138)]
DEAD = [(56, 13), (80, 218), (96, 220), (128, 222), (152, 14)]
DARK, THROAT, BARK = 218, 18, 45
PEOPLE = [0x6A, 0x6C, 0x6D]
HEAD_ROW = 24        # where a villager's frame row 4 lands on the canvas
WAIST = 21           # villager frame rows below this are legs: replaced
TRUNK_TOP = HEAD_ROW + WAIST - 4

tree = Image.open(SPR / "spr_105.png")
pal = tree.getpalette()
tree_px = np.asarray(tree)[0:32]


def light(i):
    r, g, b = pal[3 * i:3 * i + 3]
    return 0.3 * r + 0.59 * g + 0.11 * b


def ramp(v, table):
    return min(table, key=lambda t: abs(t[0] - light(v)))[1]


def figure(person, breath):
    canvas = np.zeros((64, 32), np.uint8)
    # The dead crown, the tree's own (rows 0-15), above the head.
    for y in range(16):
        for x in range(32):
            if tree_px[y, x]:
                canvas[HEAD_ROW - 12 + y, x] = ramp(int(tree_px[y, x]), DEAD)
    # Arms raised into the crown: from each shoulder up and out.
    for i in range(9):
        canvas[HEAD_ROW + 9 - i, 9 - i // 3] = BARK
        canvas[HEAD_ROW + 9 - i, 22 + i // 3] = BARK
    # The trunk and roots (tree rows 16-31), stretched to fill the waist down.
    for y in range(64 - TRUNK_TOP):
        src = 16 + y * 16 // (64 - TRUNK_TOP)
        for x in range(32):
            if tree_px[src, x]:
                canvas[TRUNK_TOP + y, x] = ramp(int(tree_px[src, x]), FLESH)
    # The person, waist up, in the same flesh and bark; dark pixels stay
    # dark, so the face keeps its eyes.
    for y in range(4, WAIST):
        for x in range(32):
            v = int(person[y, x])
            if v:
                canvas[HEAD_ROW + y - 4, x] = (DARK if light(v) < 70
                                               else ramp(v, FLESH))
    # The open mouth, under the eyes.
    mouth = HEAD_ROW + 11
    for y in range(mouth, mouth + (3 if breath else 2)):
        canvas[y, 15] = THROAT
        canvas[y, 16] = THROAT
    if breath:
        canvas[1:TRUNK_TOP + 1] = canvas[0:TRUNK_TOP].copy()
        canvas[0] = 0
    return canvas


people = [np.asarray(Image.open(SPR / f"spr_{n:03d}.png"))[0:32] for n in PEOPLE]
frames = [figure(p, False) for p in people] + [figure(p, True) for p in people]
sheet = Image.fromarray(np.vstack(frames), "P")
sheet.putpalette(pal)
sheet.save(SPR / "spr_508.png", optimize=False)
(SPR / "spr_508.tsv").write_text(
    "anim\tframe 0 4, hold\n"
    "anim\tframe 0 46, frame 3 34, loop\n"
    "anim\tframe 0 10, loop\n"
    "anim\tframe 0 26, play 1\n"
    "anim\tframe 0 6, play 1\n")
print("Built spr_508.png: three of Kolima's people, half trees, breathing")
