#!/usr/bin/env python3
"""Non-destructive Aster woodland-edge visual study using only native Vale art.

Two densities, without moving buildings, events, NPCs, gardens or roads.
This tests *complete* known-good three-layer Golden Sun tree stamps.
It does NOT modify Map180, collision or the playable ROM.
"""
from pathlib import Path
import aster_layout as town
import aster_visual_preview as vis

ROOT = Path(__file__).resolve().parents[1]
STAMP=(24,45,4,5)  # complete Vale blue-and-autumn foliage, already verified

# name, destination map x, destination map y
OUTER=(
    ("west_north_edge",3,16),
    ("east_north_edge",57,16),
    ("west_residential_edge",3,36),
    ("east_residential_edge",57,36),
    ("west_market_edge",2,54),
    ("east_market_edge",57,54),
)
RIDGE=(
    ("north_backyard_w",26,3),
    ("north_backyard_e",35,2),
)

def render(name,extra):
    native=town.load_vale()
    rows=[line.split() for line in town.source().splitlines()[1:]]
    original=[row[:] for row in rows]
    events={(x,y) for _,x,y,_ in town.INTERACTIONS}
    protected=set(events)|set(town.ACTORS)|{
        town.MEMORIAL,town.WELL,town.START,town.EXIT}
    coverage=set()
    for label,dx,dy in OUTER+extra:
        sx,sy,w,h=STAMP
        for yy in range(h):
            for xx in range(w):
                x,y=dx+xx,dy+yy
                assert 1<=x<63 and 1<=y<63,(label,x,y)
                assert town.LAYOUT[y][x]==".",(label,x,y,town.LAYOUT[y][x])
                assert (x,y) not in town.native_road_tiles()
                assert (x,y) not in protected|coverage,(label,x,y)
                assert (rows[y][x],rows[y][x+64],rows[y+64][x])==(
                    "ba","15","15"),(label,x,y,"underlying art not empty")
                coverage.add((x,y))
                # Copy ALL three source-art planes. Keep foreign-game art out.
                # This preview is not the final gameplay collision map.
                rows[y][x]=native[sy+yy][sx+xx].split(":")[0]
                rows[y][x+64]=native[sy+yy][sx+xx+30]
                rows[y+64][x]=native[sy+yy][sx+xx+60]
    for x,y in protected:
        assert all(rows[gy][gx]==original[gy][gx] for gx,gy in (
            (x,y),(x+64,y),(x,y+64))),(x,y,"protected tile changed")
    vis.load_map=lambda:rows
    vis.make(ROOT/f"tools/aster_perimeter_{name}.png",
             ROOT/f"tools/aster_perimeter_{name}_labels.png")
    print(name,len(OUTER)+len(extra),"complete original Vale tree stands")

if __name__=="__main__":
    render("sparse",())
    render("dense",RIDGE)
