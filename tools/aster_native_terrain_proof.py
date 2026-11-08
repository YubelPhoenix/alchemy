#!/usr/bin/env python3
"""Aster: exact Golden Sun Vale set_02 terrain material proof.

Shows coherent *unaltered original source terrain* at native 16px per cell,
with machine-readable resolved 3-layer map cells and behavior tokens.
These panels are source-art references, NOT an approved Aster map, not
rearranged tiles, and not an emulator capture. Deliberately never paste
rectangular source fragments onto Aster's grass. This is the prerequisite
to an artist-authored seamless new cliff/road/water transition.
"""
from pathlib import Path
import json
from PIL import Image,ImageDraw
import aster_layout as vale
import aster_visual_preview as art

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"tools/aster_native_terrain_proof.png"
DATA=ROOT/"tools/aster_native_terrain_proof.json"
# Name, source x/y and width/height in Vale Map003 16x16 metatiles;
# all sourced from Vale 30x57 with layer offsets +30/+60 in x.
REGIONS=(
    ("cliff_and_footpath",0,12,10,13),
    ("terrace_and_trees",16,18,14,14),
    ("original_water_shore",8,38,12,9),
    ("south_woodland_edge",0,48,12,9),
)
PANEL_W,PANEL_H=480,520
SCALE=2

def main():
    blocks,palette,source_sizes=art.load_tiles()
    metatiles=art.load_metatiles()
    original=vale.load_vale()  # crucial: resolve Vale original 0xFFF indices
    problems=set()
    tile_cache={}
    meta_cache={}
    def draw_metatile(token,base):
        m=int(token.split(":")[0],16)&0xFFF
        key=m,base
        if key not in meta_cache:
            meta_cache[key]=art.render_metatile(
                m,metatiles,blocks,palette,problems,tile_cache,base)
        return meta_cache[key]

    poster=Image.new("RGB",(PANEL_W*2,PANEL_H*2),(25,30,34))
    pen=ImageDraw.Draw(poster)
    output={
        "name":"Original Golden Sun Vale native terrain study",
        "source_map":"games/tbs/src/map/map_003/map.txt",
        "metatiles":"games/tbs/src/map/map_003/metatiles.tsv",
        "graphics_set":"games/tbs/src/graphics/tileset/set_02",
        "source_layer_windows":[[0,0],[30,0],[60,0]],
        "cell_pixels":16,
        "is_playable_aster":False,
        "has_new_aster_tilemap":False,
        "source_sizes":source_sizes,
        "regions":[]
    }
    for idx,(name,sx,sy,w,h) in enumerate(REGIONS):
        assert sx>=0 and sy>=0 and sx+w<=30 and sy+h<=57
        tile_img=Image.new("RGBA",(w*16,h*16),art.EMPTY_BG)
        tokens=[]
        collision=0
        ids=set()
        for y in range(h):
            line=[]
            for x in range(w):
                xx,yy=sx+x,sy+y
                native_tokens=[original[yy][xx+dx] for dx in (0,30,60)]
                line.append(native_tokens)
                collision+=int(":ff" in native_tokens[0])
                for tok,base in zip(native_tokens,(0,2,2)):
                    tile=draw_metatile(tok,base)
                    if tile is not None:
                        tile_img.alpha_composite(tile,(x*16,y*16))
                    ids.add(int(tok.split(":")[0],16)&4095)
            tokens.append(line)
        im=tile_img.resize((w*16*SCALE,h*16*SCALE),Image.Resampling.NEAREST)
        ox,oy=(idx%2)*PANEL_W,(idx//2)*PANEL_H
        pen.text((ox+10,oy+9),name.replace("_"," ").upper(),
                 fill=(255,255,255))
        pen.text((ox+10,oy+26),f"Vale x={sx}:{sx+w-1} y={sy}:{sy+h-1} | {w}x{h} cells",
                 fill=(178,195,200))
        if im.width>PANEL_W-18 or im.height>PANEL_H-62:
            # Reference is cropped, never distorted: retain exact 2x pixels.
            im=im.crop((0,0,min(im.width,PANEL_W-18),min(im.height,PANEL_H-62)))
        poster.paste(im.convert("RGB"),(ox+10,oy+48))
        pen.text((ox+10,oy+PANEL_H-17),
                 f"3 unmodified native layers | {len(ids)} unique IDs",
                 fill=(198,213,218))
        output["regions"].append({
            "name":name,"origin":[sx,sy],"size":[w,h],
            "native_ground_collision_ff_cells":collision,
            "distinct_3layer_metatiles":len(ids),
            "resolved_original_token_grid":tokens,
        })
    if problems:
        raise AssertionError(f"Invalid original Golden Sun tiles: {sorted(problems,key=str)[:15]}")
    poster.save(OUT,optimize=True)
    DATA.write_text(json.dumps(output,indent=2)+"\n",encoding="utf-8")
    print("PASS original Golden Sun 3-layer metatiles/graphics:",len(metatiles))
    for p in output["regions"]:
        print(p["name"],p["origin"],p["size"],"IDs",p["distinct_3layer_metatiles"])
    print("Original terrain proof:",OUT)
    print("Exact source tiles and ground behavior:",DATA)
    print("No gameplay, scene, palette, generated-town art or Map180 changed.")
if __name__=="__main__": main()
