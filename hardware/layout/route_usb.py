# USB2 route: J6 (A6/B6 DP, A7/B7 DM) -> U2 USBLC6 (in-line, pins1/3 in, 6/4 out) -> vias -> B.Cu -> J2 pins 105 (DP) / 103 (DM). Mech coords.
import pcbnew as P
K='/workspace/pocketmate/hardware/kicad/PocketMate.kicad_pcb'; B=P.LoadBoard(K); M=P.FromMM
def V(x,y): return P.VECTOR2I(M(x),M(-y))
DP=B.FindNet('USB_DP'); DM=B.FindNet('USB_DM'); W={'F':0.135,'B':0.135,'I':0.128}
L={'F':P.F_Cu,'B':P.B_Cu,'I':P.In2_Cu}
def tr(net,pts,l):
    for a,b in zip(pts,pts[1:]):
        t=P.PCB_TRACK(B); t.SetStart(V(*a)); t.SetEnd(V(*b)); t.SetWidth(M(W[l])); t.SetLayer(L[l]); t.SetNet(net); B.Add(t)
def via(net,x,y):
    v=P.PCB_VIA(B); v.SetPosition(V(x,y)); v.SetDrill(M(0.2)); v.SetWidth(P.F_Cu,M(0.45)); v.SetNet(net); B.Add(v)
pad={(f.GetReference(),p.GetNumber()):(P.ToMM(p.GetPosition().x),-P.ToMM(p.GetPosition().y)) for f in B.GetFootprints() for p in f.Pads()}
A6,A7,B6,B7=[pad[('J6',n)] for n in('A6','A7','B6','B7')]; e=-27.08  # pad north tips
u1,u3,u6,u4=[pad[('U2',n)] for n in('1','3','6','4')]; j105,j103=pad[('J2','105')],pad[('J2','103')]
# connector side: B6/B7 tied to A6/A7 through L3
via(DM,B7[0],-26.35); tr(DM,[B7,(B7[0],-26.35)],'F'); via(DM,A7[0],-25.55)
tr(DM,[(B7[0],-26.35),(A7[0],-25.55)],'I')
via(DP,B6[0],-26.35); tr(DP,[B6,(B6[0],-26.35)],'F'); via(DP,A6[0],-24.8)
tr(DP,[(B6[0],-26.35),(B6[0],-24.8),(A6[0],-24.8)],'I')
tr(DP,[A6,(A6[0],u1[1]),u1],'F'); yb=u3[1]; h=1.6  # 2-bump meander on DM (length match to DP)
tr(DM,[A7,(A7[0],yb),(14.15,yb),(14.15,yb-h),(14.6,yb-h),(14.6,yb),(15.05,yb),(15.05,yb-h),(15.5,yb-h),(15.5,yb),u3],'F')
tr(DP,[u1,u6],'F'); tr(DM,[u3,u4],'F')  # in-line through ESD pads
# exit to J2 (B side)
tr(DP,[u6,(20.2,u6[1]),(20.2,-24.3)],'F'); via(DP,20.2,-24.3); tr(DP,[(20.2,-24.3),(j105[0],-25.11),j105],'B')
tr(DM,[u4,(19.4,u4[1]),(19.4,-23.6)],'F'); via(DM,19.4,-23.6); tr(DM,[(19.4,-23.6),(j103[0],-25.11),j103],'B')
ds=B.GetDesignSettings(); ds.m_ViasMinSize=M(0.4); ds.m_MinThroughDrill=M(0.2)
P.SaveBoard(K,B); print('routed', u1,u3,u6,u4)
