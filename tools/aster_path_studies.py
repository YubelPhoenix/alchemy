#!/usr/bin/env python3
"""Aster dirt-path alternatives, using ONLY original Golden Sun Map003 art.

Produces offline visuals, does not update map.txt. Intentionally tests
the actual road connectivity rather than unrelated repeated brown blobs.
"""
from pathlib import Path
import aster_layout as town
import aster_visual_preview as render

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=render.load_map()
VALE=town.load_vale()
DOORS={(x,y) for _,x,y,_ in town.DOOR_APPROACHES}
EVENTS={(x,y) for _,x,y,_ in town.INTERACTIONS}

def drawn_route():
    """Narrow winding central lane, three linked side streets, six door spurs."""
    mask=set()
    def hline(y,x1,x2):
        for x in range(min(x1,x2),max(x1,x2)+1):mask.add((x,y))
    def vline(x,y1,y2):
        for y in range(min(y1,y2),max(y1,y2)+1):mask.add((x,y))
    for y in range(15,63):
        x=32 if y<24 else 31 if y<41 else 33
        mask.add((x,y))
    for y,left,right in ((18,12,52),(40,12,53),(57,11,47)):
        hline(y,left,right)
    for name,x,y,_ in town.DOOR_APPROACHES:
        vline(x,y,town.DOOR_LINK_Y[name])
    # Between north memorial and winding southern town the roads are
    # *accessible on grass*, not covered by these stone decoration tests.
    return {(x,y) for x,y in mask if
            0<=x<64 and 0<=y<64 and
            town.LAYOUT[y][x] in ".=" and
            (x,y) not in EVENTS}

ROUTE=drawn_route()
assert len(ROUTE)>150

def source_tile(kind,x,y):
    # Original Vale ground around (5,39) is actual worn earth.
    # The variants retain art from that one native texture family.
    if kind=="thin":
        return VALE[39][6].split(":")[0]
    if kind=="broken":
        if (x*3+y*7)%5==0:
            return VALE[38][5].split(":")[0]  # weak top edge
        if (x*11+y)%7==0:
            return VALE[40][8].split(":")[0]  # weak lower edge
        return VALE[39][6].split(":")[0]
    if kind=="sides":
        # 1-cell line oriented E-W or N-S; native organic edges preserve
        # a grass shoulder on straight sections (subject to image review).
        n=(x,y-1) in ROUTE
        e=(x+1,y) in ROUTE
        so=(x,y+1) in ROUTE
        w=(x-1,y) in ROUTE
        if n or so:
            tile=VALE[39][4 if (x+y)%2 else 8]
        elif e or w:
            tile=VALE[38 if (x+y)%2 else 40][6]
        else:
            tile=VALE[39][6]
        return tile.split(":")[0]
    raise ValueError(kind)

def main():
    for mode in ("thin","broken","sides"):
        output=[r[:] for r in ORIGINAL]
        for x,y in ROUTE:
            output[y][x]=source_tile(mode,x,y)
        render.load_map=lambda:output
        render.make(ROOT/f"tools/aster_path_{mode}.png",
                    ROOT/f"tools/aster_path_{mode}_labels.png")
        print(mode,len(ROUTE),"narrow path cells, all original native Golden Sun art.")

    # Proper 2-cell-wide original Vale dirt path: one native grass/dirt
    # shoulder on each side. The previous single-cell experiment had one
    # scalloped edge, making its path look like a row of grass.
    vertical={}
    horizontal={}
    def add_v(x,y0,y1):
        for y in range(y0,y1+1):
            vertical[(x-1,y)]=VALE[39][4].split(":")[0]
            vertical[(x,y)]=VALE[39][8].split(":")[0]
    def add_h(y,x0,x1):
        for x in range(x0,x1+1):
            horizontal[(x,y)]=VALE[38][6].split(":")[0]
            horizontal[(x,y+1)]=VALE[40][6].split(":")[0]
    for y in range(15,63):
        x=32 if y<24 else 31 if y<41 else 33
        add_v(x,y,y)
    for y,a,b in ((18,12,52),(40,12,53),(57,11,47)):
        add_h(y,a,b)
    for name,x,y,_ in town.DOOR_APPROACHES:
        add_v(x,y,town.DOOR_LINK_Y[name])
    for mode in ("wide","wide-worn"):
        output=[r[:] for r in ORIGINAL]
        combined={**vertical,**horizontal}
        for pos in set(vertical)&set(horizontal):
            combined[pos]=VALE[39][6].split(":")[0]
        n=0
        for (x,y),tile in combined.items():
            if not(0<=x<64 and 0<=y<64):
                continue
            if town.LAYOUT[y][x] not in ".=" or (x,y) in EVENTS:
                continue
            if mode=="wide-worn" and (x*11+y*7)%19==0:
                tile=VALE[39][5].split(":")[0]
            output[y][x]=tile
            n+=1
        render.load_map=lambda:output
        render.make(ROOT/f"tools/aster_path_{mode}.png",
                    ROOT/f"tools/aster_path_{mode}_labels.png")
        print(mode,n,"native two-cell Vale dirt tiles with connected approaches.")
if __name__=="__main__":
    main()
