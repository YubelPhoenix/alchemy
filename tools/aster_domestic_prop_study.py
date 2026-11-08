#!/usr/bin/env python3
"""Native Golden Sun Aster domestic details, source-level QA and preview.

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
def audit_and_render():
    """Verify source and real Map180 carry the approved native props."""
    rows=[line.split() for line in town.source().splitlines()[1:]]
    actual=vis.load_map()
    assert actual==rows,"Aster published map differs from generator"
    protected={(x,y) for _,x,y,_ in town.INTERACTIONS}
    for name,x,y,sx,sy in SUPPLIES:
        assert town.LAYOUT[y][x]=="B",name
        assert (x,y) not in protected
        assert rows[y][x]=="ba:ff",name
        assert rows[y][x+64]==NATIVE[sy][sx+30],name
        assert rows[y+64][x]==NATIVE[sy][sx+60],name
    for name,x,y,sx,sy,w in FENCES:
        for dx in range(w):
            px=x+dx
            assert town.LAYOUT[y][px]=="F",name
            assert (px,y) not in protected
            assert rows[y][px]=="ba:ff",name
            assert rows[y][px+64]==NATIVE[sy][sx+dx+30],name
            assert rows[y+64][px]==NATIVE[sy][sx+dx+60],name
    vis.load_map=lambda:rows
    vis.make(ROOT/"tools/aster_domestic_yards.png",
             ROOT/"tools/aster_domestic_yards_labels.png")
    print("PASS: four solid Golden Sun household props and two fence beds")
    print("Normal map only; ruin parity has a separate automated audit.")

if __name__=="__main__":
    audit_and_render()
