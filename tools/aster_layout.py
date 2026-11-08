#!/usr/bin/env python3
"""Generate Aster's 64x64 exterior using ONLY Golden Sun: The Broken Seal art.

All visible ground, paths and copied roofs/walls use the vanilla Vault
(Map019) metatile table with Vault's matching palette and tileset.
External-game spritesheets and images are not inputs to this build.

Map019 stores ground at (0,0), middle at (60,0), high at (0,60)
in a 128x128 source grid. Aster uses three 64x64 layer windows.
"""
import argparse
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "games/tbs/src/map/map_180/map.txt"
VAULT = ROOT / "games/tbs/src/map/map_019/map.txt"
SIDE = 64

# name, x, y, vault x, vault y, width, height, display character
# A repeated facade is deliberately unsettling once Isaac notices it.
BUILDINGS = (
    ("sealed_house", 3, 3, 29, 3, 11, 16, "X"),
    ("inn", 43, 3, 1, 3, 19, 16, "I"),
    ("western_home", 3, 24, 29, 3, 11, 16, "H"),
    ("eastern_home", 50, 24, 29, 3, 11, 16, "H"),
    ("shop", 3, 44, 29, 3, 11, 16, "S"),
    ("duplicate_home", 50, 44, 29, 3, 11, 16, "V"),
)
# name, x, y, map behavior. Door/landmark events currently give messages
# rather than transporting Isaac into unbuilt interiors.
INTERACTIONS = (
    ("memorial", 32, 14, "14:e2"),
    ("well", 32, 35, "14:e1"),
    ("sealed_house", 8, 19, "56:e3"),
    ("inn", 53, 19, "56:e4"),
    ("western_home", 8, 40, "56:e5"),
    ("eastern_home", 55, 40, "56:e6"),
    ("shop", 8, 60, "56:e7"),
    ("duplicate_home", 55, 60, "56:e8"),
)
ACTORS = (
    (26, 33), (49, 21), (23, 34), (35, 39),
    (45, 34), (36, 13), (41, 34),
)
WELL = (32, 34)
MEMORIAL = (32, 13)
EXIT = (32, 63)
START = (32, 61)

def load_vault():
    lines = VAULT.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("grid:128x128"), "Vault grid changed"
    result = [["0" for _ in range(128)] for _ in range(128)]
    for y, line in enumerate(lines[1:]):
        assert y < 128
        for x, token in enumerate(line.split()):
            assert x < 128
            result[y][x] = token
    # Golden Sun's editable map format uses 0xFFF for the *first*
    # appearance of each metatile. At load time these are assigned
    # sequential table indices in global grid scan order. Resolve them
    # here BEFORE relocating geometry; copying unresolved placeholders
    # would assign the wrong wall/roof graphics in the new layout.
    next_id = 0
    for y in range(128):
        for x in range(128):
            parts = result[y][x].split(":")
            packed = int(parts[0], 16)
            if (packed & 0xfff) == 0xfff:
                parts[0] = format((packed & 0xf000) | next_id, "x")
                result[y][x] = ":".join(parts)
                next_id += 1
    expected = len((ROOT / "games/tbs/src/map/map_019/metatiles.tsv")
                   .read_text(encoding="utf-8").splitlines()) - 1
    assert next_id == expected, (
        f"Vault metatile enumeration mismatch: {next_id} vs {expected}")
    return result

def blueprint():
    cells = [["." for _ in range(SIDE)] for _ in range(SIDE)]
    for y in range(SIDE):
        cells[y][0] = "#"
        cells[y][-1] = "#"
    cells[0] = ["#"] * SIDE
    cells[-1] = ["#"] * SIDE
    # Original Vault's open background uses metatile 0 (grassy base).
    # Its door approaches include metatile 0x56. Reserve that metatile for
    # paths; using it as the entire town's floor made Aster uniformly paved.
    # Slightly offset north and south sections to avoid a rigid road grid.
    for y in range(1, SIDE-1):
        center = 32 if y < 21 else 33 if y < 42 else 31
        for x in range(center-2, center+2):
            cells[y][x] = "="
    for y0, y1 in ((19, 21), (40, 42), (60, 62)):
        for y in range(y0, y1+1):
            # Streets connect all six building entrances while leaving
            # generous grass around the homes, as in Golden Sun villages.
            for x in range(2, 62):
                cells[y][x] = "="
    for y in range(29, 39):
        for x in range(28, 38):
            cells[y][x] = "="
    for _, x0, y0, _, _, w, h, marker in BUILDINGS:
        for y in range(y0, y0+h):
            for x in range(x0, x0+w):
                assert cells[y][x] not in ("#", "="), "Facade overlaps road"
                cells[y][x] = marker
    cells[MEMORIAL[1]][MEMORIAL[0]] = "M"
    cells[WELL[1]][WELL[0]] = "W"
    cells[EXIT[1]][EXIT[0]] = "G"
    return tuple("".join(row) for row in cells)

LAYOUT = blueprint()
def validate_layout():
    assert len(LAYOUT) == SIDE and all(len(r) == SIDE for r in LAYOUT)
    assert LAYOUT[EXIT[1]][EXIT[0]] == "G"
    assert sum(row.count("G") for row in LAYOUT) == 1
    assert all(LAYOUT[63][x] == "#" for x in range(SIDE) if x != 32)
    for _, x, y, _ in INTERACTIONS:
        assert LAYOUT[y][x] in ".=", f"Interaction inaccessible at {x},{y}"
    walkable = set()
    q = deque([START])
    while q:
        x, y = q.popleft()
        if not (0 <= x < SIDE and 0 <= y < SIDE):
            continue
        if (x, y) in walkable or LAYOUT[y][x] not in ".=G":
            continue
        walkable.add((x, y))
        for pos in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):
            q.append(pos)
    required = [EXIT, START] + list(ACTORS) + [(x,y) for _,x,y,_ in INTERACTIONS]
    assert all(pos in walkable for pos in required), "Aster route/actor unreachable"

def source():
    validate_layout()
    original = load_vault()
    # Square 128x128 game grid, partitioned into 64x64 windows.
    out = [["0" for _ in range(128)] for _ in range(128)]
    for y in range(SIDE):
        for x in range(SIDE):
            kind = LAYOUT[y][x]
            if kind == "#":
                out[y][x] = "0:ff"
            elif kind == "=":
                out[y][x] = "56"  # native Vault walkable street placeholder
            elif kind == "G":
                out[y][x] = "56:1"
            elif kind in "WM":
                out[y][x] = "3e:ff"
            else:
                out[y][x] = "0"  # original Vault's common grassy background
    # Transfer each building's actual source facade on all three layers.
    for _, dx, dy, sx, sy, width, height, _ in BUILDINGS:
        for yy in range(height):
            for xx in range(width):
                # Upper map layers: original Map019 layer windows begin
                # at x=60 and y=60, respectively.
                native = original[sy+yy][sx+xx]
                tile = native.split(":")[0]
                out[dy+yy][dx+xx] = tile + ":ff"  # solid until interiors exist
                out[dy+yy][dx+xx+64] = original[sy+yy][sx+xx+60]
                out[dy+yy+64][dx+xx] = original[sy+yy+60][sx+xx]
    for _, x, y, event in INTERACTIONS:
        out[y][x] = event
    return ("grid:128x128\tat:0,0\tfill:0\n"
            + "\n".join(" ".join(row) for row in out) + "\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    generated = source()
    if args.check:
        assert DEST.read_text(encoding="utf-8") == generated, "Generated Aster grid drift"
        print("PASS Aster 64x64 facade map, three layers, actors and step events")
    else:
        DEST.parent.mkdir(parents=True, exist_ok=True)
        DEST.write_text(generated, encoding="utf-8")
        print("Wrote", DEST)
if __name__ == "__main__":
    main()
