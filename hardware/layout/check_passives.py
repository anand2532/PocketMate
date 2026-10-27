# Report-only: pad-to-pin distance of every F-side passive (no moves).
# Placement pass: each F-side R/C goes next to the IC pad it serves (decoupling caps at power pins first), courtyard-checked.
import pcbnew as P, re, math
K='/workspace/pocketmate/hardware/kicad/PocketMate.kicad_pcb'; B=P.LoadBoard(K); M=P.FromMM
def V(x,y): return P.VECTOR2I(M(x),M(-y))
def mm(v): return (P.ToMM(v.x),-P.ToMM(v.y))
F={f.GetReference():f for f in B.GetFootprints()}
for f in F.values(): f.BuildCourtyardCaches()
GND=re.compile(r'^GND$|GND$')
PWR=re.compile(r'^\+|VSYS|VBAT|VBUS|3V3|5V|_REG|PMID|REGN|VDD|VIN|BTST|BOOST')
ICre=re.compile(r'^(U|Q|L|J|D)\d')
J11G={'C53','C54','R45','R46','C49','C50','C51','C52','R19','R20','R41','R42','R43','R44','R7','R8'}
pas=[r for r,f in F.items() if re.match(r'^[RC]\d',r) and r not in J11G and r!='R18' and f.GetLayer()==P.F_Cu]
def cy(f):
    c=f.GetCourtyard(P.F_CrtYd); return c.BBox() if c.OutlineCount() else f.GetBoundingBox(False,False)
KO=[(47.5,-11.5,54,2.0),(9,24,21,27),(-1,30.5,27,34.5)]
HOLES=[(2.5,-26.5),(50.5,-26.5),(2.5,6.5),(50.5,6.5)]
def ok_pt(x,y):
    for cx,cy_,sx,sy in [(2,-31,-1,-1),(51,-31,1,-1),(2,31.5,-1,1)]:
        if (x-cx)*sx>0 and (y-cy_)*sy>0 and math.hypot(x-cx,y-cy_)>2.4: return False
    return (-0.45<x<53.5 and -33.5<y<34.0) and not (x>26.5 and y>10.0) and all(math.hypot(x-a,y-b)>3.05 for a,b in HOLES)
def fits(f):
    b=cy(f); x0,x1=P.ToMM(b.GetLeft()),P.ToMM(b.GetRight()); y0,y1=-P.ToMM(b.GetBottom()),-P.ToMM(b.GetTop())
    if not all(ok_pt(x,y) for x,y in [(x0,y0),(x1,y0),(x0,y1),(x1,y1)]): return False
    return not any(a<x1 and x0<c and bb<y1 and y0<d for a,bb,c,d in KO)
occ=[cy(f) for r,f in F.items() if r not in pas and f.GetLayer()==P.F_Cu]
for t in B.GetTracks():
    if t.IsOnLayer(P.F_Cu): bb=t.GetBoundingBox(); bb.Inflate(M(0.1)); occ.append(bb)
def target(r):
    f=F[r]; nets=[p.GetNetname() for p in f.Pads()]
    sig=[n for n in nets if n and not GND.search(n)]
    best=None
    for n in sig:
        for r2,g in F.items():
            if r2==r or not ICre.match(r2) or g.GetLayer()!=P.F_Cu: continue
            for p in g.Pads():
                if p.GetNetname()==n:
                    pri=0 if r2[0]=='U' else 1
                    if best is None or pri<best[0]: best=(pri,r2,p)
    return best
def prio(r):
    nets=[F[r].Pads()[i].GetNetname() for i in range(len(F[r].Pads()))]
    dec=any(GND.search(n) for n in nets) and any(PWR.search(n) for n in nets) and r.startswith('C')
    return (0 if dec else 1, r)
def bulk(f):
    v=f.GetValue().replace('µ','u')
    m=re.match(r'([0-9.]+)\s*u',v); return f.GetReference().startswith('C') and m and float(m.group(1))>=10
bad=[]
for r in pas:
    t_=target(r)
    if not t_: continue
    px,py=mm(t_[2].GetPosition()); d=min(math.hypot(px-mm(p.GetPosition())[0],py-mm(p.GetPosition())[1]) for p in F[r].Pads() if p.GetNetname()==t_[2].GetNetname()) if any(p.GetNetname()==t_[2].GetNetname() for p in F[r].Pads()) else 99
    if d>3 and not bulk(F[r]): bad.append((r,F[r].GetValue(),t_[1],t_[2].GetNumber(),round(d,1)))
print('PAD-to-PIN>3mm (non-bulk):',len(bad),bad)

