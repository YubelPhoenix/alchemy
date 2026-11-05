#!/usr/bin/env python3
"""Give every mixed-element class line its own Psynergy kit.

Before, nearly every mixed line taught the same support set (Cutting Edge,
Thorn, Ply, Wish, Revive, Break...). Each line below now has its own families,
unlocked stage by stage as its class tiers go up (class k of a line has stages
0..k+1, so even a line's first class has two stages), capped at the 16 slots a class has. Levels are each ability's usual
level in the old table. The four pure-element lines and the heroes' own
signature moves (levels.c) are left alone.

Run once; the result is committed in games/tbs/src/game/classes.c.
"""
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "games/tbs/src/game/classes.c"

F = dict(
    QUAKE=[3, 4, 5], SPIRE=[6, 7, 8], GAIA=[9, 10, 11], GROWTH=[12, 13, 14],
    THORN=[15, 16, 17], IMPACT=[102, 103], PLANET=[196],
    FROST=[24, 25, 26], ICE=[27, 28, 29], PRISM=[30, 31, 32], DOUSE=[33, 34, 35],
    FROTH=[36, 37, 38],
    FLARE=[45, 46, 47], FIRE=[48, 49, 50], VOLCANO=[51, 52, 53], BLAST=[54, 55, 56],
    NOVA=[57, 58, 59], HEATWAVE=[194],
    BOLT=[66, 67, 68], RAY=[69, 70, 71], PLASMA=[72, 73, 74], SLASH=[75, 76, 77],
    WHIRL=[78, 79, 80],
    CURE=[90, 91, 92], PLY=[93, 94, 95], WISH=[96, 97, 98], CUREPOISON=[99],
    RESTORE=[100], REVIVE=[101], GUARD=[106, 107], WARD=[110, 111],
    IMPAIR=[108, 109], WEAKEN=[112, 113], SHELL=[174, 175], GUARDIAN=[172, 173],
    DULL=[104, 105], AVOID=[150],
    HAUNT=[122, 123, 124], DRAIN=[125, 126], SLEEP=[120], BIND=[121], DELUDE=[116],
    BREAK=[127], DEATHPLUNGE=[176], DEMONSPEAR=[170], ANGELSPEAR=[171],
    ANNIHIL=[178], ASTRAL=[195], CUTTING=[193], HELM=[162], QUICK=[163],
)

# first class id of the line -> stages (each a list of family names)
LINES = {
    40: [["THORN", "DOUSE"], ["GUARD", "CUREPOISON"], ["CURE"], ["REVIVE", "BREAK"], ["CUTTING"]],
    50: [["BLAST", "FROTH"], ["WARD", "CUREPOISON"], ["PLY"], ["RESTORE", "ASTRAL"], ["HEATWAVE"]],
    60: [["SPIRE", "FLARE"], ["FROST", "RESTORE"], ["WISH", "HELM"]],
    70: [["GAIA", "SLASH"], ["SLEEP", "WEAKEN"], ["HAUNT"], ["DRAIN"], ["AVOID", "ASTRAL"]],
    80: [["FIRE", "RAY"], ["DELUDE", "BIND"], ["IMPAIR"], ["DRAIN"], ["HEATWAVE", "DEATHPLUNGE"]],
    90: [["QUAKE", "SLASH"], ["HAUNT", "DEATHPLUNGE"], ["ANNIHIL", "QUICK"]],
    100: [["FROST", "GROWTH"], ["CURE", "CUREPOISON"], ["WARD", "RESTORE"], ["PLY"], ["WISH", "REVIVE"]],
    110: [["WHIRL", "THORN"], ["SLEEP", "GUARD"], ["WEAKEN"], ["CURE", "REVIVE"], ["DRAIN"]],
    120: [["GROWTH", "BOLT"], ["DELUDE", "SLEEP"], ["HAUNT", "DRAIN"]],
    130: [["ICE", "FLARE"], ["CURE", "GUARD"], ["IMPAIR", "CUREPOISON"], ["PRISM"], ["WISH", "REVIVE"]],
    140: [["PLASMA", "FIRE"], ["BIND", "SHELL"], ["CURE", "AVOID"], ["HEATWAVE"], ["DRAIN", "RESTORE"]],
    150: [["DOUSE", "BOLT"], ["SLEEP", "BIND"], ["HAUNT", "AVOID"]],
    160: [["IMPACT", "BLAST"], ["HELM", "GUARDIAN"], ["VOLCANO"], ["DEMONSPEAR", "DULL"], ["NOVA", "PLANET"], ["ANNIHIL", "DEATHPLUNGE"]],
    170: [["CUTTING", "QUICK", "SLASH", "BLAST"], ["DEMONSPEAR", "ANGELSPEAR", "ANNIHIL", "HAUNT"]],
    180: [["DOUSE", "SLASH"], ["CURE", "SLEEP"], ["ICE", "WARD"], ["PLASMA", "RESTORE"], ["WISH", "SHELL"], ["PRISM", "ASTRAL"]],
    190: [["CURE", "CUREPOISON", "GROWTH"], ["PLY", "REVIVE", "RESTORE", "WARD", "ASTRAL"]],
}

text = PATH.read_text()
head, body = text.split("gClass_DefinitionTable[] = {", 1)
parts = re.split(r"(\n    // )", body)
# parts: [pre, sep, row, sep, row, ...]
rows = [parts[i] for i in range(2, len(parts), 2)]

level_votes = {}
for row in rows:
    for a, l in re.findall(r"\.ability = (\d+), \.level = (\d+)", row):
        level_votes.setdefault(int(a), Counter())[int(l)] += 1
level = {a: c.most_common(1)[0][0] for a, c in level_votes.items()}

NEWNAMES = {}
for line in re.finditer(r'(\d{5})\tmessage\t(.+)',
                        (ROOT / "tools/dark_story/phase79_mixed_class_names.tsv").read_text()):
    NEWNAMES[int(line.group(1)) - 1857] = line.group(2)

kits = {}
for first, stages in LINES.items():
    k = first
    while k - first < len(stages) + (1 if first in (160, 180) else 0) and (
            k in NEWNAMES) and (k == first or k - first < 6):
        n = min(k - first + 1, len(stages) - 1)
        entries = []
        for stage in stages[: n + 1]:
            for fam in stage:
                for a in F[fam]:
                    entries.append((a, level[a]))
        kits[k] = entries[:16]
        k += 1

changed = 0
for cid in range(len(rows)):
    if cid not in kits:
        continue
    row = rows[cid]
    lines = ["        .abilities = {"]
    for a, lv in kits[cid]:
        lines.append(f"            {{.ability = {a}, .level = {lv}}},")
    lines.append("        },")
    new_block = "\n".join(lines)
    row2, n = re.subn(r"        \.abilities = \{.*?\n        \},", new_block, row, count=1, flags=re.S)
    assert n == 1, cid
    nm = NEWNAMES[cid]
    row2 = re.sub(r"^[^\n]*", nm, row2, count=1)
    rows[cid] = row2
    changed += 1

out = [parts[0]]
for i, r in enumerate(rows):
    out.append(parts[1 + 2 * i])
    out.append(r)
PATH.write_text(head + "gClass_DefinitionTable[] = {" + "".join(out))
print(changed, "classes rewritten")
