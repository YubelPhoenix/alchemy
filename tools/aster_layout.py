#!/usr/bin/env python3
"""Aster exterior, assembled with ONLY Golden Sun: The Broken Seal (Vale) art.

Use Vale Map003's three original layers, metatile table and palette.
All NPC, doorway and path locations are measured in 16px *map cells*.
No foreign tiles or imaginary tiled PNG is included in the build.

World map entrance, house interiors and dynamic well graphics are unfinished;
this code does not claim to make the experimental scene playable.
"""
import argparse
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT/"games/tbs/src/map/map_180/map.txt"
NATIVE = ROOT/"games/tbs/src/map/map_003/map.txt"
NATIVE_METATILES = ROOT/"games/tbs/src/map/map_003/metatiles.tsv"
SIDE = 64

# House name, destination origin, original Vale origin, x/y extent, symbol.
# Crops are deliberately tight: earlier 11-row versions contained slices
# of cliff and even a second roof from below the first house in Vale.
BUILDINGS = (
    ("sealed_house",   5,  3,  9,  2,  9,  9, "X"),
    ("inn",           45,  3, 19,  2,  9,  9, "I"),
    ("western_home",   5, 24, 11, 11,  9,  9, "H"),
    ("eastern_home",  50, 24, 19, 12,  8,  9, "H"),
    ("shop",           4, 44,  8, 27, 10,  9, "S"),
    ("duplicate_home",50, 44, 11, 11,  9,  9, "V"),
)
# All steps land on grass *outside* a roof, directly ahead of the visible
# Vale door and before the nearest connecting street.
DOOR_APPROACHES = (
    ("sealed_house",  11, 12, "ba:e3"),
    ("inn",           49, 12, "ba:e4"),
    ("western_home",   9, 33, "ba:e5"),
    ("eastern_home",  54, 33, "ba:e6"),
    ("shop",           9, 53, "ba:e7"),
    ("duplicate_home",54, 53, "ba:e8"),
)
# Entry narratives are at accessible approach tiles; well and memorial
# themselves remain solid until a satisfactory native visual prop exists.
INTERACTIONS = (
    ("memorial",32,14,"ba:e2"),
    ("well",32,35,"ba:e1"),
) + DOOR_APPROACHES
ACTORS = (
    (26,33), # Elder overlooking residential crossroads
    (49,21), # Innkeeper just south of inn approach
    (23,34), # Greeter on western residential street
    (35,39), # Boy to the south of the well
    (45,34), # Resident near eastern home
    (36,13), # Other Isaac facing north memorial
    (41,34), # Mirror woman east of the well
)
WELL = (32,34)
MEMORIAL = (32,13)
EXIT = (32,63)
START = (32,61)
# Vale's exact three-layer open grass. Metatile 0xba without 0x15 on both
# upper planes gives repeating foliage, not Golden Sun's bright grass.
GRASS = "ba"
BACKGROUND = (GRASS, "15", "15")

# Three kinds of intact Vale vegetation, placed in rear yards and gardens,
# NEVER on doorstep approaches, arterial routes or the two monuments.
# name, x, y, src_x, src_y, width, height
SCENERY = (
    # Use a complete, coherent native Vale shrub/tree cluster instead of
    # the earlier source crop that contained disconnected cliff pieces.
    ("north_west_tree",20, 6, 24,45, 4,5),
    ("north_east_tree",40, 7, 24,45, 4,5),
    ("west_mid_tree",  19,24, 24,45, 4,5),
    ("east_mid_tree",  40,25, 24,45, 4,5),
    ("south_west_tree",19,47, 24,45, 4,5),
    ("south_east_tree",40,46, 24,45, 4,5),
    ("south_west_shrub",20,52, 24,45, 4,5),
    ("south_east_shrub",41,52, 24,45, 4,5),
)
# Flower/shrub source patches must be approved visually before placement.
# The previous six garden stamps included water and other unrelated graphics.
GARDENS = ()

# Wooden original Vale entrance arch, positioned over the SOUTH road rather
# than as a decorative object in a random yard. It has NO solid footprint.
GATE_ARCH = (29,59, 11,50, 6,3)

# Each path is two characters wide in the planning blueprint. House entries
# have a short, protected spur connecting to the closest town street.
# Use deliberate stagger to avoid perfect rectangular road symmetry.
def corridors():
    paths=set()
    def rect(x0,y0,x1,y1):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):
                paths.add((x,y))
    for y in range(1,63):
        # One continuous north-south axis; widens near the two monuments.
        center = 32 if y<24 else 31 if y<41 else 32
        rect(center-1,y,center+1,y)
    for y0,y1,left,right in ((16,17,11,50),(37,38,9,55),(57,58,9,55)):
        rect(left,y0,right,y1)
    for x,y,limit in ((11,12,17),(49,12,17),(9,33,38),
                       (54,33,38),(9,53,58),(54,53,58)):
        rect(x,y,x,limit)
    # Plaza: do not draw a road straight through a solid well or memorial.
    rect(28,30,37,39)
    rect(29,11,36,16)
    return paths

PATH_CELLS = corridors()

def load_vale():
    lines=NATIVE.read_text(encoding="utf-8").splitlines()
    assert lines[0].startswith("grid:128x128")
    fields=dict(item.split(":",1) for item in lines[0].split("\t")[1:])
    ox,oy=map(int,fields.get("at","0,0").split(","))
    fill=fields.get("fill","0").split(":")[0]
    grid=[[fill for _ in range(128)] for _ in range(128)]
    for rr,line in enumerate(lines[1:]):
        y=oy+rr
        if y>=128:break
        for cc,token in enumerate(line.split()):
            x=ox+cc
            if x<128:grid[y][x]=token
    # First-use 0xFFF placeholders must be resolved in the ORIGINAL grid
    # before any tiles are copied elsewhere, or their images get renumbered.
    next_index=0
    for y in range(128):
        for x in range(128):
            parts=grid[y][x].split(":")
            value=int(parts[0],16)
            if value & 0xfff == 0xfff:
                parts[0]=format((value&0xf000)|next_index,"x")
                grid[y][x]=":".join(parts)
                next_index+=1
    assert next_index==len(NATIVE_METATILES.read_text(encoding="utf-8").splitlines())-1
    return grid

def blueprint():
    grid=[["." for x in range(SIDE)] for y in range(SIDE)]
    for y in range(SIDE):
        grid[y][0]=grid[y][63]="#"
    grid[0]=["#"]*SIDE
    grid[63]=["#"]*SIDE
    for x,y in PATH_CELLS:
        assert 0<x<63 and 0<y<63
        grid[y][x]="="
    for name,dx,dy,sx,sy,w,h,letter in BUILDINGS:
        for y in range(dy,dy+h):
            for x in range(dx,dx+w):
                assert grid[y][x] not in ("=","#","T"),f"{name} overlaps route"
                grid[y][x]=letter
    for name,x,y,sx,sy,w,h in SCENERY:
        for yy in range(y,y+h):
            for xx in range(x,x+w):
                assert grid[yy][xx] == ".",f"{name} obstructs street/building ({xx},{yy})"
                grid[yy][xx]="T"
    for name,x,y,sx,sy,w,h in GARDENS:
        for yy in range(y,y+h):
            for xx in range(x,x+w):
                assert grid[yy][xx]==".",f"{name} obstructs walkway"
                grid[yy][xx]="f"
    grid[MEMORIAL[1]][MEMORIAL[0]]="M"
    grid[WELL[1]][WELL[0]]="W"
    grid[EXIT[1]][EXIT[0]]="G"
    return tuple("".join(r) for r in grid)

LAYOUT = blueprint()

def verify():
    assert len(LAYOUT)==64 and all(len(r)==64 for r in LAYOUT)
    assert sum(r.count("G") for r in LAYOUT)==1 and LAYOUT[63][32]=="G"
    assert all(LAYOUT[63][x]=="#" for x in range(64) if x!=32)
    for name,x,y,event in INTERACTIONS:
        assert LAYOUT[y][x] in ".=",f"{name}: threshold not walkable"
    for name,dx,dy,sx,sy,w,h,mark in BUILDINGS:
        assert all(LAYOUT[y][x]==mark
            for y in range(dy,dy+h) for x in range(dx,dx+w)),name
    for name,x,y,_ in DOOR_APPROACHES:
        match=[b for b in BUILDINGS if b[0]==name]
        assert len(match)==1
        _,dx,dy,sx,sy,w,h,mark=match[0]
        assert dx<=x<dx+w and y==dy+h,(
            f"{name} must sit directly in front of facade at y={dy+h}")
        assert all((x,yy) in PATH_CELLS for yy in
                   range(y,17+1 if y<20 else 38+1 if y<40 else 58+1)),(
            f"{name} has no connected doorway spur")
    blocked=set((x,y) for y,row in enumerate(LAYOUT)
                for x,c in enumerate(row) if c in "#XIHSVTMW")
    require=[START,EXIT]+list(ACTORS)+[(x,y) for _,x,y,_ in INTERACTIONS]
    for pos in require:
        assert pos not in blocked, f"Actor or approach inside solid scenery {pos}"
    visited=set()
    todo=deque([START])
    while todo:
        x,y=todo.popleft()
        if not (0<=x<64 and 0<=y<64) or (x,y) in visited or (x,y) in blocked:
            continue
        visited.add((x,y))
        for nx,ny in ((x+1,y),(x-1,y),(x,y+1),(x,y-1)):
            todo.append((nx,ny))
    assert all(p in visited for p in require),"Aster disconnected by scenery"
    # The central memorial/well may not close the north-south axis.
    for y in range(1,63):
        assert any((x,y) in visited for x in range(29,35)),(
            f"Blocked Aster north/south axis at y={y}")

def source():
    verify()
    vale=load_vale()
    out=[["0" for x in range(128)] for y in range(128)]
    for y in range(SIDE):
        for x in range(SIDE):
            mark=LAYOUT[y][x]
            out[y][x]=GRASS+(":ff" if mark in "#MWT" else
                            ":1" if mark=="G" else "")
            out[y][x+64]=BACKGROUND[1]
            out[y+64][x]=BACKGROUND[2]
    # Houses: copy *only* walls, doors and roof layers. Their original Vale
    # ground includes unrelated cliffs and even roofs of neighboring houses;
    # outside scenery is now Aster's coherent open Vale lawn.
    for name,dx,dy,sx,sy,w,h,mark in BUILDINGS:
        for yy in range(h):
            for xx in range(w):
                out[dy+yy][dx+xx]=GRASS+":ff"
                out[dy+yy][dx+xx+64]=vale[sy+yy][sx+xx+30]
                out[dy+yy+64][dx+xx]=vale[sy+yy][sx+xx+60]
    # Native Vale tree/flower sheets. One intact 3-layer stamp per decoration.
    for name,dx,dy,sx,sy,w,h in (*SCENERY,*GARDENS):
        for yy in range(h):
            for xx in range(w):
                ground=vale[sy+yy][sx+xx].split(":")[0]
                out[dy+yy][dx+xx]=ground+(":ff" if name in {
                    a[0] for a in SCENERY} else "")
                out[dy+yy][dx+xx+64]=vale[sy+yy][sx+xx+30]
                out[dy+yy+64][dx+xx]=vale[sy+yy][sx+xx+60]
    # The earlier repeated Vale source tiles were actually chimney/roof
    # pixels: pink fragments appeared along all three streets. Paths still
    # exist as walkable connected routes in LAYOUT, but are intentionally
    # grass here until we verify a real Vale dirt-path stamp.
    # Vale's actual wooden arch belongs on Aster's exit road. Keeping the
    # original grassy floor passable is intentional: Isaac walks underneath.
    dx,dy,sx,sy,w,h=GATE_ARCH
    for yy in range(h):
        for xx in range(w):
            out[dy+yy][dx+xx+64]=vale[sy+yy][sx+xx+30]
            out[dy+yy+64][dx+xx]=vale[sy+yy][sx+xx+60]
    for name,x,y,event in INTERACTIONS:
        out[y][x]=event
    return "grid:128x128\tat:0,0\tfill:0\n" + "\n".join(
        " ".join(row) for row in out)+"\n"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    a=parser.parse_args()
    data=source()
    if a.check:
        assert DEST.read_text(encoding="utf-8")==data,"Aster grid drift"
        print("PASS Aster door/path/garden/actor map matches scripted generator")
    else:
        DEST.write_text(data,encoding="utf-8")
        print("Wrote",DEST)
if __name__=="__main__":
    main()
