#!/usr/bin/env python3
"""Reversible, LOCAL-ONLY Aster overworld path probe.

The original world-map entrance slot 98 is unused in the audited source.
For a disposable ROM smoke test only:
  --check    Confirm no probe patch is installed (read-only).
  --apply    Change Aster's SOUTH exit to world entrance 98 and put that
             entrance at tentative Aster site (x=5696,z=1504).
  --restore  Restore the original world-map entrance and Aster exit.

This deliberately avoids WORLD_MAP_FROM_DEBUG because that entry disables
encounters and overworld contact events, hiding route defects. The probe
does not create or activate an overworld icon: it tests the return path and
walking toward Vault in an emulator, not entry from the overworld.
Do not run --apply outside a disposable experimental worktree.
"""
from pathlib import Path
import argparse

ROOT=Path(__file__).resolve().parents[1]
WORLD=ROOT/"games/tbs/src/scene/world_map.c"
ASTER=ROOT/"games/tbs/src/scene/aster.c"
CHANGES=(
  (WORLD,
   "    {98, CONDITION_ALWAYS, 4248, 0, 2424, FACING_SOUTH, 0, -1, -1, -1, -1, 0},",
   "    {98, CONDITION_ALWAYS, 5696, 0, 1504, FACING_SOUTH, 0, -1, -1, -1, -1, 0},"),
  (ASTER,
   "SCENE_EXIT(ASTER_TO_WORLD_MAP, WorldMap, WORLD_MAP_FROM_VAULT_SOUTH)",
   "SCENE_EXIT(ASTER_TO_WORLD_MAP, WorldMap, 98)"),
)

def main():
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check",action="store_true")
    group.add_argument("--apply",action="store_true")
    group.add_argument("--restore",action="store_true")
    args=parser.parse_args()
    rows=[]
    for path,old,new in CHANGES:
        original=path.read_text(encoding="utf-8")
        n_old=original.count(old)
        n_new=original.count(new)
        if args.check or args.apply:
            if n_old!=1 or n_new:
                raise SystemExit(f"Refusing: {path} changed from baseline")
            rows.append((path,original,original.replace(old,new,1)))
        else:
            if (n_old,n_new) not in ((1,0),(0,1)):
                raise SystemExit(f"Refusing to restore ambiguous edits: {path}")
            rows.append((path,original,
                         original.replace(new,old,1) if n_new else original))
    if args.check:
        print("PASS world-map route probe is not installed")
        return
    for path,original,updated in rows:
        if original!=updated:
            path.write_text(updated,encoding="utf-8")
    if args.apply:
        print("APPLIED temporary route probe: Aster -> unused entrance 98")
        print("Test arrival at (5696,1504), walk to Vault and back in emulator.")
        print("NOT verified safe; keep using a disposable save and worktree.")
    else:
        print("RESTORED original entrance 98 and Vault placeholder Aster exit")

if __name__=="__main__":
    main()
