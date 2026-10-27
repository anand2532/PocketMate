# Imports PocketMate.net (v2) into PocketMate.kicad_pcb, rough placement per placement_plan zones. Mech coords (Y up) -> KiCad Y=-y.
import pcbnew as P, re, os, math
K='/workspace/pocketmate/hardware/kicad'; SYS='/usr/share/kicad/footprints'
B=P.LoadBoard(K+'/PocketMate.kicad_pcb'); M=P.FromMM
# v4_22: USB-C tab - carrier bottom edge locally extended to Y -35.3 for X 8.3..18.7 (receptacle moved 1.4 mm outward)
_rm=[d for d in B.GetDrawings() if d.GetLayer()==P.Edge_Cuts and d.GetShape()==P.SHAPE_T_SEGMENT and abs(P.ToMM(d.GetStart().y)-34)<1e-3 and abs(P.ToMM(d.GetEnd().y)-34)<1e-3]
for d in _rm: B.Delete(d)
# fix corner arcs (base board drew 270-degree arcs; make them 90-degree convex corners)
for d in B.GetDrawings():
    if d.GetLayer()==P.Edge_Cuts and d.GetShape()==P.SHAPE_T_ARC:
        c=d.GetCenter(); a=d.GetStart(); b=d.GetEnd(); r=math.hypot(a.x-c.x,a.y-c.y)
        mx,my=(a.x+b.x)/2-c.x,(a.y+b.y)/2-c.y; n=math.hypot(mx,my)
        d.SetArcGeometry(a,P.VECTOR2I(int(c.x+r*mx/n),int(c.y+r*my/n)),b)
def _seg(a,b):
    t=P.PCB_SHAPE(B); t.SetShape(P.SHAPE_T_SEGMENT); t.SetStart(P.VECTOR2I(M(a[0]),M(-a[1]))); t.SetEnd(P.VECTOR2I(M(b[0]),M(-b[1]))); t.SetLayer(P.Edge_Cuts); t.SetWidth(M(0.1)); B.Add(t)
for a,b in [((2,-34),(8.3,-34)),((8.3,-34),(8.3,-35.3)),((8.3,-35.3),(18.7,-35.3)),((18.7,-35.3),(18.7,-34)),((18.7,-34),(51,-34))]: _seg(a,b)
def V(x,y): return P.VECTOR2I(M(x),M(-y))
s=open(K+'/PocketMate.net').read()
comps=[]
for m in re.finditer(r'\(comp \(ref "([^"]+)"\)\s*\(value "([^"]*)"\)(.*?)\(sheetpath \(names "([^"]*)"',s,re.S):
    ref,val,body,sh=m.groups(); fp=re.search(r'\(footprint "([^"]*)"\)',body).group(1); comps.append([ref,val,fp,sh])
FLEX=[c for c in comps if c[3]=='/SideFlex/']; comps=[c for c in comps if c[3]!='/SideFlex/']
if False: comps.append(['J_SIDEKEY','FH12-16S side-key flex (RESERVED, not in netlist)','Connector_FFC-FPC:Hirose_FH12-16S-0.5SH_1x16-1MP_P0.50mm_Horizontal','/'])
# duplicate SW1: the /Audio/ one -> SW5 (unresolved in schematic)
for c in comps:
    if c[0]=='SW1' and c[3]=='/Audio/': c[0]='SW5'
nets={}
for m in re.finditer(r'\(net \(code "?(\d+)"?\) \(name "([^"]*)"\)(.*?)\)\s*\)\s*(?=\(net |\)\s*\)\s*$)',s,re.S):
    for r,p in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"',m.group(3)): nets.setdefault(r,{}).setdefault(p,[]).append(m.group(2))
tst={}
for m in re.finditer(r'\(comp \(ref "([^"]+)"\).*?\(sheetpath \(names "([^"]*)"\) \(tstamps "([^"]*)"\)\)\s*\(tstamps "([^"]*)"\)',s,re.S):
    r,nm,tp,u=m.groups(); r='SW5' if (r=='SW1' and nm=='/Audio/') else r; tst[r]=tp+u
DNP=set()
for m in re.finditer(r'\(comp \(ref "([^"]+)"\)(.*?)\(tstamps "[^"]*"\)\)\s*\(tstamps',s,re.S):
    if re.search(r'\(property \(name "dnp"\)',m.group(2)): DNP.add(m.group(1))
# existing locked parts
_j6=[f for f in B.GetFootprints() if f.GetReference()=='J6']
for f in _j6: B.Delete(f)
ex={f.GetReference():f for f in B.GetFootprints()}
if 'J_NTC' in ex: ex['J_NTC'].SetReference('J10'); ex['J10']=ex.pop('J_NTC')
def load(fpid):
    fpid=fpid.replace('Maxim_TDFN-10-1EP_2x2.5mm_P0.5mm_MAX17055_UNVERIFIED','Maxim_TDFN-10-1EP_2x2.5mm_P0.4mm_EP1.4x1.3mm_MAX17055')  # netlist lags the library rename
    lib,name=fpid.split(':'); path=(K+'/PocketMate.pretty') if lib=='PocketMate' else f'{SYS}/{lib}.pretty'
    f=P.FootprintLoad(path,name)
    if f is not None: f.SetFPID(P.LIB_ID(lib,name))
    return f
place={ # ref:(x,y,rot,side)
 'J3':(18.33,19.1,180,'F'),'J4':(36,4.9,180,'F'),'J7':(3.76,23.4,270,'F'),'J6':(13.5,-33.25,0,'F'),
 'U4':(8.5,-21,0,'F'),'U3':(21,-30.6,90,'F'),'U2':(17.6,-22.0,0,'F'),'D2':(6.5,-31.0,90,'F'),'Q1':(24.5,-23.5,0,'F'),
 'U5':(5.8,12,0,'F'),'L1':(12,5.5,0,'F'),'U6':(9.8,12.5,0,'F'),'D3':(8,6,0,'F'),'D4':(11,-12,0,'F'),
 'U8':(23,-6.5,0,'F'),'L2':(29.8,-6.5,0,'F'),'Q2':(31,-0.6,0,'F'),'Q3':(35.5,-1,0,'F'),'U7':(21.7,12.6,0,'F'),'U9':(14,-2,0,'F'),
 'J8':(36,-12,0,'F'),'Q4':(13.2,12.6,0,'F'),'Q5':(17.1,12.6,0,'F'),'TP1':(40,-10,0,'F'),'TP2':(42.5,-10,0,'F'),
 'U1':(40,-25,0,'F'),'J5':(47,-30,0,'F'),'MK1':(44,-6,0,'F'),'MK2':(2.5,32,0,'F'),'SW5':(36,-9,0,'F'),'D1':(10,29,0,'F'),
 'SW1':(14,31.3,0,'F'),'SW3':(32,-4,0,'F'),'SW4':(38,-4,0,'F'),'SW2':(40,-1,0,'F'),
 'U10':(30,1,0,'F'),'U11':(42,-18,0,'F'),'J_SIDEKEY':(19,29.4,180,'F'),'J11':(19,29.4,180,'F'),'R18':(1.0,12.5,90,'F'),'U12':(13,-13,0,'F'),'L3':(17,-13,0,'F'),'J12':(30,-30.2,0,'F'),'U13':(23.8,25.6,0,'F'),'D5':(21.8,25.2,0,'F'),'D4':(25.6,25.2,90,'F'),'J9':(46,-14,0,'F'),'R18':(1.0,12.5,90,'F'),
}
added=[];miss=[]
for ref,val,fpid,sh in comps:
    if ref in ex: f=ex[ref]
    else:
        f=load(fpid)
        if f is None: miss.append((ref,fpid)); continue
        f.SetReference(ref); B.Add(f); added.append(ref)
    f.SetValue(val)
    if hasattr(f,'SetDNP'): f.SetDNP(ref in DNP)
    if ref in tst: f.SetPath(P.KIID_PATH(tst[ref]))
    if ref in('J1','J2'):
        for pad in f.Pads():
            sz=pad.GetSize()
            if P.ToMM(sz.x)<P.ToMM(sz.y): pad.SetSize(P.VECTOR2I(sz.y,sz.x))
    if ref in('J1','J2'):
        x,y=(29.0,7.0) if ref=='J1' else (29.0,-27.0)
        f.SetPosition(V(x,y)); f.SetOrientationDegrees(90)
        if f.GetLayer()==P.F_Cu: f.Flip(f.GetPosition(),False)
        p1=[p for p in f.Pads() if p.GetNumber() in('1','101')][0]
        if P.ToMM(p1.GetPosition().x)>x: f.SetOrientationDegrees(f.GetOrientationDegrees()+180)
        f.SetLocked(True)
    elif ref in place:
        x,y,r,side=place[ref]; f.SetPosition(V(x,y)); f.SetOrientationDegrees(r)
    # nets
    for pad in f.Pads():
        n=nets.get(ref,{}).get(pad.GetNumber())
        if n:
            ni=B.FindNet(n[0])
            if ni is None: ni=P.NETINFO_ITEM(B,n[0]); B.Add(ni)
            pad.SetNet(ni)
FIXED={'R18','Q6','J8','U7','Q4','Q5','U6','U9','U3','U4','U5','L1','Q1','U8','L2','Q2','Q3','U12','L3','J12','J11','D2','U2','J1','J2','J3','J4','J6','J7','J10','H1','H2','H3','H4'}
def cy(f):
    c=f.GetCourtyard(f.GetLayer()==P.B_Cu and P.B_CrtYd or P.F_CrtYd)
    return c.BBox() if c.OutlineCount() else f.GetBoundingBox(False,False)
EDGE=B.GetBoardEdgesBoundingBox()
def fits(f):
    bb=cy(f); x0,x1=P.ToMM(bb.GetLeft()),P.ToMM(bb.GetRight()); y0,y1=-P.ToMM(bb.GetBottom()),-P.ToMM(bb.GetTop())
    pts=[(x0,y0),(x1,y0),(x0,y1),(x1,y1),((x0+x1)/2,(y0+y1)/2)]
    return all(inboard2(x,y) for x,y in pts) and not any(a<x1 and x0<c and b<y1 and y0<d for a,b,c,d in KO2)
KO2=[(47.5,-11.5,54,2.0),(9,24,21,27),(12.5,-27.1,21.0,-20.2)]  # last = USB corridor
def _arc(x,y):
    for cx,cy_,sx,sy in [(2,-31,-1,-1),(51,-31,1,-1),(2,32,-1,1)]:
        if (x-cx)*sx>0 and (y-cy_)*sy>0 and math.hypot(x-cx,y-cy_)>2.4: return False
    return True
def inboard2(x,y): return _arc(x,y) and (-0.5<x<53.5 and -33.5<y<34.5) and not (x>26.5 and y>10.0) and all(math.hypot(x-hx,y-hy)>3.0 for hx,hy in [(2.5,-26.5),(50.5,-26.5),(2.5,6.5),(50.5,6.5)])
occF=[cy(f) for f in B.GetFootprints() if f.GetReference() in FIXED and f.GetLayer()==P.F_Cu]
for ref in place:
    if ref in FIXED or ref not in {f.GetReference() for f in B.GetFootprints()}: continue
    f=[g for g in B.GetFootprints() if g.GetReference()==ref][0]; x,y,r,_=place[ref]
    for k in range(0,800):
        rr=0.25*k**0.5*2; th=k*2.4; f.SetPosition(V(x+rr*math.cos(th),y+rr*math.sin(th)))
        bb=cy(f); bb.Inflate(M(0.1))
        if fits(f) and not any(bb.Intersects(o) for o in occF): occF.append(cy(f)); break
    else: print('could not place',ref)
# passives: place around the IC they share a signal net with, simple occupancy search
def bbox(f): b=f.GetCourtyard(P.F_CrtYd).BBox() if f.GetCourtyard(P.F_CrtYd).OutlineCount() else f.GetBoundingBox(False,False); return b
fps={f.GetReference():f for f in B.GetFootprints()}
PWRN=re.compile(r'GND|^\+|VSYS|VBAT|3V3|5V',re.I)
def anchor(ref):
    jn={n for ns in nets.get('J11',{}).values() for n in ns if not PWRN.search(n)}|{n for ns in nets.get('U13',{}).values() for n in ns if not PWRN.search(n)}
    if any(n in jn for ns in nets.get(ref,{}).values() for n in ns): return 'U13'
    for p,ns in nets.get(ref,{}).items():
        for n in ns:
            if PWRN.search(n): continue
            for r2,pp in nets.items():
                if r2!=ref and re.match(r'^(U|J|Q|L|MK|SW)',r2) and any(n in v for v in pp.values()) and r2 in place: return r2
    for p,ns in nets.items(): pass
    return None
occ=[(P.F_Cu,o) for o in occF]
KO=[(47.5,-11.5,54,2.0),(9,24,21,27)]
edge=B.GetBoardEdgesBoundingBox()
def inboard(x,y): return (-0.3<x<53.3 and -33.3<y<34.3) and not (x>26.3 and y>9.8) and all(math.hypot(x-hx,y-hy)>3.6 for hx,hy in [(2.5,-26.5),(50.5,-26.5),(2.5,6.5),(50.5,6.5)]) and not any(a<x<c and b<y<d for a,b,c,d in KO)
unplaced=[]
for ref,val,fpid,sh in comps:
    if not re.match(r'^(R|C)\d',ref) or ref in FIXED: continue
    f=fps[ref]; a=anchor(ref)
    ax,ay=(P.ToMM(fps[a].GetPosition().x),-P.ToMM(fps[a].GetPosition().y)) if a else (30,-5)
    ok=False
    for k in range(1,1500):
        rr=1.2+0.3*k**0.5; th=k*2.4
        x,y=ax+rr*math.cos(th),ay+rr*math.sin(th)
        if not inboard(x,y): continue
        f.SetPosition(V(x,y)); bb=cy(f); bb.Inflate(M(0.15))
        if not fits(f) or any(l==P.F_Cu and bb.Intersects(o) for l,o in occ): continue
        occ.append((P.F_Cu,cy(f))); ok=True; break
    if not ok:
        for k in range(1,3000):
            rr=0.3*k**0.5; th=k*2.4; x,y=33+rr*math.cos(th),-12+rr*math.sin(th)
            if not inboard(x,y): continue
            f.SetPosition(V(x,y)); bb=cy(f); bb.Inflate(M(0.15))
            if not fits(f) or any(l==P.F_Cu and bb.Intersects(o) for l,o in occ): continue
            occ.append((P.F_Cu,cy(f))); ok=True; break
    if not ok: unplaced.append(ref)
B.GetDesignSettings().m_MinThroughDrill=M(0.2)
[f.SetBoardOnly(True) for f in B.GetFootprints() if f.GetReference() in('H1','H2','H3','H4')]
[f.SetLocked(True) for f in B.GetFootprints() if f.GetReference() in('J1','J2','J3','J4','J6','J7','J12','J11')]
P.SaveBoard(K+'/PocketMate.kicad_pcb',B)
print('flex parts skipped',[c[0] for c in FLEX]); print('added',len(added),'missing fp',miss,'unplaced passives',unplaced)
print('J1 pad1', [ (P.ToMM(p.GetPosition().x),-P.ToMM(p.GetPosition().y)) for p in fps['J1'].Pads() if p.GetNumber()=='1'], 'J2 pad101',[ (P.ToMM(p.GetPosition().x),-P.ToMM(p.GetPosition().y)) for p in fps['J2'].Pads() if p.GetNumber()=='101'])
print('nets on board',B.GetNetCount())
