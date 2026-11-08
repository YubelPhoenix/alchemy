#!/usr/bin/env python3
"""Golden Sun native foliage crop refinements for Aster, no playable map edits.

A field of 3x3, 3x5, or 4x5 source tiles is inspected at original grass
palette with and without original ground. Reject house roofs, cliff walls,
cut-off trunks and solid-color rectangular tree shadows.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import aster_layout as town
import aster_visual_preview as vis

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"tools/aster_foliage_refinement_atlas.png"
# Candidate label, Vale source x/y, width, height; all are native set_02
CANDIDATES=(
 ("blue_n_house_1",16,7,3,5), ("blue_n_house_2",17,7,3,5),
 ("blue_shop_a",11,35,4,5), ("blue_shop_b",12,35,4,5),
 ("blue_shop_c",12,36,4,5), ("blue_market_a",17,45,4,5),
 ("blue_market_b",17,46,4,5), ("blue_market_c",18,46,4,5),
 ("blue_low_a",7,47,4,5), ("blue_low_b",8,47,4,5),
 ("blue_low_c",8,48,4,5), ("red_cliff_a",25,12,4,4),
 ("red_cliff_b",25,13,4,4), ("red_cliff_c",24,13,4,4),
 ("red_cliff_d",25,14,4,4), ("red_north_a",3,12,4,5),
 ("red_north_b",4,13,4,5), ("inn_shrub_a",24,39,3,3),
 ("inn_shrub_b",25,40,3,3), ("inn_shrub_c",24,40,3,3),
 ("forest_hedge_a",20,40,3,3), ("forest_hedge_b",21,41,3,3),
)
MAXW,MAXH=4,5
CELLW,CELLH=298,228
COLS=3
SCALE=2

def main():
    blocks,pal,_=vis.load_tiles()
    meta=vis.load_metatiles()
    native=town.load_vale()
    bad=set()
    cache={}
    tilecache={}
    def mt(token,base):
        k=(int(token.split(":")[0],16)&4095,base)
        if k not in tilecache:
            tilecache[k]=vis.render_metatile(k[0],meta,blocks,pal,bad,cache,base)
        return tilecache[k]
    bg=Image.new("RGBA",(MAXW*16,MAXH*16),vis.EMPTY_BG)
    for y in range(MAXH):
        for x in range(MAXW):
            for val,base in ((town.GRASS,0),("15",2),("15",2)):
                sprite=mt(val,base)
                if sprite is not None:bg.alpha_composite(sprite,(x*16,y*16))
    rows=(len(CANDIDATES)+COLS-1)//COLS
    img=Image.new("RGB",(COLS*CELLW,rows*CELLH),(25,31,34))
    draw=ImageDraw.Draw(img)
    for i,(name,sx,sy,w,h) in enumerate(CANDIDATES):
        assert 0<=sx and sx+w<=30 and 0<=sy and sy+h<=57,(name,sx,sy,w,h)
        dx,dy=(i%COLS)*CELLW,(i//COLS)*CELLH
        draw.text((dx+8,dy+8),f"{name}  {sx},{sy}  {w}x{h}",fill=(255,255,255))
        for variant in range(2):
            view=bg.copy()
            for yy in range(h):
                for xx in range(w):
                    pos=(xx*16,yy*16)
                    if variant==0:
                        sprite=mt(native[sy+yy][sx+xx],0)
                        if sprite is not None:view.alpha_composite(sprite,pos)
                    for offs in (30,60):
                        sprite=mt(native[sy+yy][sx+xx+offs],2)
                        if sprite is not None:view.alpha_composite(sprite,pos)
            view=view.resize((MAXW*16*SCALE,MAXH*16*SCALE),Image.Resampling.NEAREST)
            img.paste(view.convert("RGB"),(dx+8+variant*138,dy+32))
        draw.text((dx+8,dy+198),"native ground       grass ground",fill=(194,209,209))
    img.save(OUT,optimize=True)
    if bad: print("Reject candidates containing unavailable GBA tile refs:",sorted(bad,key=str)[:20])
    print("Aster foliage refinement source atlas:",OUT,"candidates:",len(CANDIDATES))
if __name__=="__main__":
    main()
