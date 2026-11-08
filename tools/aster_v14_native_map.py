#!/usr/bin/env python3
"""Reproduce/check the isolated Aster V14 native map snapshot.

Unlike the obsolete tools/aster_layout.py, this script reconstructs exactly
the V14 packed 128x128 map from a compact, reviewable source snapshot.
It never fetches content, builds a ROM, or triggers CI.

  python3 tools/aster_v14_native_map.py --check
  python3 tools/aster_v14_native_map.py --write  # only for missing/identical map

This snapshot is a reproducibility checkpoint, NOT a parametrized map editor.
"""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "tools/aster_v14_native_snapshot.json"
DEST = ROOT / "games/tbs/src/map/map_180/map.txt"

def git_blob_sha(content: bytes) -> str:
    prefix = b"blob " + str(len(content)).encode("ascii") + b"\x00"
    return hashlib.sha1(prefix + content).hexdigest()

def render_snapshot():
    record = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    if record.get("format") != "aster-v14-native-packed-grid-rle-v1":
        raise ValueError("Unknown native snapshot format")
    if record.get("dimensions") != [128, 128]:
        raise ValueError("Unexpected packed native map dimensions")
    if record.get("map_file") != "games/tbs/src/map/map_180/map.txt":
        raise ValueError("Unexpected snapshot destination")
    dictionary = record["dictionary"]
    if not dictionary or len(dictionary) != len(set(dictionary)):
        raise ValueError("Empty or duplicate metatile dictionary")
    cells = []
    for pair in record["runs"].split(","):
        a, sep, b = pair.partition(".")
        if not sep or not a or not b:
            raise ValueError("Malformed metatile run")
        index, length = int(a, 36), int(b, 36)
        if not 0 <= index < len(dictionary) or not 1 <= length <= 16384:
            raise ValueError("Invalid metatile run")
        cells.extend([dictionary[index]] * length)
        if len(cells) > 16384:
            raise ValueError("Packed native map overrun")
    if len(cells) != 16384:
        raise ValueError("Expected exactly 16,384 packed layer tokens")
    header = record["header"]
    if header != "grid:128x128\tat:0,0\tfill:0:0:0":
        raise ValueError("Unexpected native map header")
    for token in cells:
        parts = token.split(":")
        if len(parts) > 2 or not 0 <= int(parts[0], 16) <= 0xffff:
            raise ValueError("Malformed native metatile")
    content = header + "\n" + "\n".join(
        " ".join(cells[y*128:(y+1)*128]) for y in range(128)
    ) + "\n"
    data = content.encode("utf-8")
    if git_blob_sha(data) != record["source_git_blob_sha"]:
        raise ValueError("Snapshot failed Git blob integrity check")
    return content

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--write", action="store_true")
    args = parser.parse_args()
    expected = render_snapshot()
    current = DEST.read_text(encoding="utf-8") if DEST.exists() else None
    if args.check:
        if current != expected:
            raise SystemExit("FAIL staged Map180 differs from reviewed V14 snapshot")
        print("PASS V14 reproducible native Map180; no files modified")
        return
    if current not in (None, expected):
        raise SystemExit("REFUSED: existing Map180 has unsnapshotted edits; never overwrite")
    if current is None:
        DEST.parent.mkdir(parents=True, exist_ok=True)
        DEST.write_text(expected, encoding="utf-8")
        print("Restored missing Map180 from reviewed V14 snapshot")
    else:
        print("Map180 already matches reviewed V14 snapshot; no changes written")

if __name__ == "__main__":
    main()
