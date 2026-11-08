#!/usr/bin/env python3
"""Inspect exact original Golden Sun Vale water/bank metatiles at enlarged scale.

Use this to replace the magical crystal in Aster's ordinary pond without
introducing a flat square of water or another RPG's waterfall graphics.
Every sample comes from original Vale Map003 and the set_02 palette.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import aster_layout as town
import aster_visual_preview as vis

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"tools/aster_water_tile_atlas.png"
VALE=town.load_vale()
# Exact source samples around the original pond, including water centers,
# east/west banks and bottom grass transition.
SAMPLES=(
  ("north_water",11,39),("north_center",13,39),("n_right",16,39),
  ("edge_west",9,40),("west_mid",10,41),("center_a",12,40),
  ("center_b",12,42),("center_c",13,43),("center_d",10,45),
  ("left_ripple",10,43),("left_ripple2",10,42),("right_ripple",16,43),
  ("south_west",9,44),("south_center",12,45),("south_right",17,44),
  ("shore_w",9,45),("shore_w2",8,46),("shore_e",17,45),
  ("shore_e2",18,45),("grass_e",18,46),("edge_mid",17,43),
  ("water_no_1",11,41),("water_no_2",15,41),("water_no_3",15,43),
)
NCOLS=6
CELL=156
ROWS=(len(SAMPLES)+NCOLS-1)//NCOLS
Z=7

def main():
    tiles,palette,_=vis.load_tiles()
    meta=vis.load_metatiles()
    bad=set();cache={};metacache={}
    def get(token,base):
        idx=int(token.split(":")[0],16)&4095
        key=idx,base
        if key not in metacache:
            metacache[key]=vis.render_metatile(
                idx,meta,tiles,palette,bad,cache,base)
        return metacache[key]
    img=Image.new("RGB",(NCOLS*CELL,ROWS*CELL),(24,29,34))
    draw=ImageDraw.Draw(img)
    for i,(name,sx,sy) in enumerate(SAMPLES):
        dx=i%NCOLS*CELL;dy=i//NCOLS*CELL
        ground=VALE[sy][sx];m=VALE[sy][sx+30];t=VALE[sy][sx+60]
        pic=Image.new("RGBA",(16,16),vis.EMPTY_BG)
        p=get(ground,0)
        if p is not None:pic.alpha_composite(p,(0,0))
        # Picture includes all three native layers; red/blue check means
        # the original tile contains pedestal graphics, NOT clean water.
        for token in (m,t):
            p=get(token,2)
            if p is not None:pic.alpha_composite(p,(0,0))
        v=pic.resize((16*Z,16*Z),Image.Resampling.NEAREST)
        img.paste(v.convert("RGB"),(dx+15,dy+20))
        draw.text((dx+8,dy+2),name,fill=(243,247,250))
        draw.text((dx+6,dy+138),
             f"{sx},{sy}: {ground.split(':')[0]}",fill=(193,208,212))
    img.save(OUT,optimize=True)
    print("Original Golden Sun water source comparisons:",OUT)
    if bad:raise AssertionError(f"Invalid native art IDs: {bad}")

if __name__=="__main__":main()
