#!/usr/bin/env python3
"""Aster overworld static actor-clearance audit (source-only, no game changes).

The candidate is NOT approved as walkable. This checks only separation
from existing static actor images, not terrain mesh, dynamic story events,
rivers, cliff walls, save state, arrival or actual gameplay.

  python3 tools/aster_overworld_site_audit.py
"""
from pathlib import Path
import math
import re

ROOT=Path(__file__).resolve().parents[1]
WORLD_MAP=ROOT/"games/tbs/src/scene/world_map.c"
SPRITE_IDS=ROOT/"games/tbs/include/sprite_ids.h"
CANDIDATE_X=5696
CANDIDATE_Z=1504
MIN_ICON_SPACING=96  # conservative design screening, not engine collision radius
EXPECTED_NEIGHBORS={"Vale":(5678,1200),"Vault":(5848,1576)}

def require(ok,reason):
    if not ok:
        raise AssertionError(reason)

def find_static_icons(source):
    token="struct ActorTemplate gWorldMapActorTemplates[] = {"
    start=source.find(token)
    require(start>=0,"Missing ordinary world-map actor template")
    end=source.find("\n};",start)
    require(end>start,"Can't bound ordinary actor template")
    body=source[start:end]
    # Each place is a sprite actor; dynamic story actors (Flint, caravan,
    # storms and moving NPCs) are deliberately EXCLUDED from this simple audit.
    entries=[]
    for block in re.findall(r"\{[^{}]*\}",body,re.S):
        if "SPRITE_WORLD_MAP_" not in block:
            continue
        sprite=re.search(r"SPRITE_WORLD_MAP_[A-Z0-9_]+",block)
        coords=re.search(r"PIXELS\((\d+)\),\s*0,\s*PIXELS\((\d+)\)",block)
        if sprite and coords:
            entries.append((sprite.group(),int(coords[1]),int(coords[2])))
    require(len(entries)>=35,"World-map sprite templates unexpectedly changed")
    return entries

def main():
    source=WORLD_MAP.read_text(encoding="utf-8")
    ids=SPRITE_IDS.read_text(encoding="utf-8")
    require(re.search(r"SPRITE_WORLD_MAP_VILLAGE\s*=\s*0x105\b",ids),
            "Original village icon number has changed")
    sites=find_static_icons(source)
    for label,point in EXPECTED_NEIGHBORS.items():
        require(("SPRITE_WORLD_MAP_VILLAGE",*point) in sites,
                f"{label} existing overworld icon moved")
    known=set((x,z) for _,x,z in sites)
    require((CANDIDATE_X,CANDIDATE_Z) not in known,
            "Proposed Aster site coincides with existing actor")
    rows=sorted(((math.hypot(CANDIDATE_X-x,CANDIDATE_Z-z),kind,x,z)
                 for kind,x,z in sites),key=lambda t:t[0])
    closest=rows[0]
    require(closest[0]>=MIN_ICON_SPACING,
            f"Candidate too close to an existing static icon: {closest}")
    print(f"PASS STATIC-ICON CLEARANCE ONLY at x={CANDIDATE_X}, z={CANDIDATE_Z}")
    print(f"Nearest existing icon: {closest[1]} at {closest[2:]} "
          f"({closest[0]:.1f} world pixels away)")
    print(f"Checked {len(sites)} static world-map icon entries.")
    print("NOT CERTIFIED: terrain walkability, cliff/river and bridge topology,")
    print("Flint/Caravan events, dynamic actors, first arrival or exit pairing.")
    print("NEVER register this candidate without emulator route and contact QA.")
    print("World-map icon baseline: SPRITE_WORLD_MAP_VILLAGE = 0x105,")
    print("indexed sprite spr_261.png (32x32); create NEW sprite for Aster.")

if __name__=="__main__":
    main()
