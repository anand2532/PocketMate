# v4_22b: v4_22 passive baseline updated to Layout placement (2026-10-21 IST). Source doc PocketMate_v4_22 untouched.
import FreeCAD as App, Part, Import, FreeCADGui as G, math
from FreeCAD import Vector as V
OUT='/workspace/pocketmate/mechanical'
src=App.getDocument('PocketMate_v4_22')
S={o.Name:o.Shape.copy() for o in src.Objects if o.TypeId=='Part::Feature'}
def box(x0,x1,y0,y1,z0,z1): return Part.makeBox(x1-x0,y1-y0,z1-z0,V(x0,y0,z0))
def cylY(x,z,r,y0,y1): return Part.makeCylinder(r,y1-y0,V(x,y0,z),V(0,1,0))
def cylX(y,z,r,x0,x1): return Part.makeCylinder(r,x1-x0,V(x0,y,z),V(1,0,0))
def rrect_y(cx,cz,w,h,r,y):  # rounded rect wire in XZ plane at Y=y
    x0,x1,z0,z1=cx-w/2,cx+w/2,cz-h/2,cz+h/2; e=[]
    pts=[((x0+r,z0),(x1-r,z0)),((x1,z0+r),(x1,z1-r)),((x1-r,z1),(x0+r,z1)),((x0,z1-r),(x0,z0+r))]
    cs=[(x1-r,z0+r,-90),(x1-r,z1-r,0),(x0+r,z1-r,90),(x0+r,z0+r,180)]
    for (a,b),(ccx,ccz,ang) in zip(pts,cs):
        e.append(Part.LineSegment(V(a[0],y,a[1]),V(b[0],y,b[1])).toShape())
        m=math.radians(ang+45); s=math.radians(ang); t=math.radians(ang+90)
        e.append(Part.Arc(V(ccx+r*math.cos(s),y,ccz+r*math.sin(s)),V(ccx+r*math.cos(m),y,ccz+r*math.sin(m)),V(ccx+r*math.cos(t),y,ccz+r*math.sin(t))).toShape())
    return Part.Wire(Part.__sortEdges__(e))
U=S['Al_Unibody']; B=S['Bezel_DisplayFrame_PC']
# --- probe action-button hole Z extent in right wall
zs=[z/20 for z in range(0,400) if not U.isInside(V(61.5,20,z/20),0.01,True)]
hz0,hz1=8.0,19.0   # probe: slot open Z8 up to wall top (closed by bezel)
# 1 USB-C J6: fill old opening, new 9.4x3.6 R1.6 at X13.5 Z11.36..14.96 with 0.4x45 outer chamfer
U=U.fuse(box(15.0,25.0,-37.5,-35.5,11.0,15.5))
inner=Part.Face(rrect_y(13.5,13.16,9.4,3.6,1.6,-35.4)).extrude(V(0,-2.0,0))
cham=Part.makeLoft([rrect_y(13.5,13.16,9.4,3.6,1.6,-37.1),rrect_y(13.5,13.16,10.2,4.4,2.0,-37.51)],True)
U=U.cut(inner).cut(cham)
# 4a mute slider slot moved -2.0 X (clear of J11), LED light-pipe hole, mic ports moved
U=U.fuse(box(2.0,14.0,35.5,37.5,12.0,15.5)).fuse(box(21.0,23.0,35.5,37.5,14.0,16.0)).fuse(box(-53.0,-51.0,35.5,37.5,14.0,16.0))
U=U.cut(box(0.2,11.0,35.0,38.0,12.6,14.9))           # slider knob slot 10.8 x 2.3
U=U.cut(cylY(-1.6,13.75,0.8,35.0,38.0))               # LED light pipe dia 1.6
for mx in (-52.0,-5.0): U=U.cut(cylY(mx,14.4,0.4,35.0,38.0))   # mic ports dia 0.8
# 4b action-button backing rib (Al, floor-standing), cap guides, ALS ledge
U=U.fuse(box(54.5,55.4,15.0,25.0,1.0,15.6))
U=U.fuse(box(58.9,60.6,hz_a:=13.0-0.0,13.7,hz0-0.8,hz1+0.8) if False else box(58.9,60.6,12.9,13.6,hz0-0.8,hz1-0.2)).fuse(box(58.9,60.6,26.4,27.1,hz0-0.8,hz1-0.2))
U=U.fuse(box(-60.6,-55.5,15.5,24.5,16.0,16.85))
# bezel: integral side-key backing rib + flange (PC, installed after the cell); display-tail notch
B=B.fuse(box(-49.5,-14.5,32.4,33.3,11.5,15.85)).fuse(box(-49.5,-14.5,32.4,34.0,15.2,15.85))   # rib moved to Y32.4 so the production lead U-turn (Y<=32.03) passes under nothing
B=B.cut(box(9.4,27.2,32.2,35.3,15.0,17.6)).cut(box(-54.6,-53.9,15.5,25.0,15.0,17.2))
# action cap (PC) through right wall hole y14.6..25.4
hz0,hz1=8.5,18.5   # hole is 10.8 x 10.0 rounded rect, R~4.6 (probed)
_cb=box(60.45,62.4,14.85,25.15,8.75,18.25); _cb=_cb.makeFillet(4.3,[e for e in _cb.Edges if abs(e.Vertexes[0].Point.x-e.Vertexes[1].Point.x)>1])
cap=_cb.fuse(box(59.7,60.45,13.8,26.2,hz0-0.8,hz1+0.3)).fuse(cylX(20.0,13.5,1.2,57.2,59.7))
zc=13.5
# side-key flex (0.12 PI), wall plane y35.33..35.45
F=[box(-14.62,53.2,35.33,35.45,12.0,15.1),            # top wall run (carrier zone + behind camera)
   box(-14.62,-14.5,33.3,35.45,12.0,15.1),           # jog wall->rib, 0.5 left of cell tab bend
   box(-49.6,-14.5,33.3,33.42,12.0,15.1),            # on PC backing rib (switches face wall)
   box(-49.72,-49.6,33.3,35.45,12.0,15.1),
   box(-54.08,-49.6,35.33,35.45,12.0,15.1),
   box(-54.2,-54.08,16.0,35.45,12.0,15.1),
   box(-54.2,-54.08,16.0,24.5,15.1,16.97),           # riser through bezel notch
   box(-59.8,-54.08,16.0,24.5,16.85,16.97),          # onto ALS ledge
   box(13.0,25.0,34.34,35.33,12.2,12.32),            # tail into J11 mouth (fold FAILS bend radius - see md)
   box(53.6,53.72,26.0,35.45,12.0,15.1),             # corner drop between camera and boss
   box(53.6,55.52,25.88,26.0,12.0,15.1),
   box(55.4,55.52,15.0,26.0,12.0,15.1)]              # on action rib face
flex=F[0].fuse(F[1:]).removeSplitter()
parts={k:v for k,v in S.items() if not k.startswith('Vol_')}
parts.update({'Al_Unibody':U,'Bezel_DisplayFrame_PC':B,'ActionCap_PC':cap,'SideKey_Flex':flex})
drop=['Vol_USBC','Vol_BattConn_ZH','Vol_BattLeads','Vol_BattTabBend','Vol_DSI_FPC','Vol_ALS','Vol_ActionBtn','Vol_SideBtns']
vols={k:v for k,v in S.items() if k.startswith('Vol_') and k not in drop}
vols['Vol_Carrier']=box(-1.0,54.0,-34.0,34.5,9.94,11.54)
N={}
N['Vol_J6_USBC_HRO']=Part.Face(rrect_y(13.5,13.12,8.94,3.16,1.3,-29.55)).extrude(V(0,-7.35,0))
N['Vol_J6_CarrierTab']=box(8.3,18.7,-35.3,-34.0,9.94,11.54)
N['Vol_J7_Molex205338']=box(-0.95,8.39,15.59,31.82,11.54,14.14)    # Layout final: centre (3.7,25.2), mouth -X, mated 2.60
N['Vol_J7_Housing205341']=box(-8.88,0.22,16.43,30.98,11.60,14.14)   # 14.55 x 9.1 x 2.54, mated position
N['Vol_Cell_Prod_62']=box(-53.75,-2.75,-33.5,28.5,2.3,10.8)
N['Vol_Cell_Proto_Akyga']=box(-53.75,-2.75,-33.5,32.0,2.3,9.3)
def lead(i,ye,z0,zt,od=1.6):
    xi=-20.2-1.6*i; cx,cy=-17.0,28.5; Ri=cx-xi; r1=(zt-z0)/2; yh=27.7-2.0*i; zh=12.87
    E=[]
    E.append(Part.Arc(V(xi,ye,z0),V(xi,ye+r1,(z0+zt)/2),V(xi,ye,zt)).toShape())
    if ye>cy+1e-6: E.append(Part.LineSegment(V(xi,ye,zt),V(xi,cy,zt)).toShape())
    a=math.radians(45); E.append(Part.Arc(V(xi,cy,zt),V(cx-Ri*math.cos(a),cy-Ri*math.sin(a),zt),V(cx,cy-Ri,zt)).toShape())
    E.append(Part.LineSegment(V(cx,cy-Ri,zt),V(-8.88,yh,zh)).toShape())
    W=Part.Wire(E); c=Part.Wire(Part.makeCircle(od/2,V(xi,ye,z0),V(0,1,0)))
    ps=Part.BRepOffsetAPI.MakePipeShell(W); ps.setFrenetMode(True); ps.add(c); ps.build(); ps.makeSolid(); return ps.shape(),W.Length
LP=[lead(i,28.5,6.55,12.0) for i in range(5)]; LA=[lead(i,32.0,5.8,10.1) for i in range(5)]
N['Vol_Leads_Prod62']=Part.makeCompound([l[0] for l in LP]); N['Vol_Leads_ProtoAkyga']=Part.makeCompound([l[0] for l in LA])
print('lead lengths prod',[round(l[1],1) for l in LP],'proto',[round(l[1],1) for l in LA])
N['Vol_J3_FH12_22']=box(9.71,26.89,16.05,24.05,11.54,13.54)
N['Vol_DSI_FPC_b']=box(9.71,26.89,24.05,26.3,12.0,16.75).fuse(box(9.71,26.89,26.3,33.9,15.9,16.75)).fuse(box(9.71,26.89,33.9,35.0,15.9,17.5))
N['Vol_J4_FH12_22']=box(27.45,44.55,0.95,8.85,11.54,13.54)
N['Vol_CamFPC']=box(29.0,43.0,10.4,11.0,5.0,14.6).fuse(box(29.0,43.0,8.85,10.4,13.6,14.6))
N['Vol_J11_FH12_16']=box(11.9,26.09,26.36,34.34,11.54,13.54)
N['Vol_J12_FanHdr_DNP']=box(24.65,34.55,-33.1,-26.5,11.54,14.5)   # SM04B-SRSS-TB placeholder
N['Vol_Mic1_SPH0645']=box(-53.75,-50.25,34.35,35.33,13.07,15.72)
N['Vol_Mic2_SPH0645']=box(-6.75,-3.25,34.35,35.33,13.07,15.72)
N['Vol_MuteSlider']=box(0.5,10.7,31.9,35.33,12.2,15.2)
N['Vol_MuteLED']=box(-2.4,-0.8,33.6,35.33,13.0,14.5)
N['Vol_ALS_VEML7700']=box(-59.2,-56.85,16.6,23.4,16.97,19.97)
for nm,cx in (('Pwr',-45.0),('VolUp',-30.0),('VolDn',-18.0)): N['Vol_SW_'+nm]=box(cx-1.95,cx+1.95,33.42,35.07,12.05,14.95)
N['Vol_SW_Action']=box(55.52,57.17,18.05,21.95,zc-1.45,zc+1.45)
vols.update(N)
nm='PocketMate_v4_22c'
d=App.getDocument(nm) if nm in App.listDocuments() else App.newDocument(nm)
for o in list(d.Objects): d.removeObject(o.Name)
objs={}
for n,s in list(parts.items())+list(vols.items()):
    o=d.addObject('Part::Feature',n); o.Shape=s; objs[n]=o
d.recompute()
ok={frozenset(p) for p in [('Vol_J7_Housing205341','Vol_J7_Molex205338'),('Vol_Cell_Prod_62','Vol_Battery'),('Vol_Cell_Proto_Akyga','Vol_Battery'),('Vol_Cell_Prod_62','Vol_Cell_Proto_Akyga'),('Vol_Leads_ProtoAkyga','Vol_Cell_Prod_62'),('Vol_Leads_Prod62','Vol_Cell_Proto_Akyga'),('Vol_Leads_Prod62','Vol_Leads_ProtoAkyga'),('Vol_Leads_Prod62','Vol_Battery'),('Vol_Leads_ProtoAkyga','Vol_Battery'),('Vol_Leads_Prod62','Vol_J7_Housing205341'),('Vol_Leads_ProtoAkyga','Vol_J7_Housing205341'),('Vol_J6_CarrierTab','Vol_Carrier'),('Vol_CamFPC','Vol_Camera'),('Vol_CamFPC','Vol_Carrier')]}
allS=dict(parts); allS.update(vols)
for k in list(N)+['ActionCap_PC','SideKey_Flex','Al_Unibody','Bezel_DisplayFrame_PC']:
    for n,s in allS.items():
        if n==k or frozenset((n,k)) in ok: continue
        if k in ('Al_Unibody','Bezel_DisplayFrame_PC') and n not in N: continue
        try: iv=allS[k].common(s).Volume
        except Exception as e: iv=-1
        if iv>0.01: print('CLASH',k,n,round(iv,2))
for k in N:  # nearest neighbours
    b=N[k].BoundBox
print('uni valid',U.isValid(),round(U.Volume),'bez',B.isValid())
# J12 height limit: lowest solid above footprint
lim=min(z/20 for z in range(240,440) for (x,y) in [(26,-33),(30,-30),(33.5,-27)] if B.isInside(V(x,y,z/20),0.01,True) or U.isInside(V(x,y,z/20),0.01,True) or S['Vol_Display'].isInside(V(x,y,z/20),0.01,True))
print('J12 ceiling z',lim)
Import.export([o for o in d.Objects],OUT+'/pocketmate_assembly_v4_22c.step')
Import.export([objs['Al_Unibody']],OUT+'/pocketmate_al_unibody_v4_22c.step')
Import.export([objs['Bezel_DisplayFrame_PC'],objs['ActionCap_PC']],OUT+'/pocketmate_plastics_v4_22c.step')
Import.export([objs['SideKey_Flex']],OUT+'/pocketmate_sidekey_flex_v4_22c.step')
d.saveAs(OUT+'/pocketmate_enclosure_v4_22c.FCStd')
App.ParamGet('User parameter:BaseApp/Preferences/View').SetBool('UseNavigationAnimations',False)
gd=G.getDocument(nm); v=gd.mdiViewsOfType('Gui::View3DInventor')[0]
gd.getObject('Al_Unibody').ShapeColor=(0.72,0.74,0.78); gd.getObject('Bezel_DisplayFrame_PC').ShapeColor=(0.12,0.12,0.14)
gd.getObject('SideKey_Flex').ShapeColor=(0.85,0.55,0.1); gd.getObject('ActionCap_PC').ShapeColor=(0.2,0.4,0.9)
for n in vols: gd.getObject(n).Visibility=False
v.setCameraOrientation(App.Rotation(V(1,0,0),150).multiply(App.Rotation(V(0,1,0),20)),True); v.fitAll(); G.updateGui(); v.saveImage(OUT+'/pocketmate_enclosure_v4_22c_rear_iso.png',1600,1000,'White')
v.setCameraOrientation(App.Rotation(V(0,0,1),180).multiply(App.Rotation(V(1,0,0),-60)),True); v.fitAll(); G.updateGui(); v.saveImage(OUT+'/pocketmate_enclosure_v4_22c_top_edge.png',1600,1000,'White')
gd.getObject('Bezel_DisplayFrame_PC').Visibility=False
for n in N: gd.getObject(n).Visibility=True; gd.getObject(n).ShapeColor=(0.2,0.7,0.3)
for n in ('Vol_Camera','Vol_Battery','Vol_Carrier'): gd.getObject(n).Visibility=True; gd.getObject(n).Transparency=70
v.viewIsometric(); v.fitAll(); G.updateGui(); v.saveImage(OUT+'/pocketmate_enclosure_v4_22c_internal_iso.png',1600,1000,'White')
v.viewTop(); v.fitAll(); G.updateGui(); v.saveImage(OUT+'/pocketmate_enclosure_v4_22c_internal_top.png',1600,1000,'White')
for n in list(vols)+['Bezel_DisplayFrame_PC']: gd.getObject(n).Visibility=True
d.save()
