# Quasi-static 2D finite-difference Laplace solver (C with/without dielectric) for PocketMate stackup JLC06161H-3313.
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as sl, sys
d=0.005 # grid mm
def solve(eps, cond, V):
    ny,nx=eps.shape; N=nx*ny; idx=np.arange(N).reshape(ny,nx)
    fixed=cond>=0; rows=[];cols=[];vals=[]; b=np.zeros(N)
    for j in range(ny):
        for i in range(nx):
            k=idx[j,i]
            if fixed[j,i]: rows.append(k);cols.append(k);vals.append(1);b[k]=V[cond[j,i]];continue
            s=0
            for dj,di in((1,0),(-1,0),(0,1),(0,-1)):
                jj,ii=j+dj,i+di
                if not(0<=jj<ny and 0<=ii<nx): continue  # Neumann
                e=0.5*(eps[j,i]+eps[jj,ii]); rows.append(k);cols.append(idx[jj,ii]);vals.append(e); s+=e
            rows.append(k);cols.append(k);vals.append(-s)
    A=sp.csr_matrix((vals,(rows,cols)),shape=(N,N)); return sl.spsolve(A,b).reshape(ny,nx)
def charge(phi,eps,cond,c):
    q=0; ny,nx=phi.shape
    for j,i in zip(*np.where(cond==c)):
        for dj,di in((1,0),(-1,0),(0,1),(0,-1)):
            jj,ii=j+dj,i+di
            if 0<=jj<ny and 0<=ii<nx and cond[jj,ii]<0: q+=0.5*(eps[j,i]+eps[jj,ii])*(phi[j,i]-phi[jj,ii])
    return q
def build(layers, traces, er_on=True, W=None):
    # layers: list of (thk, er, 'gnd'/'diel'/'sig') top->bottom ; traces: list of (x0,w) on sig layer (thk=copper)
    H=sum(l[0] for l in layers); nx=int(W/d); ny=int(round(H/d))
    eps=np.ones((ny,nx)); cond=-np.ones((ny,nx),int); y=0
    for t,er,kind in layers:
        n=int(round(t/d)); sl_=slice(y,y+n)
        eps[sl_,:]=er if er_on else 1
        if kind=='gnd': cond[sl_,:]=0
        if kind=='sig':
            eps[sl_,:]=(er if er_on else 1)
            for k,(x0,w) in enumerate(traces): cond[sl_,int(x0/d):int((x0+w)/d)]=k+1
        y+=n
    return eps,cond
def Z(layers,ws,s,diff,W=2.0):
    x0=W/2-(ws+s/2 if diff else ws/2); tr=[(x0,ws)]+([(x0+ws+s,ws)] if diff else [])
    res={}
    for er_on in(True,False):
        eps,cond=build(layers,tr,er_on,W)
        if diff:
            phi=solve(eps,cond,{0:0,1:1,2:-1}); q=charge(phi,eps,cond,1); res[er_on]=q  # C_odd per trace (V=+1/-1)
        else:
            phi=solve(eps,cond,{0:0,1:1}); res[er_on]=charge(phi,eps,cond,1)
    e0=8.854e-12; c=3e8; C=res[True]*e0; C0=res[False]*e0
    z=1/(c*np.sqrt(C*C0)); return (2*z if diff else z), res[True]/res[False]
# outer microstrip L1 over L2: air, soldermask(0.0152 over trace approx in air region simplified), Cu 0.035, PP3313 0.0994 er4.1, L2 GND
def outer(): return [(0.30,1.0,'diel'),(0.015,3.8,'diel'),(0.035,3.8,'sig'),(0.0994,4.1,'diel'),(0.02,1,'gnd')]
# inner L3: L2 gnd, core 0.55 er4.6, L3 sig 0.015 (in PP 4.16), PP2116 0.1088, L4 gnd
def inner(): return [(0.02,1,'gnd'),(0.55,4.6,'diel'),(0.015,4.16,'sig'),(0.1088,4.16,'diel'),(0.02,1,'gnd')]
if __name__=='__main__':
    for name,L,w,s,dfl in eval(sys.argv[1]): 
        z,ee=Z(L(),w,s,dfl); print(f'{name}: w={w} s={s} Z={z:.1f} ohm eeff={ee:.2f}',flush=True)
