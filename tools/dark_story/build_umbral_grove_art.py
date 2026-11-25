#!/usr/bin/env python3
"""Build the Umbral Rift's grove figure (SPR_508) from Kolima's cursed tree
(SPR_105).

Kolima's people were turned into trees. In the Rift the curse went the other
way: the tree is skin. The trunk keeps its shape and roots but is drawn in
the party's skin tones; its crown is dead and grey; and a face is pressed
into the bark: two hollow eyes, the left one sagging over a stain, above a
long mouth hanging open.

Frames 0-2 are the tree's own three facings; frames 3-5 are the same with
the mouth drawn a pixel longer and the crown sunk a pixel, and the idle
animation swaps the two slowly, so in a still room every tree breathes.
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SPR = ROOT / "games/tbs/src/graphics/sprite"

# Shared sprite palette entries.
SKIN = {  # trunk yellows/greens -> skin, by brightness
    108: 138, 102: 138, 101: 131, 66: 131, 65: 95, 59: 95, 58: 88,
    95: 88, 94: 88, 52: 52, 125: 45, 11: 52, 211: 45, 144: 138, 216: 45,
}
DEAD = [13, 218, 219, 220, 222]  # crown greens -> greys, dark to light
HOLE, THROAT = 122, 18           # eye and mouth black ((56,112,176) is not
HOLE = 13                        # black; use the dark grey), mouth dark red
TRUNK_TOP = 16                   # rows from here down are trunk and roots

base = Image.open(SPR / "spr_105.png")
pal = base.getpalette()
src = np.asarray(base)
assert src.shape == (96, 32), src.shape


def light(i):
    r, g, b = pal[3 * i:3 * i + 3]
    return 0.3 * r + 0.59 * g + 0.11 * b


def recolour(frame):
    out = frame.copy()
    for y in range(32):
        for x in range(32):
            v = int(frame[y, x])
            if v == 0:
                continue
            if y >= TRUNK_TOP or v in (11, 125, 211, 216):
                out[y, x] = SKIN.get(v, 88 if light(v) < 150 else 131)
            else:  # the crown: dead greys by brightness
                out[y, x] = DEAD[min(4, int(light(v) / 52))]
    return out


def face(frame, breath):
    """Two hollow eyes, uneven, the left one sagging, a stain running from
    it, and a long mouth hanging open toward the roots."""
    out = frame.copy()
    for y, x in ((17, 12), (17, 13), (18, 12), (18, 13), (19, 13),  # left
                 (17, 17), (17, 18), (18, 17), (18, 18)):           # right
        out[y, x] = HOLE
    for y in (20, 21, 22):                                          # stain
        out[y, 12] = 45
    end = 27 if breath else 26
    for y in range(21, end):
        out[y, 15] = THROAT
        out[y, 14] = HOLE
        out[y, 16] = HOLE if y < end - 1 else THROAT
    out[20, 15] = HOLE
    out[end, 15] = HOLE
    return out


def sink(frame):
    out = frame.copy()
    out[1:TRUNK_TOP] = frame[0:TRUNK_TOP - 1]
    out[0] = 0
    return out


frames = []
for f in range(3):
    tree = recolour(src[f * 32:(f + 1) * 32])
    frames.append(face(tree, False) if f == 0 else tree)
for f in range(3):
    tree = sink(recolour(src[f * 32:(f + 1) * 32]))
    frames.append(face(tree, True) if f == 0 else tree)
sheet = Image.fromarray(np.vstack(frames), "P")
sheet.putpalette(pal)
sheet.save(SPR / "spr_508.png", optimize=False)
(SPR / "spr_508.tsv").write_text(
    "anim\tframe 0 4, hold\n"
    "anim\tframe 0 46, frame 3 34, loop\n"
    "anim\tframe 0 10, loop\n"
    "anim\tframe 0 26, play 1\n"
    "anim\tframe 0 6, play 1\n")
print("Built spr_508.png: 6 frames")
