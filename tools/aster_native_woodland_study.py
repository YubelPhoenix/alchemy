#!/usr/bin/env python3
"""Aster woodland diversity trial, native Golden Sun picture layers only.

Replace six repeated tree-stamp pictures in memory with hand-inspected intact
native Vale upper-layer crops. Try four or eight *additional* tree clusters.
The GBA source map and collision are unchanged: inspect before acceptance.
"""
from pathlib import Path
import aster_layout as town
import aster_visual_preview as vis

ROOT=Path(__file__).resolve().parents[1]
# Complete silhouettes chosen from Aster's Vale foliage refinement atlas.
# x,y,w,h in original Vale Map003; no roofs, water or cliff layers copied.
BLUE=(17,46,4,5)
RED=(4,13,4,5)

EXISTING_SOURCE={
 "north_woods_w":BLUE,
 "north_woods_e":RED,
 "residential_w":BLUE,
 "residential_e":RED,
 "market_tree_w":BLUE,
 "market_tree_e":RED,
}
OUTER=(
 ("north_edge_w",3,16,RED),
 ("north_edge_e",57,16,BLUE),
 ("market_edge_w",2,54,BLUE),
 ("market_edge_e",57,54,RED),
)
EXTRA=(
 ("residential_edge_w",3,36,BLUE),
 ("residential_edge_e",57,36,RED),
 ("north_backyard_w",26,3,BLUE),
 ("north_backyard_e",35,2,RED),
)

def study(name,more):
    native=town.load_vale()
    rows=[s.split() for s in town.source().splitlines()[1:]]
    untouched=[r[:] for r in rows]
    protected=set(town.ACTORS)|set((x,y) for _,x,y,_ in town.INTERACTIONS)
    protected.update((town.WELL,town.MEMORIAL,town.START,town.EXIT))
    placed=set()
    def apply(label,dx,dy,src,original_tree):
        sx,sy,w,h=src
        assert w==4 and h==5,(label,w,h)
        for yy in range(h):
            for xx in range(w):
                x,y=dx+xx,dy+yy
                assert (x,y) not in placed|protected,(label,x,y)
                assert town.LAYOUT[y][x]==("T" if original_tree else "."),(
                    label,x,y,town.LAYOUT[y][x])
                if not original_tree:
                    assert (x,y) not in town.native_road_tiles(),(label,x,y)
                placed.add((x,y))
                # Grass stays native Aster grass:ff for solid tree cells.
                # Original Vale tree CANOPY only; do not import accidental
                # blue/cliff-colored ground from the source village.
                rows[y][x]="ba:ff"
                rows[y][x+64]=native[sy+yy][sx+xx+30]
                rows[y+64][x]=native[sy+yy][sx+xx+60]
    for label,dx,dy,_,_,w,h in town.SCENERY:
        assert (w,h)==(4,5)
        apply(label,dx,dy,EXISTING_SOURCE[label],True)
    for label,dx,dy,source in OUTER+more:
        apply(label,dx,dy,source,False)
    for x,y in protected:
        assert all(rows[yy][xx]==untouched[yy][xx]
            for xx,yy in ((x,y),(x+64,y),(x,y+64))),(x,y)
    vis.load_map=lambda:rows
    vis.make(ROOT/f"tools/aster_woodland_{name}.png",
             ROOT/f"tools/aster_woodland_{name}_labels.png")
    print("Aster native woodland test",name,"new group count:",len(OUTER+more),
          "existing trees replaced in preview:",len(town.SCENERY))

if __name__=="__main__":
    study("sparse",())
    study("full",EXTRA)
