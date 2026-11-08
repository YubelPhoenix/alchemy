#!/usr/bin/env python3
"""Aster residential block — deliberately placed Golden Sun tiles.

A district-scale, non-playable study: three neighboring homes, a shared
lane, two productive gardens, small everyday storage and a pond.
Every building, path, tree, fence, crop and jar has an authored location.
Unlike the earlier rejected attempts, nothing is sprayed onto a mask or
chosen from pixel-edge similarity. Placement must not silently fail.

Uses original Vale Map003 set_02 art only. Does NOT rewrite live Map180,
reassign Aster's story triggers, or claim an emulator collision test.
"""
from collections import deque, Counter
from pathlib import Path
import json
from PIL import Image
import aster_layout as native
import aster_visual_preview as visual

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"tools/aster_handbuilt_residential.png"
ANNOTATED=ROOT/"tools/aster_handbuilt_residential_labels.png"
CROP=ROOT/"tools/aster_handbuilt_residential_closeup.png"
REPORT=ROOT/"tools/aster_handbuilt_residential_report.json"

VALE=native.load_vale()
SIDE=64
GRASS="ba"
EMPTY="15"
# Name, destination x/y, Vale source x/y, width/height, door x/y.
HOMES=(
    ("west cottage",7,10,11,11,9,9,12,19),
    ("east cottage",30,9,19,12,8,9,34,18),
    ("garden cottage",13,30,11,11,9,9,17,39),
)
# A single connected street system *serving the three actual doorways*.
# Routes have explicitly chosen turns, rather than uniformly straight
# parallel roads across all 64 map cells.
STREETS=(
    ((12,19),(12,22),(24,22),(24,27)),
    ((34,18),(34,21),(25,21),(24,21),(24,22)),
    ((24,26),(24,42)),
    ((17,39),(17,42),(24,42)),
    ((25,26),(37,26)),
    ((24,42),(24,46)),
)
# Source-backed ORIGINAL two-by-two flower-and-herb beds, adjacent to homes.
BEDS=(
    ("west kitchen I",18,12,10,47),
    ("west kitchen II",21,13,10,47),
    ("west herbs",18,16,10,47),
    ("west vegetables",21,17,10,47),
    ("east flower border",40,12,10,47),
    ("east kitchen I",43,13,10,47),
    ("east kitchen II",40,16,10,47),
    ("south kitchen I",26,31,10,47),
    ("south kitchen II",29,32,10,47),
    ("south herbs",28,35,10,47),
)
# Native Vale low wooden border segments: each original contiguous 4 tiles.
FENCES=(
    ("west garden fence",18,20,12,54),
    ("east garden fence",40,19,12,54),
    ("south garden fence",27,39,12,54),
)
# Original jars and boxes in small *used* clusters rather than random lines.
SUPPLIES=(
    ("west water jar",16,15,17,5),
    ("west stored goods",17,17,17,6),
    ("east rain jar",38,14,17,5),
    ("east provisions",39,17,17,6),
    ("south family jar",10,35,17,5),
    ("south wood supplies",22,36,17,6),
    ("water pail area",38,35,17,5),
)
# Complete, visually intact 4x5 native Vale red/blue tree silhouettes.
# Small pairings shade back gardens and mark the edges of this district.
TREES=(
    ("north west old tree",3,3,4,13),
    ("north west shade",7,3,17,46),
    ("north orchard A",17,3,17,46),
    ("north orchard B",21,3,4,13),
    ("north east elm",37,3,4,13),
    ("north east fir",43,3,17,46),
    ("west lane tree",3,20,17,46),
    ("west lane tree 2",3,25,4,13),
    ("southwest tree",6,39,17,46),
    ("south wooded edge",11,43,4,13),
    ("east bank tree",52,21,17,46),
    ("east bank tree 2",52,27,4,13),
    ("south bank tree",51,36,17,46),
    ("garden shade",34,37,4,13),
)
# A sparse set of hand-selected wildflower dots, no random placement.
WILDFLOWERS=(
    (16,11),(23,12),(24,17),(19,19),
    (39,11),(46,15),(45,19),
    (7,28),(10,27),(10,40),(27,38),
    (29,29),(32,35),(36,29),(36,34),
    (38,39),(47,36),(50,19),
)
# Native pond from Vale: all 3 native layers, nonmagical.
# Source 8..19,38..46 includes a crystal-bearing core; replace only
# the shrine cells, with actual original Vale open-water ripple tiles.
POND=(40,24,8,38,12,9)
WATER_CLEAR=((10,41),(10,42),(10,43),(15,41),(15,43),(16,43))
# The plot keeps space for an actual well in the later town centre.
COMMONS=(24,25)

def make():
    grid=[["0"]*128 for _ in range(128)]
    use=[["."]*SIDE for _ in range(SIDE)]
    installed=Counter()
    stamps=[]
    for y in range(SIDE):
        for x in range(SIDE):
            grid[y][x]=GRASS
            grid[y][x+64]=EMPTY
            grid[y+64][x]=EMPTY
        use[y][0]=use[y][63]="#"
    use[0]=["#"]*SIDE
    use[63]=["#"]*SIDE

    def check_free(kind,coords):
        for x,y in coords:
            assert 1<=x<=62 and 1<=y<=62,(kind,"boundary",x,y)
            assert use[y][x]==".",(kind,"overlap",x,y,use[y][x])
            assert grid[y][x]==GRASS and grid[y][x+64]==EMPTY \
                   and grid[y+64][x]==EMPTY,(
                       kind,"layer overlap",x,y,grid[y][x],grid[y][x+64])
    def fill_art(name,dx,dy,sx,sy,w,h,solid=True,copy_ground=False):
        coords=[(dx+ix,dy+iy) for iy in range(h) for ix in range(w)]
        check_free(name,coords)
        for iy in range(h):
            for ix in range(w):
                x,y=dx+ix,dy+iy
                use[y][x]="H" if name.startswith("home ") else "S"
                ground=(VALE[sy+iy][sx+ix].split(":")[0]
                        if copy_ground else GRASS)
                grid[y][x]=ground+(":ff" if solid else "")
                grid[y][x+64]=VALE[sy+iy][sx+ix+30]
                grid[y+64][x]=VALE[sy+iy][sx+ix+60]
        installed[name]+=1
        stamps.append((name,dx,dy,w,h))
    # Reserve the housing footprints before laying roads.
    for name,x,y,sx,sy,w,h,doorx,doory in HOMES:
        fill_art("home "+name,x,y,sx,sy,w,h)
        assert doory==y+h and x<=doorx<x+w

    # Dirt streets are 2 native metatiles wide, hugging home thresholds.
    road=set()
    def line(start,end):
        x,y=start
        tx,ty=end
        assert x==tx or y==ty,("road must have deliberate axis turn",start,end)
        while True:
            yield x,y
            if x==tx and y==ty:break
            if x!=tx:x+=1 if tx>x else -1
            else:y+=1 if ty>y else -1
    for chain in STREETS:
        for a,b in zip(chain,chain[1:]):
            for x,y in line(a,b):
                for p in ((x,y),(x+1,y)) if x==b[0]==a[0] else ((x,y),(x,y+1)):
                    px,py=p
                    if 1<=px<63 and 1<=py<63 and use[py][px]==".":
                        road.add((px,py))
    # A *small* shared lane-side commons, not an enormous town square.
    for y in range(24,28):
        for x in range(21,29):
            if use[y][x]==".":road.add((x,y))
    for x,y in road:
        use[y][x]="="
    for x,y in road:
        west=(x-1,y) in road;east=(x+1,y) in road
        north=(x,y-1) in road;south=(x,y+1) in road
        # Native Vale shoulder and soil metatiles.
        if not west and east:src=(4,39)
        elif west and not east:src=(8,39)
        elif not north and south:src=(6,38)
        elif north and not south:src=(6,40)
        else:src=(6,39)
        grid[y][x]=VALE[src[1]][src[0]].split(":")[0]
    installed["road_cells"]=len(road)

    # Natural ordinary pond, located away from doors and homes. The source
    # bank outline is preserved; no blue rectangle or imported water.
    dx,dy,sx,sy,w,h=POND
    check_free("pond",[(dx+ix,dy+iy) for iy in range(h) for ix in range(w)])
    for iy in range(h):
        for ix in range(w):
            x,y=dx+ix,dy+iy
            sx2,sy2=sx+ix,sy+iy
            ground=VALE[sy2][sx2].split(":")[0]
            mid=VALE[sy2][sx2+30]
            high=VALE[sy2][sx2+60]
            # Clear the known central pedestal, leaving original shore tiles
            # and original water ripple variety intact, not 3b7 dark fill.
            if 11<=sx2<=16 and 41<=sy2<=44:
                mx,my=WATER_CLEAR[(ix+2*iy)%len(WATER_CLEAR)]
                ground=VALE[my][mx].split(":")[0]
                mid=high="15"
            if sy2==45 and 12<=sx2<=15:
                mid=high="15"
            grid[y][x]=ground
            grid[y][x+64]=mid
            grid[y+64][x]=high
            use[y][x]="~" if 9<=sx2<=18 and 39<=sy2<=45 else "P"
    installed["native_pond_cells"]=w*h

    for name,x,y,sx,sy in TREES:
        coords=[(x+ix,y+iy) for iy in range(5) for ix in range(4)]
        check_free(name,coords)
        for iy in range(5):
            for ix in range(4):
                px,py=x+ix,y+iy
                use[py][px]="T"
                grid[py][px]=GRASS+":ff"
                mid=VALE[sy+iy][sx+ix+30]
                if (sx,sy,ix,iy)==(4,13,3,4):mid="15"
                grid[py][px+64]=mid
                grid[py+64][px]=VALE[sy+iy][sx+ix+60]
        installed["complete_trees"]+=1
    for name,x,y,sx,sy in BEDS:
        coords=[(x+ix,y+iy) for iy in range(2) for ix in range(2)]
        check_free(name,coords)
        for iy in range(2):
            for ix in range(2):
                px,py=x+ix,y+iy
                use[py][px]="f"
                grid[py][px]=VALE[sy+iy][sx+ix].split(":")[0]
                grid[py][px+64]=VALE[sy+iy][sx+ix+30]
                grid[py+64][px]=VALE[sy+iy][sx+ix+60]
        installed["cultivated_beds"]+=1
    for name,x,y,sx,sy in FENCES:
        check_free(name,[(x+ix,y) for ix in range(4)])
        for ix in range(4):
            px=x+ix
            use[y][px]="F"
            grid[y][px]=GRASS+":ff"
            grid[y][px+64]=VALE[sy][sx+ix+30]
            grid[y+64][px]=VALE[sy][sx+ix+60]
        installed["whole_fences"]+=1
    for name,x,y,sx,sy in SUPPLIES:
        check_free(name,[(x,y)])
        use[y][x]="B"
        grid[y][x]=GRASS+":ff"
        grid[y][x+64]=VALE[sy][sx+30]
        grid[y+64][x]=VALE[sy][sx+60]
        installed["household_supplies"]+=1
    for x,y in WILDFLOWERS:
        check_free("flower",( (x,y), ))
        source_x,source_y=5,49
        grid[y][x]=VALE[source_y][source_x].split(":")[0]
        grid[y][x+64]=VALE[source_y][source_x+30]
        grid[y+64][x]=VALE[source_y][source_x+60]
        use[y][x]="v"
        installed["wildflowers"]+=1

    # Verify the exact doorstep and surrounding walkable squares.
    doorpoints=[(house[-2],house[-1]) for house in HOMES]
    for x,y in doorpoints:
        assert use[y][x] in ".=",("house entrance blocked",x,y,use[y][x])
        for nx,ny in ((x,y+1),(x-1,y),(x+1,y)):
            assert use[ny][nx] in ".=",("door approach pinched",x,y,nx,ny,use[ny][nx])
    # Pedestrians must be able to reach all three homes and both pond-side
    # outlook and shared commons, without cutting through trees or water.
    walkable={".","=","v","f"}
    q=deque([(24,46)])
    visited=set()
    while q:
        x,y=q.popleft()
        if (x,y) in visited or not(1<=x<=62 and 1<=y<=62):continue
        if use[y][x] not in walkable:continue
        visited.add((x,y))
        q.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
    targets=[*doorpoints,COMMONS,(38,27),(24,46)]
    assert all(p in visited for p in targets),(
        "disconnected",[(p,use[p[1]][p[0]]) for p in targets if p not in visited])
    assert installed["complete_trees"]==len(TREES)
    assert installed["cultivated_beds"]==len(BEDS)
    assert installed["whole_fences"]==len(FENCES)
    assert installed["household_supplies"]==len(SUPPLIES)
    assert installed["wildflowers"]==len(WILDFLOWERS)
    assert len(doorpoints)==3

    print("HAND-AUTHORED ASTER RESIDENTIAL ART STUDY",dict(installed))
    REPORT.write_text(json.dumps({
        "source":"Original Golden Sun Vale Map003 three-layer tile graphics",
        "status":"VISUAL STUDY ONLY — not an integrated ROM map",
        "placed":dict(installed),"homes":len(HOMES),
        "doorways_reachable":len(doorpoints),"pond_present":True,
        "automatic_placements":0,"silent_skips":0,
        "not_yet_tested":["visual approval","emulator priorities",
          "movement flags","story events","house interiors","world connection"]
    },indent=2)+"\n",encoding="utf-8")
    return grid,use

def main():
    grid,use=make()
    prior=visual.load_map
    labels=visual.LOCATIONS
    try:
        visual.load_map=lambda:grid
        visual.LOCATIONS={
           "West home":(12,19),"East home":(34,18),
           "Garden home":(17,39),"Shared lane":COMMONS,
           "Pond":(44,28),
        }
        visual.make(OUT,ANNOTATED)
    finally:
        visual.load_map=prior
        visual.LOCATIONS=labels
    Image.open(OUT).crop((2*16,2*16,55*16,49*16)).save(
        CROP,optimize=True)
    print("Preview:",OUT,CROP)
    print("The actual Aster map and story scene have NOT been modified.")

if __name__=="__main__":
    main()
