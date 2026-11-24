import numpy as np
from PIL import Image
from pathlib import Path
PAL_IMG=str(Path(__file__).resolve().parents[3]/'games/tbs/src/system/memory/basic.png')
pal=np.array(Image.open(PAL_IMG).getpalette()[:224*3],float).reshape(-1,3)
def to_lab(rgb):
    rgb=rgb/255.0
    rgb=np.where(rgb>0.04045,((rgb+0.055)/1.055)**2.4,rgb/12.92)
    m=np.array([[0.4124,0.3576,0.1805],[0.2126,0.7152,0.0722],[0.0193,0.1192,0.9505]])
    xyz=rgb@m.T/np.array([0.95047,1.0,1.08883])
    f=np.where(xyz>0.008856,np.cbrt(xyz),7.787*xyz+16/116)
    return np.stack([116*f[...,1]-16,500*(f[...,0]-f[...,1]),200*(f[...,1]-f[...,2])],-1)
PLAB=to_lab(pal)
def downscale(big, k, height=None):
    """big: RGBA uint8 (N*k). Area-average with alpha, threshold."""
    H,W=big.shape[:2]; h,w=H//k,W//k
    a=big[:h*k,:w*k].astype(float).reshape(h,k,w,k,4)
    al=a[...,3:4]/255
    cov=al.mean((1,3))
    col=(a[...,:3]*al).sum((1,3))/np.maximum(al.sum((1,3)),1e-6)
    out=np.zeros((h,w,4),float); out[...,:3]=col; out[...,3]=np.where(cov[...,0]>=0.45,255,0)
    return out.astype(np.uint8)
def outline(img, color=(24,24,32)):
    a=img[...,3]>0; o=img.copy()
    edge=np.zeros_like(a)
    for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
        edge|=np.roll(np.roll(a,dy,0),dx,1)
    edge&=~a
    o[edge,:3]=color; o[edge,3]=255
    return o
def darken_rim(img, f=0.55):
    a=img[...,3]>0; inner=a.copy()
    for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)): inner&=np.roll(np.roll(a,dy,0),dx,1)
    rim=a&~inner; o=img.copy(); o[rim,:3]=(o[rim,:3]*f).astype(np.uint8); return o
def quantize(img):
    vis=img[...,3]>0
    lab=to_lab(img[vis][:,:3].astype(float))
    d=((lab[:,None,:]-PLAB[None,1:,:])**2).sum(2)
    idx=np.zeros(img.shape[:2],np.uint8); idx[vis]=d.argmin(1)+1
    return idx
def to_png(idx):
    im=Image.fromarray(idx,'P'); im.putpalette(Image.open(PAL_IMG).getpalette()[:224*3]+[0]*(256-224)*3); return im
def show(idx):
    rgb=np.zeros(idx.shape+(4,),np.uint8); rgb[...,:3]=pal[idx].astype(np.uint8); rgb[...,3]=np.where(idx>0,255,0); return rgb
def downscale_sharp(big,k):
    H,W=big.shape[:2]; h,w=H//k,W//k
    a=big[:h*k,:w*k].reshape(h,k,w,k,4)
    cov=(a[...,3]>0).mean((1,3))
    # most common-ish: take pixel at block centre region median by luminance
    blk=a.transpose(0,2,1,3,4).reshape(h,w,k*k,4).astype(float)
    vis=blk[...,3]>0
    L=0.3*blk[...,0]+0.59*blk[...,1]+0.11*blk[...,2]
    L=np.where(vis,L,np.nan)
    med=np.nanmedian(np.where(vis,L,np.nan),axis=2) if True else None
    idx=np.nanargmin(np.abs(np.where(vis,L,np.inf)-med[...,None]),axis=2) if False else None
    out=np.zeros((h,w,4),np.uint8)
    for y in range(h):
        for x in range(w):
            if cov[y,x]<0.45: continue
            v=vis[y,x]; Ls=L[y,x][v]; m=np.median(Ls); j=np.argmin(np.abs(Ls-m))
            out[y,x,:3]=blk[y,x][v][j,:3]; out[y,x,3]=255
    return out
def punch(img, sat=1.25, con=1.15):
    o=img.astype(float); rgb=o[...,:3]
    L=rgb.mean(-1,keepdims=True)
    rgb=L+(rgb-L)*sat
    rgb=(rgb-128)*con+128
    o[...,:3]=rgb.clip(0,255); return o.astype(np.uint8)

def reduce_colors(img, n=20, seed=1):
    """Cluster the visible colours to n in Lab, so materials keep a few clean
    shades (as hand-drawn sprites do) before the palette mapping."""
    from scipy.cluster.vq import kmeans2
    vis=img[...,3]>0
    if vis.sum()<n: return img
    lab=to_lab(img[vis][:,:3].astype(float))
    np.random.seed(seed)
    cent,lbl=kmeans2(lab,n,minit='++',seed=seed)
    # each pixel takes its cluster's most common original colour
    rgb=img[vis][:,:3]
    out=img.copy(); new=rgb.copy()
    for c in range(n):
        m=lbl==c
        if not m.any(): continue
        u,cnt=np.unique(rgb[m],axis=0,return_counts=True)
        new[m]=u[cnt.argmax()]
    out[vis,:3]=new
    return out
def despeckle(idx):
    """Replace a pixel unlike all four neighbours (which agree) with them."""
    o=idx.copy(); H,W=idx.shape
    for y in range(1,H-1):
        for x in range(1,W-1):
            v=idx[y,x]
            if v==0: continue
            nb=[idx[y-1,x],idx[y+1,x],idx[y,x-1],idx[y,x+1]]
            if all(n!=v for n in nb) and nb.count(nb[0])>=3 and nb[0]!=0:
                o[y,x]=nb[0]
    return o

BAYER4=np.array([[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]])/16-0.5
def quantize_dither(img, amount=10.0):
    """Nearest palette colour after a small ordered (Bayer) offset in Lab
    lightness: the fine colour grain of Golden Sun's pre-rendered sprites."""
    vis=img[...,3]>0
    lab=to_lab(img[...,:3].astype(float))
    H,W=vis.shape
    off=np.tile(BAYER4,(H//4+1,W//4+1))[:H,:W]*amount
    lab[...,0]+=off
    d=((lab[vis][:,None,:]-PLAB[None,1:,:])**2).sum(2)
    idx=np.zeros((H,W),np.uint8); idx[vis]=d.argmin(1)+1
    return idx
def grade(img, light=0.9, shadow_tint=(0.86,0.82,1.0), sat=1.0, warm=(1.0,1.0,1.0)):
    """Darken toward the game's mid-tones: scale, tint the darker half, adjust
    saturation."""
    o=img.astype(float); rgb=o[...,:3]*light
    L=rgb.mean(-1,keepdims=True)/255
    t=np.array(shadow_tint)[None,None,:]
    rgb=rgb*(t+(1-t)*np.clip(L*1.4,0,1))*np.array(warm)
    m=rgb.mean(-1,keepdims=True); rgb=m+(rgb-m)*sat
    o[...,:3]=rgb.clip(0,255); return o.astype(np.uint8)
