# Generates PocketMate.kicad_pcb outline/holes/keep-outs from mechanical v3 (keepouts_v3.md / gen_board_v3.py). KiCad Y = -mech Y.
import pcbnew as P
B=P.BOARD(); M=P.FromMM
def V(x,y): return P.VECTOR2I(M(x),M(-y))
B.SetCopperLayerCount(6)
ds=B.GetDesignSettings(); ds.SetBoardThickness(M(1.6))
names={P.F_Cu:'L1.F_Sig',P.In1_Cu:'L2.GND',P.In2_Cu:'L3.Sig',P.In3_Cu:'L4.GND',P.In4_Cu:'L5.PWR',P.B_Cu:'L6.B_Sig'}
for l,n in names.items(): B.SetLayerName(l,n)
def seg(a,b,l=P.Edge_Cuts,w=0.1):
    s=P.PCB_SHAPE(B); s.SetShape(P.SHAPE_T_SEGMENT); s.SetStart(V(*a)); s.SetEnd(V(*b)); s.SetLayer(l); s.SetWidth(M(w)); B.Add(s)
def arc(c,st,ang,l=P.Edge_Cuts):
    s=P.PCB_SHAPE(B); s.SetShape(P.SHAPE_T_ARC); s.SetCenter(V(*c)); s.SetStart(V(*st)); s.SetArcAngleAndEnd(P.EDA_ANGLE(-ang,P.DEGREES_T)); s.SetLayer(l); s.SetWidth(M(0.1)); B.Add(s)
r=3;x0,x1,y0,y1,nx,ny=-1,54,-34,35,27,10.5
seg((x0+r,y0),(x1-r,y0)); arc((x1-r,y0+r),(x1-r,y0),-90); seg((x1,y0+r),(x1,ny)); seg((x1,ny),(nx,ny)); seg((nx,ny),(nx,y1))
seg((nx,y1),(x0+r,y1)); arc((x0+r,y1-r),(x0+r,y1),-90); seg((x0,y1-r),(x0,y0+r)); arc((x0+r,y0+r),(x0,y0+r),-90)
# mounting holes M2.5 NPTH-style, no copper (CM5 holes are 2.0 mm from carrier edge)
for i,(x,y) in enumerate([(2.5,-26.5),(50.5,-26.5),(2.5,6.5),(50.5,6.5)]):
    f=P.FootprintLoad('/usr/share/kicad/footprints/MountingHole.pretty','MountingHole_2.7mm_M2.5'); f.SetReference('H%d'%(i+1)); f.SetPosition(V(x,y)); B.Add(f)
def zone(pts,name,layers,tracks=True,vias=True,pads=True,copper=True,fp=True):
    z=P.ZONE(B); z.SetIsRuleArea(True); z.SetZoneName(name)
    ls=P.LSET();[ls.AddLayer(l) for l in layers]; z.SetLayerSet(ls)
    z.SetDoNotAllowTracks(not tracks); z.SetDoNotAllowVias(not vias); z.SetDoNotAllowPads(not pads); getattr(z,"SetDoNotAllowZoneFills",None) and z.SetDoNotAllowZoneFills(not copper); getattr(z,"SetDoNotAllowCopperPour",None) and z.SetDoNotAllowCopperPour(not copper); z.SetDoNotAllowFootprints(not fp)
    o=z.Outline(); o.NewOutline(); [o.Append(M(x),M(-y)) for x,y in pts]; B.Add(z)
def rect(a,b,c,d): return [(a,b),(c,b),(c,d),(a,d)]
import math
def circ(x,y,R,n=24): return [(x+R*math.cos(2*math.pi*k/n),y+R*math.sin(2*math.pi*k/n)) for k in range(n)]
ALL=[P.F_Cu,P.In1_Cu,P.In2_Cu,P.In3_Cu,P.In4_Cu,P.B_Cu]
for i,(x,y) in enumerate([(2.5,-26.5),(50.5,-26.5),(2.5,6.5),(50.5,6.5)]):
    zone(circ(x,y,3.0),'KO_hole_H%d_R3'%(i+1),[P.F_Cu,P.B_Cu],tracks=False,vias=False,pads=True,copper=False,fp=True)
for bx,by in [(57.5,-31.5),(57.5,31.5)]: zone(circ(bx,by,3.2),'KO_boss_%g_%g_R3.2'%(bx,by),ALL,False,False,False,False,False)
zone(rect(47.5,-11.5,54,-0.5),'KO_CM5_antenna_edge_nocopper',ALL,False,False,False,False,False)
zone(rect(47.5,0.0,54,2.0),'KO_UFL_pigtail_path_Y1',[P.F_Cu,P.B_Cu],tracks=True,vias=True,pads=False,copper=True,fp=False)
zone(rect(9,24,21,27),'KO_DSI_FPC_drop_noparts_F',[P.F_Cu],tracks=True,vias=True,pads=False,copper=True,fp=False)
# bottom side inside CM5 footprint: B2B only -> no other footprints on B side
zone(rect(-1,-30,54,10),'KO_B_CM5_footprint_B2B_only',[P.B_Cu],fp=True)  # rule note: only J1/J2 allowed (check by DRC rule file)
zone(rect(7,-28,37,2),'KO_SoC_pad_zone_B_nofp_exceptJ1J2',[P.B_Cu],fp=False)
# drawings on User layers
def rdraw(a,b,c,d,l,t=None):
    for p,q in [((a,b),(c,b)),((c,b),(c,d)),((c,d),(a,d)),((a,d),(a,b))]: seg(p,q,l,0.1)
    if t:
        tx=P.PCB_TEXT(B); tx.SetText(t); tx.SetPosition(V(a+0.3,d-1)); tx.SetLayer(l); tx.SetTextSize(P.VECTOR2I(M(0.8),M(0.8))); tx.SetHorizJustify(P.GR_TEXT_H_ALIGN_LEFT); B.Add(tx)
rdraw(-1,-30,54,10,P.B_Fab,'CM5 55x40 inverted (B side)')
for (a,b,c,d,t) in [(17.75,-28.4,40.25,-25.6,'J2 pins101-200 B'),(17.75,5.6,40.25,8.4,'J1 pins1-100 B')]: rdraw(a,b,c,d,P.B_Fab,t)
for (a,b,c,d,t) in [(15.5,-34,24.5,-28.1,'USB-C J6'),(0.75,21.75,8.25,26.25,'J_BATT ZH3 side'),(10,20,20,24,'DSI J3'),(28,7,40,10,'CSI J4'),(44,-33,52,-30,'FLEX'),(28,11,53,35,'camera (off-board)')]: rdraw(a,b,c,d,P.F_Fab,t)
rdraw(54.4,-25,60,11,P.Cmts_User,'RF free volume: no copper/metal X54.4..60 (off-board)')
rdraw(9,24,21,27,P.F_Fab,'DSI FPC drop >=15mm free')
rdraw(7,-28,37,2,P.B_Fab,'SoC pad/pedestal (22,-13)')
rdraw(-0.5,-33.5,53.5,10.0,P.Cmts_User,'Top-side max 4.9mm; 4.0mm in display-ledge band (~2mm inside glass edge)')
u=P.FootprintLoad('/usr/share/kicad/footprints/Connector_USB.pretty','USB_C_Receptacle_HRO_TYPE-C-31-M-17'); u.SetReference('J6'); u.SetPosition(V(20,-32.1)); u.SetLocked(True); B.Add(u)
sh=P.FootprintLoad('/usr/share/kicad/footprints/Connector_JST.pretty','JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal'); sh.SetReference('J_NTC'); sh.SetPosition(V(2,-20)); B.Add(sh)
P.SaveBoard('/workspace/pocketmate/hardware/kicad/PocketMate.kicad_pcb',B); print('saved')
