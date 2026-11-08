#!/usr/bin/env python3
"""Private experiments using only native Vale graphics, NOT gameplay maps.

Aster's main Map180 is left untouched. Each 64x64 source-derived study
tests a native dirt texture only. The Psynergy Stone experiment is banned.
Never label this a screenshot of a compiled ROM.
"""
from pathlib import Path
import aster_layout as base
import aster_visual_preview as render

root=Path(__file__).resolve().parents[1]
original=render.load_map()
vale=base.load_vale()

def start():
    return [row[:] for row in original]

def stamp(rows, name, dx,dy,sx,sy,w,h, use_ground=True,solid=False):
    for yy in range(h):
        for xx in range(w):
            gx=dx+xx;gy=dy+yy
            assert 0<=gx<64 and 0<=gy<64, name
            assert base.LAYOUT[gy][gx] not in "#XIHSVT", (name,gx,gy)
            # Retain existing event behavior at Aster's two sites.
            old=rows[gy][gx]
            if use_ground:
                v=vale[sy+yy][sx+xx].split(":")[0]
                if old.endswith(":e1") or old.endswith(":e2"):
                    v += old[old.index(":"):]
                elif solid:
                    v += ":ff"
                rows[gy][gx]=v
            rows[gy][gx+64]=vale[sy+yy][sx+xx+30]
            rows[gy+64][gx]=vale[sy+yy][sx+xx+60]

def save(label,change):
    rows=start()
    change(rows)
    # preserve original source grid and keep render entirely in memory
    render.load_map=lambda:rows
    render.make(root/f"tools/aster_square_{label}.png",
                root/f"tools/aster_square_{label}_labels.png")
    print("Golden Sun-only square study:",label)

def trial_dirt(rows):
    # A contiguous Vale ground-only patch below the southern shop, used to
    # determine whether this is true dirt or rock/roof-bearing terrain.
    dx,dy,sx,sy,w,h=29,49,3,37,5,5
    for yy in range(h):
        for xx in range(w):
            rows[dy+yy][dx+xx]=vale[sy+yy][sx+xx].split(":")[0]

if __name__=="__main__":
    # Ordinary Vale dirt only. The old Psynergy Stone, pond and gate
    # candidates were rejected and are never generated again for Aster.
    save("dirt",trial_dirt)
