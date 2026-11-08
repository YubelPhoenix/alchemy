#!/usr/bin/env python3
"""Read-only Aster-to-overworld contact and static placement contract.

This verifies the isolated TEST branch's reserved actor, event and reciprocal
entrance without pretending to prove that the world ground is walkable.
Requires the approved Ashfall base commit in the local Git checkout.
Never invokes an emulator, compiler, hosted workflow, network call or upload.
"""
from pathlib import Path
import math
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BASE = "62dd7b5331a7e23a12df0090e9e823a3aed8f425"
WORLD = "games/tbs/src/scene/world_map.c"
SITE = (5696, 1504)
RETURN = (5696, 1536)
RESERVED_ACTOR_INDEX = 39
STATIC_ICON_CLEARANCE = 96  # design screening only; NOT world collision


def need(condition, reason):
    if not condition:
        raise SystemExit("ASTER WORLD CONTRACT STOP: " + reason)


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def original(path):
    proc = subprocess.run(
        ["git", "show", f"{BASE}:{path}"],
        cwd=ROOT, text=True, capture_output=True, timeout=30,
        check=False,
    )
    need(proc.returncode == 0,
         f"Approved Ashfall baseline missing: {path}: {proc.stderr.strip()}")
    return proc.stdout


def section(text, start):
    header = start + " = {"
    need(text.count(header) == 1, f"Expected one {start} table")
    body = text.split(header, 1)[1].split("\n};", 1)[0]
    need(body, f"Empty or unterminated table {start}")
    return body


def records(text):
    rows = re.findall(r"\{[^{}]*\}", text, re.S)
    need(bool(rows), "No C entries in selected actor table")
    return rows


def canonical(text):
    return " ".join(text.split())


def confirm_world_actors(world):
    old_rows = records(section(original(WORLD), "struct ActorTemplate gWorldMapActorTemplates[]"))
    new_rows = records(section(world, "struct ActorTemplate gWorldMapActorTemplates[]"))
    need(len(old_rows) == len(new_rows) == 51,
         f"World actor table length changed: {len(old_rows)} -> {len(new_rows)}")
    need("SPRITE_SIGNPOST" in old_rows[RESERVED_ACTOR_INDEX],
         "Original reserved actor is not a signpost")
    expected = ("{ SPRITE_WORLD_MAP_ASTER, CONDITION_ALWAYS, "
                "(s32)gWorldMapAlignToMapScript, "
                "PIXELS(5696), 0, PIXELS(1504), FACING_SOUTH, "
                "TALK_FACING_KEEP, 0 }")
    need(canonical(new_rows[RESERVED_ACTOR_INDEX]) == canonical(expected),
         "Aster is not an unchanged reserved signpost actor with a new icon")
    for i, (before, after) in enumerate(zip(old_rows, new_rows)):
        if i != RESERVED_ACTOR_INDEX:
            need(canonical(before) == canonical(after),
                 f"Other world actor {i} was modified or renumbered")
    need(new_rows[RESERVED_ACTOR_INDEX + 1].count("SPRITE_SIGNPOST") == 1
         and new_rows[RESERVED_ACTOR_INDEX + 2].count("SPRITE_SIGNPOST") == 1,
         "Two remaining origin signpost slots must be left alone")
    # The runtime scan includes actor 47 (first placed actor ID 8 + index 39).
    need("CONTACT_LAST_ACTOR = 65" in world
         and "STEP_TRIGGER_AREA_BASE = 100" in world,
         "World actor contact bounds have changed")
    need("ACTOR_TO_KOLIMA_BRIDGE = ACTOR_TO_KALAY_TUNNEL_ENTRANCE + 4" in world,
         "Original three-hole signpost actor enumeration moved")
    need("STEP_TRIGGER_AREA(ACTOR_TO_KALAY_TUNNEL_ENTRANCE + 1)" in world,
         "World Aster contact no longer refers to the first unused signpost")

    # Only static icon spacing can be determined without the engine's
    # perspective geometry, height, and ground collision checks.
    icons = []
    for i, row in enumerate(new_rows):
        found = re.search(r"\b(SPRITE_WORLD_MAP_[A-Z0-9_]+)\b", row)
        coords = re.search(r"PIXELS\((\d+)\),\s*0,\s*PIXELS\((\d+)\)", row)
        if found and coords and i != RESERVED_ACTOR_INDEX:
            icons.append((found.group(1), int(coords.group(1)),
                          int(coords.group(2))))
    need(len(icons) >= 35, "Too few static original overworld icons")
    need(("SPRITE_WORLD_MAP_VILLAGE", 5848, 1576) in icons,
         "Original Vault world icon moved")
    need(("SPRITE_WORLD_MAP_VILLAGE", 5678, 1200) in icons,
         "Original Vale world icon moved")
    closest = min((math.hypot(SITE[0] - x, SITE[1] - z), kind, x, z)
                  for kind, x, z in icons)
    need(closest[0] >= STATIC_ICON_CLEARANCE,
         f"Aster too close to static world icon: {closest}")
    print(f"PASS: world actor slot 39 exclusively repurposed; "
          f"{len(new_rows)} actor table entries unchanged in count")
    print(f"PASS: nearest non-Aster static icon {closest[1]} at "
          f"({closest[2]}, {closest[3]}); {closest[0]:.1f} pixels")


def confirm_exits(world):
    exits = read("games/tbs/include/scene_exits.h")
    scene = read("games/tbs/src/scene/aster.c")
    need(exits.count("WORLD_MAP_TO_ASTER_TEST = 115") == 1,
         "Experimental exit kind 115 missing/duplicated")
    need(world.count("WORLD_MAP_TO_ASTER_TEST") == 2,
         "Expected one Aster world exit and one Aster contact")
    need(world.count("SCENE_EXIT(WORLD_MAP_TO_ASTER_TEST, Aster, ENTRANCE_DEFAULT)") == 1,
         "World icon does not enter Aster's southern default entrance")
    expected_contact = ("{ TRIGGER_EXIT, STEP_TRIGGER_AREA("
                        "ACTOR_TO_KALAY_TUNNEL_ENTRANCE + 1), "
                        "CONDITION_ALWAYS, WORLD_MAP_TO_ASTER_TEST }")
    need(canonical(expected_contact) in canonical(world),
         "Missing or conditional Aster touch contact")
    need(world.count("{98, CONDITION_ALWAYS, 5696, 0, 1536, FACING_SOUTH") == 1,
         "World return entrance 98 missing/duplicated")
    need(scene.count("SCENE_EXIT(ASTER_TO_WORLD_MAP, WorldMap, 98)") == 1,
         "Aster south exit does not return to world entrance 98")
    need(scene.count("ENTRANCE_DEFAULT, CONDITION_ALWAYS, 512, 0, 976, FACING_NORTH") == 1,
         "Aster south arrival anchor changed")
    need(RETURN[0] == SITE[0] and RETURN[1] - SITE[1] == 32,
         "World exit must emerge 32 pixels south of the Aster icon")
    need("WORLD_MAP_FROM_VAULT_SOUTH" not in scene,
         "Aster still returns to Vault instead of its own world icon")
    need((ROOT / "games/tbs/src/map/world/blocks.tsv").exists(),
         "Native world block table not found; no world terrain evidence")
    print("PASS: contact 147 -> exit 115 -> Aster default entrance")
    print("PASS: Aster south exit -> world entrance 98, 32 pixels south")


def main():
    world = read(WORLD)
    confirm_world_actors(world)
    confirm_exits(world)
    print("PASS: static source wiring only; no game files modified.")
    print("UNVERIFIED: world ground collision, Vault walking route, "
          "terrain elevation, icon visibility, return loops, progression.")
    print("STOP before merge or release until a local emulator test passes.")


if __name__ == "__main__":
    main()
