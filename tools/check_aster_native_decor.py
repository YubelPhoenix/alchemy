#!/usr/bin/env python3
"""Read-only source-integrity checks for four Aster native indexed sprites.

Checks payload integrity and correct actor/asset registrations. It does NOT
validate pixel draw priority or house interiors in an emulator.
"""
from pathlib import Path
import hashlib
import struct
import zlib
ROOT=Path(__file__).resolve().parents[1]
SPR=ROOT/"games/tbs/src/graphics/sprite"
ART={
    506:("dry well",(32,32),"aeae246d130ccffafe5acbd82a43411021371e9c"),
    507:("memorial",(32,64),"72fd5ab04960fb70f71132dd59da6009e99ede5e"),
    508:("Sanctum compact facade",(64,64),"bfec51aeb74995a1592fb535b366aa33f8a06ecc"),
    509:("additional home compact facade",(64,64),"34573a21ec50ff4dd2d9196cf4206b511b593928"),
}
NAME={506:"SPRITE_ASTER_DRY_WELL",507:"SPRITE_ASTER_MEMORIAL",
      508:"SPRITE_ASTER_SANCTUM",509:"SPRITE_ASTER_ADDITIONAL_HOME"}
POS={506:(512,544),507:(464,304),508:(672,528),509:(208,912)}
def need(ok,reason):
    if not ok: raise AssertionError(reason)
def blob_sha(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()
def png(path):
    raw=path.read_bytes()
    need(raw[:8]==b"\x89PNG\r\n\x1a\n",f"{path.name}: not a PNG")
    offset=8; palette=None; dims=None; packed=bytearray(); ended=False
    while offset<len(raw):
        need(offset+12<=len(raw),"Truncated PNG")
        length=int.from_bytes(raw[offset:offset+4],"big")
        kind=raw[offset+4:offset+8]
        chunk=raw[offset+8:offset+8+length]
        crc=raw[offset+8+length:offset+12+length]
        need(len(chunk)==length and len(crc)==4,f"{path.name}: truncated chunk")
        need(zlib.crc32(kind+chunk)==int.from_bytes(crc,"big"),
             f"{path.name}: invalid PNG CRC")
        offset+=length+12
        if kind==b"IHDR":
            w,h,depth,color,compression,filtering,interlace=struct.unpack(">IIBBBBB",chunk)
            need((depth,color,compression,filtering,interlace)==(8,3,0,0,0),
                 f"{path.name}: expected 8-bit indexed noninterlaced PNG")
            dims=(w,h)
        elif kind==b"PLTE":palette=chunk
        elif kind==b"tRNS":raise AssertionError("Use original GBA palette index 0, not PNG tRNS")
        elif kind==b"IDAT":packed.extend(chunk)
        elif kind==b"IEND":
            ended=True;break
    need(ended and offset==len(raw),"Unclosed PNG/trailing bytes")
    need(palette is not None and len(palette)==672,"Expected 224-color native sprite palette")
    w,h=dims
    decoded=zlib.decompress(packed)
    need(len(decoded)==h*(w+1),"Unexpected PNG scanline size")
    prev=[0]*w; pixels=[]
    for y in range(h):
        scan=list(decoded[y*(w+1)+1:(y+1)*(w+1)])
        filter_kind=decoded[y*(w+1)]
        for x in range(w):
            a=scan[x-1] if x else 0
            b=prev[x]
            c=prev[x-1] if x else 0
            if filter_kind==0:delta=0
            elif filter_kind==1:delta=a
            elif filter_kind==2:delta=b
            elif filter_kind==3:delta=(a+b)//2
            elif filter_kind==4:
                p=a+b-c
                da,db,dc=abs(p-a),abs(p-b),abs(p-c)
                delta=a if da<=db and da<=dc else b if db<=dc else c
            else:raise AssertionError(f"Unsupported PNG filter: {filter_kind}")
            scan[x]=(scan[x]+delta)&255
        pixels.extend(scan)
        prev=scan
    need(max(pixels)<224,"Pixels exceed the native sprite palette")
    need(pixels[0]==0,"Top-left palette index 0 expected transparent")
    need(sum(x!=0 for x in pixels)>80,"Sprite has too little visible art")
    return dims,palette
def main():
    baseline=png(SPR/"spr_261.png")[1]
    tsv=(SPR/"sprites.tsv").read_text(encoding="utf-8").splitlines()
    layout=(SPR/"layout.tsv").read_text(encoding="utf-8").splitlines()
    ids=(ROOT/"games/tbs/include/sprite_ids.h").read_text(encoding="utf-8")
    scene=(ROOT/"games/tbs/src/scene/aster.c").read_text(encoding="utf-8")
    for id,(label,dims,sha) in ART.items():
        filepath=SPR/f"spr_{id:03d}.png"
        need(blob_sha(filepath.read_bytes())==sha,f"{label}: unexpected edited artwork")
        actual,palette=png(filepath)
        need(actual==dims,f"{label}: wrong sprite size")
        need(palette==baseline,f"{label}: not using original 224-color indexed palette")
        ref=f"SPR_{id:03d}"
        need(layout.count(ref)==1,f"{label}: not exactly once in sprite layout")
        rows=[x for x in tsv if x.startswith(ref+"\t")]
        need(len(rows)==1 and len(rows[0].split("\t"))==12,
             f"{label}: invalid sprite registration")
        need(rows[0].split("\t")[-2:]==[ref,ref],f"{label}: missing art/anim")
        need((SPR/f"spr_{id:03d}.tsv").read_text().startswith("anim\tframe 0"),
             f"{label}: missing native animation definition")
        need(ids.count(NAME[id]+f" = 0x{id:x}")==1,
             f"{label}: symbol uses conflicting sprite id")
        x,y=POS[id]
        need(scene.count(NAME[id])==1,f"{label}: scenery actor not placed uniquely")
        need(scene.count(f"PIXELS({x}), 0, PIXELS({y})")==1,
             f"{label}: wrong scene anchor")
        print(f"PASS {label} indexed native PNG {dims[0]}x{dims[1]} / SPR_{id}")
    maps=(ROOT/"games/tbs/src/map/map_180/map.s").read_text(encoding="utf-8")
    need("map_offset Field_Map180, .LAsterAnimation" in maps
         and "map_003/tileset_anims.script.lz" in maps,
         "Vale native water animation was not registered in Aster Map180")
    print("PASS original Golden Sun 224-colour palette, 4 actor registrations")
    print("PASS native Vale animated water script attached to Map180")
    print("NOT YET PROVED: in-emulator appearance, cliff/bridge art or interiors")
if __name__=="__main__":
    main()
