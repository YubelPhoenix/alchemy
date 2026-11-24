import numpy as np, math
from sword import Rxyz
def arm_xform(s, down, fwd, elbow, sx=1.05, sy=8.75, ex=2.95):
    """Returns f(points)->points for side s, and the transform of a point."""
    Rs=Rxyz(fwd,0,down*s)       # lower (about z), then swing forward (about x)
    Re=Rxyz(0,elbow*-s,0)       # elbow bend about the arm's up axis (toward the front)
    ps=np.array([s*sx,sy,0.]); pe=np.array([s*ex,sy-0.3,0.])
    def T(P, weights=True):
        P=P.copy()
        if weights:
            we=np.clip((P[:,0]*s-ex)/0.35,0,1)[:,None]
            ws=np.clip((P[:,0]*s-sx)/0.45,0,1)[:,None]
        else:
            we=np.ones((len(P),1)); ws=np.ones((len(P),1))
        P=P+we*(((P-pe)@Re.T+pe)-P)
        P=P+ws*(((P-ps)@Rs.T+ps)-P)
        return P
    return T
def pose(parts, sides, ymin=7.4):
    out=[]
    for pos,uv,tex in parts:
        P=pos.reshape(-1,3).copy()
        for s,(down,fwd,elbow) in sides.items():
            m=(P[:,0]*s>1.05)&(P[:,1]>ymin)
            if m.any(): P[m]=arm_xform(s,down,fwd,elbow)(P[m])
        out.append((P.reshape(pos.shape),uv,tex))
    return out
def hand(s, down, fwd, elbow, hp=(4.5,8.29,0)):
    p=np.array([[s*hp[0],hp[1],hp[2]]]); return arm_xform(s,down,fwd,elbow)(p,weights=False)[0]
def look_rot(d):
    """Rotation mapping +Y onto direction d."""
    d=np.asarray(d,float); d/=np.linalg.norm(d); y=np.array([0,1.,0])
    v=np.cross(y,d); c=np.dot(y,d)
    if np.linalg.norm(v)<1e-9: return np.eye(3) if c>0 else np.diag([1,-1,-1])
    vx=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    return np.eye(3)+vx+vx@vx*(1/(1+c))
