# Legalize placement: resolve courtyard overlaps between movable parts and pull far passives to their pin.
# Metric: distance from passive's pad to the nearest IC pad (U/Q/L/D/J) sharing a non-GND net.
import pcbnew as P, re, math, sys
K='/workspace/pocketmate/hardware/kicad/PocketMate.kicad_pcb'; B=P.LoadBoard(K); M=P.FromMM
def V(x,y): return P.VECTOR2I(M(x),M(-y))
def mm(v): return (P.ToMM(v.x),-P.ToMM(v.y))
F={f.GetReference():f for f in B.GetFootprints()}
GND=re.compile(r'GND')
ICre=re.compile(r'^(U|Q|L|J|D)\d')
EXTRA_KO=[]   # (x0,y0,x1,y1,side)
for z in B.Zones():
    if z.GetIsRuleArea() and z.GetDoNotAllowFootprints():
        bb=z.Outline().BBox(); x0,x1=P.ToMM(bb.GetLeft()),P.ToMM(bb.GetRight()); y0,y1=-P.ToMM(bb.GetBottom()),-P.ToMM(bb.GetTop())
        sides=('F' if z.IsOnLayer(P.F_Cu) else '')+('B' if z.IsOnLayer(P.B_Cu) else '')
        if 'SoC' in z.GetZoneName() or 'CM5_footprint' in z.GetZoneName(): continue
        EXTRA_KO.append((x0,y0,x1,y1,sides,z.GetZoneName()))
def side(f): return 'B' if f.IsFlipped() else 'F'
def cbox(f):
    f.BuildCourtyardCaches(); c=f.GetCourtyard(P.B_CrtYd if f.IsFlipped() else P.F_CrtYd)
    b=c.BBox() if c.OutlineCount() else f.GetBoundingBox(False,False)
    return (P.ToMM(b.GetLeft()),-P.ToMM(b.GetBottom()),P.ToMM(b.GetRight()),-P.ToMM(b.GetTop()))
HOLES=[(2.5,-26.5),(50.5,-26.5),(2.5,6.5),(50.5,6.5)]
def inboard(x,y,m=0.25):
    for cx,cy,sx,sy in [(2,-31,-1,-1),(51,-31,1,-1),(2,31.5,-1,1)]:
        if (x-cx)*sx>0 and (y-cy)*sy>0 and math.hypot(x-cx,y-cy)>3-m: return False
    return (-1+m<x<54-m and -34+m<y<34.5-m) and not (x>27-m and y>10.5-m)
def legal(f,occ):
    x0,y0,x1,y1=cbox(f)
    if not all(inboard(x,y) for x,y in [(x0,y0),(x1,y0),(x0,y1),(x1,y1)]): return False
    if any(math.hypot(min(max(hx,x0),x1)-hx,min(max(hy,y0),y1)-hy)<3.0 for hx,hy in HOLES): return False
    s=side(f)
    if s=='B' and not (y0>10.0 or y1<-30.0): return False
    for a,b_,c,d,sd,_ in EXTRA_KO:
        if s in sd and a<x1 and x0<c and b_<y1 and y0<d: return False
    for o in occ[s]:
        if o[0]<x1 and x0<o[2] and o[1]<y1 and y0<o[3]: return False
    return True
def ic_pads(f):
    out=[]
    for p in f.Pads():
        n=p.GetNetname()
        if not n or GND.search(n): continue
        for r2,g in F.items():
            if r2==f.GetReference() or not ICre.match(r2): continue
            for q in g.Pads():
                if q.GetNetname()==n: out.append((p,q,r2))
    return out
def dist(f):
    best=(99,None)
    for p,q,r2 in ic_pads(f):
        d=math.hypot(*(lambda a,b:(a[0]-b[0],a[1]-b[1]))(mm(p.GetPosition()),mm(q.GetPosition())))
        if d<best[0]: best=(d,(r2,q.GetNumber(),mm(q.GetPosition())))
    return best
def bulk(f):
    v=f.GetValue().replace('µ','u'); m_=re.match(r'([0-9.]+)\s*u',v)
    return f.GetReference().startswith('C') and m_ and float(m_.group(1))>=10
def place_near(f,tx,ty,occ,maxr=4.0,step=0.05):
    s0=(f.GetPosition(),f.GetOrientationDegrees())
    for k in range(int((maxr/step)**2)):
        rr=step*math.sqrt(k); th=k*2.39996
        x,y=tx+rr*math.cos(th),ty+rr*math.sin(th)
        for rot in (0,90,180,270):
            f.SetOrientationDegrees(rot); f.SetPosition(V(x,y))
            if legal(f,occ): return True
    f.SetPosition(s0[0]); f.SetOrientationDegrees(s0[1]); return False
def main(fixed_extra=(),maxfar=3.0,verbose=True):
    mov=[r for r,f in F.items() if re.match(r'^[RC]\d',r) and not f.IsLocked() and r not in fixed_extra]
    # occupancy excluding movers
    occ={'F':[],'B':[]}
    for r,f in F.items():
        if r not in mov: occ[side(f)].append(cbox(f))
        for pd in f.Pads():
            if pd.GetAttribute() in (P.PAD_ATTRIB_PTH,P.PAD_ATTRIB_NPTH):
                bb=pd.GetBoundingBox(); x0,x1=P.ToMM(bb.GetLeft())-0.2,P.ToMM(bb.GetRight())+0.2; y0,y1=-P.ToMM(bb.GetBottom())-0.2,-P.ToMM(bb.GetTop())+0.2
                occ['F'].append((x0,y0,x1,y1)); occ['B'].append((x0,y0,x1,y1))
    # order: legal & close first keep; then the rest
    keep=[];redo=[]
    for r in sorted(mov):
        f=F[r]; d,_=dist(f)
        if legal(f,occ) and (d<=maxfar or bulk(f)): keep.append(r); occ[side(f)].append(cbox(f))
        else: redo.append(r)
    if verbose: print('keep',len(keep),'redo',redo)
    fail=[]
    for r in sorted(redo,key=lambda r:(0 if r.startswith('C') else 1,r)):
        f=F[r]; d,t=dist(f)
        if t: tx,ty=t[2]
        else: tx,ty=mm(f.GetPosition())
        ok=place_near(f,tx,ty,occ,4.5)
        if not ok:
            # try other side if allowed
            f.Flip(f.GetPosition(),False); ok=place_near(f,tx,ty,occ,4.5)
            if not ok: f.Flip(f.GetPosition(),False); ok=place_near(f,*mm(f.GetPosition()),occ,12)
        if ok: occ[side(f)].append(cbox(f))
        else: fail.append(r)
    bad=[(r,F[r].GetValue(),round(dist(F[r])[0],1),dist(F[r])[1][:2] if dist(F[r])[1] else None) for r in mov if dist(F[r])[0]>maxfar and not bulk(F[r])]
    print('fail',fail); print('far>3 non-bulk',len(bad),bad)
    P.SaveBoard(K,B)
if __name__=='__main__': main()
