# Reserve LTE daughterboard flex connector J14 (FH12-22S-0.5SH(55)) at left edge, cable from -X; no nets yet (netlist pending).
import pcbnew as P
K='/workspace/pocketmate/hardware/kicad/PocketMate.kicad_pcb'; B=P.LoadBoard(K); M=P.FromMM
def V(x,y): return P.VECTOR2I(M(x),M(-y))
for f in list(B.GetFootprints()):
    if f.GetReference()=='J14': B.Delete(f)
for z in list(B.Zones()):
    if z.GetZoneName().startswith('KO_LTE'): B.Delete(z)
f=P.FootprintLoad('/usr/share/kicad/footprints/Connector_FFC-FPC.pretty','Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal')
f.SetFPID(P.LIB_ID('Connector_FFC-FPC','Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal'))
f.SetReference('J14'); f.SetValue('FH12-22S-0.5SH(55) LTE flex RESERVED')
B.Add(f); f.SetOrientationDegrees(270); f.SetPosition(V(4.0,-6.5))
f.BuildCourtyardCaches(); bb=f.GetCourtyard(P.F_CrtYd).BBox()
x0=P.ToMM(bb.GetLeft()); dx=-0.95-x0; f.SetPosition(V(4.0+dx,-6.5))
f.SetDNP(True); f.SetExcludedFromBOM(True); f.SetExcludedFromPosFiles(True); f.SetLocked(True)
f.BuildCourtyardCaches(); bb=f.GetCourtyard(P.F_CrtYd).BBox()
print('J14 at',round(P.ToMM(f.GetPosition().x),2),round(-P.ToMM(f.GetPosition().y),2),'courtyard X',round(P.ToMM(bb.GetLeft()),2),round(P.ToMM(bb.GetRight()),2),'Y',round(-P.ToMM(bb.GetBottom()),2),round(-P.ToMM(bb.GetTop()),2))
# pins: which side is cable?
p1=[p for p in f.Pads() if p.GetNumber()=='1'][0]; print('pad1',[round(v,2) for v in (P.ToMM(p1.GetPosition().x),-P.ToMM(p1.GetPosition().y))])
# support-parts reservation (2x SOT-23 NMOS, ~6 passives, 2x1.5 USB switch): F side, no footprints and no tracks/vias on F.Cu
def ra(name,x0,y0,x1,y1,layers,tracks=True,vias=True,fp=True,pour=False):
    z=P.ZONE(B); z.SetIsRuleArea(True); z.SetZoneName(name)
    ls=P.LSET();[ls.AddLayer(l) for l in layers]; z.SetLayerSet(ls)
    z.SetDoNotAllowTracks(tracks); z.SetDoNotAllowVias(vias); z.SetDoNotAllowFootprints(fp); z.SetDoNotAllowPads(False)
    getattr(z,'SetDoNotAllowZoneFills',getattr(z,'SetDoNotAllowCopperPour',None))(pour)
    o=z.Outline(); o.NewOutline(); [o.Append(M(x),M(-y)) for x,y in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]]; B.Add(z)
ra('KO_LTE_support_reserved_F',7.15,-10.8,10.7,-4.45,[P.F_Cu])
P.SaveBoard(K,B)
