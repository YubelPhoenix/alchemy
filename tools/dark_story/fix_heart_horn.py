#!/usr/bin/env python3
"""Keep Heart's single horn on the same side of her head in battle.

Her supplied 64x64 poses (assets/heart/v2, left untouched) face different
ways: idle and damage face left, cast, dash and lunge face right. Her battle
sheet (build_heart_art.py) mirrors idle and damage so she always faces the
party, which carried her one horn from behind her face to in front of it
whenever she moved between those poses and an attack.

This writes assets/heart/v3: idle1, idle2 and damage with the horn moved across
her face (so, once mirrored, it sits behind her face like in the attack poses),
the space it leaves filled with her hair (idle: the hair mirrored from the
other side of her face; damage: the nearest hair on the row) and its outline
kept against the hair; cast, dash and lunge copied unchanged.
"""
import numpy as np, os, sys
from PIL import Image
from scipy.ndimage import binary_dilation,label
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'assets'/'heart'/'v2'
OUT=ROOT/'assets'/'heart'/'v3'
os.makedirs(OUT,exist_ok=True)
# Poses mirrored in the battle sheet (they face left as drawn): move the horn
# across her face so, once mirrored, it sits behind her face like in the
# attack poses. Value: the column to mirror the horn about (her face's middle).
MOVE={'idle1':31.0,'idle2':31.0,'damage':17.0}
# how the space under the moved horn is filled: 'mirror' copies her hair from
# the other side of her face; 'hair' takes the nearest hair pixel on the row
FILL={'idle1':'mirror','idle2':'mirror','damage':'hair'}
def find_horn(im):
    op=im[...,3]>0
    mx=im[...,:3].max(axis=2)/255; mn=im[...,:3].min(axis=2)/255
    s=np.where(mx>0,(mx-mn)/np.maximum(mx,1e-6),0)
    pink=op&(im[...,0]>150)&(im[...,2]>130)&(im[...,1]<im[...,0]-25)
    top=np.nonzero(pink)[0].min()
    grey=np.zeros_like(op); r=slice(top,top+24)
    grey[r]=op[r]&(s[r]<0.22)&(mx[r]>0.18)&(mx[r]<0.8)
    lab,n=label(grey&binary_dilation(pink,iterations=3))
    k=1+int(np.argmax([(lab==i).sum() for i in range(1,n+1)]))
    horn=lab==k
    # the horn's dark outline: low-saturation pixels next to it, not hair
    dark=op&(s<0.32)&~pink
    for _ in range(2):
        horn=horn|(binary_dilation(horn)&dark)
    # and the bits of its outer edge a column apart from it, on the horn's rows
    ys,xs=np.nonzero(horn)
    box=np.zeros_like(horn); box[ys.min():ys.max()+1, max(0,xs.min()-4):xs.min()]=True
    horn=horn|(box&dark)
    return horn,pink,op
for name in ['idle1','idle2','cast','damage','dash','lunge']:
    im=np.array(Image.open(SRC / f'{name}.png').convert('RGBA')).astype(int)
    if name not in MOVE:
        Image.fromarray(im.astype(np.uint8)).save(OUT / f'{name}.png'); continue
    c=MOVE[name]; horn,pink,op=find_horn(im)
    out=im.copy(); ys,xs=np.nonzero(horn)
    for y,x in zip(ys,xs):
        if FILL[name]=='mirror':
            # her hair as it falls on the other side of her face (the pixel
            # mirrored across it), outline and edge included
            mx_=int(round(2*c-x))
            out[y,x]=im[y,mx_] if 0<=mx_<64 and not horn[y,mx_] else 0
        else:
            fill=0
            for d in (1,-1,2,-2,3,-3,4,-4):
                if 0<=x+d<64 and pink[y,x+d] and not horn[y,x+d]:
                    fill=im[y,x+d]; break
            out[y,x]=fill
    # draw the horn mirrored across her face, over her hair
    for y,x in zip(ys,xs):
        nx=int(round(2*c-x))
        if 0<=nx<64 and (pink[y,nx] or not op[y,nx]):
            out[y,nx]=im[y,x]
    # Outline left a column off from the hair that now fills the horn's place:
    # close the gap, so the edge hugs the hair instead of floating beside it.
    ys2,xs2=np.nonzero((out!=im).any(axis=2))
    for y in range(ys2.min(),ys2.max()+1):
        for x in range(max(0,xs2.min()-5),xs2.min()+3):
            if x+2<64 and out[y,x,3] and not out[y,x+1,3] and out[y,x+2,3]:
                mx=out[y,x,:3].max(); mn=out[y,x,:3].min()
                if mx and (mx-mn)/mx<0.32:
                    out[y,x+1]=out[y,x]; out[y,x]=0
    Image.fromarray(out.astype(np.uint8)).save(OUT / f'{name}.png')
print('ok')
