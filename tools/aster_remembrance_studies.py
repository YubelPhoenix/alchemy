#!/usr/bin/env python3
"""Three *source-only* concepts for Aster's nonmagical memorial.

Uses checked-in Golden Sun Vale Map003 16x16 metatiles. Nothing in the
playable map is changed. DO NOT use the Psynergy Stone or crystal.
"""
from pathlib import Path
import aster_layout as town
import aster_visual_preview as image

ROOT = Path(__file__).resolve().parents[1]
original = image.load_map()
vale = town.load_vale()
trial_origin = (28, 8)

def paste_upper(grid, dx,dy,sx,sy,w,h):
    for oy in range(h):
        for ox in range(w):
            x,y=dx+ox,dy+oy
            assert 0<x<63 and 0<y<63
            grid[y][x+64]=vale[sy+oy][sx+ox+30]
            grid[y+64][x]=vale[sy+oy][sx+ox+60]

def render(label,operation):
    grid = [row[:] for row in original]
    operation(grid)
    image.load_map=lambda:grid
    image.make(ROOT/f"tools/aster_memorial_{label}.png",
               ROOT/f"tools/aster_memorial_{label}_labels.png")
    print("Aster original-Golden-Sun non-Psynergy memorial study:", label)

def fence(g):
    # Wooden entrance-frame + adjoining garden fence; the eventual memorial
    # should use the fence material, not an identical gate to Vale.
    paste_upper(g,28,8,10,50,9,5)

def notice(g):
    # Native town notice post near a fenced plot; no mystical object.
    paste_upper(g,31,8,16,5,4,6)

def stone(g):
    # Weathered masonry from ordinary Vale house chimney top, not the
    # Psynergy rock. This is a *candidate*, may read as a chimney.
    paste_upper(g,30,9,13,1,4,4)

if __name__=="__main__":
    render("fence",fence)
    render("notice",notice)
    render("masonry",stone)
