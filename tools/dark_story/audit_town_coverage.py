#!/usr/bin/env python3
"""Report untouched Golden Sun / Ashfall dialogue by region.

Use from repository root:
    python3 tools/dark_story/audit_town_coverage.py

This is a COVERAGE report, not an editorial-quality or story-completeness score.
Sequential "message" contexts are tracked through approximate event ID ranges.
A rewrite may still be a shallow paraphrase or fail to add Ashfall story beats.
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
import re

PO = Path("games/tbs/text/en.po")
REWRITES = Path("tools/dark_story")
ENTRY = re.compile(r'(?m)^msgctxt "([^"]+)"\nmsgid "(\d{5})"$')
MSGSTR = re.compile(r'(?m)^msgstr (.*)$')
LINE = re.compile(r'^"((?:\\.|[^"\\])*)"$')

# These are ORIGINAL catalogue ranges; some span transit scenes or revisit events.
# The prefix audit below is exact for named contexts; these ranges intentionally
# include unnamed, sequential story lines that a prefix-only audit would miss.
ZONES = {
    "Bilibin (early)": ((5038, 5234),),
    "Kolima / Tret": ((5235, 5416),),
    "Imil / Mercury": ((5417, 5749),),
    "Bilibin / Kolima revisit": ((5750, 6028),),
    "Fuchin / Xian": ((6029, 6332), (6660, 6768)),
    "Altin / Alpine Crossing": ((6333, 6659),),
    "Kalay (early)": ((6769, 7067),),
    "Lunpa (village before rescue)": ((7068, 7138),),
    "Kalay / Tolbi approach": ((7400, 7499),),
    "Tolbi / Colosso / Babi": ((7500, 9219),),
    "Lunpa (fortress and escape)": ((9220, 9581),),
    "Suhalla / Iodem": ((9655, 9875),),
    "Lalivero / finale": ((9876, 10499),),
}


def entries(source: str) -> dict[str, tuple[str, str]]:
    out = {}
    pieces = re.split(r"\n\s*\n", source)
    for piece in pieces:
        match = ENTRY.search(piece)
        if not match:
            continue
        ctxt, msgid = match.groups()
        body = MSGSTR.search(piece)
        if not body:
            continue
        pos = body.start()
        fragments = []
        for line in piece[pos:].splitlines():
            item = LINE.fullmatch(line.removeprefix("msgstr "))
            if not item:
                break
            fragments.append(item.group(1))
        out[msgid] = (ctxt, "".join(fragments))
    return out


def load_rows() -> tuple[dict[str, str], dict[str, str]]:
    rows, locations = {}, {}
    for path in sorted(REWRITES.glob("*.tsv")):
        for i, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not raw or raw.startswith("#"):
                continue
            parts = raw.split("\t", 2)
            if len(parts) != 3:
                raise SystemExit(f"Invalid TSV: {path}:{i}")
            key, _, replacement = parts
            if key in rows:
                raise SystemExit(f"Duplicate {key}: {locations[key]} and {path}:{i}")
            rows[key] = replacement
            locations[key] = f"{path}:{i}"
    return rows, locations


def summary(title: str, ids: list[str], original, rewritten, limit=8):
    valid = [id for id in ids if id in original]
    touched = [id for id in valid if id in rewritten]
    untouched = [id for id in valid if id not in rewritten]
    unchanged = [id for id in touched if rewritten[id] == original[id][1]]
    pct = len(touched) / len(valid) * 100 if valid else 0
    print(
        f"{title:34}  covered {len(touched):4}/{len(valid):4} "
        f"({pct:5.1f}%)   untouched {len(untouched):4}   verbatim {len(unchanged):3}"
    )
    if untouched:
        examples = [
            f"{key} {original[key][0]}"
            for key in untouched if original[key][0] != "message"
        ][:limit]
        if examples:
            print("    Named gaps: " + " | ".join(examples))


def main():
    original = entries(PO.read_text(encoding="utf-8"))
    rewritten, locations = load_rows()
    print("ASHFALL ORIGINAL-DIALOGUE COVERAGE (not a story quality rating)")
    print(f"Catalogue: {len(original)} entries | rewrite rows: {len(rewritten)}")
    print("\nApproximate original event sequence bands:")
    for zone, bands in ZONES.items():
        ids = [
            key for key in original if any(lo <= int(key) <= hi for lo, hi in bands)
        ]
        summary(zone, ids, original, rewritten, limit=3)
    print("\nExact named context prefixes (unnamed sequential messages not included):")
    prefixes = [
        "Vale", "Vault", "Bilibin", "Kolima", "Imil", "Fuchin",
        "Xian", "Altin", "Kalay", "Tolbi", "Lunpa", "Suhalla", "Lalivero",
    ]
    for prefix in prefixes:
        ids = [
            key for key, (ctx, _) in original.items()
            if ctx.startswith("Msg" + prefix)
        ]
        summary(prefix, ids, original, rewritten, limit=3)
    print(
        "\nCaution: Coverage does not establish that each line was meaningfully "
        "rewritten or that Ashfall-specific scenes exist. "
        "Story review must also inspect scene scripts, choices, and progression."
    )


if __name__ == "__main__":
    main()
