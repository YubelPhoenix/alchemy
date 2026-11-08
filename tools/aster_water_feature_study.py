#!/usr/bin/env python3
"""Aster: first *real water* visual trial using only original Golden Sun art.

This study compares two ways to remove Vale's magical crystal pedestal from
its authentic pond and place an ordinary pond near Aster's eastern residences.
All actual pond banks and water pixels originate in Vale Map003/set_02.
The rest of Aster is from the separately reviewed life-first blockout.

This is NOT a gameplay map: the game event flags, NPCs, world transitions,
tile priorities and water collision are NOT changed by this renderer.
"""
from pathlib import Path
import aster_lived_in_blockout as town
import aster_visual_preview as preview

ROOT=Path(__file__).resolve().parents[1]
VALE=town.NATIVE
DEST_X,DEST_Y=50,33
SRC_X,SRC_Y=8,38
W,H=12,10

# Copy varied native water, not the blank base tile under Vale's crystal.
# Each sample was inspected in a 16px native water/bank atlas; all these
# ground tiles are existing *unobstructed* Vale water patterns.
CLEAR_WATER=(
    (10,41),  # ordinary blue moving water
    (10,42),  # water with tiny light ripple
    (10,43),  # fuller dark/light surface variation
    (11,41),  # brighter small current
    (15,41),  # dark blue quiet surface
    (15,43),  # ordinary open water
    (12,40),  # plain water in original spring pool
)
assert all(VALE[y][x].split(":")[0]!="3b7" for x,y in CLEAR_WATER)

def is_water_source(x,y):
    """Only pond surface, not the vegetated perimeter or bank apron."""
    widths={39:(11,16),40:(9,17),41:(9,17),42:(9,18),
            43:(9,18),44:(9,18),45:(10,17)}
    if y not in widths:return False
    a,b=widths[y]
    return a<=x<=b

def source_water():
    """Copy Vale native pond picture while erasing its *magical* center."""
    old=town.empty_map
    def with_pond():
        rows,use=old()
        for dy in range(H):
            for dx in range(W):
                x,y=DEST_X+dx,DEST_Y+dy
                sx,sy=SRC_X+dx,SRC_Y+dy
                assert use[y][x]==".",(x,y,use[y][x])
                # Use the naturally curved Vale shore ONLY where source
                # actually contains the pond. The previous 12x10 stamp
                # imported a detached inn roof in the upper-right corner.
                # Do not stamp an unneeded rectangular ring of original
                # grass/house tiles around the pond.
                allowed={
                    39:(10,17),40:(8,17),41:(8,18),42:(8,18),
                    43:(8,18),44:(8,18),45:(8,18),46:(8,18),
                }
                if sy not in allowed or not (
                    allowed[sy][0]<=sx<=allowed[sy][1]):
                    continue
                ground=VALE[sy][sx].split(":")[0]
                mid=VALE[sy][sx+30]
                top=VALE[sy][sx+60]
                # The original crystal/pedestal extends through the pond.
                # Its native water below is a blank dark base tile and
                # caused an obvious rectangular patch in the first study.
                # Replace only the crystal-bearing core with authentic
                # varied open-water *metatiles*, keep all native banks.
                if 11<=sx<=16 and 40<=sy<=45:
                    mid=top="15"
                    if sy<45:
                        px,py=CLEAR_WATER[(sx*7+sy*3)%len(CLEAR_WATER)]
                        ground=VALE[py][px].split(":")[0]
                    # Preserve the actual Vale south-water transition on
                    # y45: its varied shoreline is NOT the crystal.
                if sy==46 and 11<=sx<=17:
                    # Loose pedestal fragments sit over Vale's south bank.
                    mid=top="15"
                rows[y][x]=ground
                rows[y][x+64]=mid
                rows[y+64][x]=top
                if is_water_source(sx,sy):
                    use[y][x]="~"   # provisional water barrier only
        return rows,use
    return with_pond

def render_one(mode):
    original=town.empty_map
    if mode=="shore":
        town.empty_map=source_water()
    elif mode=="clearing":
        # Without crystal removal, a single source pond crop is NOT
        # approved; compare this only as a diagnostic negative control.
        old=town.empty_map
        def untouched():
            rows,use=old()
            for dy in range(H):
                for dx in range(W):
                    x,y=DEST_X+dx,DEST_Y+dy
                    sx,sy=SRC_X+dx,SRC_Y+dy
                    rows[y][x]=VALE[sy][sx].split(":")[0]
                    rows[y][x+64]=VALE[sy][sx+30]
                    rows[y+64][x]=VALE[sy][sx+60]
                    if is_water_source(sx,sy):use[y][x]="~"
            return rows,use
        town.empty_map=untouched
    else:raise ValueError(mode)
    town.NORMAL=ROOT/f"tools/aster_water_{mode}.png"
    town.LABELS=ROOT/f"tools/aster_water_{mode}_labels.png"
    town.FOCUS=ROOT/f"tools/aster_water_{mode}_focus.png"
    try:town.main()
    finally:town.empty_map=original
    print("Aster native pond test:",mode,
          "Vale source",(SRC_X,SRC_Y,W,H),
          "Aster target",(DEST_X,DEST_Y))
    print("No changes to playable Map180, saved data or scene scripts")

if __name__=="__main__":
    render_one("shore")
