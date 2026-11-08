#!/usr/bin/env python3
"""Strict, read-only Aster source contract. Does not build or modify the ROM.

Run from any working directory with: python3 tools/check_aster.py
The companion ROM/emulator acceptance checks are documented separately.
"""
import ast
import csv
import importlib.util
import re
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
MAP_PATH = ROOT / "games/tbs/src/map/map_180/map.txt"
PO_PATH = ROOT / "games/tbs/text/en.po"
SCENE_PATH = ROOT / "games/tbs/src/scene/aster.c"
IMPORT_PATH = ROOT / "games/tbs/src/scene/import/aster.s"
LAYOUT_PATH = TOOLS / "aster_layout.py"
DIALOGUE_PATH = TOOLS / "aster_dialogue.tsv"

def require(ok, message):
    if not ok:
        raise AssertionError(message)

def read(path):
    return path.read_text(encoding="utf-8")

def message_catalog():
    """Read only Aster entries, retaining actual display-page boundaries."""
    text = read(PO_PATH)
    catalog = {}
    ids = set()
    for block in re.split(r"\n\s*\n", text):
        context = re.search(r'^msgctxt "(MsgAster[^"]+)"$', block, re.M)
        if context is None:
            continue
        name = context.group(1)
        ident = re.search(r'^msgid "(\d+)"$', block, re.M)
        require(ident is not None, f"Missing numeric msgid: {name}")
        require(name not in catalog, f"Duplicate msgctxt: {name}")
        require(int(ident.group(1)) not in ids, f"Duplicate Aster msgid: {name}")
        ids.add(int(ident.group(1)))
        quoted = []
        in_str = False
        for line in block.splitlines():
            if line == 'msgstr ""':
                in_str = True
                continue
            if in_str and line.startswith('"'):
                quoted.append(ast.literal_eval(line))
        require(quoted, f"No compiled message text: {name}")
        display = "".join(quoted)
        require(display.endswith("{end_wait}"), f"Missing message terminator: {name}")
        display = display.removesuffix("{end_wait}")
        pages = display.split("{page_break}")
        for page_index, page in enumerate(pages, 1):
            lines = page.strip("\n").split("\n")
            require(1 <= len(lines) <= 3,
                    f"{name} page {page_index}: {len(lines)} lines (max 3)")
            for line_index, line in enumerate(lines, 1):
                require(0 < len(line) <= 27,
                        f"{name} page {page_index} line {line_index}: "
                        f"{len(line)} chars (max 27): {line!r}")
        catalog[name] = display
    require(len(catalog) >= 32, f"Only {len(catalog)} Aster messages compiled")
    return catalog

def dialogue_source(catalog):
    seen = set()
    with DIALOGUE_PATH.open(newline="", encoding="utf-8") as f:
        rows = csv.DictReader(f, delimiter="\t")
        require(rows.fieldnames == ["stage","key","speaker","line1","line2","line3"],
                "Changed Aster dialogue TSV columns")
        for index, row in enumerate(rows, 2):
            require(None not in row and None not in row.values(),
                    f"TSV row {index} malformed")
            name = "MsgAster" + "".join(
                part.capitalize()
                for segment in (row["stage"], row["key"])
                for part in segment.split("_"))
            require(name not in seen, f"Duplicate staged dialogue row: {name}")
            seen.add(name)
            lines = [row[k] for k in ("line1", "line2", "line3") if row[k]]
            require(lines, f"No dialogue: {name}")
            for line in lines:
                require(len(line) <= 27, f"{name} too long: {line}")
            require(name in catalog, f"{name} missing from compiled English PO")
            require(catalog[name] == "\n".join(lines),
                    f"Source/compiled dialogue drift: {name}")
    require(len(seen) == 28, f"Expected 28 source dialogues, found {len(seen)}")
    return seen

def map_contract():
    spec = importlib.util.spec_from_file_location("aster_layout", LAYOUT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    generated = module.source()
    require(read(MAP_PATH) == generated, "Aster map.txt not generated from script")
    rows = module.LAYOUT
    require(module.SIDE == 64 and len(rows) == 64
            and all(len(row) == 64 for row in rows),
            "Aster exterior must be 64x64 cells")
    require(rows[63][32] == "G" and
            sum(r.count("G") for r in rows) == 1,
            "South gate displaced or duplicated")
    require(all(rows[63][x] == "#" for x in range(64) if x != 32),
            "Border has an accidental open edge")
    tokens = [r.split() for r in generated.splitlines()[1:]]
    require(len(tokens) == 128 and all(len(row) == 128 for row in tokens),
            "Aster three-layer 128x128 packed grid is malformed")
    for name, x, y, behavior in module.INTERACTIONS:
        require(tokens[y][x] == behavior,
                f"Missing {name} event tile at ({x},{y})")
        require(rows[y][x] in ".=",
                f"{name} trigger embedded inside solid facade")
    require(tokens[63][32] == "ba:1", "South gate exit behavior missing")
    require(all((int(t.split(":")[0],16) & 0xfff) != 0xfff
                for row in tokens for t in row),
            "Unresolved 0xFFF placeholders would scramble Aster graphics")
    require(tokens[1][65] == "15" and tokens[65][1] == "15",
            "Vale grass requires original middle+overhead layers, not ground only")
    require(len(module.BUILDINGS) == 6, "Aster six facades changed")
    require(len(module.ACTORS) == 7, "Aster actor roster changed")
    native = module.load_vale()
    # Original Golden Sun Vale walls and roofs are copied exactly.
    # The ground under houses is native grass, never imported cliffs.
    require(tokens[1][1] == "ba",
            "Open lawn must use native Vale green terrain, not an empty metatile")
    require(tokens[20][25] == "ba",
            "Aster may not use the rejected unrelated street tile")
    for name, x, y, sx, sy, w, h, ch in module.BUILDINGS:
        require(w > 0 and h > 0, f"Empty facade: {name}")
        require(all(rows[yy][xx] == ch
                    for yy in range(y, y+h) for xx in range(x, x+w)),
                f"Facade footprint changed: {name}")
        for dy in range(h):
            for dx in range(w):
                require(tokens[y+dy][x+dx] == "ba:ff",
                        f"House must use Vale grass under facade: {name} at ({dx},{dy})")
                require(tokens[y+dy][x+dx+64] ==
                        native[sy+dy][sx+dx+30],
                        f"Foreign or altered middle layer in {name}")
                require(tokens[y+dy+64][x+dx] ==
                        native[sy+dy][sx+dx+60],
                        f"Foreign or altered overhead layer in {name}")
    # No door event may float in front of a different building or on
    # a disconnected route; all six thresholds lie one cell south of roof.
    for name, x, y, behavior in module.DOOR_APPROACHES:
        homes = [b for b in module.BUILDINGS if b[0] == name]
        require(len(homes) == 1, f"Unknown house threshold: {name}")
        _, hx, hy, sx, sy, w, h, _ = homes[0]
        require(hx <= x < hx+w and y == hy+h,
                f"{name} entrance misaligned with facade")
        require(tokens[y][x] == behavior,
                f"{name} doorstep has no matching scene trigger")
    gate_x, gate_y, _, _, gate_w, gate_h = module.GATE_ARCH
    require(gate_x <= module.EXIT[0] < gate_x + gate_w
            and gate_y + gate_h <= module.EXIT[1],
            "South exit must be centered on the original Vale entrance arch")
    require(all(rows[y][x] in ".=G"
                for y in range(gate_y,gate_y+gate_h)
                for x in range(gate_x,gate_x+gate_w)),
            "South gate arch overlays a building or solid obstruction")
    # The user explicitly rejected a Vale Psynergy Stone. Keep the ordinary
    # remembrance site and its event, but NEVER the original crystal shrine.
    require(not hasattr(module, "MEMORIAL_ART"),
            "Rejected Psynergy shrine was reintroduced to Aster")
    mx,my,mw,mh = module.MEMORIAL_RESERVED
    require(mx <= module.MEMORIAL[0] < mx+mw and
            my+mh == module.INTERACTIONS[0][2],
            "Memorial reservation and south interaction do not align")
    require(rows[module.MEMORIAL[1]][module.MEMORIAL[0]] == "M",
            "Memorial needs a reserved non-walkable center")
    for dy in range(mh):
        for dx in range(mw):
            require(tokens[my+dy][mx+dx+64] == "15" and
                    tokens[my+dy+64][mx+dx] == "15",
                    "No Psynergy crystal or magic shrine may appear on memorial")
    require(len(module.PATH_PATCHES) == 3,
            "Worn ground patches count has changed without visual approval")
    for name,dx,dy,sx,sy,w,h in module.PATH_PATCHES:
        for off_y in range(h):
            for off_x in range(w):
                px, py = dx+off_x, dy+off_y
                require(rows[py][px] not in "#XIHSVTMW",
                        f"Ground wear {name} covers a prop/house")
                native_ground = native[sy+off_y][sx+off_x].split(":")[0]
                expected = native_ground
                for _, ix, iy, behavior in module.INTERACTIONS:
                    if (px,py)==(ix,iy):
                        expected = behavior
                require(tokens[py][px] == expected,
                        f"Worn-path patch {name} misdrawn at ({px},{py})")
    require(len(module.SCENERY) == 8, "Aster tree roster changed")
    for name, x, y, sx, sy, w, h in module.SCENERY:
        require(all(rows[yy][xx] == "T"
                    for yy in range(y,y+h) for xx in range(x,x+w)),
                f"Tree {name} overlaps an approach or building")
        for dy in range(h):
            for dx in range(w):
                require(tokens[y+dy][x+dx+64] ==
                        native[sy+dy][sx+dx+30],
                        f"{name} has foreign or missing middle-layer vegetation")
                require(tokens[y+dy+64][x+dx] ==
                        native[sy+dy][sx+dx+60],
                        f"{name} has foreign or missing roof-layer vegetation")
    accessible = set()
    queue = deque([module.START])
    while queue:
        x,y = queue.popleft()
        if (x,y) in accessible or not (0 <= x < 64 and 0 <= y < 64):
            continue
        if rows[y][x] not in ".=G":
            continue
        accessible.add((x,y))
        queue.extend(((x+1,y),(x-1,y),(x,y+1),(x,y-1)))
    required = [module.EXIT] + list(module.ACTORS)
    required.extend((x,y) for _,x,y,_ in module.INTERACTIONS)
    require(all(pos in accessible for pos in required),
            "Inaccessible actor, gate or building threshold")
    mapspec = read(ROOT / "games/tbs/src/map/map_180/map.s")
    for expected in (
        "map_header 0, 0, 128, 128, 3, 2, 1",
        "map_layer 0, 0, 16, 16",
        "map_layer 128, 0, 16, 16",
        "map_layer 0, 128, 16, 16",
    ):
        require(expected in mapspec, f"Aster layer/header mismatch: {expected}")

def scene_contract(catalog):
    scene = read(SCENE_PATH)
    imports = read(IMPORT_PATH)
    referenced = set(re.findall(r"\bMsgAster[A-Za-z0-9]+\b", scene))
    for name in referenced:
        require(name in catalog, f"Aster scene references uncompiled: {name}")
    # These four gate messages are written but deliberately deferred until
    # a safe, reciprocal world-map entrance and exit script exist.
    deferred = {
        "MsgAsterArrivalGate", "MsgAsterFractureGate",
        "MsgAsterRevelationGate", "MsgAsterRevelationExit",
    }
    unused = set(catalog) - referenced
    require(unused == deferred,
            f"Unwired Aster dialogue changed: {sorted(unused)}. "
            f"Only the four deferred gate lines may be unreferenced")
    for symbol in (
        "GameFlag_Get", "GameFlag_Set", "Event_Start", "Event_End",
        "Event_SetMessageId", "Event_ShowMessageAndWait", "FieldMessage_Show",
    ):
        require(f"import.{symbol}, 1" in imports, f"Missing overlay import: {symbol}")
    for marker,handler in (
        ("0xe1","Aster_VisitWell"),
        ("0xe2","Aster_VisitMemorial"),
        ("0xe3","Aster_VisitDoor"),
        ("0xe4","Aster_VisitInnThreshold"),
        ("0xe5","Aster_VisitWestHomeThreshold"),
        ("0xe6","Aster_VisitEastHomeThreshold"),
        ("0xe7","Aster_VisitShopThreshold"),
        ("0xe8","Aster_VisitDuplicateHomeThreshold"),
    ):
        require(marker in scene and f"EVENT({handler})" in scene,
                f"Landmark trigger missing: {handler}")
    for flag in re.findall(r"#define ASTER_\w+\s+(FLAG_\w+)", scene):
        require(flag.startswith("FLAG_SCENE_TEMP_"),
                f"Aster may not mutate permanent story flag: {flag}")
    require("SCENE_EXIT(ASTER_TO_WORLD_MAP, WorldMap, WORLD_MAP_FROM_VAULT_SOUTH)" in scene,
            "Prototype exit changed without reciprocal overworld entrance audit")
    tables = read(ROOT / "games/tbs/src/field/scenes.s")
    require(re.search(r"\bscene Aster,\s*0x3d3,\s*0x47,\s*2,\s*0xba\b", tables),
            "Aster scene map index changed")
    maps = read(ROOT / "games/tbs/src/field/maps.c")
    require("{{682, 13, 14, 15, 16, 17}}" in maps,
            "Aster must reference matching Vale tileset/palette resources")
    rows = re.findall(r"\{\{\s*(\d+)(?:\s*,|\s*\})", maps)
    require(len(rows) == 187 and rows[-1] == "682",
            f"Aster map resource is not appended at index 0xba (got {len(rows)} rows)")
    directory = read(ROOT / "games/tbs/src/system/resource/directory.s")
    require("resource AsterMap, Field_Map180" in directory,
            "Missing Aster map resource")
    objects = read(ROOT / "games/tbs/objects.tsv")
    for path in ("games/tbs/src/map/map_180/map",
                 "games/tbs/src/scene/entry/aster",
                 "games/tbs/src/scene/aster",
                 "games/tbs/src/scene/import/aster"):
        require(path in objects, f"Missing linked object: {path}")

def main():
    catalog = message_catalog()
    source = dialogue_source(catalog)
    print(f"PASS Aster dialogue: {len(source)} staged entries, "
          f"{len(catalog)} compiled messages, <=27 chars x <=3 lines/page")
    map_contract()
    print("PASS Aster map: native Vale grass and six three-layer cottage sections; 8 events")
    scene_contract(catalog)
    print("PASS Aster scene: compiled references, imports, reserved scene/map rows")
    print("SOURCE AUDIT ONLY: ROM build, rendered tiles, collision, actual "
          "entry/exit and emulator tests remain unverified.")

if __name__ == "__main__":
    main()
