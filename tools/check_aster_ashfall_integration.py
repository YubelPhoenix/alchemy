#!/usr/bin/env python3
"""Read-only Ashfall + Aster first-playtest source gate.

No ROM compilation, network requests, GitHub Actions, artifact creation,
or changes to game data. Passing is NOT an emulator or runtime proof.
"""
from pathlib import Path
import hashlib
import os
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
def read(path):
    return (ROOT / path).read_text(encoding="utf-8")
def need(condition, reason):
    if not condition:
        raise SystemExit("ASTER INTEGRATION STOP: " + reason)
def blob_sha(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()

EXPECTED_AI = "c1c6b07bf3c04c0fa01390e24a3d41f034df3b6b"
AI_PATH = "games/tbs/src/battle/battle/boss_ai.c"

def main():
    ai = (ROOT / AI_PATH).read_bytes()
    need(blob_sha(ai) == EXPECTED_AI,
         "Claude's verified boss AI changed; review before building")
    world = read("games/tbs/src/scene/world_map.c")
    scene = read("games/tbs/src/scene/aster.c")
    exits = read("games/tbs/include/scene_exits.h")
    scene_table = read("games/tbs/src/field/scenes.s")
    scene_ids = read("games/tbs/include/scene_ids.h")
    fields = read("games/tbs/src/field/maps.c")
    resources = read("games/tbs/src/system/resource/directory.s")
    objects = read("games/tbs/objects.tsv")
    sprites = read("games/tbs/include/sprite_ids.h")
    layout = read("games/tbs/src/graphics/sprite/layout.tsv")
    registry = read("games/tbs/src/graphics/sprite/sprites.tsv")

    need(scene_table.count("scene Aster, 0x3d3, 0x47, 2, 0xba") == 1,
         "Aster scene 201 resource registration changed")
    need(scene_ids.count("extern char SceneId_Aster;") == 1,
         "Aster scene ID not registered once")
    need(fields.count("{{682, 13, 14, 15, 16, 17}}") == 1,
         "Aster native Map180 no longer reuses Vale resource palette")
    need(resources.count("resource AsterMap, Field_Map180") == 1,
         "Aster map resource missing")
    need(resources.count("Resource_Overlay3D3") == 1,
         "Aster overlay resource missing")
    for anchor in ("games/tbs/src/map/map_180/map",
                   "games/tbs/src/scene/entry/aster",
                   "games/tbs/src/scene/aster",
                   "games/tbs/src/scene/import/aster"):
        need(objects.count(anchor) == 1, f"Missing/duplicated build object: {anchor}")
    for num, symbol in ((505, "SPRITE_WORLD_MAP_ASTER"),
                        (506, "SPRITE_ASTER_DRY_WELL"),
                        (507, "SPRITE_ASTER_MEMORIAL"),
                        (508, "SPRITE_ASTER_SANCTUM"),
                        (509, "SPRITE_ASTER_ADDITIONAL_HOME")):
        need(sprites.count(symbol + " = ") == 1, f"Missing sprite enum {symbol}")
        need(layout.splitlines().count(f"SPR_{num}") == 1,
             f"Missing sprite layout SPR_{num}")
        need(sum(line.startswith(f"SPR_{num}\t") for line in registry.splitlines()) == 1,
             f"Missing sprite registry SPR_{num}")
        need((ROOT / f"games/tbs/src/graphics/sprite/spr_{num}.png").is_file(),
             f"Missing original indexed PNG SPR_{num}")

    need("CONTACT_LAST_ACTOR = 65" in world, "World actor contact bound changed")
    need(world.count("SPRITE_WORLD_MAP_ASTER, CONDITION_ALWAYS") == 1,
         "Expected one Aster world icon in reserved signpost slot")
    need("PIXELS(5696), 0, PIXELS(1504)" in world,
         "Experimental Aster world icon position changed")
    need(world.count("WORLD_MAP_TO_ASTER_TEST") == 2,
         "Aster world contact and scene exit must each appear once")
    need("STEP_TRIGGER_AREA(ACTOR_TO_KALAY_TUNNEL_ENTRANCE + 1)" in world,
         "Aster contact actor ID changed")
    need("SCENE_EXIT(WORLD_MAP_TO_ASTER_TEST, Aster, ENTRANCE_DEFAULT)" in world,
         "World->Aster entrance no longer wired")
    need("{98, CONDITION_ALWAYS, 5696, 0, 1536, FACING_SOUTH" in world,
         "Aster return position changed")
    need("SCENE_EXIT(ASTER_TO_WORLD_MAP, WorldMap, 98)" in scene,
         "Aster south gate no longer returns through reserved world entrance")
    need("WORLD_MAP_TO_ASTER_TEST = 115" in exits,
         "Aster experimental world exit kind missing")
    need("WORLD_MAP_FROM_VAULT_SOUTH" not in scene,
         "Aster still contains fallback Vault exit")

    text = read("games/tbs/text/en.po")
    aster = re.findall(r'^msgctxt "(MsgAster[^"]+)"\nmsgid "([0-9]{5})"',
                       text, re.M)
    need(len(aster) == 36 and len(set(a for a, _ in aster)) == 36,
         "Must have exactly 36 unique Aster dialogue contexts")
    need([int(n) for _, n in aster] == list(range(10723, 10759)),
         "Aster source dialogue IDs must remain 10723..10758")
    need('#, alchemy-null\nmsgctxt "message"\nmsgid "10722"' in text,
         "Expected vanilla end marker; preparation must relocate it")
    print("PASS: Aster scene, map, sprites, dialogue and two-way test route")
    print("PASS: Claude's tactical boss AI matches the tested Ashfall baseline")
    print("PASS: Aster message source IDs do not overwrite the vanilla catalogue")

    checks = ("check_aster_branch_isolation.py",
              "check_aster_overworld_contract.py",
              "aster_v14_native_map.py --check",
              "check_aster_v14.py",
              "check_aster_native_bridge.py",
              "check_aster_native_decor.py",
              "check_aster_world_icon.py")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for command in checks:
        argv = command.split()
        proc = subprocess.run([sys.executable, "-B", str(ROOT / "tools" / argv[0]), *argv[1:]],
                              cwd=ROOT, env=env, check=False)
        need(proc.returncode == 0, "Source test failed: " + command)
    print("PASS: read-only Aster source validation; no builds were run.")
    print("NOT VERIFIED: GBA compile, native rendering, terrain, transitions, saves, NPCs.")
    print("TEST BRANCH ONLY: never merge this world contact without emulator QA.")

if __name__ == "__main__":
    main()
