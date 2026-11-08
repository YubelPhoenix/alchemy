#!/usr/bin/env python3
"""Aster terrain-study atlas made entirely from Golden Sun Vale map layers.

The approved reference towns feel inhabited because terrain constrains their
streets. Review *whole, connected* native cliff/forest clusters before the
Aster field map changes. Red guide overlays from user-exported map screenshots
are not game art. No foreign art, crystal, spring or map data edits here.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import aster_layout as town
import aster_visual_preview as render

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/"tools/aster_native_terrain_atlas.png"
VALE=town.load_vale()
COLS=4
CW=350
CH=210
# x/y/w/h measured on Vale Map003's original 30x57 metatile windows.
# Deliberately sample long continuous terrain, not scattered cliff tiles.
AREAS=(
 ("northwest_terrace",0,0,10,7),
 ("north_crest",10,0,10,7),
 ("northeast_wood",20,0,10,7),
 ("upper_west_ridge",0,8,10,7),
 ("upper_mid_terrace",10,8,10,7),
 ("upper_east_ridge",20,8,10,7),
 ("left_stone_path",0,15,10,7),
 ("main_cross_terrace",10,15,10,7),
 ("east_slope",20,15,10,7),
 ("western_south_cliff",0,22,10,7),
 ("central_cliff",10,22,10,7),
 ("east_cliff",20,22,10,7),
 ("west_low_forest",0,29,10,7),
 ("lower_west_path",0,36,10,7),
 ("market_ridge",10,36,10,7),
 ("east_low_ridge",20,36,10,7),
 ("west_mouth_valley",0,43,10,7),
 ("central_mouth_valley",10,43,10,7),
 ("east_mouth",20,43,10,7),
 ("bottom_woods_w",0,50,10,7),
 ("bottom_woods_mid",10,50,10,7),
 ("bottom_woods_e",20,50,10,7),
)

def main():
    blocks,palette,_=render.load_tiles()
    metatiles=render.load_metatiles()
    warnings=set()
    tile_cache={}
    rendered={}
    def cell(token,base):
        idx=int(token.split(":")[0],16)&4095
        key=(idx,base)
        if key not in rendered:
            rendered[key]=render.render_metatile(
                idx,metatiles,blocks,palette,warnings,tile_cache,base)
        return rendered[key]
    height=((len(AREAS)+COLS-1)//COLS)*CH
    output=Image.new("RGB",(COLS*CW,height),(29,33,36))
    pen=ImageDraw.Draw(output)
    for i,(name,sx,sy,w,h) in enumerate(AREAS):
        assert sx>=0 and sx+w<=30 and sy>=0 and sy+h<=57
        ax,ay=(i%COLS)*CW,(i//COLS)*CH
        pen.text((ax+10,ay+7),f"{name} — Vale ({sx},{sy})",fill="white")
        img=Image.new("RGBA",(w*16,h*16),render.EMPTY_BG)
        for yy in range(h):
            for xx in range(w):
                for token,base in ((VALE[sy+yy][sx+xx],0),
                                   (VALE[sy+yy][sx+xx+30],2),
                                   (VALE[sy+yy+60][sx+xx],2)):
                    part=cell(token,base)
                    if part is not None:
                        img.alpha_composite(part,(xx*16,yy*16))
        zoomed=img.resize((w*16*2,h*16*2),Image.Resampling.NEAREST)
        # Crop to 150px height for broad side-by-side comparisons.
        zoomed=zoomed.crop((0,0,w*16*2,150))
        output.paste(zoomed.convert("RGB"),(ax+10,ay+32))
        pen.text((ax+10,ay+188),"original native 3-layer terrain",fill=(200,208,208))
    output.save(OUTPUT,optimize=True)
    print("Aster native topography candidate atlas:",OUTPUT)
    print("Original Vale terrain candidates:",len(AREAS))
    if warnings:print("INVALID source tiles (reject affected crop):",
                      sorted(warnings,key=str)[:25])
    print("Do not paste source roof/cliff fragments into active Map180.")
if __name__=="__main__":
    main()
