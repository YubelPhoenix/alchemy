#!/usr/bin/env python3
"""Reference renderer for Golden Sun's original Vale village (Map003).

This source-derived reference is for comparing authentic Golden Sun scenery
with Aster's draft. It is NOT a screenshot from the emulator.
"""
import csv
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

import aster_visual_preview as art

ROOT=Path(__file__).resolve().parents[1]
VALE_MAP=ROOT/"games/tbs/src/map/map_003/map.txt"
OUTPUT=ROOT/"tools/aster_vale_reference.png"
GRID_OUTPUT=ROOT/"tools/aster_vale_coordinates.png"

def source_grid():
    lines=VALE_MAP.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("grid:128x128")
    meta=dict(part.split(":",1) for part in lines[0].split("\t")[1:])
    ax,ay=map(int,meta.get("at","0,0").split(","))
    fill=meta.get("fill","0")
    # An omitted cell contains fill: metatile, behavior, and shape.
    met=fill.split(":")[0]
    matrix=[[met for _ in range(128)] for _ in range(128)]
    for offset,row in enumerate(lines[1:]):
        y=ay+offset
        if y>=128:
            break
        for x,token in enumerate(row.split()):
            if ax+x<128:
                matrix[y][ax+x]=token
    return matrix

def main():
    # The original Vale map uses its own native set_02 graphics and metatiles;
    # do not mix them with Vault's set_16 palette.
    art.BASE=ROOT/"games/tbs/src/graphics/tileset/set_02"
    art.METATILES=ROOT/"games/tbs/src/map/map_003/metatiles.tsv"
    blocks,palette,source_sizes=art.load_tiles()
    meta=art.load_metatiles()
    rows=source_grid()
    # Resolve each 0xFFF metatile placeholder in the full 128x128 grid.
    # Original Golden Sun numbered each new picture at its first occurrence;
    # ignoring this turns an intact reference village into apparent garbage.
    next_id=0
    for yy in range(128):
        for xx in range(128):
            parts=rows[yy][xx].split(":")
            packed=int(parts[0],16)
            if (packed & 0xfff)==0xfff:
                parts[0]=format((packed & 0xf000)|next_id,"x")
                rows[yy][xx]=":".join(parts)
                next_id+=1
    assert next_id==len(meta), (
        f"Vale has {next_id} placeholders but {len(meta)} metatiles")
    # Vale map.s: map_header 60x114 in 8-pixel tiles => 30x57 16px cells.
    # The three source windows begin at 0, 60 and 120 *8px tiles,
    # equivalently (0,0), (30,0), (60,0) map cells.
    w,h=30,57
    canvas=Image.new("RGBA",(w*16,h*16),art.EMPTY_BG)
    bad=set()
    cache={}
    cache_meta={}
    for layer,charbase in ((0,0),(30,2),(60,2)):
        for y in range(h):
            for x in range(w):
                raw=int(rows[y][x+layer].split(":")[0],16)&0xfff
                key=(raw,charbase)
                if key not in cache_meta:
                    cache_meta[key]=art.render_metatile(
                        raw,meta,blocks,palette,bad,cache,charbase)
                tile=cache_meta[key]
                if tile is not None:
                    canvas.alpha_composite(tile,(x*16,y*16))
    canvas.convert("RGB").save(OUTPUT,optimize=True)
    # Spatial reference to choose complete doors/paths while designing Aster.
    # Each original Vale metatile is 16 pixels; label 4-cell grid points.
    scaled=canvas.convert("RGB").resize((w*32,h*32),
                                      Image.Resampling.NEAREST)
    d=ImageDraw.Draw(scaled,"RGBA")
    for xx in range(0,w+1):
        d.line((xx*32,0,xx*32,h*32),
               fill=(0,0,0,160 if xx%4==0 else 38),width=2 if xx%4==0 else 1)
    for yy in range(0,h+1):
        d.line((0,yy*32,w*32,yy*32),
               fill=(0,0,0,160 if yy%4==0 else 38),width=2 if yy%4==0 else 1)
    for yy in range(0,h,4):
        for xx in range(0,w,4):
            label=f"{xx},{yy}"
            d.rectangle((xx*32+2,yy*32+2,xx*32+7*len(label)+7,
                         yy*32+14),fill=(0,0,0,185))
            d.text((xx*32+4,yy*32+2),label,fill=(255,255,255,255))
    scaled.save(GRID_OUTPUT,optimize=True)
    print("Vale reference generated:",OUTPUT)
    print("Native set_02 source sheets:",source_sizes)
    print("Metatile count:",len(meta),"tile count:",sum(map(len,blocks.values())))
    print("Missing graphics:",sorted(bad,key=str)[:20])
    if bad:
        raise AssertionError("Original Vale tileset references missing graphics")

if __name__=="__main__":
    main()
