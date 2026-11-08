#!/usr/bin/env python3
"""Golden Sun Vale foliage crop atlas for Aster (source art only).

Render original 4x5-cell source regions on the same 3-layer grass used by
Aster, full ground vs. upper-layers-only. This makes mismatched ground
squares, cropped tree limbs, cliffs and palette artifacts obvious BEFORE
copying art into the playable Aster grid. No map file is modified.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import aster_layout as town
import aster_visual_preview as vis

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"tools/aster_foliage_candidate_atlas.png"
# name, source Vale x and y; all 4x5 native map metatiles
CANDIDATES=(
 ("north_autumn",2,11), ("north_blue",17,7), ("cliff_red",22,13),
 ("cliff_green",24,12),("east_autumn",23,16), ("grove_blue",18,18),
 ("grove_south",14,23),("shop_blue",13,33), ("inn_blue",23,38),
 ("west_shrub",2,39), ("fountain_tree",15,34), ("cliff_sapling",18,29),
 ("market_tree",19,45), ("mixed_tree",24,45), ("blue_low",8,46),
 ("west_forest",1,49), ("east_forest",23,50), ("southeast_woods",25,51),
)
W,H=4,5
SCALE=2
CELL_W=298
CELL_H=228
COLS=3

def main():
    blocks,palette,_=vis.load_tiles()
    meta=vis.load_metatiles()
    vale=town.load_vale()
    bad=set()
    cache={}
    rendered={}
    def metatile(token,charbase):
        i=int(token.split(":")[0],16)&0xfff
        k=(i,charbase)
        if k not in rendered:
            rendered[k]=vis.render_metatile(i,meta,blocks,palette,bad,cache,charbase)
        return rendered[k]
    empty=Image.new("RGBA",(W*16,H*16),vis.EMPTY_BG)
    for yy in range(H):
        for xx in range(W):
            for tile in (metatile(town.BACKGROUND[0],0),
                         metatile(town.BACKGROUND[1],2),
                         metatile(town.BACKGROUND[2],2)):
                if tile is not None:
                    empty.alpha_composite(tile,(xx*16,yy*16))
    rows=(len(CANDIDATES)+COLS-1)//COLS
    atlas=Image.new("RGB",(COLS*CELL_W,rows*CELL_H),(27,34,36))
    painter=ImageDraw.Draw(atlas)
    for i,(name,sx,sy) in enumerate(CANDIDATES):
        assert 0<=sx and sx+W<=30 and 0<=sy and sy+H<=57,(name,sx,sy)
        col,row=i%COLS,i//COLS
        x0,y0=col*CELL_W,row*CELL_H
        painter.text((x0+8,y0+8),f"{name} ({sx},{sy})",fill=(240,240,240))
        for mode in range(2):
            pic=empty.copy()
            for yy in range(H):
                for xx in range(W):
                    # Full three-layer version vs clean Aster grass beneath
                    # original Golden Sun upper overlays only.
                    if mode==0:
                        ground=metatile(vale[sy+yy][sx+xx],0)
                        if ground is not None:pic.alpha_composite(ground,(xx*16,yy*16))
                    for offx,offy in ((30,0),(60,0)):
                        src=vale[sy+yy][sx+xx+offx]
                        tile=metatile(src,2)
                        if tile is not None:pic.alpha_composite(tile,(xx*16,yy*16))
            large=pic.resize((W*16*SCALE,H*16*SCALE),Image.Resampling.NEAREST)
            atlas.paste(large.convert("RGB"),(x0+8+mode*138,y0+32))
        painter.text((x0+8,y0+198),"all 3 layers      grass + upper",fill=(200,209,209))
    atlas.save(OUT,optimize=True)
    if bad:
        print("REJECT candidate tiles with missing palette/charblock data:",
              sorted(bad,key=str)[:15])
    print("Native Golden Sun foliage source crop atlas:",OUT,
          "candidate count:",len(CANDIDATES))
    print("Visual candidate selection only; no Aster source-map changes.")
if __name__=="__main__":
    main()
