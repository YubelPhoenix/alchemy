#!/usr/bin/env python3
"""Read-only Aster story-persistence and save-flag namespace audit.

Use locally before a ROM build. This does not write a save, compile, upload,
run GitHub Actions, or claim a successful emulator/save migration test.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
FLAGS = ROOT / "games/tbs/include/flags.h"
SCENE = ROOT / "games/tbs/src/scene/aster.c"
SAVE = ROOT / "games/tbs/include/save_block.h"

# Save-backed bits already exist; reserve only these five unused IDs.
STORY_FLAGS = {
    "ASTER_SEEN_WELL": ("FLAG_DARK_ASTER_SEEN_WELL", 0x8d9),
    "ASTER_SEEN_MEMORIAL": ("FLAG_DARK_ASTER_SEEN_MEMORIAL", 0x8da),
    "ASTER_HEARD_GREETER": ("FLAG_DARK_ASTER_HEARD_GREETER", 0x8db),
    "ASTER_FRACTURED": ("FLAG_DARK_ASTER_FRACTURED", 0x8dc),
    "ASTER_REVEALED": ("FLAG_DARK_ASTER_REVEALED", 0x8dd),
}

def need(ok, msg):
    if not ok:
        raise SystemExit("ASTER SAVE FLAG STOP: " + msg)

def function(source, name):
    start = f"static void {name}(void) {{"
    need(source.count(start) == 1, f"Expected one {name} function")
    return source.split(start, 1)[1].split("\n}", 1)[0]

def verify():
    flags = FLAGS.read_text(encoding="utf-8")
    scene = SCENE.read_text(encoding="utf-8")
    save = SAVE.read_text(encoding="utf-8")

    need("the 0x200 bytes of game" in save and
         "Saving writes it whole" in save,
         "Existing 0x200-byte saved flag block no longer documented")
    need("#define FLAG_SCENE_TEMP_FIRST 0x200" in flags and
         "#define FLAG_SCENE_TEMP_LAST 0x2ff" in flags,
         "Scene-temporary flag boundaries changed")
    need("#define FLAG_AREA_TEMP_FIRST 0x300" in flags and
         "#define FLAG_AREA_TEMP_LAST 0x3ff" in flags,
         "Area-temporary flag boundaries changed")

    # All named definitions with literal numeric IDs, not just the five new
    # names. This rejects accidental sharing with any canonical story flag.
    defs = re.findall(
        r"(?m)^#define\s+(FLAG_[A-Za-z0-9_]+)\s+0x([0-9a-fA-F]+)\b",
        flags,
    )
    for alias, (name, number) in STORY_FLAGS.items():
        need(0x800 <= number <= 0xfff,
             f"Flag out of existing save-backed range: {name}")
        matches = [n for n, raw in defs if int(raw, 16) == number]
        need(matches == [name],
             f"Flag 0x{number:x} is shared/missing: {matches}")
        need(scene.count(f"#define {alias} {name}") == 1,
             f"Scene does not use save-backed {name}")
        need(not re.search(r"\bGameFlag_Clear\(\s*" + re.escape(alias) +
                           r"\s*\)", scene),
             f"Major story flag cleared in Aster: {alias}")

    # No direct numeric use of these newly allocated IDs in other source
    # files. Prefer named symbols to prevent hidden collisions.
    raw_ids = re.compile(
        r"(?i)(?<![\w])0x8d(?:9|a|b|c|d)(?![\da-f])"
    )
    unreviewed = []
    for folder in (ROOT / "games/tbs/src", ROOT / "games/tbs/include"):
        for ext in ("*.c", "*.h"):
            for path in folder.rglob(ext):
                if path == FLAGS:
                    continue
                source = path.read_text(encoding="utf-8", errors="replace")
                if raw_ids.search(source):
                    unreviewed.append(str(path.relative_to(ROOT)))
    need(not unreviewed,
         "Potential raw numeric flag reuse; review these files: " +
         ", ".join(unreviewed[:20]))

    # The clue order is independent of the visiting order: each of the
    # three clue handlers saves its own bit before checking the fracture.
    fracture = function(scene, "Aster_CheckFracture")
    for alias in ("ASTER_SEEN_WELL", "ASTER_SEEN_MEMORIAL",
                  "ASTER_HEARD_GREETER"):
        need(f"GameFlag_Get({alias})" in fracture,
             f"Missing fracture prerequisite {alias}")
    need(fracture.count("GameFlag_Set(ASTER_FRACTURED)") == 1,
         "Fracture must set the permanent stage flag exactly once")
    for name, flag in (
        ("Aster_VisitWell", "ASTER_SEEN_WELL"),
        ("Aster_VisitMemorial", "ASTER_SEEN_MEMORIAL"),
        ("Aster_TalkGreeter", "ASTER_HEARD_GREETER"),
    ):
        handler = function(scene, name)
        need(f"GameFlag_Set({flag})" in handler,
             f"{name} does not permanently retain its clue")
        need("Aster_CheckFracture();" in handler,
             f"{name} does not check whether the third clue was found")
    other = function(scene, "Aster_TalkOther")
    need(other.count("GameFlag_Set(ASTER_REVEALED)") == 1,
         "The revelation must set its permanent flag after the exchange")
    need(other.index("GameFlag_Get(ASTER_FRACTURED)") <
         other.index("GameFlag_Set(ASTER_REVEALED)"),
         "Other Isaac revelation must require the fracture first")
    need("FLAG_SCENE_TEMP_0E" in scene and
         "FLAG_SCENE_TEMP_18" in scene,
         "Door threshold one-shot flags must remain temporary")
    need("Scene_Initialize(void) { return 0; }" in scene,
         "Scene initialization now mutates story flags")
    print("PASS: five named save-backed story flags 0x8d9..0x8dd are unique")
    print("PASS: all clue orders feed fracture; revelation depends on fracture")
    print("PASS: temporary door text is separate; no save layout modifications")
    print("NOT VERIFIED: ROM compile, in-emulator save/load or legacy SAV upgrade")

if __name__ == "__main__":
    verify()
