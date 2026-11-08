#!/usr/bin/env python3
"""Read-only Aster 32x32 native overworld icon registry and PNG integrity audit.

This is source validation, not GBA sprite renderer or route testing.
"""
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
SPRITES = ROOT / "games/tbs/src/graphics/sprite"

def need(ok, what):
    if not ok:
        raise AssertionError(what)

def indexed_png(path):
    raw = path.read_bytes()
    need(raw.startswith(b"\x89PNG\r\n\x1a\n"), f"{path.name}: not PNG")
    pos, palette, compressed = 8, None, b""
    while pos + 12 <= len(raw):
        n = int.from_bytes(raw[pos:pos+4], "big")
        tag = raw[pos+4:pos+8]
        chunk = raw[pos+8:pos+8+n]
        crc = raw[pos+8+n:pos+12+n]
        need(len(chunk)==n and len(crc)==4, "Truncated PNG chunk")
        need(zlib.crc32(tag+chunk)==int.from_bytes(crc,"big"),
             f"{path.name}: bad CRC {tag!r}")
        pos += n+12
        if tag == b"IHDR":
            need(struct.unpack(">IIBBBBB", chunk)==(32,32,8,3,0,0,0),
                 f"{path.name}: native 32x32 indexed PNG required")
        elif tag == b"PLTE":
            palette=chunk
        elif tag == b"tRNS":
            raise AssertionError("Transparency must use palette index 0, not tRNS")
        elif tag == b"IDAT":
            compressed+=chunk
        elif tag == b"IEND":
            break
    need(pos==len(raw) and palette is not None,"Unclosed PNG or trailing bytes")
    need(len(palette)==224*3,"Expected original 224-colour sprite palette")
    scanlines=zlib.decompress(compressed)
    previous=bytearray(32)
    pixels=bytearray()
    cursor=0
    for y in range(32):
        need(cursor+33<=len(scanlines),"Incomplete indexed PNG")
        kind=scanlines[cursor]
        current=bytearray(scanlines[cursor+1:cursor+33])
        cursor+=33
        for x in range(32):
            left=current[x-1] if x else 0
            top=previous[x]
            up_left=previous[x-1] if x else 0
            if kind==0: correction=0
            elif kind==1: correction=left
            elif kind==2: correction=top
            elif kind==3: correction=(left+top)//2
            elif kind==4:
                estimate=left+top-up_left
                nearest=min((left,top,up_left),key=lambda n:abs(n-estimate))
                correction=nearest
            else:raise AssertionError("Unsupported PNG scanline filter")
            current[x]=(current[x]+correction)&255
        previous=current
        pixels.extend(current)
    need(cursor==len(scanlines),"Unexpected PNG data after final row")
    need(max(pixels)<224,"Invalid index outside 224-colour palette")
    return palette,bytes(pixels)

def main():
    source_pal,source=indexed_png(SPRITES/"spr_261.png")
    aster_pal,aster=indexed_png(SPRITES/"spr_505.png")
    need(source_pal==aster_pal,"Custom icon does not use original village palette")
    need(all((a==0)==(b==0) for a,b in zip(source,aster)),
         "Transparency silhouette changed")
    changed=sum(a!=b for a,b in zip(source,aster))
    need(changed>=150,f"Not distinctive enough: {changed} changed pixels")
    lines=(SPRITES/"sprites.tsv").read_text(encoding="utf-8").splitlines()
    def registered(key):
        matches=[line.split("\t") for line in lines if line.startswith(key+"\t")]
        need(len(matches)==1,f"Missing or duplicate registration {key}")
        return matches[0]
    original=registered("SPR_261")
    custom=registered("SPR_505")
    need(custom[:10]==["SPR_505"]+original[1:10],
         "Aster sprite differs in native village dimensions/scale/draw")
    need(custom[10:]==["SPR_505","SPR_505"],
         "Aster art/animation paths are not connected")
    layout=(SPRITES/"layout.tsv").read_text(encoding="utf-8").splitlines()
    need(layout.count("SPR_505")==1,"Aster icon not registered exactly once in layout")
    need((SPRITES/"spr_505.tsv").read_bytes()==(SPRITES/"spr_261.tsv").read_bytes(),
         "Aster animation table not compatible with village sprite")
    ids=(ROOT/"games/tbs/include/sprite_ids.h").read_text(encoding="utf-8")
    need(ids.count("SPRITE_WORLD_MAP_ASTER = 0x1f9")==1,
         "Aster icon ID is not registered at unused slot 505")
    print(f"PASS distinct Aster SPR_505 icon: 32x32, indexed, 224 colours; {changed} changed pixels")
    print("PASS shared palette/transparency, GBA metadata and animation table")
    print("NOT VERIFIED: overworld actor, walkability, world route or emulator rendering")

if __name__=="__main__":
    main()
