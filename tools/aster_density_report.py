#!/usr/bin/env python3
"""Measure how empty Aster's current layout actually is.

Read-only diagnostic, not proof of visual appeal or emulator correctness.
Used while replacing the sprawling six-house plan with one compact town.
Does NOT read or generate the abandoned ruined-state map.
"""
from collections import Counter
import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LAYOUT=ROOT/"tools/aster_layout.py"

def main():
    spec=importlib.util.spec_from_file_location("aster_layout",LAYOUT)
    town=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(town)
    rows=town.LAYOUT
    assert len(rows)==64 and all(len(row)==64 for row in rows)
    counts=Counter("".join(rows))
    inside=62*62  # exclude the reserved one-cell map boundary
    bare=counts["."]
    occupied=sum(counts[ch] for ch in "XIHSVTMWBF")
    roads=counts["="]
    useful=occupied+roads+counts["f"]
    print("=== Aster single-town spatial baseline (NOT emulator result) ===")
    print(f"Active source windows: 64x64 ({inside} inner cells)")
    print(f"Undifferentiated walkable meadow: {bare} / {inside} "
          f"({100*bare/inside:.1f}%)")
    print(f"Buildings/trees/props/landmarks footprint: {occupied} cells")
    print(f"Planned streets/plaza: {roads} cells")
    print(f"Small planted garden cells: {counts['f']}")
    print(f"Recognizable structures: {len(town.BUILDINGS)}")
    print(f"Town NPCs: {len(town.ACTORS)}")
    print(f"Scene interaction sites: {len(town.INTERACTIONS)}")
    print("Design: reduce the *functional settlement footprint* to roughly")
    print("46x46 cells inside the existing 64x64 native map format.")
    print("Do not falsely solve low density by scattering unrelated props.")
    print("Ruin map is archived and excluded from active release criteria.")

if __name__=="__main__":
    main()
