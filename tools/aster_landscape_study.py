#!/usr/bin/env python3
"""Aster native meadow landscaping verification render, Golden Sun only.

Copies small complete three-layer meadow regions from ORIGINAL Vale Map003.
This checks the four staged garden crops in the experimental source map.
The source is still experimental until an actual emulator playtest.
"""
from pathlib import Path
import aster_layout as town
import aster_visual_preview as vis

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"tools/aster_landscape_study.png"
LABELLED=ROOT/"tools/aster_landscape_study_labels.png"

# name, destination x/y, original Vale source x/y, width/height.
# From Vale's unbuilt flower meadow *south* of the fountain.
# Four occupied addresses get modest flower plots; the two
# deliberately unsettling northern houses remain sparse.
FLOWER_TESTS=(
    ("west_cottage", 17,34,10,47,3,3),
    ("east_cottage", 45,36,12,46,3,3),
    ("shop_herbs", 17,50,9,46,3,3),
    ("inn_flowers", 38,53,14,47,3,3),
)

def study():
    native=town.load_vale()
    rows=[r.split() for r in town.source().splitlines()[1:]]
    events={(x,y) for _,x,y,_ in town.INTERACTIONS}
    covered=set()
    for name,dx,dy,sx,sy,w,h in FLOWER_TESTS:
        assert 1<=dx and dx+w<63 and 1<=dy and dy+h<63
        assert 1<=sx and sx+w<30 and 1<=sy and sy+h<57
        for yy in range(h):
            for xx in range(w):
                x,y=dx+xx,dy+yy
                assert town.LAYOUT[y][x]=="f", (name,x,y,town.LAYOUT[y][x])
                assert (x,y) not in town.native_road_tiles(),(name,x,y,"road")
                assert (x,y) not in events and (x,y) not in covered
                covered.add((x,y))
                # Assert copied original three-layer pictures, not source behavior.
                assert rows[y][x]==native[sy+yy][sx+xx].split(":")[0]
                assert rows[y][x+64]==native[sy+yy][sx+xx+30]
                assert rows[y+64][x]==native[sy+yy][sx+xx+60]
    vis.load_map=lambda:rows
    vis.make(OUT,LABELLED)
    print("Experimental Aster map verified: 4 original Golden Sun flower plots.")
    print("No map modified by this QA renderer; compare output before approval.")

if __name__=="__main__":
    study()
