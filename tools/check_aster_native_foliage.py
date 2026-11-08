#!/usr/bin/env python3
"""Verify the twelve added Aster V14 native 3-layer woodland silhouettes.

Read-only source check; no GitHub Actions, ROM build or file changes.
This tests actual Vale Map003 three-layer source metatiles, exact footprint,
transparent ground preservation and the provenance manifest. It is not an
emulator render or in-game collision certification.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MAP=ROOT/"games/tbs/src/map/map_180/map.txt"
VALE=ROOT/"games/tbs/src/map/map_003/map.txt"
META=ROOT/"games/tbs/src/map/map_003/metatiles.tsv"
MANIFEST=ROOT/"tools/aster_native_boundary_manifest.json"
SNAPSHOT=ROOT/"tools/aster_v14_native_snapshot.json"

def require(value, reason):
    if not value:
        raise AssertionError(reason)

def load_map(path, native=False):
    lines=path.read_text(encoding="utf-8").splitlines()
    require(lines and lines[0].startswith("grid:128x128"),
            f"{path}: wrong source header")
    fields=dict(field.split(":",1)
                for field in lines[0].split("\t")[1:])
    start_x,start_y=map(int,fields.get("at","0,0").split(","))
    fill=fields.get("fill","0").split(":")[0]
    output=[[fill for _ in range(128)] for _ in range(128)]
    for sy,line in enumerate(lines[1:]):
        tiles=line.split()
        require(start_y+sy<128, f"{path}: row exceeds packed grid")
        for sx,token in enumerate(tiles):
            require(start_x+sx<128, f"{path}: column exceeds packed grid")
            output[start_y+sy][start_x+sx]=token
    if native:
        idx=0
        for y in range(128):
            for x in range(128):
                parts=output[y][x].split(":")
                number=int(parts[0],16)
                if number&4095==4095:
                    parts[0]=format((number&0xf000)|idx,"x")
                    output[y][x]=":".join(parts)
                    idx+=1
        metatile_count=len(META.read_text(encoding="utf-8").splitlines())-1
        require(idx==metatile_count,
                f"Vale 0xfff resolution drift: {idx} vs {metatile_count}")
    return output

def verify():
    grid=load_map(MAP)
    original=load_map(VALE,native=True)
    record=json.loads(MANIFEST.read_text(encoding="utf-8"))
    snap=json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    require(record["new_map_blob"]==snap["source_git_blob_sha"],
            "Foliage provenance does not match native map snapshot")
    trees=record["new_native_trees"]
    require(len(trees)==12,"Expected 12 additional native trees")
    baseline={(item["x"],item["y"]):item["ground"]
              for item in record["transparent_base_cells"]}
    require(len(baseline)==66,"Transparent ground baseline count drifted")
    used=set()
    opaque=0
    transparent=0
    for tree in trees:
        x,y,sx,sy=(tree[k] for k in ("x","y","source_x","source_y"))
        require((sx,sy) in ((17,46),(4,13)),
                f"Non-native or unapproved tree source: {sx},{sy}")
        require(tree["width"]==4 and tree["height"]==5,
                "Altered tree dimensions")
        for dy in range(5):
            for dx in range(4):
                px,py=x+dx,y+dy
                require(1<=px<=62 and 1<=py<=62,
                        "A tree extends outside the playable inner map")
                require((px,py) not in used,
                        f"Two tree stamps overlap at {px},{py}")
                used.add((px,py))
                middle=original[sy+dy][sx+dx+30]
                if (sx,sy,dx,dy)==(4,13,3,4):
                    middle="15"  # native silhouette's stray blue fragment
                top=original[sy+dy][sx+dx+60]
                require(grid[py][px+64]==middle,
                        f"Altered source foliage middle tile at {px},{py}")
                require(grid[py+64][px]==top,
                        f"Altered source foliage top tile at {px},{py}")
                if middle=="15" and top=="15":
                    transparent+=1
                    require((px,py) in baseline,
                            f"Unreviewed transparent tree cell at {px},{py}")
                    require(grid[py][px]==baseline[(px,py)],
                            f"Tree added invisible collision at {px},{py}")
                else:
                    opaque+=1
                    require(grid[py][px].endswith(":ff"),
                            f"Visible tree lacks collision at {px},{py}")
    require(opaque==174 and transparent==66,
            "Native tree opacity/collision profile drifted")
    require(len(baseline)==transparent,"Stale transparent-cell baseline")
    print("PASS twelve original Golden Sun native 4x5 tree silhouettes")
    print("PASS 174 visible solid tiles and 66 original transparent ground cells")
    print("PASS Vale three-layer source references, no scenery overlap")
    print("SOURCE-ONLY: requires GBA render and emulator collision review")
    return opaque,transparent

if __name__=="__main__":
    verify()
