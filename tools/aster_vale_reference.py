#!/usr/bin/env python3
"""Reference renderer for Golden Sun's original Vale village (Map003).

This source-derived reference is for comparing authentic Golden Sun scenery
with Aster's draft. It is NOT a screenshot from the emulator.
"""
import csv
from pathlib import Path
from PIL import Image

import aster_visual_preview as art

ROOT=Path(__file__).resolve().parents[1]
VALE_MAP=ROOT/"games/tbs/src/map/map_003/map.txt"
OUTPUT=ROOT/"tools/aster_vale_reference.png"

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
    atlas,palette,source_sizes=art.load_tiles()
    meta=art.load_metatiles()
    rows=source_grid()
    # Vale map.s: map_header 60x114 in 8-pixel tiles => 30x57 16px cells.
    # The three source windows begin at 0, 60 and 120 *8px tiles,
    # equivalently (0,0), (30,0), (60,0) map cells.
    w,h=30,57
    canvas=Image.new("RGBA",(w*16,h*16),art.EMPTY_BG)
    bad=set()
    cache={}
    cache_meta={}
    for layer in (0,30,60):
        for y in range(h):
            for x in range(w):
                raw=int(rows[y][x+layer].split(":")[0],16)&0xfff
                if raw not in cache_meta:
                    cache_meta[raw]=art.render_metatile(
                        raw,meta,atlas,palette,bad,cache)
                tile=cache_meta[raw]
                if tile is not None:
                    canvas.alpha_composite(tile,(x*16,y*16))
    canvas.convert("RGB").save(OUTPUT,optimize=True)
    print("Vale reference generated:",OUTPUT)
    print("Native set_02 source sheets:",source_sizes)
    print("Metatile count:",len(meta),"tile count:",len(atlas))
    print("Missing graphics:",sorted(bad,key=str)[:20])
    if bad:
        raise AssertionError("Original Vale tileset references missing graphics")

if __name__=="__main__":
    main()
