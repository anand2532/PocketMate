# Apply v4_22b outline: top edge Y 35 -> 34.5 (gen_board_v4_22b.py y1=34.5), J6 tab unchanged.
import pcbnew as P
K='/workspace/pocketmate/hardware/kicad/PocketMate.kicad_pcb'; B=P.LoadBoard(K); M=P.FromMM
def V(x,y): return P.VECTOR2I(M(x),M(-y))
for d in list(B.GetDrawings()):
    if d.GetLayer()!=P.Edge_Cuts: continue
    if d.GetShape()==P.SHAPE_T_ARC and abs(P.ToMM(d.GetStart().x)+1)<0.01 and P.ToMM(-d.GetStart().y)>30:
        d.SetArcGeometry(V(-1,31.5),V(2-3*0.7071068,31.5+3*0.7071068),V(2,34.5)); continue
    for g,sg in ((d.GetStart,d.SetStart),(d.GetEnd,d.SetEnd)):
        q=g(); x,y=P.ToMM(q.x),-P.ToMM(q.y)
        if abs(y-35)<0.01: sg(V(x,34.5))
        elif abs(x+1)<0.01 and abs(y-32)<0.01: sg(V(-1,31.5))
P.SaveBoard(K,B); print('outline v4_22b applied')
B=P.LoadBoard(K)
for z in B.Zones():
    if z.GetZoneName()=='KO_DSI_FPC_drop_noparts_F':
        o=z.Outline(); bb=o.BBox(); x0,x1=P.ToMM(bb.GetLeft()),P.ToMM(bb.GetRight())
        o.RemoveAllContours(); o.NewOutline()
        for x,y in [(x0,24.05),(x1,24.05),(x1,26.3),(x0,26.3)]: o.Append(M(x),M(-y))
        print('DSI drop KO now X',x0,x1,'Y 24.05..26.3')
P.SaveBoard(K,B)
