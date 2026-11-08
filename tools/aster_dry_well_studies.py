#!/usr/bin/env python3
"""Aster dry well — real Golden Sun assets, VISUAL EXPERIMENTS ONLY.

Try arrangements made from original Vale's plain stone, earth and wooden
household assets. Nothing from the Psynergy Stone, spring, or Paradox tiles
is used; this does not update the playable map or event collisions.
"""
from pathlib import Path
import aster_layout as town
import aster_visual_preview as vis

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=vis.load_map()
VALE=town.load_vale()
GROUNDS=[("soil",6,39),("dust",5,39)]
CENTER=(32,33)

def make(mode):
    grid=[row[:] for row in ORIGINAL]
    cx,cy=CENTER
    if mode=="porch_stones":
        # The tiny oval river rocks outside Vale cottages, relocated to
        # the central plaza over earth but without the cottage's roof.
        for yy in range(2):
            for xx in range(4):
                x,y=cx-2+xx,cy+yy
                sx,sy=14+xx,9+yy
                grid[y][x]=VALE[39][6].split(":")[0]
                grid[y][x+64]=VALE[sy][sx+30]
                grid[y+64][x]=VALE[sy][sx+60]
    elif mode=="stone_rim":
        # Native plain oval rocks in a 3x3 rim; the inside is *dry* brown
        # earth, not colored water, a glowing crystal or a magic source.
        # This small well is deliberately away from the remembrance garden.
        for dy in range(-1,2):
            for dx in range(-1,2):
                x,y=cx+dx,cy+dy
                grid[y][x]="361" if dx==0 and dy==0 else "13a"
    elif mode=="stone_rim_b":
        for dy in range(-1,2):
            for dx in range(-1,2):
                x,y=cx+dx,cy+dy
                grid[y][x]="361" if dx==0 and dy==0 else "1cd"
    elif mode=="masonry":
        # Native gray masonry at the top of original Vale cottage's
        # chimney (non-magical); crop no adjoining roof or golden sun art.
        for yy in range(2):
            for xx in range(3):
                x,y=cx-1+xx,cy+yy
                grid[y][x]=VALE[39][6].split(":")[0]
                grid[y][x+64]=VALE[2+yy][13+xx+30]
                grid[y+64][x]=VALE[2+yy][13+xx+60]
    elif mode=="chimney_only":
        # Original Golden Sun Vale stone chimney cap + masonry column,
        # precisely x14..15 y2..4. The adjacent house roof is not copied.
        for yy in range(3):
            for xx in range(2):
                x,y=cx-1+xx,cy-1+yy
                sx,sy=14+xx,2+yy
                grid[y][x]=VALE[39][6].split(":")[0]
                grid[y][x+64]=VALE[sy][sx+30]
                grid[y+64][x]=VALE[sy+60][sx]
    elif mode=="stone_cistern":
        # Use exact native gray cap over a plain brown earth opening.
        # Structure is 2x2 (32x32 px) atop worn soil, with gray stone
        # at the front and a dark unwatered cavity behind.
        for yy in range(2):
            for xx in range(2):
                x,y=cx-1+xx,cy+yy
                grid[y][x]=VALE[39][6].split(":")[0]
                sx,sy=14+xx,2+yy
                grid[y][x+64]=VALE[sy][sx+30]
                grid[y+64][x]=VALE[sy+60][sx]
    else:raise ValueError(mode)
    # Well event stays on original southern interaction (32,35).
    assert grid[35][32]==ORIGINAL[35][32],mode
    assert grid[34][32].split(":")[0] != "fff",mode
    vis.load_map=lambda:grid
    vis.make(ROOT/f"tools/aster_dry_well_{mode}.png",
             ROOT/f"tools/aster_dry_well_{mode}_labels.png")
    print("Golden Sun dry well candidate rendered:",mode)

if __name__=="__main__":
    for name in ("porch_stones","stone_rim","stone_rim_b",
                 "masonry","chimney_only","stone_cistern"):
        make(name)
