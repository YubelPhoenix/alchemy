import numpy as np, math
def box(c0,c1):
    (x0,y0,z0),(x1,y1,z1)=c0,c1
    v=np.array([[x0,y0,z0],[x1,y0,z0],[x1,y1,z0],[x0,y1,z0],[x0,y0,z1],[x1,y0,z1],[x1,y1,z1],[x0,y1,z1]],float)
    f=[(0,1,2),(0,2,3),(4,6,5),(4,7,6),(0,4,5),(0,5,1),(3,2,6),(3,6,7),(0,3,7),(0,7,4),(1,5,6),(1,6,2)]
    return v[np.array(f)]
def solid(rgb):
    return np.array([[list(rgb)+[255]]],np.uint8)
def sword(length=5.2, blade_w=0.32, blade_t=0.08):
    """A sword along +Y from the grip at the origin."""
    parts=[]
    blade=box((-blade_w/2,0.9,-blade_t/2),(blade_w/2,0.9+length,blade_t/2))
    # taper the tip: pull the top 4 verts of the blade together
    tip=blade.reshape(-1,3); top=tip[:,1]>0.9+length-1e-6; tip[top,0]*=0.15
    parts.append((tip.reshape(-1,3,3),np.zeros((len(blade),3,2)),solid((214,222,236))))
    # a darker fuller down one face
    parts.append((box((-0.05,1.0,blade_t/2),(0.05,0.9+length*0.8,blade_t/2+0.01)),None,solid((150,160,180))))
    parts.append((box((-0.75,0.75,-0.14),(0.75,0.95,0.14)),None,solid((214,170,60))))   # guard
    parts.append((box((-0.1,-0.75,-0.1),(0.1,0.75,0.1)),None,solid((110,60,40))))       # grip
    parts.append((box((-0.18,-0.98,-0.18),(0.18,-0.75,0.18)),None,solid((214,170,60))))  # pommel
    return [(p,np.zeros((len(p),3,2)) if u is None else u,t) for p,u,t in parts]
def place(parts, R, t):
    return [((p.reshape(-1,3)@R.T+t).reshape(p.shape),u,tx) for p,u,tx in parts]
def Rxyz(ax,ay,az):
    ax,ay,az=map(math.radians,(ax,ay,az))
    Rx=np.array([[1,0,0],[0,math.cos(ax),-math.sin(ax)],[0,math.sin(ax),math.cos(ax)]])
    Ry=np.array([[math.cos(ay),0,math.sin(ay)],[0,1,0],[-math.sin(ay),0,math.cos(ay)]])
    Rz=np.array([[math.cos(az),-math.sin(az),0],[math.sin(az),math.cos(az),0],[0,0,1]])
    return Rz@Ry@Rx
