#!/usr/bin/env python3
"""Read-only checks for the isolated Aster V14 native map/scene staging branch.

Does NOT compile a ROM, touch GitHub, build artifacts, repair the map,
or certify an emulator playthrough. Run from any working directory:
    python3 tools/check_aster_v14.py
"""
from collections import deque
from pathlib import Path
import hashlib
import re

ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "games/tbs/src/map/map_180/map.txt"
SCENE = ROOT / "games/tbs/src/scene/aster.c"
METATILES = ROOT / "games/tbs/src/map/map_003/metatiles.tsv"
EXPECTED_EVENTS = {
    "e1": (32, 36), "e2": (29, 20), "e3": (18, 22),
    "e4": (16, 35), "e5": (17, 47), "e6": (41, 48),
    "e7": (48, 35), "e8": (45, 22), "1": (32, 62),
}
EXPECTED_ACTORS = [
    ("Elder", 27, 32), ("Innkeeper", 16, 36),
    ("Greeter", 24, 36), ("Boy", 34, 38),
    ("Resident", 42, 49), ("Other Isaac", 28, 21),
    ("Mirror woman", 38, 36),
]
# x,y,w,h for six FULL native Golden Sun facades.
HOUSES = [
    ("sealed", 13, 12, 9, 9), ("duplicate", 41, 12, 9, 9),
    ("inn", 11, 24, 11, 10), ("shop", 44, 25, 10, 9),
    ("west", 13, 37, 9, 9), ("east", 38, 38, 8, 9),
]
RESERVED_NEW = [("sanctum", 40, 27, 4, 7),
                ("additional_home", 11, 51, 4, 7)]
OLD_EVENTS = {"e1": (32, 35), "e2": (32, 14), "e3": (12, 13),
              "e4": (47, 54), "e5": (12, 35), "e6": (53, 36),
              "e7": (11, 54), "e8": (52, 14), "1": (32, 63)}

def require(ok, reason):
    if not ok:
        raise AssertionError(reason)

def main():
    from aster_v14_native_map import render_snapshot
    if MAP.read_text(encoding="utf-8") != render_snapshot():
        raise AssertionError("Native V14 Map180 differs from immutable snapshot")
    text = MAP.read_text(encoding="utf-8").splitlines()
    require(text[0] == "grid:128x128\tat:0,0\tfill:0:0:0",
            "Wrong native map header")
    grid = [line.split() for line in text[1:]]
    require(len(grid) == 128 and all(len(r) == 128 for r in grid),
            "Expected 128x128 packed three-layer native map")
    # The GBA graphics encoder resolves 12-bit metatile indices through
    # this Vale table. Scan all packed layers, not just ground: an invalid
    # overhead ID can crash rendering even when walking tests pass.
    metatile_count = len(METATILES.read_text(encoding="utf-8").splitlines()) - 1
    require(metatile_count >= 1, "No original Vale metatiles found")
    allowed_behaviors = {"ff", *EXPECTED_EVENTS.keys()}
    for y, row in enumerate(grid):
        for x, token in enumerate(row):
            bits = token.split(":")
            require(1 <= len(bits) <= 2,
                    f"Malformed packed map token at {x},{y}: {token!r}")
            number = int(bits[0], 16)
            require(0 <= number <= 0xffff,
                    f"Out-of-range encoded tile at {x},{y}: {token!r}")
            index = number & 0xfff
            require(index < metatile_count,
                    f"Unknown Vale metatile index at {x},{y}: {token!r}")
            require(index != 0xfff,
                    f"Unresolved Vale metatile placeholder at {x},{y}")
            if len(bits) == 2:
                require(x < 64 and y < 64 and bits[1] in allowed_behaviors,
                        f"Unsupported behavior/out-of-layer token at {x},{y}: {token!r}")
    ground = [grid[y][:64] for y in range(64)]
    occurrences = {}
    for y, row in enumerate(ground):
        for x, value in enumerate(row):
            bits = value.split(":")
            require(len(bits) <= 2, f"Unexpected extra map token at {x},{y}")
            base = int(bits[0], 16)
            require((base & 0xfff) != 0xfff,
                    f"Unresolved native metatile placeholder at {x},{y}")
            if len(bits) > 1 and bits[1] in EXPECTED_EVENTS:
                require(bits[1] not in occurrences, f"Duplicate trigger {bits[1]}")
                occurrences[bits[1]] = (x, y)
    require(occurrences == EXPECTED_EVENTS,
            f"Trigger locations changed: {occurrences}")
    def solid(x, y):
        bits = ground[y][x].split(":")
        return len(bits) == 2 and bits[1] == "ff"
    house_cells = set()
    for name, x0, y0, w, h in HOUSES:
        for y in range(y0, y0 + h):
            for x in range(x0, x0 + w):
                require(solid(x, y), f"{name} facade walkable at {(x,y)}")
                require((x,y) not in house_cells, "Overlapping houses")
                house_cells.add((x,y))
    new_cells = set()
    for name, x0, y0, w, h in RESERVED_NEW:
        for y in range(y0, y0+h):
            for x in range(x0, x0+w):
                require(solid(x,y), f"{name} reservation not solid at {(x,y)}")
                require((x,y) not in house_cells, f"{name} overlaps old house")
                new_cells.add((x,y))
    scene = SCENE.read_text(encoding="utf-8")
    actor_start = scene.index("static struct ActorTemplate sAsterActors[] = {")
    actor_end = scene.index("static struct Trigger sAsterTriggers[] = {", actor_start)
    actor_table = scene[actor_start:actor_end]
    require(actor_table.count("MOVEMENT_TYPE_STAND") == 11,
            "Aster requires seven NPCs followed by four native scenery actors")
    decor = [
        ("SPRITE_ASTER_DRY_WELL", 32, 34),
        ("SPRITE_ASTER_MEMORIAL", 29, 19),
        ("SPRITE_ASTER_SANCTUM", 42, 33),
        ("SPRITE_ASTER_ADDITIONAL_HOME", 13, 57),
    ]
    after_npc = actor_table.split("SPRITE_ASTER_DRY_WELL", 1)
    require(len(after_npc) == 2,
            "Decorative actors must follow all seven original NPCs")
    for sprite, x, y in decor:
        require(actor_table.count(sprite) == 1, f"Missing native decor {sprite}")
        require(actor_table.count(f"PIXELS({x*16}), 0, PIXELS({y*16})") == 1,
                f"Native decor actor not at approved anchor: {sprite}")
    for name, x, y in EXPECTED_ACTORS:
        anchor = f"PIXELS({16*x}), 0, PIXELS({16*y})"
        require(actor_table.count(anchor) == 1,
                f"{name} scene anchor missing/duplicate")
    require("WORLD_MAP_FROM_VAULT_SOUTH" in scene,
            "Prototype world return was changed without reciprocal audit")
    require("SCENE_EXITS(Aster)" in scene, "Scene exit table was changed")
    require("Scene_Initialize" in scene, "Scene implementation missing")
    for pos in EXPECTED_EVENTS.values():
        require(not solid(*pos), f"Event {pos} is solid")
    for name,x,y in EXPECTED_ACTORS:
        require(not solid(x,y), f"Actor {name} in solid scenery")
    require(not solid(32,61) and not solid(32,62) and not solid(32,63),
            "Southern entrance, event, or edge is blocked")
    # Flood-fill native ground behavior. This does not prove engine priorities.
    pending = deque([(32,61)])
    visited = set()
    while pending:
        x,y = pending.popleft()
        if not (0<=x<64 and 0<=y<64) or (x,y) in visited or solid(x,y):
            continue
        visited.add((x,y))
        pending.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
    require(all(pos in visited for pos in EXPECTED_EVENTS.values()),
            "Some story event tiles are unreachable from spawn")
    require(all((x,y) in visited for _,x,y in EXPECTED_ACTORS),
            "Some placed NPCs are unreachable from spawn")
    edge = {(x,y) for x,y in visited if x in (0,63) or y in (0,63)}
    require(edge == {(32,63)}, f"Unexpected reachable map exits: {sorted(edge)}")
    require((0,35) not in visited, "Unwired west exit is open")
    require((32,34) not in visited, "Well's solid core is walkable")
    # Inspect native foliage and original transparent tile behavior.
    from check_aster_native_foliage import verify as verify_native_foliage
    verify_native_foliage()
    print("PASS staged Aster V14 native map: 128x128 packed, original metatiles")
    print("PASS eight story markers, one south exit; seven aligned NPC anchors")
    print("PASS six solid native house facades, two reserved new sites")
    print("PASS four indexed scenery actors follow the seven dialogue NPCs")
    print(f"PASS source-grid reachability: {len(visited)} cells, only south edge open")
    print("NOT VERIFIED: sprite priorities, collision in engine, world contact,")
    print("Sanctum or house interiors, final water/cliff art, ROM build, emulator")
    print("WARNING: Existing tools/aster_layout.py is the old generator.")
    print("WARNING: Exit still targets temporary Vault world-map arrival.")

if __name__ == "__main__":
    main()
