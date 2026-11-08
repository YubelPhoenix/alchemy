#!/usr/bin/env python3
"""Visual source atlas for original Golden Sun Vale tiles and map_009.

Offline studies only. Samples original The Broken Seal background tiles and
original Vale Eruption map using its SEPARATE set_08 art; no imported art and no gameplay map changes.
Identifies possible earth paths, ordinary stonework and ruined architecture.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import aster_layout as town
import aster_visual_preview as render
ROOT=Path(__file__).resolve().parents[1]

def native_grid(which):
    path=ROOT/f"games/tbs/src/map/map_{which}/map.txt"
    header,*content=path.read_text(encoding="utf-8").splitlines()
    assert header.startswith("grid:128x128")
    settings=dict(z.split(":",1) for z in header.split("\t")[1:])
    ax,ay=map(int,settings.get("at","0,0").split(","))
    fill=settings.get("fill","0").split(":")[0]
    rows=[[fill for _ in range(128)] for _ in range(128)]
    for yi,row in enumerate(content):
        for xi,token in enumerate(row.split()):
            if ay+yi<128 and ax+xi<128:rows[ay+yi][ax+xi]=token
    n=0
    for y in range(128):
        for x in range(128):
            p=rows[y][x].split(":")
            v=int(p[0],16)
            if (v&4095)==4095:
                p[0]=format((v&0xf000)|n,"x")
                rows[y][x]=":".join(p)
                n+=1
    expected=len((ROOT/f"games/tbs/src/map/map_{which}/metatiles.tsv").read_text().splitlines())-1
    assert n==expected,(which,n,expected)
    return rows

def make_eruption():
    # Map009 = the actual Vale eruption scene, but it uses tileset set_08,
    # NOT set_02. Never import its metatile values or palette directly into
    # Aster's Map003/set_02 graph without a tested art conversion.
    grid=native_grid("009")
    from csv import reader
    with (ROOT/"games/tbs/src/map/map_009/metatiles.tsv").open() as f:
        hdr=next(f)
        meta=[[int(t,0) for t in row] for row in reader(f,delimiter="\t") if row]
    saved_base=render.BASE
    render.BASE=ROOT/"games/tbs/src/graphics/tileset/set_08"
    try:
        blocks,pal,_=render.load_tiles()
    finally:
        render.BASE=saved_base
    w,h=50,32
    canvas=Image.new("RGBA",(w*16,h*16),render.EMPTY_BG)
    bad=set()
    cache={}
    metacache={}
    for xoff,yoff,charbase in ((0,0,0),(0,32,2),(50,0,2)):
        for y in range(h):
            for x in range(w):
                idx=int(grid[y+yoff][x+xoff].split(":")[0],16)&4095
                key=(idx,charbase)
                if key not in metacache:
                    metacache[key]=render.render_metatile(idx,meta,blocks,pal,bad,cache,charbase)
                tile=metacache[key]
                if tile is not None:canvas.alpha_composite(tile,(x*16,y*16))
    out=ROOT/"tools/aster_native_vale_eruption_reference.png"
    canvas.convert("RGB").save(out,optimize=True)
    print("Vale eruption set_08 (NOT compatible with Aster set_02):",out,"metatiles",len(meta),"unmapped",sorted(bad,key=str)[:15])
    if bad:raise AssertionError("Unknown Vale eruption tile reference")

def make_earth_atlas():
    # Show a 13x13-cell ground-only crop of the original Vale field by
    # the original south dirt/stone walk, at true native palette.
    native=town.load_vale()
    blocks,pal,_=render.load_tiles()
    meta=render.load_metatiles()
    bg=render.render_metatile(0xba,meta,blocks,pal,set(),{},0)
    middle=render.render_metatile(0x15,meta,blocks,pal,set(),{},2)
    cols,rows=16,16
    scale=3
    tile_width=52
    tile_height=62
    gridpic=Image.new("RGB",(cols*tile_width,rows*tile_height),(36,41,45))
    draw=ImageDraw.Draw(gridpic)
    bad=set()
    cache={}
    for y in range(rows):
        for x in range(cols):
            # Native Vale ground region around the river bank. Each cell
            # has its actual index & the other BGs are native repeat grass.
            sx,sy=x+1,y+28
            value=int(native[sy][sx].split(":")[0],16)&0xfff
            cell=Image.new("RGBA",(16,16),(132,225,95,255))
            for t in (bg,render.render_metatile(value,meta,blocks,pal,bad,cache,0),middle):
                if t is not None:cell.alpha_composite(t)
            cell=cell.resize((48,48),Image.Resampling.NEAREST)
            px=x*tile_width
            py=y*tile_height
            gridpic.paste(cell.convert("RGB"),(px+2,py+12))
            draw.text((px+2,py),f"{sx},{sy} {value:x}",fill=(255,255,255))
    out=ROOT/"tools/aster_native_earth_atlas.png"
    gridpic.save(out,optimize=True)
    print("Aster dirt reference atlas",out,"errors",len(bad))

if __name__=="__main__":
    make_eruption()
    make_earth_atlas()
