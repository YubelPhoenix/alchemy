#!/usr/bin/env python3
"""Source-only Aster DRY well assembly studies, original Golden Sun Vale tiles.

No foreign sprites, imported water, glowing shrine, invented graphics, or
changes to the actual Aster exterior. Compare these with genuine Golden
Sun source previews before selecting a gameplay prop and collision footprint.
"""
from pathlib import Path
import aster_layout as town
import aster_visual_preview as vis

ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=vis.load_map()
VALE=town.load_vale()
EVENTS={(x,y) for _,x,y,_ in town.INTERACTIONS}
SITE=(32,34)

def make(mode):
    data=[row[:] for row in ORIGINAL]
    # Stone/earth from native Vale ground, no water tiles or magic source.
    # Only the existing well symbol is solid; study variations are
    # intentionally NOT collision-authoritative or playable.
    def soil(x,y,sx=6,sy=39):
        assert (x,y) not in EVENTS,(mode,x,y,"event")
        old=data[y][x].split(":")
        ground=VALE[sy][sx].split(":")[0]
        data[y][x]=ground+(":"+":".join(old[1:]) if len(old)>1 else "")
    def upper(x,y,sx,sy):
        assert (x,y) not in EVENTS,(mode,x,y,"event")
        data[y][x+64]=VALE[sy][sx+30]
        data[y+64][x]=VALE[sy][sx+60]
    def stones():
        # The ordinary oval Vale doorstep stone from (15,9), reused
        # only where a clear source overlay exists.
        for x,y in ((31,33),(33,33),(31,34),(33,34)):
            upper(x,y,15,9)
    # A small earthen well apron, aligned to original landmark at 32,34.
    for x,y in ((31,33),(32,33),(33,33),(31,34),(32,34),(33,34)):
        soil(x,y)
    if mode=="open_stone":
        stones()
    elif mode=="wood_frame":
        stones()
        # The small, nonmagical timber entry arch of Vale, upper layers.
        # It is only a visual trial: do not claim it has a working winch.
        for yy in range(3):
            for xx in range(4):
                upper(30+xx,30+yy,12+xx,50+yy)
    elif mode=="wood_bucket":
        stones()
        for yy in range(3):
            for xx in range(4):
                upper(30+xx,30+yy,12+xx,50+yy)
        upper(34,34,17,5)  # small native Vale jar, no fluid
    elif mode=="stone_apron":
        # A cluster of native oval doorstep stones, not a magical basin.
        for x,y in ((31,32),(33,32),(31,34),(33,34)):
            upper(x,y,15,9)
        for x,y in ((31,33),(33,33)):
            upper(x,y,15,10)
    elif mode in ("well_cave_a","well_cave_b","well_cave_c"):
        stones()
        for yy in range(3):
            for xx in range(4):
                upper(30+xx,30+yy,12+xx,50+yy)
        upper(34,34,17,5)
        # Source candidates from Vale's NATURAL cave mouth (ground plane).
        # Test only. Preserve 32,34 solid and 32,35 event; do not assume
        # a cliff-side dark tile is a valid freestanding well shaft.
        source={"well_cave_a":(11,26),
                "well_cave_b":(12,26),
                "well_cave_c":(10,27)}[mode]
        sx,sy=source
        data[33][32]=VALE[sy][sx].split(":")[0]
    else:
        raise ValueError(mode)
    assert data[35][32]==ORIGINAL[35][32]=="ba:e1"
    assert data[34][32].endswith(":ff"),"Well symbol must stay solid"
    assert all(data[y][x]==ORIGINAL[y][x] for x,y in EVENTS),mode
    vis.load_map=lambda:data
    vis.make(ROOT/f"tools/aster_well_{mode}_study.png",
             ROOT/f"tools/aster_well_{mode}_study_labels.png")
    print(mode,"original Golden Sun assets ONLY; art study, not runtime well")

if __name__=="__main__":
    for name in ("open_stone","wood_frame","wood_bucket","stone_apron",
                 "well_cave_a","well_cave_b","well_cave_c"):
        make(name)
