#!/usr/bin/env python3
"""Golden Sun Vale native meadow/flower metatiles for Aster's lived-in lawns.

Preview grass variation at original 16px scale and zoom. Aster currently
uses one repeated bare grass metatile across huge areas. Select actual
Golden Sun plain/flower/bush tiles, not random generated pixels and not
water/cliff/roof leftovers.
"""
from PIL import Image,ImageDraw
from pathlib import Path
import aster_layout as town
import aster_visual_preview as vis

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"tools/aster_ground_cover_atlas.png"
VALE=town.load_vale()
SAMPLES=(
 (2,34),(4,34),(6,34),(7,35),(3,38),(5,38),
 (2,42),(4,42),(6,42),(7,42),(18,42),(20,42),
 (2,45),(4,45),(6,45),(7,45),(19,45),(22,45),
 (3,47),(5,47),(7,47),(9,47),(18,47),(21,47),
 (3,48),(5,48),(7,48),(9,48),(11,48),(17,48),
 (18,48),(20,48),(22,48),(24,48),(26,48),(28,48),
 (3,49),(5,49),(7,49),(9,49),(17,49),(24,49),
)
NC=7
SIZE=142
SCALE=7

def main():
    blocks,pal,_=vis.load_tiles()
    meta=vis.load_metatiles()
    bad=set();cache={};mc={}
    def draw(tok,base):
        v=int(tok.split(":")[0],16)&4095
        key=(v,base)
        if key not in mc:mc[key]=vis.render_metatile(
            v,meta,blocks,pal,bad,cache,base)
        return mc[key]
    h=((len(SAMPLES)+NC-1)//NC)*SIZE
    out=Image.new("RGB",(NC*SIZE,h),(25,31,35))
    pen=ImageDraw.Draw(out)
    for i,(sx,sy) in enumerate(SAMPLES):
        ox=(i%NC)*SIZE
        oy=(i//NC)*SIZE
        im=Image.new("RGBA",(16,16),vis.EMPTY_BG)
        for tok,base in ((VALE[sy][sx],0),
                         (VALE[sy][sx+30],2),
                         (VALE[sy][sx+60],2)):
            sprite=draw(tok,base)
            if sprite is not None:im.alpha_composite(sprite,(0,0))
        out.paste(im.resize((16*SCALE,16*SCALE),
                           Image.Resampling.NEAREST).convert("RGB"),
                  (ox+15,oy+16))
        pen.text((ox+5,oy+3),f"{sx},{sy} / {VALE[sy][sx].split(':')[0]}",
                 fill=(237,240,244))
    out.save(OUT,optimize=True)
    if bad:raise AssertionError("Missing native graphics: "+repr(bad))
    print("Aster original Golden Sun meadow tiles:",OUT)
if __name__=="__main__":main()
