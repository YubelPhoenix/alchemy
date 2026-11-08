#!/usr/bin/env python3
"""Review EVERY native Golden Sun Vale metatile near the pond's south bank.

Exact Map003/source coordinates, complete 16x16 layered art. This is an
inspection atlas for hand selecting bank curves; it is not a new pond.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import aster_layout as vale
import aster_visual_preview as vis
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"tools/aster_pond_south_bank_atlas.png"
NATIVE=vale.load_vale()
X0,X1=8,19
Y0,Y1=42,47
SCALE=5
CELL_W,CELL_H=100,116

def main():
    blocks,palette,_=vis.load_tiles()
    meta=vis.load_metatiles()
    bad=set();cache={};mc={}
    W=(X1-X0+1)*CELL_W
    H=(Y1-Y0+1)*CELL_H
    img=Image.new("RGB",(W,H),(25,30,34))
    pen=ImageDraw.Draw(img)
    for sy in range(Y0,Y1+1):
        for sx in range(X0,X1+1):
            xy=(sx-X0)*CELL_W,(sy-Y0)*CELL_H
            pic=Image.new("RGBA",(16,16),vis.EMPTY_BG)
            for token,base in zip(
                (NATIVE[sy][sx],NATIVE[sy][sx+30],NATIVE[sy][sx+60]),(0,2,2)):
                idx=int(token.split(":")[0],16)&4095
                key=idx,base
                if key not in mc:
                    mc[key]=vis.render_metatile(
                        idx,meta,blocks,palette,bad,cache,base)
                fragment=mc[key]
                if fragment is not None:
                    pic.alpha_composite(fragment,(0,0))
            px,py=xy
            img.paste(pic.resize((16*SCALE,16*SCALE),Image.Resampling.NEAREST).convert("RGB"),(px+10,py+18))
            pen.text((px+6,py+2),f"({sx},{sy})",fill=(236,243,244))
            pen.text((px+6,py+102),NATIVE[sy][sx].split(":")[0],fill=(175,208,216))
    if bad:raise AssertionError(f"Unmapped original art: {bad}")
    img.save(OUT,optimize=True)
    print("Exact original Vale bank tiles",X0,X1,Y0,Y1,OUT)
    print("NOT an Aster map or gameplay screenshot.")
if __name__=="__main__":main()
