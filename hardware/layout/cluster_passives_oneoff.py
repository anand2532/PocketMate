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
TC={}
def dist(r):
    t=TC.get(r) or TC.setdefault(r,target(r))
    if not t: return 0
    px,py=mm(t[2].GetPosition()); ps=[p for p in F[r].Pads() if p.GetNetname()==t[2].GetNetname()]
    return min(math.hypot(px-mm(p.GetPosition())[0],py-mm(p.GetPosition())[1]) for p in ps)
for f in F.values(): f.BuildCourtyardCaches()
def poly(f): return f.GetCourtyard(P.F_CrtYd)
trk=[t for t in B.GetTracks() if t.IsOnLayer(P.F_Cu)]
def _bb(g):
    c=poly(g); b=c.BBox() if c.OutlineCount() else g.GetBoundingBox(False,False)
    return (P.ToMM(b.GetLeft()),P.ToMM(b.GetRight()),-P.ToMM(b.GetBottom()),-P.ToMM(b.GetTop()))
BBS={r2:_bb(g) for r2,g in F.items() if not g.IsFlipped()}
TB=[]
for t in trk:
    b=t.GetBoundingBox(); TB.append((P.ToMM(b.GetLeft())-0.15,P.ToMM(b.GetRight())+0.15,-P.ToMM(b.GetBottom())-0.15,-P.ToMM(b.GetTop())+0.15))
def legal(r):
    f=F[r]; f.BuildCourtyardCaches()
    if not fits(f): return False
    a=_bb(f)
    for r2,b in BBS.items():
        if r2!=r and a[0]<b[1] and b[0]<a[1] and a[2]<b[3] and b[2]<a[3]: return False
    for b in TB:
        if a[0]<b[1] and b[0]<a[1] and a[2]<b[3] and b[2]<a[3]: return False
    return True
def spots(r,lim=2.95):
    f=F[r]; t=TC.get(r) or TC.setdefault(r,target(r)); px,py=mm(t[2].GetPosition()); out=[]
    ox,oy,orot=*mm(f.GetPosition()),f.GetOrientationDegrees()
    for rot in (0,90):
        f.SetOrientationDegrees(rot)
        for i in range(-24,25):
            for j in range(-24,25):
                x,y=px+i*0.15,py+j*0.15
                f.SetPosition(V(x,y))
                if dist(r)<=lim and legal(r): out.append((dist(r),x,y,rot))
    f.SetPosition(V(ox,oy)); f.SetOrientationDegrees(orot); f.BuildCourtyardCaches()
    return sorted(out)
def place(r,s): F[r].SetOrientationDegrees(s[3]); F[r].SetPosition(V(s[1],s[2])); F[r].BuildCourtyardCaches(); BBS[r]=_bb(F[r])

def park(r): F[r].SetPosition(V(-80,-80)); F[r].BuildCourtyardCaches(); BBS[r]=_bb(F[r])
def tgtic(r):
    t=TC.get(r) or TC.setdefault(r,target(r)); return t[1] if t else None
def best_spot(r,lim):
    s=spots(r,lim); return s[0] if s else None
def cluster(ic):
    mine=[r for r in pas if tgtic(r)==ic]
    icx,icy=mm(F[ic].GetPosition())
    foreign=[r for r in pas if r not in mine and math.hypot(mm(F[r].GetPosition())[0]-icx,mm(F[r].GetPosition())[1]-icy)<5.5]
    save={r:(0,*mm(F[r].GetPosition()),F[r].GetOrientationDegrees()) for r in mine+foreign}
    for r in mine+foreign: park(r)
    nb=sorted([r for r in mine if not bulk(F[r])],key=lambda r:(0 if r.startswith('C') else 1,r))
    fails=[]
    for r in nb:
        b=best_spot(r,2.95)
        if b: place(r,b)
        else: fails.append(r)
    for r in [r for r in mine if bulk(F[r])]+sorted(foreign)+fails:
        b=best_spot(r,2.95) or best_spot(r,4.0)
        if b: place(r,b); continue
        b=spots(r,8.0)
        if b: place(r,b[0])
        else: place(r,save[r]); print('  could not re-place',r,'restored')
    print(ic,'->',[(r,round(dist(r),1)) for r in mine+foreign if not bulk(F[r]) and dist(r)>3])
for ic in ['U8','U5','U12','U1','U9','U4','U11','L3','J4','U6','U7']:
    if ic in F: cluster(ic)
for it in range(2):
    bad=sorted({tgtic(r) for r in pas if not bulk(F[r]) and dist(r)>3.0} - {None})
    print('pass',it,bad)
    for ic in bad: cluster(ic)
rem=[(r,round(dist(r),1)) for r in pas if not bulk(F[r]) and dist(r)>3.0]
print('remaining far',len(rem),rem)
with open('/workspace/pocketmate/hardware/layout/passive_table.py','w') as o:
    o.write("# Explicit F-side passive placements (ref, x, y, rot) in mech coords; generated once, then hand-checked. Applied by hand_place.py.\nTABLE=[\n")
    for r in sorted(pas, key=lambda r:(r[0],int(re.sub(r'\D','',r) or 0))):
        f=F[r]; x,y=mm(f.GetPosition()); o.write("('%s',%.2f,%.2f,%d),\n"%(r,x,y,round(f.GetOrientationDegrees())%360))
    o.write("]\n")
