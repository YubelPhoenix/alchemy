#!/usr/bin/env python3
"""Reversible two-way Aster overworld probe for LOCAL experimental ROM builds.

This script temporarily uses one unused signpost in the NORMAL world-map
actor set as the Aster icon. It does not insert or shift any actor ID,
and it preserves the untouched original sprite used by existing villages.

The source changes are intentionally NOT present in the committed ROM sources.
--check    Read-only: check six original source anchors are intact.
--apply    Activate: native Aster icon contact -> Aster; Aster south exit ->
           temporary world entrance 98 at proposed X=5696, Z=1504.
--restore  Return all six edits to the exact original source text.

The local build shell helper applies/restores this on an isolated worktree.
Neither this script nor the shell helper launches GitHub Actions. There is
NO assurance the candidate is walkable until an emulator playtest passes.
"""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORLD = ROOT / "games/tbs/src/scene/world_map.c"
ASTER = ROOT / "games/tbs/src/scene/aster.c"
EXITS = ROOT / "games/tbs/include/scene_exits.h"

# Existing world-map slot 39 is the FIRST of three unused signposts at (0,0).
# Its ID is ACTOR_TO_KALAY_TUNNEL_ENTRANCE + 1 (not an inserted actor).
# The contact scan stops at ID 65, so this slot remains within its range.
# Exit kind 115 is unused in the audited WorldMap exit enum.
EDITS = (
    (
        WORLD,
        "    { SPRITE_SIGNPOST, CONDITION_ALWAYS, (s32)gWorldMapAlignToMapScript,\n"
        "        0, 0, 0, FACING_SOUTH, TALK_FACING_KEEP, 0 },",
        "    { SPRITE_WORLD_MAP_ASTER, CONDITION_ALWAYS, "
        "(s32)gWorldMapAlignToMapScript,\n"
        "        PIXELS(5696), 0, PIXELS(1504), FACING_SOUTH, TALK_FACING_KEEP, 0 },",
    ),
    (
        WORLD,
        "    { TRIGGER_EXIT, STEP_TRIGGER_AREA(ACTOR_TO_VALE_PLAZA), "
        "CONDITION_ALWAYS, WORLD_MAP_TO_VALE_PLAZA },",
        "    { TRIGGER_EXIT, STEP_TRIGGER_AREA(ACTOR_TO_VALE_PLAZA), "
        "CONDITION_ALWAYS, WORLD_MAP_TO_VALE_PLAZA },\n"
        "    { TRIGGER_EXIT, "
        "STEP_TRIGGER_AREA(ACTOR_TO_KALAY_TUNNEL_ENTRANCE + 1), "
        "CONDITION_ALWAYS, WORLD_MAP_TO_ASTER_TEST },",
    ),
    (
        WORLD,
        "    SCENE_EXIT(WORLD_MAP_TO_ROCK_ROOMS, RockRooms,\n"
        "               ROCK_ROOMS_FROM_SUHALLA_GATE_CHECKPOINT),\n"
        "    SCENE_EXITS_END,",
        "    SCENE_EXIT(WORLD_MAP_TO_ROCK_ROOMS, RockRooms,\n"
        "               ROCK_ROOMS_FROM_SUHALLA_GATE_CHECKPOINT),\n"
        "    SCENE_EXIT(WORLD_MAP_TO_ASTER_TEST, Aster, ENTRANCE_DEFAULT),\n"
        "    SCENE_EXITS_END,",
    ),
    (
        WORLD,
        "    {98, CONDITION_ALWAYS, 4248, 0, 2424, FACING_SOUTH, "
        "0, -1, -1, -1, -1, 0},",
        "    {98, CONDITION_ALWAYS, 5696, 0, 1504, FACING_SOUTH, "
        "0, -1, -1, -1, -1, 0},",
    ),
    (
        ASTER,
        "SCENE_EXIT(ASTER_TO_WORLD_MAP, WorldMap, WORLD_MAP_FROM_VAULT_SOUTH)",
        "SCENE_EXIT(ASTER_TO_WORLD_MAP, WorldMap, 98)",
    ),
    (
        EXITS,
        "  WORLD_MAP_TO_MIA_REUNITES = 114,\n};",
        "  WORLD_MAP_TO_MIA_REUNITES = 114,\n"
        "  /// Local-only Aster test exit, using a previously unassigned kind.\n"
        "  WORLD_MAP_TO_ASTER_TEST = 115,\n};",
    ),
)

def prepare(mode):
    original = {}
    changed = {}
    for path, _, _ in EDITS:
        if path not in original:
            original[path] = path.read_text(encoding="utf-8")
            changed[path] = original[path]
    # Refuse source drift before writing ANY file. --restore tolerates a
    # partially installed test probe so an interrupted build is recoverable.
    for path, old, new in EDITS:
        source = changed[path]
        n_old = source.count(old)
        n_new = source.count(new)
        # One replacement contains its original trigger as a prefix.
        # A string prefix is not evidence of an independent old anchor.
        if old in new:
            is_installed = n_new == 1
            is_baseline = n_new == 0 and n_old == 1
        else:
            is_installed = n_new == 1 and n_old == 0
            is_baseline = n_old == 1 and n_new == 0
        if mode in ("check", "apply"):
            if not is_baseline:
                raise SystemExit(
                    f"STOP: unexpected or previously patched source: {path}")
            if mode == "apply":
                changed[path] = source.replace(old, new, 1)
        else:
            if not (is_installed or is_baseline):
                raise SystemExit(f"STOP: cannot safely restore {path}")
            if is_installed:
                changed[path] = source.replace(new, old, 1)
    # Catch structural drift that could redirect other destinations.
    world = changed[WORLD] if mode == "apply" else original[WORLD]
    if "CONTACT_LAST_ACTOR = 65" not in world:
        raise SystemExit("STOP: the contact scan boundary changed")
    if world.count("ACTOR_TO_KALAY_TUNNEL_ENTRANCE + 4") != 1:
        raise SystemExit("STOP: the three unused signpost slots changed")
    if mode == "apply":
        if changed[WORLD].count("WORLD_MAP_TO_ASTER_TEST") != 2:
            raise SystemExit("STOP: failed to add exactly one Aster contact and exit")
    return original, changed

def write_with_rollback(original, changed):
    written = []
    try:
        for path, old_content in original.items():
            if changed[path] != old_content:
                path.write_text(changed[path], encoding="utf-8")
                written.append(path)
    except OSError:
        for path in reversed(written):
            try:
                path.write_text(original[path], encoding="utf-8")
            except OSError:
                print(f"WARNING: source restore failed for {path}. "
                      "Do not reuse this worktree.")
        raise

def main():
    parser = argparse.ArgumentParser()
    opts = parser.add_mutually_exclusive_group(required=True)
    opts.add_argument("--check", action="store_true")
    opts.add_argument("--apply", action="store_true")
    opts.add_argument("--restore", action="store_true")
    args = parser.parse_args()
    mode = "check" if args.check else ("apply" if args.apply else "restore")
    original, changed = prepare(mode)
    if mode == "check":
        print("PASS: both directions of the optional Aster probe are inactive")
        print("Unused signpost, exit kind 115 and entrance 98 are reserved for local QA")
        return
    write_with_rollback(original, changed)
    if mode == "apply":
        print("APPLIED temporary Aster world icon using unused signpost actor slot")
        print("World icon contact -> Aster default entrance -> south gate")
        print("Aster south gate -> unused world entrance 98 at (5696,1504)")
        print("ONLY for disposable emulator testing; terrain and story NOT verified")
    else:
        print("RESTORED unchanged world actors, contact, exit table, "
              "Aster return and world entry 98")

if __name__ == "__main__":
    main()
