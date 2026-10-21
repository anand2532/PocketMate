# One-off solver (run once): finds legal spots for far passives, prints an explicit table for hand_place.py.
import pcbnew as P, re, math, itertools
K='/workspace/pocketmate/hardware/kicad/PocketMate.kicad_pcb'; B=P.LoadBoard(K); M=P.FromMM
def V(x,y): return P.VECTOR2I(M(x),M(-y))
def mm(v): return (P.ToMM(v.x),-P.ToMM(v.y))
F={f.GetReference():f for f in B.GetFootprints()}
_src=open('/workspace/pocketmate/hardware/layout/place_passives.py').read()
exec(_src[_src.index('def cy(f):'):_src.index('occ=[')])
J11G={'C53','C54','R45','R46','C49','C50','C51','C52','R19','R20','R41','R42','R43','R44','R7','R8'}
pas=[r for r,f in F.items() if re.match(r'^[RC]\d',r) and r not in J11G and r!='R18' and not f.IsFlipped()]
GND=re.compile(r'GND$'); ICre=re.compile(r'^(U|Q|L|J|D)\d')
def bulk(f):
    m=re.match(r'([0-9.]+)\s*u',f.GetValue().replace('µ','u')); return f.GetReference().startswith('C') and m and float(m.group(1))>=10
def target(r):
    best=None
    for n in [p.GetNetname() for p in F[r].Pads() if p.GetNetname() and not GND.search(p.GetNetname())]:
        for r2,g in F.items():
            if r2==r or not ICre.match(r2) or g.IsFlipped(): continue
            for p in g.Pads():
                if p.GetNetname()==n:
                    pri=0 if r2[0]=='U' else 1
                    if best is None or pri<best[0]: best=(pri,r2,p)
    return best
def dist(r):
    t=target(r)
    if not t: return 0
    px,py=mm(t[2].GetPosition()); ps=[p for p in F[r].Pads() if p.GetNetname()==t[2].GetNetname()]
    return min(math.hypot(px-mm(p.GetPosition())[0],py-mm(p.GetPosition())[1]) for p in ps)
for f in F.values(): f.BuildCourtyardCaches()
def poly(f): return f.GetCourtyard(P.F_CrtYd)
trk=[t for t in B.GetTracks() if t.IsOnLayer(P.F_Cu)]
def legal(r):
    f=F[r]; f.BuildCourtyardCaches()
    if not fits(f): return False
    c=poly(f)
    if c.OutlineCount()==0: return False
    for r2,g in F.items():
        if r2==r or g.IsFlipped(): continue
        c2=poly(g)
        if c2.OutlineCount() and c.Collide(c2): return False
        if c2.OutlineCount()==0:
            if c.BBox().Intersects(g.GetBoundingBox(False,False)): return False
    bb=c.BBox()
    for t in trk:
        tb=t.GetBoundingBox(); tb.Inflate(M(0.15))
        if bb.Intersects(tb): return False
    return True
def spots(r,lim=2.95):
    f=F[r]; t=target(r); px,py=mm(t[2].GetPosition()); out=[]
    ox,oy,orot=*mm(f.GetPosition()),f.GetOrientationDegrees()
    for rot in (0,90,180,270):
        f.SetOrientationDegrees(rot)
        for i in range(-40,41):
            for j in range(-40,41):
                x,y=px+i*0.1,py+j*0.1
                f.SetPosition(V(x,y))
                if dist(r)<=lim and legal(r): out.append((dist(r),x,y,rot))
    f.SetPosition(V(ox,oy)); f.SetOrientationDegrees(orot); f.BuildCourtyardCaches()
    return sorted(out)
def place(r,s): F[r].SetOrientationDegrees(s[3]); F[r].SetPosition(V(s[1],s[2])); F[r].BuildCourtyardCaches()
far=[r for r in pas if not bulk(F[r]) and dist(r)>3.0]
print('far',len(far),far)
moved={}
for r in sorted(far,key=lambda r:dist(r)):
    s=spots(r)
    if s: place(r,s[0]); moved[r]=s[0]; print('OK',r,s[0]); continue
    # eviction: move one nearby passive with slack to another legal spot within its own 3mm
    t=target(r); px,py=mm(t[2].GetPosition()); done=False
    near=sorted([q for q in pas if q!=r and not bulk(F[q]) and math.hypot(mm(F[q].GetPosition())[0]-px,mm(F[q].GetPosition())[1]-py)<4.0],key=lambda q:-dist(q))
    for q in near:
        old=(dist(q),*mm(F[q].GetPosition()),F[q].GetOrientationDegrees())
        F[q].SetPosition(V(-50,-50)); F[q].BuildCourtyardCaches()
        s=spots(r)
        if s:
            place(r,s[0]); s2=spots(q)
            if s2: place(q,s2[0]); moved[r]=s[0]; moved[q]=s2[0]; print('EVICT',r,s[0],q,s2[0]); done=True; break
            F[r].SetPosition(V(-60,-60))
        place(q,old)
    if not done: print('FAIL',r,round(dist(r),2))
print('remaining far',[ (r,round(dist(r),1)) for r in pas if not bulk(F[r]) and dist(r)>3.0])
with open('/tmp/opt/table.txt','w') as o:
    for r in sorted(pas):
        f=F[r]; x,y=mm(f.GetPosition()); o.write("('%s',%.2f,%.2f,%d),\n"%(r,x,y,round(f.GetOrientationDegrees())%360))
