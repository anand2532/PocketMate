"""3-D polyline with exact circular corner fillets (tangent-continuous, every bend radius = R or larger)."""
import math
def _sub(a,b): return tuple(a[i]-b[i] for i in range(3))
def _add(a,b): return tuple(a[i]+b[i] for i in range(3))
def _mul(a,k): return tuple(a[i]*k for i in range(3))
def _len(a): return math.sqrt(sum(x*x for x in a))
def _unit(a): l=_len(a); return tuple(x/l for x in a)
def _dot(a,b): return sum(a[i]*b[i] for i in range(3))
def fillet_polyline(W, R):
    """W: waypoints (list of xyz); R: float or list (per interior corner). Returns list of items
    ('L', p0, p1) and ('A', p0, pmid, p1), plus a report list of (corner, theta_deg, t, avail)."""
    n=len(W); Rs=R if isinstance(R,(list,tuple)) else [R]*(n-2)
    segs=[]; rep=[]
    cur=W[0]
    for i in range(1,n-1):
        u_in=_unit(_sub(W[i],W[i-1])); u_out=_unit(_sub(W[i+1],W[i]))
        c=max(-1,min(1,_dot(u_in,u_out))); th=math.acos(c)      # turn angle
        r=Rs[i-1]
        if th<1e-6: continue
        t=r*math.tan(th/2)
        a_in=_len(_sub(W[i],W[i-1])); a_out=_len(_sub(W[i+1],W[i]))
        rep.append((i,round(math.degrees(th),1),round(t,2),round(a_in,2),round(a_out,2)))
        p0=_sub(W[i],_mul(u_in,t)); p1=_add(W[i],_mul(u_out,t))
        # arc centre on the bisector
        bis=_unit(_sub(u_out,u_in)); dc=r/math.cos(th/2)
        cen=_add(W[i],_mul(bis,dc))
        mid=_add(cen,_mul(_unit(_sub(W[i],cen)),r))
        segs.append(('L',cur,p0)); segs.append(('A',p0,mid,p1,r*th,cen,r)); cur=p1
    segs.append(('L',cur,W[-1]))
    return segs,rep
def length(segs):
    L=0
    for s in segs:
        L+= _len(_sub(s[2],s[1])) if s[0]=='L' else s[4]
    return L
def sample(segs, step=0.4):
    """points along the centreline (list of xyz)"""
    import numpy as np
    out = []
    for s in segs:
        if s[0] == 'L':
            a, b = np.array(s[1]), np.array(s[2]); n = max(1, int(np.linalg.norm(b-a)/step))
            out += [tuple(a+(b-a)*k/n) for k in range(n)]
        else:
            a, b, c = np.array(s[1]), np.array(s[3]), np.array(s[5]); r = s[6]
            ua = (a-c)/r; ub = (b-c)/r
            ang = math.acos(max(-1, min(1, float(np.dot(ua, ub))))); nrm = np.cross(ua, ub); nrm /= np.linalg.norm(nrm)
            vperp = np.cross(nrm, ua); n = max(2, int(r*ang/step))
            out += [tuple(c + r*(ua*math.cos(ang*k/n) + vperp*math.sin(ang*k/n))) for k in range(n)]
    last = segs[-1]; out.append(tuple(last[2] if last[0] == 'L' else last[3]))
    return out
