"""Tiny COLLADA (.dae) loader and software rasterizer for sprite renders.
Usage: render(dae_path, yaw_deg, pitch_deg, size) -> RGBA numpy array."""
import re, math, os
import numpy as np
import xml.etree.ElementTree as ET
from PIL import Image
NS={'c':'http://www.collada.org/2005/11/COLLADASchema'}

def load(path):
    root=ET.parse(path).getroot(); base=os.path.dirname(path)
    images={im.get('id'):os.path.join(base,im.find('c:init_from',NS).text) for im in root.iter('{%s}image'%NS['c'])}
    effects={}
    for ef in root.iter('{%s}effect'%NS['c']):
        surf={}
        for np_ in ef.iter('{%s}newparam'%NS['c']):
            s=np_.find('c:surface/c:init_from',NS)
            if s is not None: surf[np_.get('sid')]=s.text
            smp=np_.find('c:sampler2D/c:source',NS)
            if smp is not None: surf[np_.get('sid')]=surf.get(smp.text)
        tex=ef.find('.//c:diffuse/c:texture',NS)
        img=surf.get(tex.get('texture')) if tex is not None else None
        effects[ef.get('id')]=images.get(img)
    mats={m.get('id'):effects.get(m.find('c:instance_effect',NS).get('url')[1:]) for m in root.iter('{%s}material'%NS['c'])}
    geos={}
    for g in root.iter('{%s}geometry'%NS['c']):
        mesh=g.find('c:mesh',NS)
        src={s.get('id'):np.array(s.find('c:float_array',NS).text.split(),float).reshape(-1,int(s.find('.//c:accessor',NS).get('stride'))) for s in mesh.findall('c:source',NS)}
        verts={v.get('id'):src[v.find('c:input',NS).get('source')[1:]] for v in mesh.findall('c:vertices',NS)}
        tris=[]
        for prim in list(mesh):
            tag=prim.tag.split('}')[1]
            if tag not in ('triangles','polylist'): continue
            inputs=prim.findall('c:input',NS); stride=max(int(i.get('offset')) for i in inputs)+1
            p=np.array(prim.find('c:p',NS).text.split(),int).reshape(-1,stride)
            pos=uv=None
            for i in inputs:
                sem,off=i.get('semantic'),int(i.get('offset')); sid=i.get('source')[1:]
                arr=verts.get(sid, src.get(sid))
                if sem=='VERTEX': pos=arr[p[:,off]]
                if sem=='TEXCOORD' and uv is None: uv=arr[p[:,off]][:,:2]
            if tag=='polylist':
                vc=np.array(prim.find('c:vcount',NS).text.split(),int); idx=[];k=0
                for n in vc:
                    for t in range(1,n-1): idx+= [k,k+t,k+t+1]
                    k+=n
                pos=pos[idx]; uv=uv[idx] if uv is not None else None
            tris.append((prim.get('material'),pos.reshape(-1,3,3),None if uv is None else uv.reshape(-1,3,2)))
        geos[g.get('id')]=tris
    out=[]
    for ig in root.iter('{%s}instance_geometry'%NS['c']):
        bind={im.get('symbol'):im.get('target')[1:] for im in ig.iter('{%s}instance_material'%NS['c'])}
        for mat,pos,uv in geos[ig.get('url')[1:]]:
            img=mats.get(bind.get(mat,mat))
            out.append((pos,uv,np.asarray(Image.open(img).convert('RGBA')) if img else None))
    return out

def rot(yaw,pitch):
    y,p=math.radians(yaw),math.radians(pitch)
    Ry=np.array([[math.cos(y),0,math.sin(y)],[0,1,0],[-math.sin(y),0,math.cos(y)]])
    Rx=np.array([[1,0,0],[0,math.cos(p),-math.sin(p)],[0,math.sin(p),math.cos(p)]])
    return Rx@Ry

def render(parts,yaw=0,pitch=0,size=256,light=(-0.5,0.7,0.6),ambient=0.55,fit=None):
    R=rot(yaw,pitch)
    allp=np.concatenate([p.reshape(-1,3) for p,_,_ in parts])@R.T
    if fit is None:
        lo,hi=allp.min(0),allp.max(0); span=max(hi[0]-lo[0],hi[1]-lo[1])*1.05
        cx,cy=(lo[0]+hi[0])/2,(lo[1]+hi[1])/2; fit=(cx,cy,span)
    cx,cy,span=fit
    img=np.zeros((size,size,4),float); zb=np.full((size,size),-1e9)
    L=np.array(light,float); L/=np.linalg.norm(L)
    for pos,uv,tex in parts:
        P=pos@R.T
        for t in range(len(P)):
            v=P[t]; n=np.cross(v[1]-v[0],v[2]-v[0]); nn=np.linalg.norm(n)
            if nn==0: continue
            n/=nn
            shade=ambient+(1-ambient)*abs(np.dot(n,L))
            sx=(v[:,0]-cx)/span*size+size/2; sy=size/2-(v[:,1]-cy)/span*size
            x0,x1=int(max(0,np.floor(sx.min()))),int(min(size-1,np.ceil(sx.max())))
            y0,y1=int(max(0,np.floor(sy.min()))),int(min(size-1,np.ceil(sy.max())))
            if x1<x0 or y1<y0: continue
            xs,ys=np.meshgrid(np.arange(x0,x1+1)+0.5,np.arange(y0,y1+1)+0.5)
            d=(sy[1]-sy[2])*(sx[0]-sx[2])+(sx[2]-sx[1])*(sy[0]-sy[2])
            if abs(d)<1e-12: continue
            a=((sy[1]-sy[2])*(xs-sx[2])+(sx[2]-sx[1])*(ys-sy[2]))/d
            b=((sy[2]-sy[0])*(xs-sx[2])+(sx[0]-sx[2])*(ys-sy[2]))/d
            c=1-a-b; m=(a>=-1e-6)&(b>=-1e-6)&(c>=-1e-6)
            if not m.any(): continue
            z=a*v[0,2]+b*v[1,2]+c*v[2,2]
            Y,X=np.nonzero(m); Y+=y0; X+=x0; zz=z[m]
            if tex is not None and uv is not None:
                u=a[m]*uv[t,0,0]+b[m]*uv[t,1,0]+c[m]*uv[t,2,0]
                w=a[m]*uv[t,0,1]+b[m]*uv[t,1,1]+c[m]*uv[t,2,1]
                th,tw=tex.shape[:2]
                tx=(np.floor(u*tw).astype(int))%tw; ty=(np.floor((1-w)*th).astype(int))%th
                col=tex[ty,tx].astype(float)
            else:
                col=np.tile([200,200,200,255],(len(Y),1)).astype(float)
            ok=(col[:,3]>=128)&(zz>zb[Y,X])
            Y,X,zz,col=Y[ok],X[ok],zz[ok],col[ok]
            # resolve duplicates within triangle: fine (same tri)
            zb[Y,X]=zz
            img[Y,X,:3]=col[:,:3]*shade; img[Y,X,3]=255
    return np.clip(img,0,255).astype(np.uint8),fit
