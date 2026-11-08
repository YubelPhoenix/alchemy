#!/usr/bin/env python3
"""Fail-closed, read-only Ashfall/Aster branch isolation and regression gate.

No ROM builds, GitHub network/API calls, uploads, checkout mutation or Actions.
Requires a full Git checkout of the isolated first-playtest branch with the
approved Ashfall base commit available in local history.
"""
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_BRANCH = "experiment/ashfall-aster-first-playtest"
APPROVED_BASE = "62dd7b5331a7e23a12df0090e9e823a3aed8f425"

# Exact baseline-relative file inventory: all changes must be Aster additions
# or the eleven deliberately reconciled Ashfall integration registrations.
# Any new path or increased removal/addition counts needs explicit review.
ADDED = set([
  "docs/aster-ashfall-first-playtest-status.md",
  "docs/aster-overworld-placement-proposal.md",
  "docs/aster-v14-selective-integration-plan.md",
  "docs/aster-v14-world-probe-qa.md",
  "games/tbs/src/graphics/sprite/spr_505.png",
  "games/tbs/src/graphics/sprite/spr_505.tsv",
  "games/tbs/src/graphics/sprite/spr_506.png",
  "games/tbs/src/graphics/sprite/spr_506.tsv",
  "games/tbs/src/graphics/sprite/spr_507.png",
  "games/tbs/src/graphics/sprite/spr_507.tsv",
  "games/tbs/src/graphics/sprite/spr_508.png",
  "games/tbs/src/graphics/sprite/spr_508.tsv",
  "games/tbs/src/graphics/sprite/spr_509.png",
  "games/tbs/src/graphics/sprite/spr_509.tsv",
  "games/tbs/src/map/map_180/map.s",
  "games/tbs/src/map/map_180/map.txt",
  "games/tbs/src/scene/aster.c",
  "games/tbs/src/scene/entry/aster.s",
  "games/tbs/src/scene/import/aster.s",
  "tools/aster_dialogue.tsv",
  "tools/aster_native_boundary_manifest.json",
  "tools/aster_polish_dialogue.py",
  "tools/aster_prepare_messages.py",
  "tools/aster_v14_native_map.py",
  "tools/aster_v14_native_snapshot.json",
  "tools/check_aster_ashfall_integration.py",
  "tools/check_aster_branch_isolation.py",
  "tools/check_aster_overworld_contract.py",
  "tools/check_aster_native_bridge.py",
  "tools/check_aster_native_decor.py",
  "tools/check_aster_native_foliage.py",
  "tools/check_aster_v14.py",
  "tools/check_aster_world_icon.py",
  "tools/prepare_aster_ashfall_dialogue.py"
])
MODIFIED_STATS = {
  "games/tbs/include/scene_exits.h": [
    2,
    0
  ],
  "games/tbs/include/scene_ids.h": [
    2,
    0
  ],
  "games/tbs/include/sprite_ids.h": [
    7,
    0
  ],
  "games/tbs/objects.tsv": [
    5,
    0
  ],
  "games/tbs/src/field/maps.c": [
    3,
    0
  ],
  "games/tbs/src/field/scenes.s": [
    2,
    0
  ],
  "games/tbs/src/graphics/sprite/layout.tsv": [
    5,
    0
  ],
  "games/tbs/src/graphics/sprite/sprites.tsv": [
    5,
    5
  ],
  "games/tbs/src/scene/world_map.c": [
    5,
    3
  ],
  "games/tbs/src/system/resource/directory.s": [
    4,
    1
  ],
  "games/tbs/text/en.po": [
    225,
    0
  ]
}


def stop(reason):
    raise SystemExit("ASTER ISOLATION STOP: " + reason)


def git(*argv):
    result = subprocess.run(
        ["git", *argv], cwd=ROOT, capture_output=True, text=True,
        check=False, timeout=30,
    )
    if result.returncode:
        stop("git " + " ".join(argv) + ": " + result.stderr.strip())
    return result.stdout.strip()


def verify():
    branch = git("branch", "--show-current")
    if branch != EXPECTED_BRANCH:
        stop(f"Wrong checkout branch: {branch!r}; expected {EXPECTED_BRANCH!r}")
    git("merge-base", "--is-ancestor", APPROVED_BASE, "HEAD")
    if git("status", "--porcelain", "--untracked-files=no"):
        stop("Tracked working files are dirty; use a clean checkout for source QA")
    name_status = git("diff", "--no-renames", "--name-status",
                      APPROVED_BASE, "HEAD")
    numstat = git("diff", "--no-renames", "--numstat",
                  APPROVED_BASE, "HEAD")
    statuses = {}
    for line in name_status.splitlines():
        parts = line.split("\t")
        if len(parts) != 2:
            stop("Unexpected diff status: " + line)
        status, path = parts
        if path in statuses:
            stop("Duplicate modified path: " + path)
        statuses[path] = status
    stats = {}
    for line in numstat.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            stop("Unexpected diff numstat: " + line)
        added, removed, path = parts
        if added == "-" or removed == "-":
            # Binary Aster sprite assets have no textual additions/deletions.
            if path not in ADDED:
                stop("Unexpected changed binary file: " + path)
            stats[path] = None
        else:
            stats[path] = (int(added), int(removed))
    if set(statuses) != set(stats):
        stop("Git name-status/numstat disagree on changed paths")
    unknown = set(statuses) - ADDED - set(MODIFIED_STATS)
    missing = (ADDED | set(MODIFIED_STATS)) - set(statuses)
    if unknown:
        stop("Unexpected changes outside Aster integration: " + str(sorted(unknown)))
    if missing:
        stop("Expected Aster integration resources missing: " + str(sorted(missing)))
    for path, status in statuses.items():
        if path in ADDED:
            if status != "A":
                stop(f"New Aster-only file {path} is no longer an addition: {status}")
        else:
            if status != "M" or stats[path] != tuple(MODIFIED_STATS[path]):
                stop(f"Unexpected Ashfall baseline delta for {path}: "
                     f"status={status}, additions/deletions={stats[path]}; "
                     f"expected M {tuple(MODIFIED_STATS[path])}")
    print(f"PASS: {len(statuses)} reviewed Aster-only file deltas; "
          "no unreviewed changes to Ashfall")
    print("PASS: boss AI, balance, non-Aster scenes and workflows remain untouched")
    print("NO ROM compilation, workflow run or artifact creation was performed")


if __name__ == "__main__":
    verify()
