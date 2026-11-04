#!/usr/bin/env python3
"""Reshuffle which enemy groups appear in which random-encounter zone.

Only zones with a nonzero rate change (scripted, mimic, Djinn and event zones
are left alone). Each formation keeps a home level (the mean level of the
zones it appears in today) and may only be moved into a zone whose level is
within BAND of it, so difficulty stays about where it was. Every slot keeps
its weight; only the formation in it changes. Deterministic (SEED).

Run once; the result is committed in games/tbs/src/overworld/encounter_zones.c.
"""
import random
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "games/tbs/src/overworld/encounter_zones.c"
SEED = 2026
BAND = 3

text = PATH.read_text()
start = text.index("gEncounterZones[]")
head, body = text[:start], text[start:]

zone_re = re.compile(
    r"\{\s*\.rate = (\d+),\s*\.level = (\d+),\s*\.enemies = \{([^}]*)\},"
    r"\s*\.weights = \{([^}]*)\},\s*\}")
zones = []
for m in zone_re.finditer(body):
    zones.append({
        "span": m.span(),
        "rate": int(m.group(1)),
        "level": int(m.group(2)),
        "en": [int(x) for x in m.group(3).split(",") if x.strip()],
    })

random_zones = [z for z in zones if z["rate"] > 0]
seen = defaultdict(list)
for z in random_zones:
    for f in z["en"]:
        seen[f].append(z["level"])
home = {f: sum(v) / len(v) for f, v in seen.items()}
pool = sorted(home)

rng = random.Random(SEED)
changed = 0
for z in random_zones:
    near = [f for f in pool if abs(home[f] - z["level"]) <= BAND]
    if len(near) < len(z["en"]):
        near = sorted(pool, key=lambda f: abs(home[f] - z["level"]))[
            :max(len(z["en"]) * 2, 8)]
    picks = rng.sample(near, len(z["en"]))
    changed += sum(a != b for a, b in zip(picks, z["en"]))
    z["new"] = picks

out = []
last = 0
for z in zones:
    if "new" not in z:
        continue
    a, b = z["span"]
    chunk = body[a:b]
    chunk = re.sub(r"(\.enemies = \{)[^}]*(\})",
                   lambda m: m.group(1) + ", ".join(map(str, z["new"])) + m.group(2),
                   chunk, count=1)
    out.append(body[last:a])
    out.append(chunk)
    last = b
out.append(body[last:])
PATH.write_text(head + "".join(out))
print(f"{len(random_zones)} zones remixed, {changed} slots changed, "
      f"{len(pool)} formations in the pool")
