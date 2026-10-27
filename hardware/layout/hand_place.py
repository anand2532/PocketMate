# Deterministic placement of all passives from the explicit table in passive_table.py (no search, no randomness).
import pcbnew as P, sys
sys.path.insert(0,'/workspace/pocketmate/hardware/layout'); from passive_table import TABLE
K='/workspace/pocketmate/hardware/kicad/PocketMate.kicad_pcb'; B=P.LoadBoard(K); M=P.FromMM
F={f.GetReference():f for f in B.GetFootprints()}
n=0
for r,x,y,rot,side in TABLE:
    f=F.get(r)
    if not f: print('missing',r); continue
    if f.IsFlipped()!=(side=='B'): f.Flip(f.GetPosition(),False)
    f.SetOrientationDegrees(rot); f.SetPosition(P.VECTOR2I(M(x),M(-y))); n+=1
P.SaveBoard(K,B); print('hand-placed',n)
