#!/usr/bin/env python3
"""Unwired RUIN visual study, made entirely from original Golden Sun Vale art.

Uses current Aster Map180 and its exact same 64x64 geography. Only changes
scenery on background layers. Not a separate playable map or scene state.
Do not call this an emulator screenshot or a finished ruined version.
"""
from pathlib import Path
import aster_layout as town
import aster_visual_preview as vis

ROOT=Path(__file__).resolve().parents[1]
native=town.load_vale()
unchanged=vis.load_map()
ruin=[row[:] for row in unchanged]

# Existing Vale multicolor shrubs/trees creep over walls/roofs from outside.
# They are deliberately placed behind each building's street-facing approach,
# so the *visible* door and the roads remain recognizable in this study.
VINES=(
    ("sealed_back_wall",9, 6,24,45,4,5),
    ("inn_back_wall",51,7,24,45,4,5),
    ("west_home_rear", 7,25,24,45,4,5),
    ("east_home_rear",54,25,24,45,4,5),
    ("shop_back_wall",10,46,24,45,4,5),
    ("duplicate_roof",55,46,24,45,4,5),
)

def decorate(name,dx,dy,sx,sy,w,h):
    assert 0<=dx and dx+w<=64 and 0<=dy and dy+h<=64,name
    # Copy original Vale 3-layer art in the position of roof overgrowth.
    # Leave underlying *gameplay* ground/behavior/shape intact.
    for yy in range(h):
        for xx in range(w):
            ruin[dy+yy][dx+xx+64]=native[sy+yy][sx+xx+30]
            ruin[dy+yy+64][dx+xx]=native[sy+yy][sx+xx+60]

for entry in VINES:
    decorate(*entry)

# No changes to movement/scene triggers at any point in this trial.
for name,x,y,behavior in town.INTERACTIONS:
    assert unchanged[y][x]==ruin[y][x]==behavior,(name,x,y)
for x,y in (town.START,town.EXIT,town.WELL,town.MEMORIAL):
    assert unchanged[y][x]==ruin[y][x]
# All buildings remain at the same addresses. This is intentional: an
# alternate timeline should not suddenly move the entire village.
for name,dx,dy,sx,sy,w,h,ch in town.BUILDINGS:
    assert all(town.LAYOUT[dy+yy][dx+xx]==ch
               for yy in range(h) for xx in range(w)),name

vis.load_map=lambda:ruin
vis.make(ROOT/"tools/aster_ruin_visual_study.png",
         ROOT/"tools/aster_ruin_visual_study_labels.png")
print("Aster ruin overgrowth study only; no ROM-state changes.")
