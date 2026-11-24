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
LEGS={-1:(8,-14),1:(10,16)}
def frame(rs, ls, sdir, legsp=LEGS, lz=0, lx=0, yaw=-30, sword_len=3.9):
    p=legs(pose(base,{-1:rs,1:ls}),legsp)
    sw=place(sword(length=sword_len,blade_w=0.5),look_rot(sdir),hand(-1,*rs))
    return lean(p+sw,lz,lx)
POSES={
 'idle':  frame((-60,40,30),(-68,-15,25),(-0.7,0.5,0.7)),
 'idle2': frame((-62,38,30),(-69,-15,25),(-0.72,0.42,0.7)),
 'dash':  frame((-25,-10,60),(-60,40,30),(0.45,0.6,-0.6),legsp={-1:(6,-20),1:(8,22)},lz=4,lx=6,sword_len=3.2),
 'lunge': frame((-20,70,5),(-65,-30,20),(-0.95,0.1,0.5),legsp={-1:(8,-22),1:(6,18)},lz=7,lx=8,sword_len=2.5),
 'cast':  frame((-75,10,20),(70,25,15),(-0.4,-0.7,0.5)),
 'damage':frame((-40,-20,40),(-45,-30,40),(0.2,0.8,0.6),legsp={-1:(10,-4),1:(10,8)},lz=6,lx=-8,sword_len=3.2),
}
# common framing so every frame shares one scale and baseline
allp=np.concatenate([q.reshape(-1,3) for v in POSES.values() for q,_,_ in v])
R=rot(-30,12); P=allp@R.T
idlep=np.concatenate([q.reshape(-1,3) for q,_,_ in POSES['idle']])@R.T
lo,hi=idlep.min(0),idlep.max(0)
span=(hi[1]-lo[1])*1.06; cx=(lo[0]+hi[0])/2+0.4; cy=lo[1]+span/2-0.12
k=8; out={}
for n,v in POSES.items():
    big,_=render(v,-30,12,64*k,ambient=0.6,fit=(cx,cy,span))
    idx=quantize(darken_rim(outline(punch(downscale_sharp(big,k)),(20,16,28)),0.7))
    from scipy import ndimage
    lab,nl=ndimage.label(idx>0)
    for c in range(1,nl+1):
        if (lab==c).sum()<5: idx[lab==c]=0
    out[n]=idx
    Image.fromarray(show(idx)).save(OUT/f'{n}.png')
print('Rendered', ', '.join(out))
