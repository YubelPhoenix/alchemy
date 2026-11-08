#!/usr/bin/env python3
"""Aster art-direction comparison using intact native Golden Sun town sets.

Unlike rejected Aster collage studies, these are *unchanged* original
game maps rendered with their own compatible set, palette, metatiles,
and three source layers. Vault and Xian are NOT Aster layouts to copy.
This determines whether a richer native terrain vocabulary should
replace the too-limited Vale set_02 reference.

No changes to Map180, Aster scene code, gameplay art or saves.
"""
from pathlib import Path
from PIL import Image,ImageDraw
import aster_visual_preview as vis

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"tools/aster_original_town_set_comparison.png"

# Confirmed in games/tbs/src/field/scenes.s:
# scene Vault ... graphics set 0x05 ... map id 0x13
# scene Xian  ... graphics set 0x17 ... map id 0x4a
# Each map.s supplies native 8px dimensions and three layer offsets;
# we convert these to 16px metatile cell coordinates.
SOURCES=(
    ("Vault","019","05",60,60,((0,0),(60,0),(0,60))),
    ("Xian","074","17",36,33,((0,0),(36,0),(72,0))),
)

def source_grid(path):
    lines=path.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("grid:128x128")
    header=dict(field.split(":",1) for field in lines[0].split("\t")[1:])
    ox,oy=map(int,header.get("at","0,0").split(","))
    fill=header.get("fill","0:0:0").split(":")[0]
    result=[[fill for x in range(128)] for y in range(128)]
    for dy,line in enumerate(lines[1:]):
        y=oy+dy
        if y>=128:break
        for dx,word in enumerate(line.split()):
            x=ox+dx
            if x<128:result[y][x]=word
    next_index=0
    for yy in range(128):
        for xx in range(128):
            tokens=result[yy][xx].split(":")
            raw=int(tokens[0],16)
            if raw & 0xfff==0xfff:
                tokens[0]=format((raw&0xf000)|next_index,"x")
                result[yy][xx]=":".join(tokens)
                next_index+=1
    return result,next_index

def draw_map(name,map_number,set_number,w,h,offsets):
    vis.BASE=ROOT/f"games/tbs/src/graphics/tileset/set_{set_number}"
    vis.METATILES=ROOT/f"games/tbs/src/map/map_{map_number}/metatiles.tsv"
    src=ROOT/f"games/tbs/src/map/map_{map_number}/map.txt"
    data,resolved=source_grid(src)
    blocks,palette,_=vis.load_tiles()
    meta=vis.load_metatiles()
    assert len(meta)==resolved,(name,"metatile indexing mismatch",resolved,len(meta))
    bad=set()
    cache={}
    mt_cache={}
    canvas=Image.new("RGBA",(w*16,h*16),vis.EMPTY_BG)
    for base,(dx,dy) in zip((0,2,2),offsets):
        for y in range(h):
            for x in range(w):
                raw=int(data[y+dy][x+dx].split(":")[0],16)&4095
                key=raw,base
                if key not in mt_cache:
                    mt_cache[key]=vis.render_metatile(
                        raw,meta,blocks,palette,bad,cache,base)
                pic=mt_cache[key]
                if pic is not None:
                    canvas.alpha_composite(pic,(x*16,y*16))
    out=ROOT/f"tools/aster_reference_{name.lower()}_native.png"
    canvas.convert("RGB").save(out,optimize=True)
    print(name,"native source",w,"x",h,"metatiles,",resolved,
          "resolved originals; unexpected gfx:",sorted(bad,key=str)[:8])
    # A diagnostic reference can contain native game animation or
    # character RAM tiles that static rendering does not reproduce.
    return canvas.convert("RGB"),len(bad)

def main():
    results=[]
    for args in SOURCES:
        name=args[0]
        im,invalid=draw_map(*args)
        results.append((name,im,invalid))
    # Same fixed visual scale, side by side; the comparison is of the
    # original maps, not a new district pretending to use their pixels.
    cols=2;W=720;H=805
    poster=Image.new("RGB",(W*cols,H),(24,28,32))
    d=ImageDraw.Draw(poster)
    for i,(name,im,invalid) in enumerate(results):
        x0=i*W
        d.text((x0+20,14),
               f"{name} — original Golden Sun compatible tileset",
               fill=(245,245,245))
        region=im.copy()
        factor=min((W-40)/region.width,745/region.height)
        nw=int(region.width*factor);nh=int(region.height*factor)
        # Never bilinear blur original pixel art.
        region=region.resize((nw,nh),Image.Resampling.NEAREST)
        poster.paste(region,(x0+20,46))
        d.text((x0+20,775),
               f"Native renderer / {name}; static tile warnings: {invalid}",
               fill=(185,198,201))
    poster.save(OUT,optimize=True)
    print("Original town set review:",OUT)
    print("Not Aster, not a new ROM, not cross-palette mixed assets.")

if __name__=="__main__":main()
