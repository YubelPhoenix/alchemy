#!/usr/bin/env python3
"""Search authentic Golden Sun Vale dark cave/door components for Aster's well.

A tiny dark dry opening on soil must read as a real well, not a borrowed
cliff/cave, building doorway, water pool or Psynergy Stone. Visual comparison
only, do not alter Aster's playable or ruined map.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import aster_layout as town
import aster_visual_preview as art

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"tools/aster_well_mouth_atlas.png"
# Name, source Vale x,y,w,h: deliberate neighboring crop offsets.
CROPS=(
 ("cave_left",6,25,4,4),
 ("cave_center",7,26,4,4),
 ("cave_right",8,26,4,4),
 ("cave_lower",7,27,4,4),
 ("cave_base",8,27,3,4),
 ("cliff_opening",9,27,3,4),
 ("home_door_a",12,6,4,4),
 ("home_door_b",13,6,4,4),
 ("home_door_c",13,7,3,4),
 ("home_door_d",12,7,4,4),
 ("house_shadow",22,18,4,4),
 ("cellar_door",21,19,4,4),
 ("east_door",22,18,3,5),
 ("cave_north",7,24,4,4),
 ("shadow_well",10,25,4,4),
 ("inset_dark",8,28,3,3),
)
W,H=4,5
COLS=4
CW,CH=268,222
Z=2

def main():
    vale=town.load_vale()
    blocks,pal,_=art.load_tiles()
    meta=art.load_metatiles()
    bad=set()
    cache={}
    seen={}
    def mt(tok,base):
        n=int(tok.split(":")[0],16)&4095
        key=n,base
        if key not in seen:seen[key]=art.render_metatile(n,meta,blocks,pal,bad,cache,base)
        return seen[key]
    grass=Image.new("RGBA",(W*16,H*16),art.EMPTY_BG)
    for y in range(H):
        for x in range(W):
            for tok,base in (("ba",0),("15",2),("15",2)):
                im=mt(tok,base)
                if im is not None: grass.alpha_composite(im,(x*16,y*16))
    rows=(len(CROPS)+COLS-1)//COLS
    atlas=Image.new("RGB",(COLS*CW,rows*CH),(25,30,34))
    draw=ImageDraw.Draw(atlas)
    for i,(name,sx,sy,w,h) in enumerate(CROPS):
        assert sx+w<=30 and sy+h<=57
        ox,oy=(i%COLS)*CW,(i//COLS)*CH
        draw.text((ox+6,oy+5),f"{name} {sx},{sy} {w}x{h}",fill=(244,244,244))
        for mode in range(2):
            view=grass.copy()
            for dy in range(h):
                for dx in range(w):
                    p=(dx*16,dy*16)
                    if mode==0:
                        im=mt(vale[sy+dy][sx+dx],0)
                        if im is not None:view.alpha_composite(im,p)
                    for off in (30,60):
                        im=mt(vale[sy+dy][sx+dx+off],2)
                        if im is not None:view.alpha_composite(im,p)
            view=view.resize((W*16*Z,H*16*Z),Image.Resampling.NEAREST)
            atlas.paste(view.convert("RGB"),(ox+4+mode*132,oy+27))
        draw.text((ox+6,oy+197),"native ground      Aster grass",fill=(199,208,208))
    atlas.save(OUT,optimize=True)
    print("Golden Sun well mouth component atlas:",OUT)
    if bad:print("Invalid source entries:",sorted(bad,key=str)[:20])
    print("No Aster gameplay map changed")
if __name__=="__main__":
    main()
