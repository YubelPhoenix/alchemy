#!/usr/bin/env python3
"""Aster lived-in detail pass — realistic property clusters, no tile overlap.

This is an image/art study built on the improved native-water/forest prototype.
It places Golden Sun Vale supplies, flower beds and short property fences as
*work areas attached to occupied buildings*, never anonymous random clutter.
Every inserted 16px cell is checked for original grass, transparent upper
layers and a collision-safe footprint. Whole groups are rejected rather
than painted across tree canopies, roads, event cells or other props.

Not the playable Map180, no new interiors or GBA movement claim.
"""
from collections import deque, Counter
from pathlib import Path
from PIL import Image
import aster_native_woodland_synthesis as base
import aster_lived_in_blockout as town
import aster_visual_preview as render

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/"tools/aster_lived_in_activity.png"
LABELS=ROOT/"tools/aster_lived_in_activity_labels.png"
FOCUS=ROOT/"tools/aster_lived_in_activity_focus.png"
VALE=town.NATIVE

# Source metatiles are actual complete Golden Sun Vale details:
# x17,y5 = open-topped water jar, x17,y6 = wooden supply crate.
# x10..11,y47..48 = 2x2 coherent low native floral garden.
# x12..15,y54 = short native timber/flower property edging.
# These source crops were tested in Aster's earlier original-palette atlases.

# Each named placement belongs to one functional area.
# Keep a variety of objects, not dozens of repeated identical tiles.
CARGO=(
    ("western_home_water",18,33,17,5),
    ("western_home_goods",20,33,17,6),
    ("eastern_home_water",47,34,17,5),
    ("eastern_home_goods",46,36,17,6),
    ("shed_stock_north",12,34,17,6),
    ("shed_stock_south",12,36,17,6),
    ("shed_jug",13,38,17,5),
    ("shop_delivery_crate",19,42,17,6),
    ("shop_delivery_jar",20,41,17,5),
    ("shop_spares",21,41,17,6),
    ("inn_laundry_water",48,45,17,5),
    ("inn_luggage",49,47,17,6),
    ("inn_water_jar",48,49,17,5),
    ("pond_carried_water",48,38,17,5),
)
# Small property-edge gardens; each cropped as an intact *2x2 block*.
PLANTINGS=(
    ("west_kitchen_patch",17,27,10,47),
    ("west_herb_patch",21,28,10,47),
    ("east_kitchen_patch",46,28,10,47),
    ("east_herb_patch",49,30,10,47),
    ("shed_work_patch",13,32,10,47),
    ("shop_customer_garden",20,47,10,47),
    ("shop_owner_garden",23,45,10,47),
    ("inn_service_garden",48,43,10,47),
    ("inn_guest_garden",51,45,10,47),
)
# Native 4-cell timber/flower beds: short property lines, never blocking
# public streets. Do not surround the entire village with a fake fence.
PROPERTY_EDGES=(
    ("west_garden_boundary",19,35,12,54),
    ("east_garden_boundary",46,38,12,54),
    ("shop_stock_boundary",19,44,12,54),
    ("inn_service_boundary",47,51,12,54),
)
# Sparse flowers in human-use spaces: 5,49 is a complete native pink
# meadow tile, NOT tree/cliff remnants or foreign imported artwork.
FLOWER_CORNERS=(
    (18,25),(20,26),(22,31),(17,36),(19,37),
    (33,29),(35,30),(47,27),(49,32),(45,38),
    (16,42),(19,40),(22,43),(24,49),
    (34,43),(47,42),(51,45),(50,51),
)

def main():
    rows,use=base.synthesize(with_usage=True)
    recorded=Counter()
    rejected=[]
    protected={town.WELL,town.WELL_EVENT,town.MEMORIAL_EVENT,
               town.MEMORIAL,town.START,town.EXIT}
    protected.update((x,y) for x,y,_ in town.DOORS.values())
    protected.update(tuple(pos) for _,pos,_ in town.PEOPLE)
    protected.update((x,y) for x,y,_ in ())

    # Only grass with no scenery can receive a solid prop.
    # This catches clipping even when the *logical* use grid says empty,
    # which previous prototypes failed to check.
    def untouched(points):
        return all(
            1<=x<63 and 1<=y<63
            and (x,y) not in protected
            and use[y][x]=="."
            and rows[y][x]=="ba"
            and rows[y][x+64]=="15"
            and rows[y+64][x]=="15"
            for x,y in points)
    # A one-cell pedestrian halo is mandatory around each new solid
    # group wherever it is next to an actual threshold or event.
    doorway_halo=set()
    for x,y in protected:
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                doorway_halo.add((x+dx,y+dy))

    def place_cargo(name,x,y,sx,sy):
        if not untouched(((x,y),)) or (x,y) in doorway_halo:
            rejected.append((name,"occupied layer, reserved doorway or road"))
            return
        use[y][x]="B"
        rows[y][x]="ba:ff"
        rows[y][x+64]=VALE[sy][sx+30]
        rows[y+64][x]=VALE[sy][sx+60]
        recorded["solid_supplies"]+=1

    def place_garden(name,x,y,sx,sy):
        points=[(x+dx,y+dy) for dx in range(2) for dy in range(2)]
        if not untouched(points) or any(p in doorway_halo for p in points):
            rejected.append((name,"garden overlaps art, road, or reserved space"))
            return
        for dy in range(2):
            for dx in range(2):
                xx,yy=x+dx,y+dy
                use[yy][xx]="f"
                rows[yy][xx]=VALE[sy+dy][sx+dx].split(":")[0]
                rows[yy][xx+64]=VALE[sy+dy][sx+dx+30]
                rows[yy+64][xx]=VALE[sy+dy][sx+dx+60]
        recorded["cultivated_beds"]+=1

    def place_fence(name,x,y,sx,sy):
        points=[(x+dx,y) for dx in range(4)]
        if not untouched(points) or any(p in doorway_halo for p in points):
            rejected.append((name,"whole fence rejected: overlap or door halo"))
            return
        for dx in range(4):
            xx=x+dx
            use[y][xx]="F"
            rows[y][xx]="ba:ff"
            rows[y][xx+64]=VALE[sy][sx+dx+30]
            rows[y+64][xx]=VALE[sy][sx+dx+60]
        recorded["short_yard_fences"]+=1

    for arg in PLANTINGS:place_garden(*arg)
    for arg in CARGO:place_cargo(*arg)
    for arg in PROPERTY_EDGES:place_fence(*arg)
    for x,y in FLOWER_CORNERS:
        if not untouched(((x,y),)):continue
        sx,sy=5,49
        rows[y][x]=VALE[sy][sx].split(":")[0]
        rows[y][x+64]=VALE[sy][sx+30]
        rows[y+64][x]=VALE[sy][sx+60]
        recorded["small_wildflowers"]+=1

    q=deque([town.START])
    reached=set()
    while q:
        x,y=q.popleft()
        if (x,y) in reached or not(0<=x<64 and 0<=y<64):continue
        if use[y][x] not in ".=G":continue
        reached.add((x,y))
        q.extend(((x+1,y),(x-1,y),(x,y+1),(x,y-1)))
    required=[
        town.START,town.EXIT,town.WELL_EVENT,town.MEMORIAL_EVENT,
        *[v[:2] for v in town.DOORS.values()],
        *[pos for _,pos,_ in town.PEOPLE],
    ]
    missing=[pos for pos in required if pos not in reached]
    assert not missing,("Details blocked a door/event/NPC:",missing)
    assert len(required)==17,("Unexpected story actor/trigger count",len(required))
    assert recorded["solid_supplies"]>=3,("No useful additional objects",recorded)
    print("ASTER NATIVE LIVELIHOOD STUDY — NOT A ROM CHANGE")
    print("Successfully placed:",dict(recorded))
    for name,why in rejected:print("REJECTED:",name,why)
    print("All 8 planned interactions and 7 NPC positions still reachable.")
    print("Unaltered source-map trigger and door coordinates remain protected.")

    old=render.load_map
    old_locs=render.LOCATIONS
    try:
        render.load_map=lambda:rows
        render.LOCATIONS={
            "Work shed":(7,34),
            "Shop":(14,48),"Inn":(41,50),
            "West home":(12,31),"East home":(41,33),
            "Pond":(56,37),"Memorial":town.MEMORIAL_EVENT,
        }
        render.make(OUTPUT,LABELS)
    finally:
        render.load_map=old
        render.LOCATIONS=old_locs
    Image.open(OUTPUT).crop((1*16,2*16,63*16,63*16)).save(
        FOCUS,optimize=True)
    print("Preview image:",OUTPUT)
    print("No edits to live Map180, Aster C scene, saves, or world transitions")

if __name__=="__main__":
    main()
