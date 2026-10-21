# PocketMate enclosure v2 (125x75x20, Al heat-spreader back plate) - based on v0 layout - parametric builder (edit P, re-run in FreeCAD)
import FreeCAD as App, Part, os
from FreeCAD import Vector as V
OUT='/workspace/pocketmate/mechanical'; VER='v2'
P=dict(L=125.,W=75.,T=20.,wall=2.0,rc=8.,rf=3.,split=9.,
 disp=(106.1,67.8,5.2),            # 43H-800480-IPS CTP glass variant (glass footprint, total module depth)
 panel=(105.5,67.2,2.8), act=(95.04,53.856), dispGap=0.25,
 batt=(51.,64.,7.),               # pocket for Akyga LP655063 / THOR-655060 (50x63x6.5 +0.5 all round)
 cm5=(55.,40.,4.94),              # CM5 + Amphenol 10164227-1001A1RLF 1.5mm stack (mounted height)
 carrier=(55.,69.,1.6), pad=1.0,
 cam=(25.,24.,11.5),              # Pi Camera Module 3 (IMX708) board 25x24, depth VERIFY
 plate_t=1.5, ped=(30.,30.,0.5), grip_d=0.6, ntc=(4.,2.5), battpad=0.8,
 spk=(15.,11.,3.5), boss_r=3.0, screw_r=1.1, insert_r=1.6)
def rbox(l,w,t,rc,rf,z0=0):
    b=Part.makeBox(l,w,t,V(-l/2,-w/2,z0))
    b=b.makeFillet(rc,[e for e in b.Edges if abs(e.Vertexes[0].Point.z-e.Vertexes[1].Point.z)>1e-6])
    hz=[e for e in b.Edges if abs(e.BoundBox.ZLength)<1e-6 and (abs(e.BoundBox.ZMin-z0)<1e-6 or abs(e.BoundBox.ZMin-z0-t)<1e-6)]
    return b.makeFillet(rf,hz)
def box(c,s): return Part.makeBox(s[0],s[1],s[2],V(c[0]-s[0]/2,c[1]-s[1]/2,c[2]))
def cyl(r,h,p,d=V(0,0,1)): return Part.makeCylinder(r,h,p,d)
def rrect(l,w,t,rc,z0=0,c=(0,0)):
    b=Part.makeBox(l,w,t,V(c[0]-l/2,c[1]-w/2,z0)); return b.makeFillet(rc,[e for e in b.Edges if e.BoundBox.ZLength>t-1e-4])
def plate_parts():
    L,W,pt=P['L'],P['W'],P['plate_t']
    pl=rrect(L-6.4,W-6.4,pt,P['rc']-3.2)
    pl=pl.fuse(box((26.5,-10,pt),P['ped']))                                         # pedestal under CM5 pad
    for x,y in [(57,31),(-57,31),(57,-31),(-57,-31)]:
        pl=pl.cut(cyl(1.1,5,V(x,y,-1))).cut(Part.makeCone(2.2,1.1,1.1,V(x,y,-0.001)))   # M2 countersunk
    pl=pl.cut(cyl(5.0,5,V(40.5,23,-1)))                                              # camera window hole
    grips=[rrect(17,50,P['grip_d']+0.01,4,-0.01,(-48,0)), rrect(13,36,P['grip_d']+0.01,4,-0.01,(50.5,-8))]
    for g in grips: pl=pl.cut(g)
    pl=pl.cut(box((-55.3,-10,pt-0.4),(P['ntc'][1],P['ntc'][0],1)))                    # case NTC pocket (inner face)
    inl=[g.common(rrect(200,200,P['grip_d'],1,0)) for g in grips]
    inl=[rrect(16.6,49.6,P['grip_d'],3.8,0,(-48,0)), rrect(12.6,35.6,P['grip_d'],3.8,0,(50.5,-8))]
    win=cyl(4.9,pt,V(40.5,23,0))
    bp=Part.makeBox(51,64,P['battpad'],V(-54,-32,pt)).cut(box((-28.5,10,pt-0.5),(P['ntc'][1]+0.5,P['ntc'][0]+0.5,3)))
    return pl,inl,win,bp
def build():
    L,W,T,w=P['L'],P['W'],P['T'],P['wall']
    outer=rbox(L,W,T,P['rc'],P['rf']); inner=rbox(L-2*w,W-2*w,T-2*w,P['rc']-w,P['rf']-w*0.75,w)
    sh=outer.cut(inner); big=1000
    cuts=[]
    g=P['disp']; gp=P['dispGap']
    cuts.append(box((0,0,T-w-0.5),(g[0]+2*gp,g[1]+2*gp,w+1)))      # front-loaded display glass opening (glass flush)
    cuts.append(cyl(1.25,w+2,V(-58,20,T-w-1)))   # ambient light sensor window 2.5mm
    # top edge (y+): power, vol+, vol- (front shell), mic-mute slider ; 2 mic ports
    for x,lx in((-45,8),(-30,10),(-18,10)): cuts.append(box((x,W/2-1,P['split']+1.2),(lx,4,3.2)))
    cuts.append(box((8,W/2-1,P['split']+1.4),(12,4,2.8)))
    for x in(-52,22): cuts.append(cyl(0.6,5,V(x,W/2-3,13),V(0,1,0)))
    # right side: distinctive action button, 11mm round
    cuts.append(cyl(5.5,5,V(L/2-3,20,12.5),V(1,0,0)))
    # bottom edge: USB-C (receptacle on carrier top side) + speaker side-fire grille
    usb=Part.makeBox(9.4,5,3.6,V(-4.7+20,-W/2-1,9.45)); usb=usb.makeFillet(1.6,[e for e in usb.Edges if e.BoundBox.YLength>1]); cuts.append(usb)
    for i in range(6): cuts.append(Part.makeBox(1.0,5,2.4,V(-48+i*2.2,-W/2-1,10.6)))
    # back: camera window, passive-assist vent slots beside CM5 pad zone
    cuts.append(cyl(4.5,5,V(40.5,23,-1)))
    sh=sh.cut(Part.makeCompound(cuts))
    lo=Part.makeBox(big,big,P['split'],V(-big/2,-big/2,0)); hi=Part.makeBox(big,big,big,V(-big/2,-big/2,P['split']))
    back=sh.common(lo); front=sh.common(hi)
    g=P['disp']; z0=T-g[2]
    ring=rbox(L-2*w+0.2,W-2*w+0.2,1.0,P['rc']-w,0.01,z0-1.0) if False else Part.makeBox(109,W-2*w,1.0,V(-54.5,-(W-2*w)/2,z0-1.0))
    ring=ring.cut(box((0,0,z0-2),(g[0]-4,g[1]-3,4))).common(inner)
    front=front.fuse(ring)
    bp=[(57,31),(-57,31),(57,-31),(-57,-31)]
    for x,y in bp:
        back=back.fuse(cyl(P['boss_r'],P['split']-1,V(x,y,1))).cut(cyl(P['screw_r'],big,V(x,y,-1)))
        front=front.fuse(cyl(P['boss_r'],T-w-P['split']+0.5,V(x,y,P['split']))).cut(cyl(P['insert_r'],5,V(x,y,P['split']-0.1)))
    back=back.common(outer); front=front.common(outer)
    # Al plate pocket (flush), central opening, 1.5mm ledge ring holding plate (notched at camera)
    back=back.cut(rrect(L-6,W-6,P['plate_t']+0.01,P['rc']-3,-0.01)).cut(rrect(L-12,W-12,3.0,P["rc"]-6+0.5,-0.5))
    ledge=rrect(L-2*w,W-2*w,1.5,P['rc']-w,P['plate_t']).cut(rrect(L-12,W-12,3,2.5,1)).cut(box((40.5,23.5,0),(27,26,5))).common(inner.fuse(rrect(L-2*w,W-2*w,2,P['rc']-w,1)))
    back=back.fuse(ledge).common(outer).cut(box((-28.5,0,P['plate_t']-0.01),(51.6,64.6,8.5)))   # clear battery pocket
    # internal keep-out volumes
    g=P['disp']; c5=P['cm5']; cr=P['carrier']
    zc5=w+P['pad']; zcar=zc5+c5[2]
    vols={
     'Vol_Display':box((0,0,T-g[2]),g),
     'Vol_ThermalPad':box((26.5,-10,w),(30,30,P['pad'])),
     'Vol_CM5':box((26.5,-10,zc5),c5),            # inverted: SoC faces back cover via pad
     'Vol_Carrier':box((26.5,0.5,zcar),cr).cut(box((40.5,23.5,0),(27,26,30))),
     'Vol_Battery':box((-28.5,0,P['plate_t']+P['battpad']),P['batt']),
     'Vol_NTC_Batt':box((-28.5,10,P['plate_t']+P['battpad']-0.6),(P['ntc'][1],P['ntc'][0],0.6)),
     'Vol_NTC_Case':box((-55.3,-10,P['plate_t']-0.4),(P['ntc'][1],P['ntc'][0],0.8)),
     'Vol_BattConn_ZH':box((4.5,24,zcar+cr[2]),(7.5,4.5,3.5)),
     'Vol_ALS':box((-58,20,T-w-2.0),(4,4,2.0)),
     'Vol_BattLeads':box((-12,32.5,9.35),(30,3,0.6)),
     'Vol_Camera':box((40.5,23,w),P['cam']),
     'Vol_Speaker':box((-42.5,-29.5,10.),P['spk']),
     'Vol_ActionBtn':cyl(5,6,V(L/2-w-6,20,12.5),V(1,0,0)),
     'Vol_SideBtns':box((-31,W/2-w-2.5,P['split']+1.0),(32,5,3.6)),
     'Vol_USBC':box((20,-W/2+w+3.7,zcar+cr[2]+0.05),(9,7.4,3.3))}
    return front,back,vols
doc=App.getDocument('PocketMate_v2') if 'PocketMate_v2' in App.listDocuments() else App.newDocument('PocketMate_v2')
for o in list(doc.Objects): doc.removeObject(o.Name)
ss=doc.addObject('Spreadsheet::Sheet','Params')
for i,(k,v) in enumerate(P.items()): ss.set('A%d'%(i+1),k); ss.set('B%d'%(i+1),str(v))
f,b,vols=build()
F=doc.addObject('Part::Feature','FrontShell'); F.Shape=f
B=doc.addObject('Part::Feature','BackFrame'); B.Shape=b
pl,inl,win,bp=plate_parts()
AL=doc.addObject('Part::Feature','AlBackPlate'); AL.Shape=pl
GI=[]
for i,g in enumerate(inl):
    o=doc.addObject('Part::Feature','GripInlay_%s'%('L','R')[i]); o.Shape=g; GI.append(o)
CW=doc.addObject('Part::Feature','CameraWindow_PC'); CW.Shape=win
BP=doc.addObject('Part::Feature','BattPad_NTCpocket'); BP.Shape=bp
VO=[]
for k,s in vols.items():
    o=doc.addObject('Part::Feature',k); o.Shape=s; VO.append(o)
doc.recompute()
import FreeCADGui as G
gd=G.getDocument(doc.Name)
gd.getObject('FrontShell').ShapeColor=(0.2,0.22,0.25); gd.getObject('FrontShell').Transparency=55
gd.getObject('BackFrame').ShapeColor=(0.2,0.22,0.25); gd.getObject('BackFrame').Transparency=40
gd.getObject('AlBackPlate').ShapeColor=(0.75,0.77,0.8)
for o in GI: gd.getObject(o.Name).ShapeColor=(0.1,0.1,0.1)
gd.getObject('CameraWindow_PC').ShapeColor=(0.3,0.5,0.7); gd.getObject('CameraWindow_PC').Transparency=50
gd.getObject('BattPad_NTCpocket').ShapeColor=(0.95,0.95,0.6)
cols=[(0.1,0.4,0.9),(0.2,0.8,0.3),(0.1,0.5,0.1),(0.9,0.1,0.1),(0.9,0.9,0.1),(1.,0.,0.),(1.,0.,0.),(1.,0.5,0.),(1.,0.5,0.),(0.6,0.2,0.8),(1.0,0.4,0.6),(0.5,0.5,0.5),(0.3,0.9,0.9),(0.4,0.4,0.4)]
for o,c in zip(VO,cols): gd.getObject(o.Name).ShapeColor=c
import Import
parts=[F,B,AL]+GI+[CW,BP]
Import.export(parts+VO,OUT+'/pocketmate_assembly_%s.step'%VER)
Import.export([F],OUT+'/pocketmate_front_shell_%s.step'%VER); Import.export([B],OUT+'/pocketmate_back_frame_%s.step'%VER)
Import.export([AL],OUT+'/pocketmate_al_back_plate_%s.step'%VER); Import.export(GI+[CW,BP],OUT+'/pocketmate_inserts_%s.step'%VER)
doc.saveAs(OUT+'/pocketmate_enclosure_%s.FCStd'%VER)
for o in parts: print(o.Name,'valid',o.Shape.isValid(),'vol',round(o.Shape.Volume),o.Shape.BoundBox)
for k,s_ in vols.items(): print(k,s_.BoundBox)
solids={'F':f,'B':b,'AL':pl,'BP':bp}
for k,s_ in vols.items():
    for n,sh in solids.items():
        iv=s_.common(sh).Volume
        if iv>0.3: print('CLASH',k,n,round(iv,1))
for a_,b_ in [('F','B'),('F','AL'),('B','AL'),('AL','BP'),('B','BP')]:
    iv=solids[a_].common(solids[b_]).Volume
    if iv>0.3: print('PCLASH',a_,b_,round(iv,1))
