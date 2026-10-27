# One-off: fix DRC-conflicting / far passives on the current board, then dump a COMPLETE explicit table (both sides).
import pcbnew as P, re, math
K='/workspace/pocketmate/hardware/kicad/PocketMate.kicad_pcb'; B=P.LoadBoard(K); M=P.FromMM
def V(x,y): return P.VECTOR2I(M(x),M(-y))
def mm(v): return (P.ToMM(v.x),-P.ToMM(v.y))
F={f.GetReference():f for f in B.GetFootprints()}
_src=open('place_passives.py').read(); exec(_src[_src.index('def cy(f):'):_src.index('occ=[')])
exec(_src[_src.index('def b_ok(f):'):_src.index('def search(')])
GND=re.compile(r'GND$'); ICre=re.compile(r'^(U|Q|L|J|D)\d')
J11G={'C53','C54','R45','R46','C49','C50','C51','C52','R19','R20','R41','R42','R43','R44','R7','R8'}
pas=[r for r in F if re.match(r'^[RC]\d',r) and r not in J11G and r!='R18']
def bulk(f):
    m=re.match(r'([0-9.]+)\s*u',f.GetValue().replace('µ','u')); return f.GetReference().startswith('C') and m and float(m.group(1))>=10
TC={}
def target(r):
    if r in TC: return TC[r]
    best=None
    for n in [p.GetNetname() for p in F[r].Pads() if p.GetNetname() and not GND.search(p.GetNetname())]:
        for r2,g in F.items():
            if r2==r or not ICre.match(r2) or g.IsFlipped(): continue
            for p in g.Pads():
                if p.GetNetname()==n:
                    pri=0 if r2[0]=='U' else 1
                    if best is None or pri<best[0]: best=(pri,r2,p)
    TC[r]=best; return best
def dist(r):
    t=target(r)
    if not t: return 0
    px,py=mm(t[2].GetPosition()); ps=[p for p in F[r].Pads() if p.GetNetname()==t[2].GetNetname()]
    return min(math.hypot(px-mm(p.GetPosition())[0],py-mm(p.GetPosition())[1]) for p in ps)
def side(f): return 'B' if f.IsFlipped() else 'F'
def cyd(f):
    f.BuildCourtyardCaches(); c=f.GetCourtyard(P.B_CrtYd if f.IsFlipped() else P.F_CrtYd); return c
def box(f):
    c=cyd(f); b=c.BBox() if c.OutlineCount() else f.GetBoundingBox(False,False); return b
PTH=[]
for f in F.values():
    for pd in f.Pads():
        if pd.GetAttribute() in (P.PAD_ATTRIB_PTH,P.PAD_ATTRIB_NPTH): b=pd.GetBoundingBox(); b.Inflate(M(0.25)); PTH.append(b)
TRK=[]
for t in B.GetTracks():
    b=t.GetBoundingBox(); b.Inflate(M(0.15)); TRK.append((t.IsOnLayer(P.F_Cu),t.IsOnLayer(P.B_Cu),b))
def legal(r):
    f=F[r]; s=side(f)
    if s=='F' and not fits(f): return False
    if s=='B' and not b_ok(f): return False
    c=cyd(f); b=box(f); b.Inflate(M(0.03))
    for r2,g in F.items():
        if r2==r or side(g)!=s: continue
        b2=box(g)
        if not b.Intersects(b2): continue
        c2=cyd(g)
        if c2.OutlineCount()==0 or c.OutlineCount()==0 or c.Collide(c2): return False
    for onF,onB,tb in TRK:
        if ((s=='F' and onF) or (s=='B' and onB)) and b.Intersects(tb): return False
    if s=='B' and any(b.Intersects(x) for x in PTH): return False
    return True
def spots(r,lim):
    f=F[r]; t=target(r); px,py=mm(t[2].GetPosition()); out=[]
    o=(mm(f.GetPosition()),f.GetOrientationDegrees(),f.IsFlipped())
    for flip in (False,True):
        if f.IsFlipped()!=flip: f.Flip(f.GetPosition(),False)
        for rot in (0,90):
            f.SetOrientationDegrees(rot)
            for i in range(-22,23):
                for j in range(-22,23):
                    f.SetPosition(V(px+i*0.15,py+j*0.15)); d=dist(r)
                    if d<=lim and legal(r): out.append((d+(0.3 if flip else 0),px+i*0.15,py+j*0.15,rot,flip))
    if f.IsFlipped()!=o[2]: f.Flip(f.GetPosition(),False)
    f.SetOrientationDegrees(o[1]); f.SetPosition(V(*o[0]))
    return sorted(out)
def put(r,s):
    f=F[r]
    if f.IsFlipped()!=s[4]: f.Flip(f.GetPosition(),False)
    f.SetOrientationDegrees(s[3]); f.SetPosition(V(s[1],s[2]))
def park(r): F[r].SetPosition(V(-80,-80))
import subprocess
bad=set()
for r in pas:
    if not bulk(F[r]) and target(r) and dist(r)>3.0: bad.add(r)
for r in pas:
    if not legal(r): bad.add(r)
print('to fix',sorted(bad))
for r in sorted(bad): park(r)
order=sorted(bad,key=lambda r:(1 if bulk(F[r]) else 0, r))
fails=[]
for r in order:
    if not target(r):
        s=None
    else:
        s=spots(r,2.95) or spots(r,4.5) or spots(r,7.0)
    if s: put(r,s[0]); print('fix',r,[round(v,2) if isinstance(v,float) else v for v in s[0]])
    else: fails.append(r)
print('FAILS',fails)
rem=[(r,round(dist(r),1)) for r in pas if not bulk(F[r]) and target(r) and dist(r)>3.0]
print('remaining far',rem)
with open('passive_table.py','w') as o:
    o.write("# Explicit passive placements (ref, x, y, rot, side) in mech coords (origin body centre, +Y up). Applied by hand_place.py; no search.\nTABLE=[\n")
    for r in sorted(pas,key=lambda r:(r[0],int(re.sub(r'\D','',r)))):
        f=F[r]; x,y=mm(f.GetPosition()); o.write("('%s',%.2f,%.2f,%d,'%s'),\n"%(r,x,y,round(f.GetOrientationDegrees())%360,side(f)))
    o.write("]\n")
