import numpy as np
from sword import Rxyz
def turn_head(parts, yaw_deg, tilt_deg=0, y0=8.95, y1=9.35, pivot=(0, 9.1, 0), scale=1.0):
    """Turn the head about the neck (a vertical axis through pivot), blending
    in between heights y0 and y1 so the neck bends rather than tears."""
    """scale enlarges the head about the neck, as sprites do to keep a face
    readable at 64 pixels."""
    piv=np.array(pivot,float); R=Rxyz(tilt_deg,yaw_deg,0)*scale; out=[]
    for pos,uv,tex in parts:
        P=pos.reshape(-1,3).copy()
        # the head only: in the T-pose the arms reach out past |x| = 1.2
        w=(np.clip((P[:,1]-y0)/(y1-y0),0,1)*(np.abs(P[:,0])<1.2))[:,None]
        m=w[:,0]>0
        if m.any():
            Q=P[m]; P[m]=Q+w[m]*(((Q-piv)@R.T+piv)-Q)
        out.append((P.reshape(pos.shape),uv,tex))
    return out
