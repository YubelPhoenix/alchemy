#!/usr/bin/env python3
"""Render Karis's battle poses (assets/karis/*.png) from Golden Sun: Dark Dawn's
battle model (caris.dae, from The Models Resource; not kept in the repository).

    python3 tools/dark_story/dd_render/karis_frames.py path/to/caris.dae

The model has no skeleton, so the arms and legs are bent here by hand
(pose2.py, legs.py) and a sword is added (sword.py). Each pose is rendered at
8x (daerender.py), shrunk by block medians, given a dark outline and mapped to
the shared sprite palette (sprite64.py). build_karis_art.py packs the result.
"""
import sys, os
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from daerender import *; from pose2 import *; from sword import *; from legs import legs; from sprite64 import *
import math
base=load(sys.argv[1])
OUT=HERE.parents[2]/'assets/karis'
def lean(parts, ang_z=0, ang_x=0, piv=(0,0,0)):
    R=Rxyz(ang_x,0,ang_z); piv=np.array(piv,float)
    return [(((p.reshape(-1,3)-piv)@R.T+piv).reshape(p.shape),u,t) for p,u,t in parts]
# Her stance from Dark Dawn's battle screen, as that game shows its party:
# side on, turned to the right where the Golden Sun party stands and a little
# away from us, feet apart, the sword low at her right hip slanting up and
# ahead of her.
YAW=100
LEGS={-1:(9,-16),1:(9,14)}
def frame(rs, ls, sdir, legsp=LEGS, lz=0, lx=0, sword_len=4.6, grip_back=0.2):
    p=legs(pose(base,{-1:rs,1:ls}),legsp)
    h=hand(-1,*rs); d=np.array(sdir,float); d/=np.linalg.norm(d)
    sw=place(sword(length=sword_len,blade_w=0.5),look_rot(d),h-d*grip_back)
    return lean(p+sw,lz,lx)
POSES={
 'idle':  frame((-78,18,25),(-74,-10,20),(-0.2,0.55,1)),
 'idle2': frame((-79,16,27),(-75,-10,20),(-0.2,0.5,1)),
 'dash':  frame((40,-30,50),(-60,40,30),(-0.3,0.8,-0.6),legsp={-1:(6,-20),1:(8,22)},lx=-4,sword_len=3.6,grip_back=0),
 'lunge': frame((-20,70,5),(-65,-30,20),(-0.1,0.05,1),legsp={-1:(8,-24),1:(6,20)},lx=10,sword_len=3.6,grip_back=0),
 'cast':  frame((-75,10,20),(70,25,15),(-0.2,-0.7,-0.4),sword_len=3.9,grip_back=0),
 'damage':frame((-40,-20,40),(-45,-30,40),(-0.5,0.5,-0.7),legsp={-1:(10,-4),1:(10,8)},lx=-10,sword_len=3.6,grip_back=0),
}
# common framing so every frame shares one scale and baseline
allp=np.concatenate([q.reshape(-1,3) for v in POSES.values() for q,_,_ in v])
R=rot(YAW,12); P=allp@R.T
idlep=np.concatenate([q.reshape(-1,3) for q,_,_ in POSES['idle']])@R.T
lo,hi=idlep.min(0),idlep.max(0)
span=(hi[1]-lo[1])*1.06; cx=(lo[0]+hi[0])/2; cy=lo[1]+span/2-0.12
k=8; out={}
for n,v in POSES.items():
    # Golden Sun's battle sprites are pre-rendered too, and were reduced to
    # this palette with error diffusion: soft light from the upper left,
    # cool shadows, the same many-hued grain, a dark outline.
    big,_=render(v,YAW,12,64*k,ambient=0.45,fit=(cx,cy,span),light=(-0.5,0.75,0.45))
    img=grade(downscale_sharp(big,k),1.0,(0.9,0.88,1.0),1.1)
    img=darken_rim(outline(img,(24,16,24)),0.7)
    idx=quantize_fs(img,0.8)
    from scipy import ndimage
    lab,nl=ndimage.label(idx>0)
    for c in range(1,nl+1):
        if (lab==c).sum()<5: idx[lab==c]=0
    out[n]=idx
    Image.fromarray(show(idx)).save(OUT/f'{n}.png')
print('Rendered', ', '.join(out))
