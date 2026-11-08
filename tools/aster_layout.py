#!/usr/bin/env python3
"""Aster's native-Golden-Sun exterior, using Vale (Map003) tiles only.

This draws a new 64x64 experimental village from small original *complete*
Vale cottage footprints and Vale grass. It never uses the rejected Paradox art.
The world/dialogue scene, NPCs and eight step events stay in Aster's overlay.
"""
import argparse
from collections import deque
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/"games/tbs/src/map/map_180/map.txt"
NATIVE=ROOT/"games/tbs/src/map/map_003/map.txt"
NATIVE_METATILES=ROOT/"games/tbs/src/map/map_003/metatiles.tsv"
SIDE=64
# Name, destination (x,y), source Vale (x,y), width, height, marker.
# Original Vale has ground (x, y), middle (x+30,y), overhead (x+60,y).
# Crop complete houses, not the partial architecture from Vault Map019.
BUILDINGS=(
    ("sealed_house", 5, 3, 9, 2, 9, 11, "X"),
    ("inn", 45, 3, 19, 2, 9, 11, "I"),
    ("western_home", 5, 24, 11, 11, 9, 11, "H"),
    ("eastern_home", 50, 24, 19, 12, 9, 11, "H"),
    ("shop", 4, 44, 8, 27, 12, 10, "S"),
    ("duplicate_home", 50, 44, 11, 11, 9, 11, "V"),
)
# Outdoor step-on locations. House interiors are still a separate task.
INTERACTIONS=(
    ("memorial", 32, 14, "ba:e2"),
    ("well", 32, 35, "ba:e1"),
    ("sealed_house", 8, 19, "ba:e3"),
    ("inn", 53, 19, "ba:e4"),
    ("western_home", 8, 40, "ba:e5"),
    ("eastern_home", 55, 40, "ba:e6"),
    ("shop", 8, 60, "ba:e7"),
    ("duplicate_home", 55, 60, "ba:e8"),
)
ACTORS=((26,33),(49,21),(23,34),(35,39),(45,34),(36,13),(41,34))
WELL=(32,34)
MEMORIAL=(32,13)
EXIT=(32,63)
START=(32,61)
# Vale's broad repeatable grass metatile. 0x2b also appears as its
# source map's outside-grid fill but is NOT a replacement for all yard art.
GRASS="ba"

def load_vale():
    lines=NATIVE.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("grid:128x128")
    fields=dict(x.split(":",1) for x in lines[0].split("\t")[1:])
    fx,fy=map(int,fields.get("at","0,0").split(","))
    fill=fields.get("fill","0").split(":")[0]
    result=[[fill for _ in range(128)] for _ in range(128)]
    for row,line in enumerate(lines[1:]):
        y=fy+row
        if y>=128:break
        for col,token in enumerate(line.split()):
            x=fx+col
            if x<128:result[y][x]=token
    # Golden Sun's first-use 0xFFF placeholders are converted to sequential
    # metatile table entries across the WHOLE 128x128 original source.
    next_id=0
    for y in range(128):
        for x in range(128):
            parts=result[y][x].split(":")
            packed=int(parts[0],16)
            if (packed & 0xfff)==0xfff:
                parts[0]=format((packed&0xf000)|next_id,"x")
                result[y][x]=":".join(parts)
                next_id+=1
    expected=len(NATIVE_METATILES.read_text(encoding="utf-8").splitlines())-1
    assert next_id==expected, (next_id,expected)
    return result

def blueprint():
    cells=[["." for _ in range(SIDE)] for _ in range(SIDE)]
    for y in range(SIDE):
        cells[y][0]="#"
        cells[y][-1]="#"
    cells[0]=["#"]*SIDE
    cells[-1]=["#"]*SIDE
    for y in range(1,SIDE-1):
        c=32 if y<21 else 33 if y<42 else 31
        for x in range(c-2,c+2): cells[y][x]="="
    for y0,y1 in ((19,21),(40,42),(60,62)):
        for y in range(y0,y1+1):
            for x in range(2,62):cells[y][x]="="
    for y in range(29,39):
        for x in range(28,38):cells[y][x]="="
    for _,dx,dy,sx,sy,w,h,char in BUILDINGS:
        for y in range(dy,dy+h):
            for x in range(dx,dx+w):
                assert cells[y][x] not in ("#","="), ("Overlapping house",x,y)
                cells[y][x]=char
    cells[MEMORIAL[1]][MEMORIAL[0]]="M"
    cells[WELL[1]][WELL[0]]="W"
    cells[EXIT[1]][EXIT[0]]="G"
    return tuple("".join(r) for r in cells)

LAYOUT=blueprint()
def validate_layout():
    assert len(LAYOUT)==SIDE and all(len(r)==SIDE for r in LAYOUT)
    assert LAYOUT[63][32]=="G" and sum(r.count("G") for r in LAYOUT)==1
    assert all(LAYOUT[63][x]=="#" for x in range(64) if x!=32)
    for _,x,y,_ in INTERACTIONS:assert LAYOUT[y][x] in ".="
    walkable=set()
    queue=deque([START])
    while queue:
        x,y=queue.popleft()
        if (x,y) in walkable or not(0<=x<64 and 0<=y<64):continue
        if LAYOUT[y][x] not in ".=G":continue
        walkable.add((x,y))
        for p in ((x-1,y),(x+1,y),(x,y-1),(x,y+1)):queue.append(p)
    assert all(p in walkable for p in (EXIT,START,*ACTORS,
        *((x,y) for _,x,y,_ in INTERACTIONS))),"Actor, trigger or gate blocked"

def source():
    validate_layout()
    vale=load_vale()
    out=[["0" for _ in range(128)] for _ in range(128)]
    for y in range(SIDE):
        for x in range(SIDE):
            mark=LAYOUT[y][x]
            if mark=="#":out[y][x]=GRASS+":ff"
            elif mark=="G":out[y][x]=GRASS+":1"
            elif mark in "MW":out[y][x]=GRASS+":ff"
            else:out[y][x]=GRASS
    for _,dx,dy,sx,sy,w,h,_ in BUILDINGS:
        for yy in range(h):
            for xx in range(w):
                val=vale[sy+yy][sx+xx]
                # Temporary solid facade footprint. Preserve original pixel
                # art and layers, without importing Vale's story behaviors.
                out[dy+yy][dx+xx]=val.split(":")[0]+":ff"
                out[dy+yy][dx+xx+64]=vale[sy+yy][sx+xx+30]
                out[dy+yy+64][dx+xx]=vale[sy+yy][sx+xx+60]
    for _,x,y,token in INTERACTIONS:out[y][x]=token
    return ("grid:128x128\tat:0,0\tfill:0\n"+
            "\n".join(" ".join(row) for row in out)+"\n")

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    a=parser.parse_args()
    result=source()
    if a.check:
        assert DEST.read_text(encoding="utf-8")==result, "Aster generated map drift"
        print("PASS native Golden Sun Vale-based Aster 64x64 grid + 6 complete house crops")
    else:
        DEST.write_text(result,encoding="utf-8")
        print("Wrote",DEST)
if __name__=="__main__":
    main()
