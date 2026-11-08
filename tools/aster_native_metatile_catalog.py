#!/usr/bin/env python3
"""Catalog genuine Vale background metatiles for a dry nonmagical Aster well.

No ROM changes. Labels all metatile IDs and shows the same indexed art in
base-character block 0 and overlay block 2 for accurate Golden Sun reuse.
Any proposed well must be constructed from compatible source art, not
from Vale's Psynergy Stone, pond or graphics from other games.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import aster_visual_preview as vis
ROOT=Path(__file__).resolve().parents[1]
blocks,palette,_=vis.load_tiles()
metatiles=vis.load_metatiles()
NUM_COLS=15
NUM_ROWS=16
ITEMS=NUM_COLS*NUM_ROWS
TILE_ZOOM=2
WIDTH=90
HEIGHT=52
issues=set()
cache={}
base=Image.new("RGBA",(16,16),(108,185,76,255))
for start in range(0,len(metatiles),ITEMS):
    image=Image.new("RGB",(NUM_COLS*WIDTH,NUM_ROWS*HEIGHT),(24,30,35))
    draw=ImageDraw.Draw(image)
    for item in range(start,min(start+ITEMS,len(metatiles))):
        row,col=divmod(item-start,NUM_COLS)
        px,py=col*WIDTH,row*HEIGHT
        draw.text((px+2,py+1),f"{item:03x} / {item:d}",fill=(255,255,255))
        for offset,charbase in ((0,0),(43,2)):
            tile=vis.render_metatile(item,metatiles,blocks,palette,issues,cache,charbase)
            sample=base.copy()
            if tile is not None:sample.alpha_composite(tile)
            tile32=sample.resize((32,32),Image.Resampling.NEAREST)
            image.paste(tile32.convert("RGB"),(px+offset+2,py+16))
    file=ROOT/f"tools/aster_vale_metatile_{start//ITEMS:02d}.png"
    image.save(file,optimize=True)
    print(file,"metatile range",start,min(start+ITEMS,len(metatiles))-1)
if issues:raise AssertionError(f"Unmapped source assets: {sorted(issues,key=str)[:20]}")
