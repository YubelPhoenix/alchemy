#!/usr/bin/env python3
"""Aster's first complete *inhabited ecology* study, native Golden Sun only.

Unlike the rejected forest/cliff cards, this places FULL native Golden Sun
tree silhouettes in loose interlocking groves, dots native pink wildflowers
through property edges, clusters domestic jars/crates at working buildings,
and links an ordinary nonmagical pond to the east residential lane.

The six exterior scene sites and all 8 story triggers remain conceptual;
the playable Map180, Aster C scene, interiors and world exit are UNCHANGED.
"""
from pathlib import Path
from collections import deque
from PIL import Image
import aster_lived_in_blockout as town
import aster_water_feature_study as water
import aster_visual_preview as render

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"tools/aster_lived_in_ecology.png"
ANNOTATED=ROOT/"tools/aster_lived_in_ecology_labels.png"
FOCUS=ROOT/"tools/aster_lived_in_ecology_focus.png"
NATIVE=town.NATIVE

# Each is a complete 4x5 original Vale silhouette, NOT a square ground
# crop. Many touch shoulder-to-shoulder as small copse groups. Where an
# existing road, house or garden occupies a footprint, skip the whole
# tree rather than cut its canopy in half.
COPSES=(
  # Northern woodland is a set of adjoining groves, not lone trees.
  ("nw1",1,1,17,46),("nw2",5,1,4,13),("nw3",1,6,4,13),
  ("n_mid1",18,1,4,13),("n_mid2",22,1,17,46),
  ("n_mid3",26,1,4,13),("n_mid4",30,1,17,46),
  ("n_mid5",20,6,4,13),("n_mid6",24,6,17,46),
  ("ne1",50,1,4,13),("ne2",54,1,17,46),
  ("ne3",58,1,4,13),("ne4",54,6,17,46),
  ("ne5",58,6,4,13),
  # Older northern side lanes, modest surrounding home gardens
  ("north_lane_w",18,15,17,46),("north_lane_e",34,16,4,13),
  ("w_cottage_a",18,21,17,46),("w_cottage_b",22,22,4,13),
  ("w_cottage_c",19,26,4,13),
  ("e_cottage_a",46,22,17,46),("e_cottage_b",50,22,4,13),
  ("e_cottage_c",46,27,4,13),
  # Thick western hedge that frames village work/market lanes.
  ("west1",1,18,17,46),("west2",1,23,4,13),
  ("west3",1,28,17,46),("west4",1,33,4,13),
  ("west5",1,38,17,46),("west6",5,38,4,13),
  ("west7",1,43,4,13),("west8",5,43,17,46),
  ("west9",1,48,17,46),("west10",5,48,4,13),
  ("west11",1,53,4,13),("west12",5,53,17,46),
  ("west13",9,54,4,13),("west14",13,54,17,46),
  ("west15",1,58,17,46),("west16",5,58,4,13),
  ("west17",9,59,17,46),("west18",13,59,4,13),
  ("west19",17,58,17,46),
  # Water-side natural buffer, inn service yard and east boundary.
  ("east1",55,17,17,46),("east2",59,17,4,13),
  ("east3",55,22,4,13),("east4",59,22,17,46),
  ("east5",55,27,17,46),("east6",59,27,4,13),
  ("east7",55,44,4,13),("east8",59,44,17,46),
  ("east9",55,49,17,46),("east10",59,49,4,13),
  ("east11",55,54,4,13),("east12",59,54,17,46),
  ("east13",51,57,17,46),("east14",47,57,4,13),
  ("east15",43,57,17,46),
)
SUPPLIES=(
  ("west_water_jar",18,32,17,5),
  ("west_woodpile",20,33,17,6),
  ("east_work_crate",46,31,17,6),
  ("east_water_jar",46,35,17,5),
  ("shop_stock_a",19,42,17,6),
  ("shop_stock_b",20,40,17,6),
  ("inn_wash_jar",48,48,17,5),
  ("inn_crate",50,48,17,6),
  ("shore_water_jar",48,39,17,5),
)
# Existing source native 2x2 garden art, adjacent to productive yards.
ADDITIONAL_GARDENS=(
  ("west_veg",18,34,10,47,2,2),
  ("west_herbs",21,34,10,47,2,2),
  ("east_veg",31,31,10,47,2,2),
  ("east_herbs",34,33,10,47,2,2),
  ("market_flower",21,46,10,47,2,2),
  ("inn_flower",30,46,10,47,2,2),
)

def ecological_study():
    saved=town.empty_map
    saved_trees=town.TREES
    town.empty_map=water.source_water()
    # Existing isolated Vale tree placements are rejected as the default
    # geometry. Replant deliberate groups from COPSES instead; otherwise
    # they block every useful connected grove we try to construct.
    town.TREES=()
    try:
        rows,use=town.make()
    finally:
        town.empty_map=saved
        town.TREES=saved_trees
    coverage={"trees":0,"gardens":0,"supplies":0,"pink_meadow":0,
              "shore_path":0,"skipped":[]}
    def clear(cells):
        return all(1<=x<=62 and 1<=y<=62 and use[y][x]=="." for x,y in cells)
    def set_native_upper(x,y,sx,sy):
        rows[y][x]="ba:ff"
        rows[y][x+64]=NATIVE[sy][sx+30]
        rows[y+64][x]=NATIVE[sy][sx+60]
    # Make a short walk to the ordinary east-bank pond. The existing
    # east-home lane continues to the water rather than ending in grass.
    shore_path=((45,35),(46,35),(47,35),(48,35),(49,35),
                (47,36),(48,36),(49,36),(48,37),(49,37))
    for x,y in shore_path:
        if use[y][x]==".":
            use[y][x]="="
            rows[y][x]=NATIVE[39][6].split(":")[0]
            coverage["shore_path"]+=1
    for name,x,y,sx,sy in COPSES:
        cells=[(x+dx,y+dy) for dy in range(5) for dx in range(4)]
        if not clear(cells):
            coverage["skipped"].append(name)
            continue
        for dy in range(5):
            for dx in range(4):
                xx,yy=x+dx,y+dy
                use[yy][xx]="T"
                rows[yy][xx]="ba:ff"
                mid=NATIVE[sy+dy][sx+dx+30]
                if (sx,sy,dx,dy)==(4,13,3,4):mid="15"
                rows[yy][xx+64]=mid
                rows[yy+64][xx]=NATIVE[sy+dy][sx+dx+60]
        coverage["trees"]+=1
    for name,x,y,sx,sy,w,h in ADDITIONAL_GARDENS:
        cells=[(x+dx,y+dy) for dy in range(h) for dx in range(w)]
        if not clear(cells):
            coverage["skipped"].append(name)
            continue
        for dy in range(h):
            for dx in range(w):
                xx,yy=x+dx,y+dy
                use[yy][xx]="f"
                rows[yy][xx]=NATIVE[sy+dy][sx+dx].split(":")[0]
                rows[yy][xx+64]=NATIVE[sy+dy][sx+dx+30]
                rows[yy+64][xx]=NATIVE[sy+dy][sx+dx+60]
        coverage["gardens"]+=1
    for name,x,y,sx,sy in SUPPLIES:
        if not clear(((x,y),)):
            coverage["skipped"].append(name)
            continue
        use[y][x]="B"
        set_native_upper(x,y,sx,sy)
        coverage["supplies"]+=1

    # More wildflowers near paths, yards, shops, water, not a deterministic
    # blanket over all meadow. Exact native pink flowers from Vale 5,49
    # (verified as a complete 16px tile in the source atlas).
    FLOWER_SOURCE=(5,49)
    def near_life(x,y):
        if 2<=x<=61 and 4<=y<=55:
            home_near=any(
                bx-6<=x<=bx+bw+6 and by-6<=y<=by+bh+7
                for _,bx,by,_,_,bw,bh in town.BUILDINGS)
            pond_near=45<=x<=61 and 29<=y<=45
            return home_near or pond_near
        return False
    for y in range(3,58):
        for x in range(3,62):
            if use[y][x]!="." or not near_life(x,y):
                continue
            # ~4% within active neighborhoods, biased into small colonies.
            seed=(x*71+y*193+(x//5)*17+(y//7)*23)%97
            if seed not in (3,7,11,23):continue
            sx,sy=FLOWER_SOURCE
            rows[y][x]=NATIVE[sy][sx].split(":")[0]
            rows[y][x+64]=NATIVE[sy][sx+30]
            rows[y+64][x]=NATIVE[sy][sx+60]
            coverage["pink_meadow"]+=1

    # Source-only accessibility check *after* adding water, trees and
    # household props. This isn't a GBA movement-priority test.
    q=deque([town.START])
    visited=set()
    while q:
        x,y=q.popleft()
        if not (0<=x<64 and 0<=y<64) or (x,y) in visited:continue
        if use[y][x] not in ".=G":continue
        visited.add((x,y))
        q.extend(((x-1,y),(x+1,y),(x,y-1),(x,y+1)))
    required=[town.EXIT,*[v[:2] for v in town.DOORS.values()],
              town.MEMORIAL_EVENT,town.WELL_EVENT,
              *[pos for _,pos,_ in town.PEOPLE]]
    assert all(pos in visited for pos in required),[
        pos for pos in required if pos not in visited]
    print("=== Aster ecological village study (NOT PLAYABLE) ===")
    for key,val in coverage.items():print(key,":",val)
    print("All draft actors, 8 narrative interaction sites and gate accessible.")
    return rows,use

def main():
    rows,use=ecological_study()
    old=render.load_map
    loc=render.LOCATIONS
    try:
        render.load_map=lambda:rows
        render.LOCATIONS={
            "Well (unbuilt)":town.WELL,
            "Memorial":town.MEMORIAL_EVENT,
            "Pond":(56,37),
            "Shop":(14,48),
            "Inn":(41,50),
        }
        render.make(OUT,ANNOTATED)
    finally:
        render.load_map=old
        render.LOCATIONS=loc
    Image.open(OUT).crop((2*16,3*16,63*16,63*16)).save(
        FOCUS,optimize=True)
    print("Art study only; original scene/map/save files unchanged.")

if __name__=="__main__":main()
