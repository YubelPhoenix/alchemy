#!/usr/bin/env python3
"""Aster, a second 64x64 map SOURCE for a structurally ruined counterpart.

Experimental, NOT registered as a playable scene or Map181. Preserve the
normal settlement's layout, collision, eight event triggers, and south exit.
All visible edits are made only from Golden Sun Map003's already-linked
art. Roof damage is a source study, not proof of in-game destruction.
"""
import argparse
from pathlib import Path
import aster_layout as normal

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"tools/aster_ruined_map.txt"

# These are facade-relative *roof* holes, not random pasted foliage.
# Keep the entrances and their adjacent paths recognizable.
DAMAGED_ROOFS = {
    "sealed_house": ((2,2),(3,2),(3,3),(4,3)),
    "duplicate_home": ((5,1),(5,2),(6,2),(6,3)),
    "shop": ((1,2),(2,2),(2,3)),
    "inn": ((7,3),(8,3),(8,4)),
}
# A damaged, interrupted section of the existing plain flower garden, not a
# mystical altar. The well remains at exactly the original cell.
GARDEN_DAMAGE=((32,11),(33,11))
EMPTY_UPPER="15"  # native 100% transparent metatile in both upper layers

def generate():
    native=normal.load_vale()
    normal_grid=normal.source().splitlines()
    assert normal_grid[0].startswith("grid:128x128")
    grid=[line.split() for line in normal_grid[1:]]
    assert len(grid)==128 and all(len(r)==128 for r in grid)
    affected=set()
    homes={b[0]:b for b in normal.BUILDINGS}
    for name,coords in DAMAGED_ROOFS.items():
        _,bx,by,sx,sy,w,h,marker=homes[name]
        for dx,dy in coords:
            assert 0<=dx<w and 0<=dy<h-2,(name,dx,dy)
            x,y=bx+dx,by+dy
            assert normal.LAYOUT[y][x]==marker,(name,x,y)
            assert (x,y) not in affected,(name,x,y)
            affected.add((x,y))
            # Broken roof opens onto ordinary worn wood/dirt. The entire
            # house retains its impassable ground behavior (0xff) until
            # an actual collision/door test is completed.
            grid[y][x]=native[39][6].split(":")[0]+":ff"
            grid[y][x+64]=EMPTY_UPPER
            grid[y+64][x]=EMPTY_UPPER
    gx,gy,sx,sy,w,h=normal.MEMORIAL_GARDEN
    for x,y in GARDEN_DAMAGE:
        assert gx<=x<gx+w and gy<=y<gy+h
        grid[y][x+64]=EMPTY_UPPER
        grid[y+64][x]=EMPTY_UPPER

    # The two versions MUST agree on every actor position, story event, and
    # ordinary door/exit trigger, with no invisible new walls in the roads.
    original=[line.split() for line in normal_grid[1:]]
    protected={(x,y) for _,x,y,_ in normal.INTERACTIONS}
    protected.update((normal.EXIT, normal.START, normal.WELL, normal.MEMORIAL))
    protected.update(normal.ACTORS)
    for x,y in protected:
        assert grid[y][x] == original[y][x],(
            "Ruined Aster silently changed an interaction",x,y)
    for y in range(normal.SIDE):
        for x in range(normal.SIDE):
            if (x,y) not in affected:
                assert grid[y][x]==original[y][x],(
                    "Ruined map unexpectedly changed walking/ground behavior",x,y)
    assert all(grid[y][x].endswith(":ff") for x,y in affected)
    assert not hasattr(normal,"MEMORIAL_ART"),"Psynergy Stone forbidden"
    return normal_grid[0]+"\n"+"\n".join(" ".join(r) for r in grid)+"\n"

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    data=generate()
    if args.check:
        assert OUT.read_text(encoding="utf-8")==data,"Ruin source differs from generator"
        print("PASS paired Aster ruin: same geography, events and routes; 14 native roof injuries")
    else:
        OUT.write_text(data,encoding="utf-8")
        print("Wrote source-only ruined Aster map:",OUT)
if __name__=="__main__":
    main()
