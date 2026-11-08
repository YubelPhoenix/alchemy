#!/usr/bin/env python3
"""Dry-run test of Aster's reversible two-way WORLD MAP staging patch.

All edits are rendered into memory. This test DOES NOT WRITE to source files,
build a ROM, start a GitHub workflow, or assert that terrain is walkable.
"""
import re
from pathlib import Path
import aster_world_route_probe as probe

ROOT=Path(__file__).resolve().parents[1]
SPRITES=ROOT/"games/tbs/include/sprite_ids.h"
SCENE_TABLES=ROOT/"games/tbs/include/scene_tables.h"

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)

def actor_slots(text):
    head="struct ActorTemplate gWorldMapActorTemplates[] = {"
    begin=text.index(head)+len(head)
    end=text.index("{ SCENE_TABLE_END }",begin)
    chunks=re.findall(r"\{[^{}]*\}",text[begin:end],flags=re.S)
    return [re.sub(r"\s+"," ",part).strip() for part in chunks]

def main():
    # Probe still uninstalled in the committed branch.
    original,checked=probe.prepare("check")
    need(original==checked,"Read-only check unexpectedly changed source")
    original,staged=probe.prepare("apply")
    world_before=original[probe.WORLD]
    world_after=staged[probe.WORLD]
    aster_before=original[probe.ASTER]
    aster_after=staged[probe.ASTER]
    exits_before=original[probe.EXITS]
    exits_after=staged[probe.EXITS]
    previous=actor_slots(world_before)
    current=actor_slots(world_after)
    need(len(previous)==len(current)==48,
         "World actor registration count changed; would shift story IDs")
    need("SPRITE_SIGNPOST" in previous[39] and "0, 0, 0" in previous[39],
         "Unused first signpost actor (slot 39) was already repurposed")
    need("SPRITE_WORLD_MAP_ASTER" in current[39],
         "Aster icon not in unused first signpost slot")
    need("PIXELS(5696)" in current[39] and "PIXELS(1504)" in current[39],
         "Proposed icon coordinates not installed")
    need(all(a==b for i,(a,b) in enumerate(zip(previous,current)) if i!=39),
         "Another world actor was changed")
    need("ACTOR_FIRST_PLACED = 8" in
         SCENE_TABLES.read_text(encoding="utf-8"),
         "First placed actor index has changed")
    need("CONTACT_LAST_ACTOR = 65" in world_before,
         "World contact scan bound changed")
    actor_id=8+39
    need(actor_id<=65,"Unused signpost actor outside world-map contact scan")
    need(world_before.count("ACTOR_TO_KOLIMA_BRIDGE = "
                            "ACTOR_TO_KALAY_TUNNEL_ENTRANCE + 4")==1,
         "Unused signpost relation changed")
    need("SPRITE_WORLD_MAP_ASTER = 0x1f9" in
         SPRITES.read_text(encoding="utf-8"),
         "Dedicated registered Aster native icon missing")
    need(world_after.count("WORLD_MAP_TO_ASTER_TEST")==2,
         "Missing or duplicate temporary Aster contact/exit")
    need("SCENE_EXIT(WORLD_MAP_TO_ASTER_TEST, Aster, ENTRANCE_DEFAULT)" in
         world_after,"World -> Aster default entrance not wired")
    need("STEP_TRIGGER_AREA(ACTOR_TO_KALAY_TUNNEL_ENTRANCE + 1)" in
         world_after,"Contact trigger not tied to unused actor")
    need("SCENE_EXIT(ASTER_TO_WORLD_MAP, WorldMap, 98)" in aster_after,
         "Aster -> unused world entrance 98 not wired")
    need("{98, CONDITION_ALWAYS, 5696, 0, 1504" in world_after,
         "World return coordinates missing")
    need("WORLD_MAP_TO_ASTER_TEST = 115" in exits_after,
         "Unused exit kind was not declared")
    need("WORLD_MAP_TO_ASTER_TEST" not in exits_before,
         "An exit already uses test kind 115")
    need("WORLD_MAP_TO_ASTER_TEST" not in world_before,
         "Aster contact must not be permanently active yet")
    need("WORLD_MAP_FROM_VAULT_SOUTH" in aster_before,
         "Original experimental safe return changed")
    # Simulate reverting each staged substitution. Restore must reproduce
    # every original file byte-for-byte, even for the prefix-containing trigger.
    restored={path:value for path,value in staged.items()}
    for path,old,new in reversed(probe.EDITS):
        need(restored[path].count(new)==1,
             f"Cannot identify unique temporary edit in {path}")
        restored[path]=restored[path].replace(new,old,1)
    need(restored==original,
         "Dry-run restore does not reproduce exact original source files")
    print("PASS dry-run two-way Aster icon contact + reciprocal south gate")
    print(f"PASS 48 original world actor slots unchanged; Aster uses slot 39/ID {actor_id}")
    print("PASS new contact within actor scan limit 65 and unused exit kind 115")
    print("PASS 6 reversible edits across 3 files restore exactly")
    print("NOT VERIFIED: actual overworld ground/route, renderer or ROM compile")

if __name__=="__main__":
    main()
