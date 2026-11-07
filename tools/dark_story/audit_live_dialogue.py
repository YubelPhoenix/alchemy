#!/usr/bin/env python3
"""Audit SOURCE-REFERENCED Golden Sun dialogue, not just TSV line counts.

Use from the repository root:
    python3 tools/dark_story/audit_live_dialogue.py
    python3 tools/dark_story/audit_live_dialogue.py --json /tmp/live-dialogue.json

Only explicit Msg* symbols in C scene code are proven source references here.
Sequential unnamed "message" entries, computed IDs, conditionally unreachable
branches, and the QUALITY of rewritten prose require separate scene/play audits.
This tool reports candidates; it does not certify a scene or mark it completed.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
import re

CATALOGUE = Path("games/tbs/text/en.po")
REWRITES = Path("tools/dark_story")
SCENES = Path("games/tbs/src/scene")
ENTRY = re.compile(r'^msgctxt "([^"]+)"\nmsgid "(\d{5})"$', re.MULTILINE)
REF = re.compile(r"\bMsg[A-Za-z0-9_]+\b")
BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
LINE_COMMENT = re.compile(r"//[^\n]*")


def read_catalogue() -> dict[str, tuple[str, str]]:
    result = {}
    for entry in re.split(r"\n\s*\n", CATALOGUE.read_text(encoding="utf-8")):
        match = ENTRY.search(entry)
        if not match:
            continue
        ctx, msgid = match.groups()
        fragments = []
        in_str = False
        for line in entry.splitlines():
            if line.startswith("msgstr "):
                in_str = True
                line = line[7:]
            elif not in_str or not line.startswith('"'):
                if in_str:
                    break
                continue
            if line.startswith('"') and line.endswith('"'):
                fragments.append(line[1:-1])
        result[ctx] = (msgid, "".join(fragments))
    return result


def read_replacements() -> dict[str, tuple[str, str, str]]:
    result = {}
    for file in sorted(REWRITES.glob("*.tsv")):
        for number, line in enumerate(file.read_text(encoding="utf-8").splitlines(), 1):
            if not line or line.startswith("#"):
                continue
            cells = line.split("\t")
            if len(cells) != 3:
                raise ValueError(f"{file}:{number}: malformed TSV")
            key, ctx, value = cells
            if key in result:
                raise ValueError(f"{file}:{number}: duplicate replacement {key}")
            result[key] = (ctx, value, str(file))
    return result


def region(file: Path) -> str:
    name = file.stem
    if name.startswith(("vale", "sol_sanctum")):
        return "Vale / Sol Sanctum"
    if name.startswith(("vault", "goma_cave")):
        return "Vault / Goma"
    if name.startswith(("bilibin", "kolima", "tret_tree")):
        return "Bilibin / Kolima"
    if name.startswith(("imil", "mercury_lighthouse")):
        return "Imil / Mercury"
    if name.startswith(("fuchin", "xian", "mogall", "lama")):
        return "Fuchin / Xian / Lama"
    if name.startswith("altin"):
        return "Altin"
    if name.startswith(("kalay", "karagol")):
        return "Kalay / Karagol"
    if name.startswith(("tolbi", "babi", "colosso", "altmiller")):
        return "Tolbi / Colosso / Babi"
    if name.startswith(("lunpa", "west_lunpa")):
        return "Lunpa"
    if name.startswith("suhalla"):
        return "Suhalla"
    if name.startswith(("lalivero", "venus_lighthouse")):
        return "Lalivero / Venus"
    return "Other areas"


def audit():
    catalogue = read_catalogue()
    replacements = read_replacements()
    references = defaultdict(set)
    for source in sorted(SCENES.rglob("*.c")):
        code = source.read_text(encoding="utf-8")
        code = LINE_COMMENT.sub("", BLOCK_COMMENT.sub("", code))
        for name in set(REF.findall(code)):
            if name in catalogue:
                references[name].add(str(source))
    report = defaultdict(list)
    for ctx, files in sorted(references.items()):
        msgid, original = catalogue[ctx]
        replacement = replacements.get(msgid)
        if replacement is None:
            status = "NO_REPLACEMENT"
        elif replacement[0] != ctx:
            status = "CONTEXT_MISMATCH"
        elif replacement[1] == original:
            status = "VERBATIM_REPLACEMENT"
        else:
            status = "HAS_REPLACEMENT_UNVERIFIED"
        for file in sorted(files):
            report[region(Path(file))].append({
                "id": msgid, "context": ctx, "status": status,
                "scene": file, "replacement_file": replacement[2] if replacement else None
            })
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", metavar="FILE", help="Save the complete report")
    args = parser.parse_args()
    report = audit()
    for area, entries in sorted(report.items()):
        unique = {e["id"]: e for e in entries}
        counts = defaultdict(int)
        for entry in unique.values():
            counts[entry["status"]] += 1
        gaps = [e for e in unique.values() if e["status"] != "HAS_REPLACEMENT_UNVERIFIED"]
        print(
            f"{area:26} refs={len(unique):4} "
            f"missing={counts['NO_REPLACEMENT']:3} "
            f"verbatim={counts['VERBATIM_REPLACEMENT']:3} "
            f"context_err={counts['CONTEXT_MISMATCH']:3}"
        )
        for entry in gaps[:10]:
            print(f"    {entry['id']} {entry['context']} ({entry['status']})")
    print(
        "WARNING: explicit source refs only. A patched line may still be "
        "unreachable, shallow, grammatically poor, or wrong for its speaker. "
        "Sequential dialogue and actual ROM build/play testing are separate."
    )
    if args.json:
        output = Path(args.json)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8"
        )


if __name__ == "__main__":
    main()
