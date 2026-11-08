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
    # Aster's original geography: a quiet northern remembrance lane,
    # staggered residential cottages, and a southern market by the gate.
    # Golden Sun supplies the art; these are NOT Vale's original locations.
    ("sealed_house",    7,  4,  9,  2,  9,  9, "X"),
    ("duplicate_home", 48,  5, 11, 11,  9,  9, "V"),
    ("western_home",    8, 26, 11, 11,  9,  9, "H"),
    ("eastern_home",   49, 27, 19, 12,  8,  9, "H"),
    ("shop",            6, 45,  8, 27, 10,  9, "S"),
    ("inn",            42, 44, 17, 34, 11, 10, "I"),
)
# Six short, visible-door approaches; no trigger is placed beneath a roof.
DOOR_APPROACHES = (
    ("sealed_house",  12, 13, "ba:e3"),
    ("inn",           47, 54, "ba:e4"),
    ("western_home",  12, 35, "ba:e5"),
    ("eastern_home",  53, 36, "ba:e6"),
    ("shop",          11, 54, "ba:e7"),
    ("duplicate_home",52, 14, "ba:e8"),
)
DOOR_LINK_Y = {
    "sealed_house":18, "duplicate_home":18,
    "western_home":40, "eastern_home":40,
    "shop":57, "inn":57,
}
# Entry narratives are at accessible approach tiles; well and memorial
# themselves remain solid until a satisfactory native visual prop exists.
INTERACTIONS = (
    ("memorial",32,14,"ba:e2"),
    ("well",32,35,"ba:e1"),
) + DOOR_APPROACHES
ACTORS = (
    (26,33), # Elder overlooking residential crossroads
    (46,55), # Innkeeper beside southern market entrance
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
# Original Golden Sun Vale foliage upper planes: a complete blue tree
# (17,46) and autumn-red tree (4,13). This removes the old 4x5 native-ground
# card artifact while retaining solid tree collision. The outer trees are
# staggered to frame Aster's original streets, not lined up like a grid.
# Name, destination (x,y), Vale art source (x,y), width, height.
SCENERY = (
    ("north_woods_w",20,7,17,46,4,5),
    ("north_woods_e",40,6,4,13,4,5),
    ("residential_w",20,27,17,46,4,5),
    ("residential_e",41,25,4,13,4,5),
    ("market_tree_w",22,45,17,46,4,5),
    ("market_tree_e",56,47,4,13,4,5),
    ("north_edge_w",3,17,4,13,4,5),
    ("north_edge_e",57,20,17,46,4,5),
    ("residential_edge_w",3,37,17,46,4,5),
    ("residential_edge_e",57,38,4,13,4,5),
    ("market_edge_w",2,53,17,46,4,5),
    ("market_edge_e",58,55,4,13,4,5),
)
# Small original Vale south-meadow wildflower patches, not foreign props.
# Domestic gardens near occupied homes and shops contrast with the deliberately
# sparse sealed and duplicate houses in the northern district.
# Name, destination, source Vale origin, width/height in 16px cells.
GARDENS = (
    ("west_cottage", 17,34,10,47,2,2),
    ("east_cottage", 45,36,10,47,2,2),
    ("shop_herbs", 17,50,10,47,2,2),
    ("inn_flowers", 38,53,10,47,2,2),
)

# Everyday props distinguish the occupied central/southern buildings from
# Aster's eerily unoccupied northern house pair. All source tiles below come
# from original Golden Sun Vale Map003 / set_02, NOT foreign artwork.
# Name, destination x/y, original Vale source x/y (16px native metatiles).
SUPPLIES = (
    ("west_jar",18,33,17,5),
    ("east_crate",47,33,17,6),
    ("shop_crate",18,52,17,6),
    ("inn_jar",39,55,17,5),
)
# Original Vale low flower-and-wood fence tiles, never reusing Aster's gate.
# Name, destination x/y, native source x/y, length in cells.
YARD_FENCES = (
    ("shop_yard",17,47,12,54,4),
    ("inn_yard",37,49,12,54,4),
)

# Wooden original Vale entrance arch, positioned over the SOUTH road rather
# than as a decorative object in a random yard. It has NO solid footprint.
GATE_ARCH = (29,59, 11,50, 6,3)

# No Psynergy Stone, crystal or shrine: Aster's memorial must be an ordinary
# place of remembrance, not a magical landmark borrowed from Vale.
# Current script trigger and protected patch remain while we test native
# fencing, stones or wooden markers for a different final silhouette.
MEMORIAL_RESERVED = (30,8,5,6)
# Nonmagical remembrance garden: wildflowers and wooden slats from Vale's
# ordinary village fence, with the gate arch excluded. Different silhouette
# and placement from any original Vale monument or Psynergy landmark.
MEMORIAL_GARDEN = (28,11, 10,53, 9,2)

# The old 5x5 crossroads ground crops contained stray blue cliff/water pixels.
# Remove them; the native three-cell roads now paint intersections directly.
PATH_PATCHES = ()

# Each path is two characters wide in the planning blueprint. House entries
# have a short, protected spur connecting to the closest town street.
# Use deliberate stagger to avoid perfect rectangular road symmetry.
def corridors():
    paths=set()
    def rect(x0,y0,x1,y1):
        for y in range(y0,y1+1):
            for x in range(x0,x1+1):
                paths.add((x,y))
    # A crooked market lane and a northern remembrance path; asymmetrical,
    # with businesses concentrated near the south entrance.
    for y in range(1,63):
        center = 32 if y<24 else 31 if y<41 else 33
        rect(center-1,y,center+1,y)
    for y0,y1,left,right in ((18,19,12,53),(40,41,12,54),(57,58,11,53)):
        rect(left,y0,right,y1)
    for name,x,y,_ in DOOR_APPROACHES:
        street=DOOR_LINK_Y[name]
        assert street>=y, (name,y,street)
        rect(x,y,x,street)
    # Plaza: do not draw a road straight through a solid well or memorial.
    rect(28,30,37,39)
    rect(29,11,36,16)
    return paths

PATH_CELLS = corridors()

def native_road_tiles():
    """Paint three-cell roads with intact Golden Sun dirt and grass shoulders.

    Each straight lane has a native soil center and matching Vale edges.
    Native edges are taken from one compatible set_02 dirt family. The
    three-lane intersections use ordinary soil, rather than crossing two
    scalloped shoulders and leaving strips of bright grass in the road.
    Roads remain decorative ground: obstacles and scene behaviors come
    from the blueprint and are never overwritten.
    """
    vertical, horizontal = {}, {}
    def vline(x, y0, y1):
        for y in range(y0, y1+1):
            vertical[(x-1,y)] = (4,39)
            vertical[(x,y)] = (6,39)
            vertical[(x+1,y)] = (8,39)
    def hline(y, x0, x1):
        for x in range(x0, x1+1):
            horizontal[(x,y-1)] = (6,38)
            horizontal[(x,y)] = (6,39)
            horizontal[(x,y+1)] = (6,40)
    for y in range(15,63):
        center = 32 if y<24 else 31 if y<41 else 33
        vline(center,y,y)
    for y,x0,x1 in ((18,12,52),(40,12,53),(57,11,47)):
        hline(y,x0,x1)
    for name,x,y,_ in DOOR_APPROACHES:
        vline(x,y,DOOR_LINK_Y[name])
    roads = {**vertical, **horizontal}
    for point in set(vertical)&set(horizontal):
        roads[point] = (6,39)
    # Sparse wear belongs on the earth center, not the crisp grass borders.
    for (x,y),tile in tuple(roads.items()):
        if tile == (6,39) and (x*11+y*7)%19 == 0:
            roads[(x,y)] = (5,39)
    return {(x,y):tile for (x,y),tile in roads.items()
            if 0<=x<SIDE and 0<=y<SIDE and LAYOUT[y][x] in ".="}

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
    for name,x,y,sx,sy in SUPPLIES:
        assert grid[y][x]==".",f"{name} conflicts with existing scenery"
        grid[y][x]="B"
    for name,x,y,sx,sy,w in YARD_FENCES:
        for xx in range(x,x+w):
            assert grid[y][xx]==".",f"{name} obstructs route or other feature"
            grid[y][xx]="F"
    # The shrine has a physically solid stone body. The (32,14) message
    # trigger stays one cell south of it and can always be approached.
    for yy in range(10,13):
        for xx in range(31,34):
            assert grid[yy][xx] in ".=", "Memorial blocks a building or tree"
            grid[yy][xx]="M"
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
                   range(y,DOOR_LINK_Y[name]+1)),(
            f"{name} has no connected doorway spur")
    blocked=set((x,y) for y,row in enumerate(LAYOUT)
                for x,c in enumerate(row) if c in "#XIHSVTMWBF")
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
            out[y][x]=GRASS+(":ff" if mark in "#MWTBF" else
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
                is_tree=name in {a[0] for a in SCENERY}
                # Keep Aster's real grass under trees. Importing Vale's
                # original ground made the foliage into green-blue squares.
                ground=GRASS if is_tree else vale[sy+yy][sx+xx].split(":")[0]
                out[dy+yy][dx+xx]=ground+(":ff" if is_tree else "")
                # Vale's complete red-tree silhouette has one detached
                # blue fragment in its lower-right source tile. Use the
                # original transparent Golden Sun metatile instead.
                source_mid=vale[sy+yy][sx+xx+30]
                if is_tree and (sx,sy,xx,yy)==(4,13,3,4):
                    source_mid="15"
                out[dy+yy][dx+xx+64]=source_mid
                out[dy+yy+64][dx+xx]=vale[sy+yy][sx+xx+60]
    # Small native Golden Sun jars/crates, with grass under the sprites.
    # Distinct solid footprint prevents Isaac walking through their art.
    for name,x,y,sx,sy in SUPPLIES:
        out[y][x+64]=vale[sy][sx+30]
        out[y+64][x]=vale[sy][sx+60]
    # Fence segments use the intact native Vale timber-and-flower strip,
    # not new textures or an enlarged shrine.
    for name,x,y,sx,sy,w in YARD_FENCES:
        for dx in range(w):
            out[y][x+dx+64]=vale[sy][sx+dx+30]
            out[y+64][x+dx]=vale[sy][sx+dx+60]
    # Kept as an empty extension hook; old 5x5 ground crops were removed
    # after visual QA found blue cliff/water pixels at crossroads.
    for name,dx,dy,sx,sy,w,h in PATH_PATCHES:
        for yy in range(h):
            for xx in range(w):
                gx,gy=dx+xx,dy+yy
                assert LAYOUT[gy][gx] not in "#XIHSVTMW"
                out[gy][gx]=vale[sy+yy][sx+xx].split(":")[0]
    # Native shoulders and a soil center replace sharp, broken intersections.
    # The blueprint still controls walkability and event behavior.
    for (x,y),(sx,sy) in native_road_tiles().items():
        out[y][x]=vale[sy][sx].split(":")[0]
    # The memorial, well and six doorway approach tiles are rewritten at
    # the end to preserve their intentional Aster-only event behaviours.
    # Aster's remembrance garden is a physical row of native village
    # flowers and wooden fencing. NO Psynergy Stone or crystalline monument.
    gx,gy,sx,sy,w,h=MEMORIAL_GARDEN
    for yy in range(h):
        for xx in range(w):
            out[gy+yy][gx+xx+64]=vale[sy+yy][sx+xx+30]
            out[gy+yy+64][gx+xx]=vale[sy+yy][sx+xx+60]
    # Vale's actual wooden arch belongs on Aster's exit road. Keeping the
    # original grassy floor passable is intentional: Isaac walks underneath.
    dx,dy,sx,sy,w,h=GATE_ARCH
    for yy in range(h):
        for xx in range(w):
            out[dy+yy][dx+xx+64]=vale[sy+yy][sx+xx+30]
            out[dy+yy+64][dx+xx]=vale[sy+yy][sx+xx+60]
    for name,x,y,event in INTERACTIONS:
        out[y][x]=event
    return "grid:128x128\tat:0,0\tfill:0:0:0\n" + "\n".join(
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
