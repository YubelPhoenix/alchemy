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
    require(read(MAP_PATH) == generated, "Aster map.txt is not generated source")
    rows = module.LAYOUT
    require(len(rows) == 32 and all(len(row) == 32 for row in rows),
            "Aster must be 32x32 cells")
    require(rows[31][15] == "G", "South exit displaced")
    require(sum(r.count("G") for r in rows) == 1, "Exit should be unique")
    token_rows = [r.split() for r in generated.splitlines()[1:]]
    require(len(token_rows) == 32 and all(len(r) == 32 for r in token_rows),
            "Generated grid has malformed dimensions")
    for x,y,token,near in (
        (16,17,"14:e1",(16,16)),
        (16,11,"14:e2",(16,10)),
        (6,6,"0:e3",(6,5)),
    ):
        require(token_rows[y][x] == token,
                f"Missing landmark approach behavior at ({x},{y})")
        require(rows[near[1]][near[0]] in "WMX",
                f"Landmark at {near} unexpectedly walkable")
    require(token_rows[31][15] == "0:1", "Missing exit behavior")
    actors = ((12,16),(20,17),(8,17),(15,24),(24,19),(18,11),(25,21))
    targets = actors + ((16,17),(16,11),(6,6),(15,31))
    accessible = set()
    queue = deque([(15,28)])
    while queue:
        x,y = queue.popleft()
        if (x,y) in accessible or not (0 <= x < 32 and 0 <= y < 32):
            continue
        if rows[y][x] not in ".=nG":
            continue
        accessible.add((x,y))
        queue.extend(((x+1,y),(x-1,y),(x,y+1),(x,y-1)))
    for point in targets:
        require(point in accessible, f"Actor/landmark/exit unreachable: {point}")
    require(not any(point == (15,31) for point in actors),
            "NPC blocks the south exit")

def scene_contract(catalog):
    scene = read(SCENE_PATH)
    imports = read(IMPORT_PATH)
    for name in set(re.findall(r"\bMsgAster[A-Za-z0-9]+\b", scene)):
        require(name in catalog, f"Aster scene references uncompiled: {name}")
    for symbol in (
        "GameFlag_Get", "GameFlag_Set", "Event_Start", "Event_End",
        "Event_SetMessageId", "Event_ShowMessageAndWait", "FieldMessage_Show",
    ):
        require(f"import.{symbol}, 1" in imports, f"Missing overlay import: {symbol}")
    for marker,handler in (
        ("0xe1","Aster_VisitWell"),
        ("0xe2","Aster_VisitMemorial"),
        ("0xe3","Aster_VisitDoor"),
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
    print("PASS Aster map: 32x32 grid, solid landmarks, reachable events and exit")
    scene_contract(catalog)
    print("PASS Aster scene: compiled references, imports, reserved scene/map rows")
    print("SOURCE AUDIT ONLY: ROM build, rendered tiles, collision, actual "
          "entry/exit and emulator tests remain unverified.")

if __name__ == "__main__":
    main()
