#!/usr/bin/env python3
"""Native Golden Sun Aster domestic-activity comparisons; gameplay unchanged.

Aster's ordinary inhabited half gets small jars, supplies and hand-sized
fences cropped from Vale Map003. Northern sealed/duplicate houses deliberately
lack these lived-in details. DO NOT import tiles or palettes from other RPGs.
"""
from pathlib import Path
import aster_layout as town
import aster_visual_preview as vis

ROOT=Path(__file__).resolve().parents[1]
NATIVE=town.load_vale()
ORIGINAL=vis.load_map()

# name, new location (x,y), original Vale source (x,y).
# Original Vale one-cell jar and wood supply are COMPLETE upper-layer props.
SUPPLIES=(
  ("west_jar",18,33,17,5),
  ("east_crate",47,33,17,6),
  ("shop_crate",18,52,17,6),
  ("inn_jar",39,55,17,5),
)
# Fencing uses original Vale's lower native wooden palisade (source y54).
FENCES=(
  ("shop_yard",17,47,12,54,4),
  ("inn_yard",37,49,12,54,4),
)
def render(mode):
    grid=[row[:] for row in ORIGINAL]
    event={(x,y) for _,x,y,_ in town.INTERACTIONS}
    actor=set(town.ACTORS)
    used=set()
    def place(name,x,y,sx,sy):
        assert 1<=x<63 and 1<=y<63
        assert town.LAYOUT[y][x]==".",(name,x,y,town.LAYOUT[y][x])
        assert (x,y) not in event|actor|used
        assert (grid[y][x],grid[y][x+64],grid[y+64][x])==(
            "ba","15","15"),(name,x,y,"source not empty")
        used.add((x,y))
        grid[y][x]="ba:ff"  # small barrel/crate/fence is physically solid
        grid[y][x+64]=NATIVE[sy][sx+30]
        grid[y+64][x]=NATIVE[sy][sx+60]
    for item in SUPPLIES:place(*item)
    if mode=="yards":
        for name,x,y,sx,sy,w in FENCES:
            for dx in range(w):
                place(name,x+dx,y,sx+dx,sy)
    elif mode!="supplies":raise ValueError(mode)
    assert all(grid[y][x]=="ba:ff" for x,y in used)
    assert all(grid[y][x]==ORIGINAL[y][x] for x,y in event)
    vis.load_map=lambda:grid
    vis.make(ROOT/f"tools/aster_domestic_{mode}.png",
             ROOT/f"tools/aster_domestic_{mode}_labels.png")
    print("Aster domestic prop trial",mode,":",len(used),"native 16px cells.")

if __name__=="__main__":
    render("supplies")
    render("yards")
