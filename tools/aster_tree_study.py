#!/usr/bin/env python3
"""Visually test six DIFFERENT native Golden Sun tree stamps in Aster.

Does not modify Map180. Trees are transferred from intact source Vale
upper layers, keeping Aster's own collision/grass on the ground plane.
This is a source-art QA preview, not an emulator screenshot.
"""
from pathlib import Path
import aster_layout as town
import aster_visual_preview as vis

ROOT=Path(__file__).resolve().parents[1]
original=vis.load_map()
vale=town.load_vale()
mapdata=[r[:] for r in original]
# Study: original destination x/y and size, different native Vale source x/y.
# Each source is a complete free-standing tree or small shrub region.
CANDIDATES={
  "north_woods_w":  (19,46),
  "north_woods_e":  (4,40),
  "residential_w": (9,46),
  "residential_e": (24,45),
  "market_tree_w": (20,46),
  "market_tree_e": (4,40),
}
for name,dx,dy,old_sx,old_sy,w,h in town.SCENERY:
    sx,sy=CANDIDATES[name]
    for yy in range(h):
        for xx in range(w):
            x,y=dx+xx,dy+yy
            assert town.LAYOUT[y][x]=="T",(name,x,y)
            # Preserve original solid grass/shape; vary the drawn tree.
            mapdata[y][x+64]=vale[sy+yy][sx+xx+30]
            mapdata[y+64][x]=vale[sy+yy][sx+xx+60]
vis.load_map=lambda:mapdata
vis.make(ROOT/"tools/aster_native_trees_varied.png",
         ROOT/"tools/aster_native_trees_varied_labels.png")
print("Varied native Vale vegetation study only; game map untouched.")
