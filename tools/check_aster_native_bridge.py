#!/usr/bin/env python3
"""Read-only native west river bridge audit for Aster V14.

Verifies the exact original Vale source metatiles and rail tiles were stamped
over the existing 18 passable crossing cells without introducing invisible
collision, changing NPC/events, or opening a new map exit.
This does not certify the art's rendered appearance or physical collision.
"""
from pathlib import Path
import json
import hashlib

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "games/tbs/src/map/map_180/map.txt"
VALE = ROOT / "games/tbs/src/map/map_003/map.txt"
META = ROOT / "games/tbs/src/map/map_003/metatiles.tsv"
MANIFEST = ROOT / "tools/aster_native_boundary_manifest.json"
SNAPSHOT = ROOT / "tools/aster_v14_native_snapshot.json"

def require(ok, reason):
    if not ok:
        raise AssertionError(reason)

def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def source_grid(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    require(lines and lines[0].startswith("grid:128x128"), f"{path}: invalid map")
    info = dict(item.split(":", 1) for item in lines[0].split("\t")[1:])
    x0, y0 = map(int, info.get("at", "0,0").split(","))
    fill = info.get("fill", "0").split(":")[0]
    data = [[fill for _ in range(128)] for _ in range(128)]
    for y, line in enumerate(lines[1:]):
        for x, tile in enumerate(line.split()):
            require(x0+x < 128 and y0+y < 128, "Map source exceeds grid")
            data[y0+y][x0+x] = tile
    return data

def original_vale():
    grid = source_grid(VALE)
    resolved = 0
    for y in range(128):
        for x in range(128):
            parts = grid[y][x].split(":")
            value = int(parts[0], 16)
            if value & 0xfff == 0xfff:
                parts[0] = f"{(value & 0xf000) | resolved:x}"
                grid[y][x] = ":".join(parts)
                resolved += 1
    require(resolved == len(META.read_text().splitlines())-1 == 1331,
            "Vale metatile resolution or original source changed")
    return grid

def verify():
    text = MAP.read_bytes()
    grid = source_grid(MAP)
    original = original_vale()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    snap = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    bridge = manifest["new_native_west_river_bridge"]
    require(manifest["new_map_blob"] == snap["source_git_blob_sha"] ==
            git_blob(text), "Bridge provenance map SHA mismatches native snapshot")
    require(bridge["source_top_left"] == [9,38] and
            bridge["destination_top_left"] == [3,35] and
            (bridge["width"], bridge["height"]) == (9,2),
            "Bridge source/destination footprint changed")
    pre = bridge["previous_ground_and_upper_layers"]
    by_pos = {(tile["x"],tile["y"]):tile for tile in pre}
    require(len(pre) == len(by_pos) == 18, "Missing or duplicate crossing cells")
    base = set()
    for dy in range(2):
        for dx in range(9):
            x,y=3+dx,35+dy
            sx,sy=9+dx,38+dy
            base.add((x,y))
            old = by_pos[(x,y)]
            require(all(old[k] == "15" for k in ("middle","top")),
                    f"Bridge replaced existing overhead art at {(x,y)}")
            require(":" not in old["ground"],
                    f"Bridge baseline collision/marker was not passable at {(x,y)}")
            src = original[sy][sx]
            require(":" in src and not src.endswith(":ff"),
                    f"Original Vale source deck is not walkable at {(sx,sy)}")
            ground=src.split(":")[0]
            upper=original[sy][sx+60]
            expected_middle=upper if upper!="2b" else "15"
            require(grid[y][x] == ground,
                    f"Wrong native Vale deck tile at {(x,y)}")
            require(grid[y][x+64] == expected_middle,
                    f"Wrong native Vale upper/deck tile at {(x,y)}")
            require(grid[y+64][x] == old["top"],
                    f"Bridge changed Aster top-layer art at {(x,y)}")
            require(not grid[y][x].endswith(":ff") and ":" not in grid[y][x],
                    f"West bridge became blocked or acquired event at {(x,y)}")
    require(set(by_pos) == base, "Bridge provenance includes unreviewed cells")
    event_tokens = {"e1","e2","e3","e4","e5","e6","e7","e8","1"}
    found = {}
    for y in range(64):
        for x in range(64):
            parts = grid[y][x].split(":")
            if len(parts)==2 and parts[1] in event_tokens:
                require(parts[1] not in found, "Duplicate story marker")
                found[parts[1]] = (x,y)
    require(found == {"e1":(32,36), "e2":(29,20), "e3":(18,22),
                      "e4":(16,35), "e5":(17,47), "e6":(41,48),
                      "e7":(48,35), "e8":(45,22), "1":(32,62)},
            "Bridge pass altered Aster event markers")
    require(grid[63][32].split(":")[1] != "ff", "South exit blocked")
    print("PASS native Vale 9x2 bridge deck + overhead tiles at Aster west crossing")
    print("PASS all 18 original crossing cells still walkable and marker-free")
    print("PASS nine original event markers; no added west world-map exit")
    print("SOURCE ONLY: original Vale bridge appearance and collision need emulator QA")

if __name__ == "__main__":
    verify()
