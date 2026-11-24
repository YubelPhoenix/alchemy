#!/usr/bin/env python3
"""Remix the 28 Djinn: what each one unleashes, and what it gives while set.

A Djinni's name is its ability's name, so the ids stay put. Within each
element's seven (ids 300-306, 320-326, 340-346, 360-366) the ability bodies
(target, formula, effect, range, power; never the element) and their one-line
descriptions are dealt round to a different Djinni, no one keeping its own, and
the stat bonuses in gDjinn_DefinitionTable (rows 0-6, 20-26, 40-46, 60-66) are
dealt the same way.

Run once; the results are committed in abilities.c, djinn_table.c and
tools/dark_story/phase78_djinn_remix.tsv (the new descriptions).
"""
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ABIL = ROOT / "games/tbs/src/game/abilities.c"
TABLE = ROOT / "games/tbs/src/game/djinn_table.c"
PO = ROOT / "games/tbs/text/en.po"
TSV = ROOT / "tools/dark_story/phase78_djinn_remix.tsv"
SEED = 7
DESC_BASE = 1338
FIRSTS = (300, 320, 340, 360)


def derange(n, rng):
    while True:
        p = list(range(n))
        rng.shuffle(p)
        if all(i != v for i, v in enumerate(p)):
            return p


rng = random.Random(SEED)

# --- abilities.c
text = ABIL.read_text()
start = text.index("gAbilityDefinitions[]")
head, body = text[:start], text[start:]
pat = re.compile(r"(\n    // [^\n]*\n    \{\n)(.*?)(\n    \},)", re.S)
matches = list(pat.finditer(body))
assert len(matches) == 519, len(matches)


def split(block):
    lines = block.split("\n")
    elem = [l for l in lines if l.strip().startswith(".element")]
    rest = [l for l in lines if not l.strip().startswith(".element")]
    return elem, rest


bodies = {}
for first in FIRSTS:
    for i in range(first, first + 7):
        bodies[i] = split(matches[i].group(2))
perm = {}
for first in FIRSTS:
    p = derange(7, rng)
    for k in range(7):
        perm[first + k] = first + p[k]   # slot first+k receives body of perm
new_blocks = {}
for slot, src in perm.items():
    elem, _ = bodies[slot]
    _, rest = bodies[src]
    # keep the slot's element line where the source's would sit: after targetMode/flags
    out = []
    placed = False
    for l in rest:
        out.append(l)
        if not placed and l.strip().startswith(".flags"):
            out.extend(elem)
            placed = True
    assert placed
    new_blocks[slot] = "\n".join(out)

pieces, last = [], 0
for i, m in enumerate(matches):
    if i in new_blocks:
        pieces.append(body[last:m.start(2)])
        pieces.append(new_blocks[i])
        last = m.end(2)
pieces.append(body[last:])
ABIL.write_text(head + "".join(pieces))

# --- descriptions
po = PO.read_text()
ents = {i: (c, s) for c, i, s in re.findall(
    r'msgctxt "([^"]*)"\nmsgid "(\d+)"\nmsgstr "((?:[^"\\]|\\.)*)"', po)}
rows = ["# Djinn remix: each Djinni's description follows the effect it was dealt."]
for slot, src in sorted(perm.items()):
    key = "%05d" % (DESC_BASE + slot)
    ctx = ents[key][0]
    rows.append(f"{key}\t{ctx}\t{ents['%05d' % (DESC_BASE + src)][1]}")
TSV.write_text("\n".join(rows) + "\n")

# --- djinn_table.c
tt = TABLE.read_text()
tpat = re.compile(r"(    // [^\n]*\n    \{\n        \.abilityId = [^\n]*\n)(.*?)(    \},)", re.S)
tm = list(tpat.finditer(tt))
assert len(tm) == 80, len(tm)
stats = [m.group(2) for m in tm]
newstats = list(stats)
for e in range(4):
    p = derange(7, rng)
    for k in range(7):
        newstats[e * 20 + k] = stats[e * 20 + p[k]]
pieces, last = [], 0
for m, s in zip(tm, newstats):
    pieces.append(tt[last:m.start(2)])
    pieces.append(s)
    last = m.end(2)
pieces.append(tt[last:])
TABLE.write_text("".join(pieces))
print("remixed", len(perm), "Djinn abilities and 28 stat sets")
