#!/usr/bin/env python3
"""Aster LIFE-FIRST blockout using original Golden Sun Vale set_02 art.

This is a non-playable street/yard composition to compare with real Ashfall
town maps. DO NOT replace live Map180 or move scene actors/triggers from this
preview. Preserve the original normal-town map while assessing whether this
plan looks genuinely inhabited rather than merely more decorated.
"""
from collections import deque, Counter
from pathlib import Path
from PIL import Image, ImageDraw
import aster_layout as old
import aster_visual_preview as vis

ROOT=Path(__file__).resolve().parents[1]
NORMAL=ROOT/"tools/aster_lived_in_blockout.png"
LABELS=ROOT/"tools/aster_lived_in_blockout_labels.png"
FOCUS=ROOT/"tools/aster_lived_in_focus.png"
SIZE=64
NATIVE=old.load_vale()

# Function drives all spatial choices: ordinary homes flank a small shared
# commons, businesses face the same market street, the memorial is beyond
# the quieter northern lane. The extra two cottages are CONTEXT studies,
# not functioning interiors or assigned story homes.
BUILDINGS=(
    ("sealed",       8, 6,  9, 2, 9,9),
    ("duplicate",   38, 7, 11,11, 9,9),
    ("west_home",    8,22, 11,11, 9,9),
    ("east_home",   37,24, 19,12, 8,9),
    ("shop",         9,39,  8,27,10,9),
    ("inn",         36,40, 17,34,11,10),
)
DOORS={
    "sealed": (12,15,"e3"),
    "duplicate":(42,16,"e8"),
    "west_home":(12,31,"e5"),
    "east_home":(41,33,"e6"),
    "shop":(14,48,"e7"),
    "inn":(41,50,"e4"),
}
# These are concept-level actor targets; not modified in the playable scene.
PEOPLE=(
    ("elder",(26,23),"memorial keeper / often in commons"),
    ("greeter",(32,55),"welcomes southern arrivals"),
    ("boy",(25,39),"plays near communal yard"),
    ("home_resident",(19,33),"works beside west garden"),
    ("innkeeper",(40,53),"stands outside the inn"),
    ("mirror_woman",(35,36),"crosses the east-home path"),
    ("other_isaac",(34,19),"appears near northern lane"),
)
WELL=(28,35)
WELL_EVENT=(28,36)
MEMORIAL=(28,17)
MEMORIAL_EVENT=(28,19)
EXIT=(32,63)
START=(32,61)
GATE=(29,59,11,50,6,3)
MEMORIAL_GARDEN=(24,16,10,53,9,2)
# Natural tree silhouettes already approved in the single-town map. These
# positions favor field boundaries, rear lanes and property edges rather than
# arbitrary trees in the center of empty squares.
TREES=(
    ("northwest_forest", 3, 5, 17,46),
    ("northwest_shade", 4,17, 4,13),
    ("north_backyard", 19, 4,17,46),
    ("north_hedge", 32, 4, 4,13),
    ("northeast_wood", 49, 7,17,46),
    ("east_old_lane", 50,18, 4,13),
    ("west_lane", 3,27,17,46),
    ("west_yard", 20,25, 4,13),
    ("east_yard", 47,28,17,46),
    ("west_market", 3,42, 4,13),
    ("market_front", 6,50,17,46),
    ("market_rear", 49,43, 4,13),
    ("gate_west", 11,54,17,46),
    ("gate_east", 45,54, 4,13),
    ("southwest_woods", 3,55,17,46),
    ("southeast_woods", 55,56, 4,13),
    ("north_grove", 25, 3,17,46),
)
# Yard use is explicit; native flowers are never random open-lawn sprinkles.
FLOWERS=(
    ("west_kitchen_garden",18,30,10,47,2,2),
    ("east_kitchen_garden",32,31,10,47,2,2),
    ("shop_herb_plot",20,46,10,47,2,2),
    ("inn_small_garden",32,45,10,47,2,2),
)
# One-cell native household items from Vale.
SUPPLIES=(
    ("home_jar",19,29,17,5),
    ("east_crate",34,30,17,6),
    ("shop_supplies",20,42,17,6),
    ("shop_jar",21,43,17,5),
    ("inn_supply",48,47,17,6),
    ("inn_jar",49,49,17,5),
)
# Short native Vale timber-and-flower fence segments. These are fenced
# productive beds alongside a home or trade building, not freestanding hedges.
FENCES=(
    ("west_plot_front",18,32,12,54,4),
    ("east_plot_front",31,29,12,54,4),
    ("shop_front",20,44,12,54,4),
    ("inn_yard_front",31,43,12,54,4),
)

def empty_map():
    rows=[["0"]*128 for _ in range(128)]
    use=[["."]*SIZE for _ in range(SIZE)]
    for y in range(SIZE):
        for x in range(SIZE):
            rows[y][x]="ba"
            rows[y][x+64]="15"
            rows[y+64][x]="15"
    for y in range(SIZE):
        use[y][0]=use[y][-1]="#"
    use[0]=["#"]*SIZE
    use[-1]=["#"]*SIZE
    return rows,use

def make():
    rows,use=empty_map()
    stats=Counter()
    def claim(x,y,name,kind,strict=True):
        if x<1 or x>=63 or y<1 or y>=63 or use[y][x] not in ".=":
            if strict:raise AssertionError((name,x,y,use[y][x] if 0<=x<64 and 0<=y<64 else "off map"))
            return False
        use[y][x]=kind
        return True
    for name,x,y,sx,sy,w,h in BUILDINGS:
        for dy in range(h):
            for dx in range(w):
                claim(x+dx,y+dy,name,"H")
                rows[y+dy][x+dx]="ba:ff"
                rows[y+dy][x+dx+64]=NATIVE[sy+dy][sx+dx+30]
                rows[y+dy+64][x+dx]=NATIVE[sy+dy][sx+dx+60]
        stats["houses"]+=1

    def segment(a,b):
        x,y=a
        tx,ty=b
        yield x,y
        while (x,y)!=(tx,ty):
            if x!=tx and (abs(tx-x)>=abs(ty-y) or y==ty):
                x+=1 if tx>x else -1
            else:
                y+=1 if ty>y else -1
            yield x,y
    # A place grows from shared needs: north lane -> residential commons ->
    # market -> gate. Roads are short, staggered connections, not three
    # edge-to-edge straight corridors.
    PATHS=(
        ((32,62),(32,56),(30,54),(29,51),(28,47),(28,42),(27,38),(27,32),(27,25),(28,20)),
        ((12,15),(12,17),(17,19),(24,20),(28,20)),
        ((42,16),(42,18),(36,20),(28,20)),
        ((12,31),(14,33),(18,35),(25,36)),
        ((41,33),(40,35),(35,37),(29,37)),
        ((14,48),(17,50),(23,51),(29,51)),
        ((41,50),(38,52),(34,53),(30,54)),
        ((28,20),(28,25),(29,30),(28,34)),
    )
    road=set()
    for points in PATHS:
        for a,b in zip(points,points[1:]):
            for x,y in segment(a,b):
                for yy in range(y-1,y+2):
                    for xx in range(x-1,x+2):
                        if 1<=xx<=62 and 1<=yy<=62 and use[yy][xx]==".":
                            road.add((xx,yy))
    # Busy communal apron, smaller and less rectangular than the old town.
    for y in range(34,41):
        for x in range(22,34):
            if ((x-28)/6.2)**2+((y-37)/3.5)**2<1 and use[y][x]==".":
                road.add((x,y))
    for x,y in road:
        use[y][x]="="
    for x,y in road:
        n=(x,y-1) in road
        s=(x,y+1) in road
        w=(x-1,y) in road
        e=(x+1,y) in road
        # Grass-to-earth transitions are original Vale set_02 tiles, never
        # copied cliff backgrounds. Sparse native dirt gives worn town roads.
        if not w and e:src=(4,39)
        elif w and not e:src=(8,39)
        elif not n and s:src=(6,38)
        elif n and not s:src=(6,40)
        else:src=(5,39) if (x*13+y*7)%23==0 else (6,39)
        rows[y][x]=NATIVE[src[1]][src[0]].split(":")[0]
    stats["road_cells"]=len(road)

    # Ordinary wooden remembrance area with native flowers, no magic stone.
    mx,my,sx,sy,mw,mh=MEMORIAL_GARDEN
    for dy in range(mh):
        for dx in range(mw):
            px,py=mx+dx,my+dy
            if use[py][px]=="H":raise AssertionError("Memorial overlaps house")
            use[py][px]="M"
            rows[py][px]="ba:ff"
            rows[py][px+64]=NATIVE[sy+dy][sx+dx+30]
            rows[py+64][px]=NATIVE[sy+dy][sx+dx+60]
    stats["memorial_cells"]=mw*mh

    skipped=[]
    for name,x,y,sx,sy in TREES:
        footprint=[(x+dx,y+dy) for dy in range(5) for dx in range(4)]
        if any(not (1<=px<=62 and 1<=py<=62) or use[py][px] not in "."
               for px,py in footprint):
            skipped.append((name,"not enough clear land"))
            continue
        for dy in range(5):
            for dx in range(4):
                px,py=x+dx,y+dy
                use[py][px]="T"
                rows[py][px]="ba:ff"
                mid=NATIVE[sy+dy][sx+dx+30]
                if (sx,sy,dx,dy)==(4,13,3,4):mid="15"
                rows[py][px+64]=mid
                rows[py+64][px]=NATIVE[sy+dy][sx+dx+60]
        stats["native_tree_groups"]+=1

    for name,x,y,sx,sy,w,h in FLOWERS:
        footprint=[(x+dx,y+dy) for dy in range(h) for dx in range(w)]
        if any(not (1<=px<=62 and 1<=py<=62) or use[py][px] not in "."
               for px,py in footprint):
            skipped.append((name,"garden meets road or facade"))
            continue
        for dy in range(h):
            for dx in range(w):
                px,py=x+dx,y+dy
                use[py][px]="f"
                rows[py][px]=NATIVE[sy+dy][sx+dx].split(":")[0]
                rows[py][px+64]=NATIVE[sy+dy][sx+dx+30]
                rows[py+64][px]=NATIVE[sy+dy][sx+dx+60]
        stats["garden_plots"]+=1

    for name,x,y,sx,sy in SUPPLIES:
        if not claim(x,y,name,"B",False):
            skipped.append((name,"blocked supply location"))
            continue
        rows[y][x]="ba:ff"
        rows[y][x+64]=NATIVE[sy][sx+30]
        rows[y+64][x]=NATIVE[sy][sx+60]
        stats["domestic_supplies"]+=1
    for name,x,y,sx,sy,w in FENCES:
        if any(use[y][x+dx]!="." for dx in range(w)):
            skipped.append((name,"fence interferes with street/building"))
            continue
        for dx in range(w):
            use[y][x+dx]="F"
            rows[y][x+dx]="ba:ff"
            rows[y][x+dx+64]=NATIVE[sy][sx+dx+30]
            rows[y+64][x+dx]=NATIVE[sy][sx+dx+60]
        stats["yard_fences"]+=1
    # The gate remains at its original south approach to avoid an
    # unsupported fake world-map connection in a source-only study.
    gx,gy,sx,sy,gw,gh=GATE
    for dy in range(gh):
        for dx in range(gw):
            px,py=gx+dx,gy+dy
            rows[py][px+64]=NATIVE[sy+dy][sx+dx+30]
            rows[py+64][px]=NATIVE[sy+dy][sx+dx+60]
    # Preserve a *dry-well site*, not a fake cropped cave mouth. Show a
    # readable marker in labelled preview only until compatible art exists.
    use[WELL[1]][WELL[0]]="W"
    rows[WELL[1]][WELL[0]]="ba:ff"
    use[EXIT[1]][EXIT[0]]="G"
    rows[EXIT[1]][EXIT[0]]="ba:1"
    EVENTS=((MEMORIAL_EVENT,"e2"),(WELL_EVENT,"e1"))+tuple(
        ((x,y),behavior) for x,y,behavior in DOORS.values())
    for (x,y),behavior in EVENTS:
        assert use[y][x] in ".=",("inaccessible event",x,y,use[y][x])
        rows[y][x]="ba:"+behavior
    for name,(x,y),purpose in PEOPLE:
        assert use[y][x] in ".=",("actor misplaced",name,x,y,use[y][x])
    for x,y in (START,):
        assert use[y][x] in ".=",("start blocked",x,y,use[y][x])
    # Basic physical access, not a claim that GBA engine collision works.
    walk={".","=","G"}
    q=deque([START])
    seen=set()
    while q:
        x,y=q.popleft()
        if (x,y) in seen or not (0<=x<64 and 0<=y<64):continue
        if use[y][x] not in walk:continue
        seen.add((x,y))
        q.extend(((x+1,y),(x-1,y),(x,y+1),(x,y-1)))
    targets=[EXIT,*[p for p,v in EVENTS],*[p for _,p,_ in PEOPLE]]
    for pos in targets:
        assert pos in seen,("disconnected town target",pos)
    stats["reachable_points"]=len(targets)
    stats["meadow_cells"]=sum(row.count(".") for row in use)
    stats["skipped"]=len(skipped)
    stats["structures"]=len(BUILDINGS)
    assert len(BUILDINGS)==6 and len(EVENTS)==8 and len(PEOPLE)==7
    assert all(len(row)==128 for row in rows) and len(rows)==128
    print("ASTER LIFE-FIRST ART STUDY (NOT PLAYABLE MAP180)")
    for k,v in stats.items():print(" ",k,":",v)
    for name,why in skipped:print("  SKIPPED",name,why)
    return rows, use

def main():
    rows,use=make()
    original_load=vis.load_map
    old_labels=vis.LOCATIONS
    try:
        vis.load_map=lambda:rows
        labels={name.replace("_"," ").title():(x,y) for name,(x,y,_) in DOORS.items()}
        labels.update({"Well site":WELL,"Memorial":MEMORIAL_EVENT,"South gate":START})
        vis.LOCATIONS=labels
        vis.make(NORMAL,LABELS)
    finally:
        vis.load_map=original_load
        vis.LOCATIONS=old_labels
    pic=Image.open(NORMAL)
    # Inspect the actual occupied blocks rather than the unused 64-cell
    # technical canvas around them. This is a CROP, not new/foreign art.
    pic.crop((2*16,3*16,54*16,63*16)).save(FOCUS,optimize=True)
    print("Visual compare:",NORMAL,FOCUS)
    print("Not an emulator render, no finished well, interior or NPC movement.")
if __name__=="__main__":
    main()
