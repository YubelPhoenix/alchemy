#!/usr/bin/env python3
"""Non-destructive Aster lived-in landscaping study, Golden Sun native only.

Copies small complete three-layer meadow regions from ORIGINAL Vale Map003.
This is a visual test, not a new game prop, playable garden or approved map.
The source fields below can only become live GARDENS after visual review.
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
    ("east_cottage", 45,37,12,46,3,3),
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
                assert town.LAYOUT[y][x]==".", (name,x,y,town.LAYOUT[y][x])
                assert (x,y) not in town.native_road_tiles(),(name,x,y,"road")
                assert (x,y) not in events and (x,y) not in covered
                covered.add((x,y))
                # Copy the picture, but not Vale's collision and event codes.
                rows[y][x]=native[sy+yy][sx+xx].split(":")[0]
                rows[y][x+64]=native[sy+yy][sx+xx+30]
                rows[y+64][x]=native[sy+yy][sx+xx+60]
    vis.load_map=lambda:rows
    vis.make(OUT,LABELLED)
    print("Source-only lived-in Aster flower study, 4 native patches.")
    print("Original Map180 unchanged; verify visual before accepting crop.")

if __name__=="__main__":
    study()
