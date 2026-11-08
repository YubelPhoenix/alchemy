#!/usr/bin/env python3
"""Aster: manually edited, palette-correct Golden Sun waterbank test.

An original Vale pond (with Psynergy crystal) is compared with the same
bank geometry after hand-replacing only crystal-bearing interior cells
using real observed open-water metatiles from Vale Map003. The original
three-layer source data is preserved at the bank.

No random tile placement, no foreign art, no gameplay/map_180 changes.
This is a native 16px material test, NOT finished Aster shoreline.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import aster_layout as vale
import aster_visual_preview as vis

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"tools/aster_crystal_free_pond_test.png"
VALE=vale.load_vale()

# Original visual source: Vale pond at x8..18, y38..46.
# Manually avoid the neighboring inn's roof in upper-right source rows.
# (Original 3-layer waterbanks are retained; this is not a fake tile card.)
SRC_RECT=(8,38,11,9)
GRASS="ba";EMPTY="15"
# These exact source cells are checked visually in the native water-tile
# atlas: real unobstructed water, not the dark base under the shrine.
WATER_CELLS=((11,41),(15,41),(10,43),(16,43),(10,42),(15,43))
for x,y in WATER_CELLS:
    assert VALE[y][x].split(":")[0] not in ("3b6","3b7"),(x,y)

def source_allowed(sx,sy):
    # Curved pond footprint from native Vale banks, with clear lawn beyond.
    # We do NOT bring along the eastern inn or other buildings.
    spans={38:(10,16),39:(9,16),40:(8,17),41:(8,17),
           42:(8,18),43:(8,18),44:(8,18),45:(9,18),46:(9,17)}
    a,b=spans[sy]
    if not a<=sx<=b:return False
    if sy<=40 and sx>=17:return False
    return True

def build_pixels(clean,blocks,palette,metatiles,bad,tile_cache,mtcache):
    """Construct a deliberately limited 15x13 tile test card."""
    cells={}
    w,h=15,13
    for yy in range(h):
        for xx in range(w):
            cells[(xx,yy)]=(GRASS,EMPTY,EMPTY)
    sx0,sy0,sw,sh=SRC_RECT
    for yy in range(sh):
        for xx in range(sw):
            sx,sy=sx0+xx,sy0+yy
            if not source_allowed(sx,sy):continue
            cells[(xx+2,yy+2)]=tuple(VALE[sy][sx+30*i] for i in range(3))
            if clean and 11<=sx<=16 and 41<=sy<=45:
                # Hand-chosen six-tile pattern, checked against original Vale
                # water images; no repeated black/flat deep-water base.
                ix=(sx-11)%3;iy=(sy-41)%2
                wx,wy=WATER_CELLS[iy*3+ix]
                cells[(xx+2,yy+2)]=(VALE[wy][wx].split(":")[0],EMPTY,EMPTY)
    picture=Image.new("RGBA",(w*16,h*16),vis.EMPTY_BG)
    for yy in range(h):
        for xx in range(w):
            for token,base in zip(cells[(xx,yy)],(0,2,2)):
                key=int(token.split(":")[0],16)&4095,base
                if key not in mtcache:
                    mtcache[key]=vis.render_metatile(
                        key[0],metatiles,blocks,palette,bad,tile_cache,base)
                tile=mtcache[key]
                if tile is not None:picture.alpha_composite(tile,(xx*16,yy*16))
    return picture

def main():
    blocks,palette,_=vis.load_tiles()
    metatiles=vis.load_metatiles()
    bad=set();tile_cache={};mtcache={}
    before=build_pixels(False,blocks,palette,metatiles,bad,tile_cache,mtcache)
    after=build_pixels(True,blocks,palette,metatiles,bad,tile_cache,mtcache)
    assert not bad,f"Invalid original Vale 16px graphics: {bad}"
    # Two full 15x13-cell panels at 2x nearest-neighbor, no scale changes.
    W,H=1020,525
    out=Image.new("RGB",(W,H),(25,30,34))
    pen=ImageDraw.Draw(out)
    panels=(("ORIGINAL VALE POND + CRYSTAL",before),
            ("AST ER TEST: ORIGINAL BANK + CLEAR WATER".replace("AST ER","ASTER"),after))
    for i,(title,pic) in enumerate(panels):
        x=12+i*510
        pen.text((x+4,13),title,fill="white")
        pen.text((x+4,30),"Real Vale Map003/set_02 metatiles | 2x enlargement",fill=(185,205,211))
        out.paste(pic.resize((480,416),Image.Resampling.NEAREST).convert("RGB"),(x+4,57))
    pen.text((16,H-35),"No new town map. Crystal removal is hand-assigned; bank finish still requires visual review.",
             fill=(211,225,228))
    out.save(OUT,optimize=True)
    print("PASS: Golden Sun native 3-layer waterbank material source")
    print("Sampled clean open-water sources:",WATER_CELLS)
    print("Source waterbank x/y:",SRC_RECT,"Preview:",OUT)
    print("Do not treat this as a GBA emulator/animated water demonstration.")
if __name__=="__main__":main()
