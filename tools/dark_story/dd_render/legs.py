import numpy as np, math
from sword import Rxyz
def legs(parts, spec, top=4.1, full=3.3, hip_y=4.6):
    """spec: {side: (out_deg about z, fwd_deg about x)}; side +1 = model +x."""
    out=[]
    for pos,uv,tex in parts:
        P=pos.reshape(-1,3).copy()
        for s,(outd,fwd) in spec.items():
            m=(P[:,0]*s>-0.05)&(P[:,1]<top)
            if not m.any(): continue
            Q=P[m]; w=np.clip((top-Q[:,1])/(top-full),0,1)[:,None]
            piv=np.array([s*0.55,hip_y,0.])
            R=Rxyz(fwd,0,outd*s)
            Q=Q+w*(((Q-piv)@R.T+piv)-Q)
            P[m]=Q
        out.append((P.reshape(pos.shape),uv,tex))
    return out
