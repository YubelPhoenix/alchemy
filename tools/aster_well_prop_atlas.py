#!/usr/bin/env python3
"""Inspect only original Golden Sun Vale Map003 household props for Aster's dry well.

Place complete native upper-layer crops on Aster's three-layer grass; compare
against their original ground so cliff, roof, liquid, and palette residues are
obvious. This generator changes no actual scene or gameplay map.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import aster_layout as town
import aster_visual_preview as render

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"tools/aster_well_prop_atlas.png"
# Crops near a doorstep, bucket, chimney, village wood fence and stone ornaments.
# label, Vale x,y,w,h. Some are deliberate NEGATIVE controls.
STUDIES=(
  ("door_pebble_a",13,8,3,3),
  ("door_pebble_b",14,9,3,3),
  ("door_pebble_c",12,8,3,3),
  ("door_pebble_d",12,9,3,3),
  ("upper_chimney",13,2,3,3),
  ("upper_chimney_b",14,2,2,2),
  ("barrel_house",17,5,3,4),
  ("barrel_west",10,13,3,5),
  ("porch_stones",20,20,3,4),
  ("vale_porches",22,19,3,4),
  ("low_fence",10,53,4,3),
  ("upper_hedge",13,52,3,3),
  ("wood_gate",12,49,4,4),
  ("wood_gate_b",11,50,4,4),
  ("small_rocks",7,33,3,4),
  ("stone_path",6,35,3,4),
  ("bare_soil",4,38,4,4),
  ("stone_pond",9,38,4,4),
  ("tile_household",12,35,4,4),
  ("marker",2,35,3,4),
)
W,H=4,5
COLS=4
CARD_W=265
CARD_H=219
Z=2

def main():
    native=town.load_vale()
    tiles,pal,_=render.load_tiles()
    meta=render.load_metatiles()
    invalid=set()
    cached={}
    art={}
    def draw_mt(token,base):
        val=int(token.split(":")[0],16)&0xfff
        key=(val,base)
        if key not in art:
            art[key]=render.render_metatile(val,meta,tiles,pal,invalid,cached,base)
        return art[key]
    bg=Image.new("RGBA",(W*16,H*16),render.EMPTY_BG)
    for y in range(H):
        for x in range(W):
            for tile,base in (("ba",0),("15",2),("15",2)):
                pic=draw_mt(tile,base)
                if pic is not None:bg.alpha_composite(pic,(x*16,y*16))
    R=(len(STUDIES)+COLS-1)//COLS
    atlas=Image.new("RGB",(CARD_W*COLS,CARD_H*R),(25,31,34))
    painter=ImageDraw.Draw(atlas)
    for i,(name,sx,sy,w,h) in enumerate(STUDIES):
        assert sx+w<=30 and sy+h<=57,(name,sx,sy)
        ax,ay=(i%COLS)*CARD_W,(i//COLS)*CARD_H
        painter.text((ax+5,ay+5),f"{name} {sx},{sy}:{w}x{h}",fill=(240,240,240))
        for mode in range(2):
            frame=bg.copy()
            for dy in range(h):
                for dx in range(w):
                    loc=(dx*16,dy*16)
                    if mode==0:
                        p=draw_mt(native[sy+dy][sx+dx],0)
                        if p is not None:frame.alpha_composite(p,loc)
                    for shift in (30,60):
                        p=draw_mt(native[sy+dy][sx+dx+shift],2)
                        if p is not None:frame.alpha_composite(p,loc)
            frame=frame.resize((W*16*Z,H*16*Z),Image.Resampling.NEAREST)
            atlas.paste(frame.convert("RGB"),(ax+3+mode*132,ay+25))
        painter.text((ax+5,ay+194),"native ground       Aster grass",fill=(200,210,210))
    atlas.save(OUT,optimize=True)
    print("Native Vale candidate props:",len(STUDIES),"atlas:",OUT)
    if invalid: print("Bad source graphics (do not use):",sorted(invalid,key=str)[:20])
    print("Source-only diagnostic. No Aster Map180 changes.")
if __name__=="__main__":
    main()
