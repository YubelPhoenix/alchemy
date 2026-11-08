#!/usr/bin/env python3
"""Free local-only Aster V14 preflight. Read-only; never runs GitHub Actions.

Run in a local, disposable checkout:
    python3 tools/aster_v14_preflight.py

A successful preflight is NOT a ROM build or an emulator pass.
"""
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
TOOLS=ROOT/"tools"
EXPECTED_BRANCH="experiment/aster-v14-native-map-staging"
CHECKS=(
    ("Reproducible 3-layer map", ("aster_v14_native_map.py", "--check")),
    ("V14 map and scene collision", ("check_aster_v14.py",)),
    ("Dedicated native Aster overworld icon", ("check_aster_world_icon.py",)),
    ("Provisional overworld icon spacing", ("aster_overworld_site_audit.py",)),
    ("Clean reversible world-map route probe", ("aster_world_route_probe.py", "--check")),
    ("Two-way world contact dry-run and source restore", ("check_aster_world_route_staging.py",)),
    ("Combined dialogue, resource and stage source audit", ("check_aster.py",)),
    ("Development shortcut absent from tracked source", ("aster_dev_entry.py", "--check")),
)

def main():
    git=ROOT/".git"
    if git.exists():
        result=subprocess.run(
            ["git", "branch", "--show-current"],cwd=ROOT,
            text=True,capture_output=True,check=False)
        branch=result.stdout.strip()
        if result.returncode!=0 or branch!=EXPECTED_BRANCH:
            raise SystemExit(
                f"Refusing preflight on branch {branch!r}; expected "
                f"{EXPECTED_BRANCH!r}. No files changed.")
        status=subprocess.run(
            ["git", "status", "--porcelain", "--",
             "games/tbs/src/map/map_180/map.txt",
             "games/tbs/src/scene/aster.c",
             "tools/aster_v14_native_snapshot.json"],
            cwd=ROOT,text=True,capture_output=True,check=False)
        if status.returncode!=0 or status.stdout.strip():
            raise SystemExit("Source files have uncommitted edits; preserve "
                             "them and inspect diff before proceeding.")
    else:
        print("NOTE: not a Git checkout; checking local source files only.")
    for title,cmd in CHECKS:
        print(f"\n== {title} ==",flush=True)
        path=TOOLS/cmd[0]
        if not path.exists():
            raise SystemExit(f"Missing expected checker: {path}")
        result=subprocess.run(
            [sys.executable,str(path),*cmd[1:]],
            cwd=ROOT,check=False)
        if result.returncode!=0:
            raise SystemExit(
                f"STOP: '{title}' failed (exit={result.returncode}). "
                "Do not start a ROM build or merge.")
    print("\nPASS V14 read-only source preflight.")
    print("NO GitHub workflows or remote builds were used.")
    print("NOT RELEASE READY: native shores/cliffs, two new building facades,")
    print("interiors, reciprocal overworld contact and emulator QA remain.")
    print("In a disposable checkout, use INSTALL.md for a LOCAL ROM build.")
    print("Save files and other Ashfall branches were not modified.")

if __name__=="__main__":
    main()
