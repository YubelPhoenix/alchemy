#!/usr/bin/env python3
"""Aster native Golden Sun woodland synthesis — nonplayable map art study.

Unlike the rejected 10x7 rectangular source crops and isolated 4x5
trees, this assembles *one irregular forest boundary* with original
Golden Sun Vale foliage metatiles. It chooses adjacent original native
tile art by actual 16px edge continuity and tree-canopy coverage.

One real pond and existing buildings are retained. No foreign PNGs,
painted approximation, arbitrary sprite scaling, or modifications to
Map180, Aster's triggers, NPC anchors or the overworld.
"""
from collections import deque, Counter
from pathlib import Path
from PIL import Image
import aster_lived_in_blockout as town
import aster_water_feature_study as water
import aster_lived_in_ecology as life
import aster_visual_preview as vis

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"tools/aster_forest_synthesis.png"
ANNOTATED=ROOT/"tools/aster_forest_synthesis_labels.png"
FOCUS=ROOT/"tools/aster_forest_synthesis_focus.png"
VALE=town.NATIVE

# These original Vale locations contain densely connected woodland on
# the game's authentic set_02 tile sheets; no buildings or Psynergy Stone.
FOREST_SOURCE=(
    (0,10,50,56),(19,29,50,56),
    (0,8,43,49),(20,29,45,49),
)
def candidates():
    blocks,palette,_=vis.load_tiles()
    meta=vis.load_metatiles()
    invalid=set()
    cache={}
    mtcache={}
    def sprite(token,base):
        idx=int(token.split(":")[0],16)&4095
        key=idx,base
        if key not in mtcache:
            mtcache[key]=vis.render_metatile(
                idx,meta,blocks,palette,invalid,cache,base)
        return mtcache[key]
    gr=sprite("ba",0).copy()
    opts=[]
    def add(mid,top,sx,sy):
        upper=Image.new("RGBA",(16,16),(0,0,0,0))
        for tok in (mid,top):
            tile=sprite(tok,2)
            if tile is not None:upper.alpha_composite(tile,(0,0))
        cov=sum(1 for a in upper.getchannel("A").getdata() if a>0)/256
        picture=gr.copy()
        picture.alpha_composite(upper,(0,0))
        px=picture.convert("RGB")
        edges=(
            tuple(px.getpixel((0,k)) for k in range(16)),
            tuple(px.getpixel((15,k)) for k in range(16)),
            tuple(px.getpixel((k,0)) for k in range(16)),
            tuple(px.getpixel((k,15)) for k in range(16)),
        )
        opts.append((sx,sy,mid,top,cov,edges))
    add("15","15",None,None)
    visited=set()
    for sx0,sx1,sy0,sy1 in FOREST_SOURCE:
        for sy in range(sy0,sy1+1):
            for sx in range(sx0,sx1+1):
                if (sx,sy) in visited:continue
                visited.add((sx,sy))
                mid=VALE[sy][sx+30]
                top=VALE[sy][sx+60]
                if mid.split(":")[0]=="15" and top.split(":")[0]=="15":
                    continue
                add(mid,top,sx,sy)
    assert not invalid,f"Broken original Vale tile references: {invalid}"
    return opts

def forest_mask(use):
    """Terrain encircles streets but does not cover homes or passable roads."""
    target=set()
    for y in range(1,63):
        for x in range(1,63):
            if use[y][x]!=".":continue
            # A household's work space must exist BEFORE deciding where
            # trees belong. Otherwise a forest model consumes every yard.
            # The west service shed links the inhabited cottage to trade;
            # kitchen beds and market stock have their own cleared plots.
            reserved=(
                (3<=x<=12 and 31<=y<=40) or
                (17<=x<=25 and 25<=y<=36) or
                (31<=x<=36 and 28<=y<=35) or
                (45<=x<=53 and 27<=y<=38) or
                (18<=x<=25 and 41<=y<=51) or
                (47<=x<=54 and 43<=y<=52)
            )
            if reserved:continue
            # Irregular shoulders, never a rectangular native-map crop.
            left=(5 + (y*7//11)%3 + ((y*13)%7==0))
            right=(57 - (y*5//13)%3)
            top=(4 + (x*11//13)%3)
            bottom=(58 - (x*3//17)%3)
            ring=(x<=left or x>=right or y<=top or y>=bottom)
            # Smaller tree-covered property borders from the same
            # native vegetation system, like Vale's forest-backed homes.
            west_yard=(18<=x<=25 and 18<=y<=30 and
                       (x-18)*2+(y-18) <= 22)
            east_yard=(45<=x<=54 and 19<=y<=30 and
                       (54-x)+(y-19)//3<=8)
            market_yard=(19<=x<=25 and 40<=y<=47 and
                         (x-19)+(y-40)//2<=5)
            inn_yard=(47<=x<=54 and 42<=y<=52 and
                      (x-47)+abs(y-47)//2<=5)
            if ring or west_yard or east_yard or market_yard or inn_yard:
                target.add((x,y))
    return target

def diff(edge_a,edge_b):
    return sum(abs(v-w)
        for a,b in zip(edge_a,edge_b)
        for v,w in zip(a,b))

def synthesize(with_usage=False):
    original_empty=town.empty_map
    original_tree=town.TREES
    town.empty_map=water.source_water()
    town.TREES=()
    try:
        rows,use=town.make()
    finally:
        town.empty_map=original_empty
        town.TREES=original_tree
    opts=candidates()
    print("Native Golden Sun canopy metatile candidates:",len(opts))
    # Cache all pairwise natural edge compatibility scores once.
    # Order: left/right/top/bottom source-pixel boundaries.
    N=len(opts)
    cost_lr=[[0]*N for _ in range(N)]
    cost_tb=[[0]*N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            cost_lr[i][j]=diff(opts[i][5][1],opts[j][5][0])
            cost_tb[i][j]=diff(opts[i][5][3],opts[j][5][2])
    mask=forest_mask(use)
    chosen={}
    dense=0
    kept=0
    for y in range(1,63):
        for x in range(1,63):
            if (x,y) not in mask:continue
            n=sum((x+dx,y+dy) in mask
                  for dx,dy in ((-1,0),(1,0),(0,-1),(0,1)))
            # A soft natural transition to ordinary grass, more canopy
            # inside forest and less at the edges of the commons.
            target_cover=(0.80 if n==4 else 0.56 if n==3 else
                          0.34 if n==2 else 0.16)
            left=chosen.get((x-1,y),0)
            top=chosen.get((x,y-1),0)
            scores=[]
            for j,opt in enumerate(opts):
                sx,sy,mid,upper,cov,_=opt
                # Penalize boxy crop edges, not whole panels. Continuity
                # comes from neighboring RGB edges and source adjacency.
                score=(cost_lr[left][j]*1.3+
                       cost_tb[top][j]*1.3+
                       abs(cov-target_cover)*7000)
                if j==0 and target_cover>0.30:
                    score+=2300
                leftopt=opts[left]
                topopt=opts[top]
                if (leftopt[0] is not None and sx is not None and
                    (sx,sy)==(leftopt[0]+1,leftopt[1])):
                    score-=2200
                if (topopt[0] is not None and sx is not None and
                    (sx,sy)==(topopt[0],topopt[1]+1)):
                    score-=2200
                scores.append((score,j))
            scores.sort()
            # Avoid a hard-coded checkerboard: vary among the best
            # genuinely compatible original-source choices.
            best=[j for _,j in scores[:3]]
            j=best[(x*13+y*17+(y//7)*11)%len(best)]
            chosen[(x,y)]=j
            sx,sy,mid,upper,cov,_=opts[j]
            if j==0 or cov<0.08:
                kept+=1
                continue
            rows[y][x+64]=mid
            rows[y+64][x]=upper
            if cov>0.23:
                rows[y][x]="ba:ff"
                use[y][x]="T"
                dense+=1
    # Keep the ordinary village details from a separate reviewed study.
    stats=Counter(forest_cells=dense,soft_clearings=kept,trees_source=N)
    def free(points):
        return all(1<=x<63 and 1<=y<63 and use[y][x]=="." for x,y in points)
    # One actual Golden Sun small wooden outbuilding, rather than a
    # fabricated sprite. It's source-only scenery with NO functional
    # entrance: a proper room/service door remains a future task.
    # Crop is the intact Vale wood storage facade (original Map003).
    SHED=("west_work_shed",3,32,19,3,8,7)
    name,bx,by,sx,sy,bw,bh=SHED
    footprint=[(bx+dx,by+dy) for dy in range(bh) for dx in range(bw)]
    if free(footprint):
        for dy in range(bh):
            for dx in range(bw):
                x,y=bx+dx,by+dy
                use[y][x]="H"
                rows[y][x]="ba:ff"
                rows[y][x+64]=VALE[sy+dy][sx+dx+30]
                rows[y+64][x]=VALE[sy+dy][sx+dx+60]
        stats["support_sheds"]+=1
    else:
        print("REJECT west shed: site conflicts with town circulation")
        # Do not approve the new composition unless this is fixed.
        raise AssertionError("Native west service shed requires an unobstructed site")
    # An ordinary service alley joins the work shed to the real southern
    # business street. Previous prototypes had decorative buildings with
    # no plausible route by which goods could be carried.
    service_path=([(7,y) for y in range(39,50)]+
                  [(x,49) for x in range(7,15)])
    for x,y in service_path:
        if use[y][x]==".":
            use[y][x]="="
            rows[y][x]=VALE[39][6].split(":")[0]
            stats["service_path_cells"]+=1
    # Properties need cultivated areas, not random identical flower dots.
    # These native 2x2 Vale beds are grouped beside homes, shop and inn.
    WORK_PLOTS=(
        ("western_herbs_a",18,27,10,47,2,2),
        ("western_herbs_b",21,28,10,47,2,2),
        ("western_herbs_c",18,31,10,47,2,2),
        ("eastern_garden_a",46,27,10,47,2,2),
        ("eastern_garden_b",49,29,10,47,2,2),
        ("shop_kitchen_a",20,45,10,47,2,2),
        ("shop_kitchen_b",23,46,10,47,2,2),
        ("inn_garden_a",49,46,10,47,2,2),
    )
    for name,x,y,sx,sy,w,h in WORK_PLOTS:
        points=[(x+dx,y+dy) for dy in range(h) for dx in range(w)]
        if not free(points):continue
        for dy in range(h):
            for dx in range(w):
                xx,yy=x+dx,y+dy
                rows[yy][xx]=VALE[sy+dy][sx+dx].split(":")[0]
                rows[yy][xx+64]=VALE[sy+dy][sx+dx+30]
                rows[yy+64][xx]=VALE[sy+dy][sx+dx+60]
                use[yy][xx]="f"
        stats["gardens"]+=1
    EXTRA_SUPPLIES=(
        ("shed_goods_a",11,35,17,6),
        ("shed_goods_b",11,37,17,6),
        ("shed_water_jar",12,38,17,5),
    )
    for name,x,y,sx,sy in (*life.SUPPLIES,*EXTRA_SUPPLIES):
        if not free([(x,y)]):continue
        use[y][x]="B"
        rows[y][x]="ba:ff"
        rows[y][x+64]=VALE[sy][sx+30]
        rows[y+64][x]=VALE[sy][sx+60]
        stats["market_supplies"]+=1
    for y in range(3,58):
        for x in range(3,62):
            if use[y][x]!=".":continue
            near_home=any(
                bx-5<=x<=bx+bw+5 and by-5<=y<=by+bh+6
                for name,bx,by,sx,sy,bw,bh in town.BUILDINGS)
            if not near_home:continue
            if (x*71+y*193)%103 not in (3,7,11,23):continue
            rows[y][x]=VALE[49][5].split(":")[0]
            rows[y][x+64]=VALE[49][5+30]
            rows[y+64][x]=VALE[49][5+60]
            stats["native_pink_flowers"]+=1
    q=deque([town.START]);seen=set()
    while q:
        x,y=q.popleft()
        if not (0<=x<64 and 0<=y<64) or (x,y) in seen:continue
        if use[y][x] not in ".=G":continue
        seen.add((x,y))
        q.extend(((x+1,y),(x-1,y),(x,y+1),(x,y-1)))
    anchors=[town.EXIT,town.START,town.WELL_EVENT,town.MEMORIAL_EVENT,
             *[v[:2] for v in town.DOORS.values()],
             *[pos for _,pos,_ in town.PEOPLE]]
    unreachable=[p for p in anchors if p not in seen]
    assert not unreachable,("Forest made draft scene unusable",unreachable)
    print("Forest synthesis outcome (not a verified ROM):",dict(stats))
    print("Source-only flood-fill pass: all 8 events and 7 actors reachable")
    return (rows,use) if with_usage else rows

def main():
    rows=synthesize()
    saved=vis.load_map
    labels=vis.LOCATIONS
    try:
        vis.load_map=lambda:rows
        vis.LOCATIONS={
            "Well reserved":town.WELL,"Memorial":town.MEMORIAL_EVENT,
            "Pond":(56,38),"Inn":(41,50),"Shop":(14,48),
        }
        vis.make(OUT,ANNOTATED)
    finally:
        vis.load_map=saved
        vis.LOCATIONS=labels
    Image.open(OUT).crop((16,16,1008,1008)).save(FOCUS,optimize=True)
    print("WFC-lite Golden Sun foliage (no new graphics/metatiles) study:",OUT)
    print("Important: only source preview; no actual game Map180 edits")

if __name__=="__main__":main()
