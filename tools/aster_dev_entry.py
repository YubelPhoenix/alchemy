#!/usr/bin/env python3
"""Aster opt-in *development only* field-entry shortcut.

The production source and normal Aster ROM builds are NOT modified unless
--apply is explicitly used in a disposable checkout. For a manual smoke test
from a loaded field, hold B+L+R while pressing Start to visit Aster scene201.
The game remains ordinary in all unmodified builds. Requires a compiled
Aster map/overlay and does not supply a release-quality world-map entrance.

Usage:
  python3 tools/aster_dev_entry.py --check    # non-mutating, CI-safe
  python3 tools/aster_dev_entry.py --apply    # deliberate local test patch
  python3 tools/aster_dev_entry.py --restore  # remove ONLY our exact patch
  make tbs-en                                  # after --apply

Never commit the patched field source to a production branch.
"""
import argparse
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/"games/tbs/src/overworld/overworld/scene_manager.c"
SCENES=ROOT/"games/tbs/src/field/scenes.s"

EXISTING="""          if (gDebugMode != 0 && (gKeysHeld & KEY_B) != 0) {
            DebugMapSelect_RunFar();
          }"""
DEVELOPMENT="""          // ASTER_DEV_ONLY_BEGIN -- local test checkout, not release source.
          // Press Start while holding B+L+R to enter SceneId_Aster (201).
          // Avoid the unextended debug selector (its rows stop at 200).
          if ((gKeysHeld & (KEY_B | KEY_L | KEY_R)) ==
              (KEY_B | KEY_L | KEY_R)) {
            Event_SetDestinationFar(201, 0);
          } else if (gDebugMode != 0 && (gKeysHeld & KEY_B) != 0) {
            DebugMapSelect_RunFar();
          }
          // ASTER_DEV_ONLY_END"""

def check_scene():
    # This explicit count is deliberately strict. If the scene table grows,
    # recalculate the destination instead of silently warping to wrong place.
    rows=[l for l in SCENES.read_text(encoding="utf-8").splitlines()
          if l.lstrip().startswith("scene ")]
    if len(rows)!=202 or not rows[201].strip().startswith("scene Aster,"):
        raise SystemExit("Aster is no longer scene 201; test route is unsafe.")

def main():
    ap=argparse.ArgumentParser()
    mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check",action="store_true")
    mode.add_argument("--apply",action="store_true")
    mode.add_argument("--restore",action="store_true")
    args=ap.parse_args()
    check_scene()
    data=TARGET.read_text(encoding="utf-8")
    current=data.count(EXISTING)
    active=data.count("ASTER_DEV_ONLY_BEGIN")
    if args.check:
        if active:
            raise SystemExit("Development entry shortcut is in tracked source!"
                             " Restore it before committing.")
        if current != 1:
            raise SystemExit(f"Expected one field debug-menu branch, got {current}")
        print("PASS Aster dev-only entry: scene201 + safe opt-in source patch")
        return
    if args.apply:
        if active:
            raise SystemExit("Development shortcut already applied; no change.")
        if current != 1:
            raise SystemExit("Cannot identify unique safe field-menu branch")
        TARGET.write_text(data.replace(EXISTING,DEVELOPMENT,1),
                          encoding="utf-8")
        print("Aster test shortcut installed in local checkout ONLY:")
        print("  Start + B + L + R on a field -> Aster scene201 entrance0")
        print("  DO NOT commit modified scene_manager.c into release branch.")
        return
    if args.restore:
        if data.count(DEVELOPMENT)!=1:
            raise SystemExit("Unexpected edited source; refusing unsafe restore")
        TARGET.write_text(data.replace(DEVELOPMENT,EXISTING,1),
                          encoding="utf-8")
        print("Restored original field-menu source; no debug shortcut remains.")

if __name__=="__main__":
    main()
