#!/usr/bin/env python3
"""Second Aster life-first blockout: a SETTLEMENT ENCLOSED BY TERRAIN.

All graphics are actual Golden Sun Vale set_02 layers. Build a *new*
topographic shell behind the clustered Aster study buildings and streets:
a contiguous northern ridge, two flank escarpments, southern wooded edges.
Not approved gameplay art: patch terrain is provisionally nonwalkable.
Map180, script triggers and user game saves remain unchanged.
"""
from pathlib import Path
import aster_lived_in_blockout as study
import aster_visual_preview as vis

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL_EMPTY=study.empty_map

# name, dest x/y, original native Vale source x/y, width, height.
# Whole-source topographic bands, not cropped individual roof/cliff pixels.
# Northern 20x7 cliff is one CONTIGUOUS source strip (Vale x10..29 y22..28).
# The western and eastern ridges help the street feel physically enclosed.
TERRAIN=(
    ("north_cliff_backdrop",17,1,10,22,20,7),
    ("west_old_lane_wall",1,17,0,15,6,7),
    ("west_market_bluff",1,36,0,15,7,7),
    ("east_residential_slope",53,22,20,22,9,7),
    ("north_east_woodland",53,9,20,0,9,5),
    ("southwest_treebelt",1,52,0,50,9,7),
    ("southeast_wooded_slope",53,52,20,50,9,7),
)

def terrain_enclosure():
    grid,used=ORIGINAL_EMPTY()
    vale=study.NATIVE
    registered=set()
    for name,dx,dy,sx,sy,w,h in TERRAIN:
        assert 1<=dx and 1<=dy and dx+w<=63 and dy+h<=63
        assert 0<=sx and sx+w<=30 and 0<=sy and sy+h<=57
        for oy in range(h):
            for ox in range(w):
                x,y=dx+ox,dy+oy
                assert used[y][x]==".",(name,x,y,used[y][x])
                assert (x,y) not in registered,(name,x,y,"overlap")
                registered.add((x,y))
                used[y][x]="R"
                # Native original 3-layer pixels only; gameplay movement
                # across sloping source transitions is NOT tested.
                grid[y][x]=vale[sy+oy][sx+ox].split(":")[0]+":ff"
                grid[y][x+64]=vale[sy+oy][sx+ox+30]
                grid[y+64][x]=vale[sy+oy][sx+ox+60]
    print("Original Golden Sun ridge/forest cells:",len(registered))
    return grid,used

def main():
    study.empty_map=terrain_enclosure
    study.NORMAL=ROOT/"tools/aster_lived_in_terrain.png"
    study.LABELS=ROOT/"tools/aster_lived_in_terrain_labels.png"
    study.FOCUS=ROOT/"tools/aster_lived_in_terrain_focus.png"
    study.main()
    print("Topographic Aster prototype only. LIVE Map180 unchanged.")
    print("No second ruined map and no borrowed waterfall/pond/spring.")

if __name__=="__main__":
    main()
