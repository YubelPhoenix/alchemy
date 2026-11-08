#!/usr/bin/env python3
"""Golden Sun Aster — water + connected woodland settlement study.

Use *living* native Vale tree canopy from a continuous forest strip, not
isolated objects pasted onto blank grass; add a genuine water feature on
the eastern edge. The six functional building facades, story-stage count
and placement checks remain in the non-playable blockout.

NO changes to live Map180/scene actors/exit flags. No ruined town, no
imported tilesets, no Psynergy Stone. Tree solidity and water barrier
are design-only until actual engine collision is tested.
"""
from pathlib import Path
import aster_lived_in_blockout as town
import aster_water_feature_study as water

ROOT=Path(__file__).resolve().parents[1]
VALE=town.NATIVE

# Each source is from Vale's *actual contiguous forest* at the south edge.
# We copy only the vegetation upper layers: original base terrain created
# rectangular background cards in previously rejected experiments.
# label, dest x/y, Vale source x/y, width/height (16px cells).
WOODS=(
 ("nw_hillside",1,1,0,50,7,7),
 ("n_copse",21,1,20,50,10,7),
 ("ne_hillside",53,1,20,50,10,7),
 ("west_lanes",1,17,0,50,7,7),
 ("east_lanes",53,16,20,50,10,7),
 ("west_trade_lane",1,43,0,50,7,7),
 ("east_trade_lane",53,44,20,50,10,7),
 ("southwest_belt",1,55,0,50,10,7),
 ("southeast_belt",53,55,20,50,10,7),
)
# At the edges of the true Vale forest we use complete 4x5 tree silhouettes
# to soften transitions into the residential streets. Keep trees INSIDE
# native grass only, away from travel routes, events and working yards.
EDGE_TREES=(
 ("northwest_edge",9,3,17,46),
 ("northeast_edge",49,5,4,13),
 ("west_lower",9,49,4,13),
 ("east_lower",49,50,17,46),
 ("west_wood_outcrop",9,18,17,46),
 ("east_wood_outcrop",49,18,4,13),
)
def main():
    original=town.empty_map
    pond=water.source_water()
    def village_ground():
        rows,use=pond()
        total=0
        for name,tx,ty,sx,sy,w,h in WOODS:
            assert 1<=tx and tx+w<=63 and 1<=ty and ty+h<=63
            assert 0<=sx and sx+w<=30 and 0<=sy and sy+h<=57
            for dy in range(h):
                for dx in range(w):
                    x,y=tx+dx,ty+dy
                    mid=VALE[sy+dy][sx+dx+30]
                    top=VALE[sy+dy][sx+dx+60]
                    # Preserve natural silhouette; do not paint a rectangle
                    # of forest background or transparent ground as solid.
                    if mid.split(":")[0]=="15" and top.split(":")[0]=="15":
                        continue
                    if use[y][x]!=".":
                        continue
                    use[y][x]="T"
                    rows[y][x]="ba:ff"
                    rows[y][x+64]=mid
                    rows[y+64][x]=top
                    total+=1
        print("Native Vale forest-overlay cells:",total)
        return rows,use
    town.empty_map=village_ground
    town.NORMAL=ROOT/"tools/aster_water_woodland.png"
    town.LABELS=ROOT/"tools/aster_water_woodland_labels.png"
    town.FOCUS=ROOT/"tools/aster_water_woodland_focus.png"
    try:
        town.main()
    finally:
        town.empty_map=original
    print("Source-rendered village ecology study; game map unchanged.")

if __name__=="__main__":main()
