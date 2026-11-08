#!/usr/bin/env python3
"""One approved *source-only* visual reference for Aster's nonmagical memorial.

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

def garden(g):
    # Two low rows of Vale's ORIGINAL wooden fence and wildflowers.
    # Strip away the arch completely. Aster's empty memorial is a patch
    # of ordinary soil with a fence, not a Psynergy ritual site.
    paste_upper(g,28,11,10,53,9,2)

if __name__=="__main__":
    # Only this nonmagical candidate survived visual review.
    render("garden",garden)
