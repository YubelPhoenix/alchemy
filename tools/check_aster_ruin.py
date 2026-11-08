#!/usr/bin/env python3
"""Strict source-level audit of Aster's unregistered ruined-state grid.

Does NOT claim a playable second scene, actual art quality, or emulator
verification. Prevents the usual oversight: changed assets on screen but
different event triggers, impassable door approaches or relocated houses.
"""
from pathlib import Path
import aster_layout as town
import aster_ruin_variant as ruin

ROOT=Path(__file__).resolve().parents[1]
def require(condition,message):
    if not condition:raise AssertionError(message)

def rows(text):
    header,*lines=text.splitlines()
    require(header.startswith("grid:128x128"),"Bad map header")
    grid=[row.split() for row in lines]
    require(len(grid)==128 and all(len(r)==128 for r in grid),
            "Ruin source must have same packed 128x128 map layers")
    return grid

def main():
    a=rows(town.source())
    output=ruin.generate()
    b=rows(output)
    require(ruin.OUT.exists(),"Generated ruined map is missing")
    require(ruin.OUT.read_text(encoding="utf-8")==output,
            "Ruined source does not match committed generated grid")
    require(town.SIDE==64 and len(town.BUILDINGS)==6,
            "Original town geometry changed unexpectedly")
    require(len(town.ACTORS)==7 and len(town.INTERACTIONS)==8,
            "Ruin must preserve all NPC and event positions")
    affected={
        (bx+dx,by+dy)
        for name,coords in ruin.DAMAGED_ROOFS.items()
        for bname,bx,by,sx,sy,w,h,marker in town.BUILDINGS if name==bname
        for dx,dy in coords
    }
    require(len(affected)==14,"Expected fourteen bounded roof injuries")
    garden=set(ruin.GARDEN_DAMAGE)
    require(len(garden)==2 and not(garden & affected),
            "Fence damage overlaps roof damage")
    changed_ground=set()
    changed_middle=set()
    changed_overhead=set()
    for y in range(64):
        for x in range(64):
            if a[y][x]!=b[y][x]:changed_ground.add((x,y))
            if a[y][x+64]!=b[y][x+64]:changed_middle.add((x,y))
            if a[y+64][x]!=b[y+64][x]:changed_overhead.add((x,y))
    require(changed_ground==affected,
            f"Unexpected ruin ground behavior edits: {changed_ground^affected}")
    require(changed_middle==affected|garden,
            "Ruin middle-plane damage is not exactly the planned geometry")
    require(changed_overhead==affected|garden,
            "Ruin roof-plane damage is not exactly the planned geometry")
    require(all(b[y][x].endswith(":ff") for x,y in affected),
            "Collapsed roofs must keep original solid-house collision")
    for name,x,y,behavior in town.INTERACTIONS:
        require(a[y][x]==b[y][x]==behavior,
                f"{name} story trigger lost in ruin")
    for x,y in (*town.ACTORS,town.START,town.EXIT,town.WELL,town.MEMORIAL):
        require(a[y][x]==b[y][x],f"Town anchor shifted: ({x},{y})")
    require(b[63][32]=="ba:1","South exit no longer matches ordinary Aster")
    for layer in b:
        for v in layer:
            require((int(v.split(":")[0],16)&4095)!=4095,
                    "Ruin added an unresolved first-use Golden Sun metatile")
    require(not hasattr(town,"MEMORIAL_ART"),
            "Banned Psynergy Stone was reintroduced")
    print("PASS Aster ruined source: all 6 addresses, 8 events, 7 NPCs,")
    print("  14 solid roof-damage cells and 2 broken-fence cells; no stray changes")
    print("NOTE: geometry-only; appearance and gameplay NOT approved")

if __name__=="__main__":
    main()
