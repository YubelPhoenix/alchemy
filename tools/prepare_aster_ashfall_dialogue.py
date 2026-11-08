#!/usr/bin/env python3
"""Prepare Aster + Ashfall dialogue ONLY inside a disposable test checkout.

The inherited dark-story rewrite adds MsgDark entries at the end of en.po.
Aster contributes 36 pre-numbered MsgAster entries after vanilla null 10722.
Running the inherited rewrite unmodified would reuse those numeric IDs.
The safe sequence moves the null marker first, then applies dark dialogue,
verifies both namespaces, and polishes Aster's lines. This script changes
only the disposable checkout's .po/TSV; NEVER run against stable branches.

Read-only source validation:
  python3 tools/prepare_aster_ashfall_dialogue.py --check

Intentional one-time test-build preparation (on integration branch only):
  ASTER_DISPOSABLE_BUILD=1 python3 tools/prepare_aster_ashfall_dialogue.py --apply
"""
from pathlib import Path
import os
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BRANCH = "experiment/ashfall-aster-first-playtest"
PO = ROOT / "games/tbs/text/en.po"

def fail(why):
    raise SystemExit("ASTER DIALOGUE STOP: " + why)

def check_source():
    data = PO.read_text(encoding="utf-8")
    ids = re.findall(r'^msgctxt "(MsgAster[^"]+)"\nmsgid "(\d{5})"', data, re.M)
    if len(ids) != 36 or len({x[0] for x in ids}) != 36:
        fail("Expected exactly 36 unique Aster messages")
    if [int(num) for _, num in ids] != list(range(10723, 10759)):
        fail("Aster source IDs must remain 10723..10758")
    if "alchemy-null" not in data:
        fail("Missing original catalogue terminator")
    return data

def run(*args):
    print("Checking", " ".join(args), flush=True)
    result = subprocess.run(
        [sys.executable, "-B", str(ROOT / "tools" / args[0]), *args[1:]],
        cwd=ROOT, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
        check=False)
    if result.returncode:
        fail("Stopped at " + " ".join(args))

def main():
    if sys.argv[1:] == ["--check"]:
        check_source()
        print("PASS: Aster source message IDs 10723..10758 are intact.")
        print("NOT PREPARED: compile only after disposable --apply pipeline.")
        return
    if sys.argv[1:] != ["--apply"]:
        fail("Use --check, or --apply in a disposable integration checkout")
    if os.environ.get("ASTER_DISPOSABLE_BUILD") != "1":
        fail("Refusing to edit en.po without ASTER_DISPOSABLE_BUILD=1")
    current = os.environ.get("GITHUB_REF_NAME")
    if not current:
        current = subprocess.run(
            ["git", "branch", "--show-current"], cwd=ROOT,
            capture_output=True, text=True, check=False).stdout.strip()
    if current != BRANCH:
        fail(f"Refusing branch {current!r}; only {BRANCH!r} is allowed")
    check_source()
    run("aster_prepare_messages.py")
    run("dark_story_rewrite.py")
    run("aster_prepare_messages.py", "--verify")
    run("aster_polish_dialogue.py", "--apply")
    run("aster_polish_dialogue.py", "--check")
    print("PASS: disposable Ashfall and Aster messages prepared.")
    print("NO ROM build, Actions workflow, or file upload launched.")

if __name__ == "__main__":
    main()
