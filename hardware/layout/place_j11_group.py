# Puts the side-key flex support parts (U13 ESD, D4, D5, pull-ups/filters/divider/33R) on the B side directly under/next to J11.
import pcbnew as P, re
K='/workspace/pocketmate/hardware/kicad/PocketMate.kicad_pcb'; B=P.LoadBoard(K); M=P.FromMM
def V(x,y): return P.VECTOR2I(M(x),M(-y))
F={f.GetReference():f for f in B.GetFootprints()}
PW=re.compile(r'GND|^\+|VSYS|VBAT|3V3|5V')
jn={p.GetNetname() for r in('J11','U13') for p in F[r].Pads() if p.GetNetname() and not PW.search(p.GetNetname())}
grp=sorted(r for r,f in F.items() if re.match(r'^[RC]\d',r) and r not in ('C53','C54','R45','R46') and any(p.GetNetname() in jn for p in f.Pads()))
def put(f,x,y,rot=0):
    if f.GetLayer()==P.F_Cu: f.Flip(f.GetPosition(),False)
    f.SetPosition(V(x,y)); f.SetOrientationDegrees(rot)
put(F['U13'],19,31.3); put(F['D5'],13.5,30.8,90)
if 'D4' in F: put(F['D4'],24.5,30.8,90)
if 'Q6' in F: put(F['Q6'],9.8,30.4,0)
xs=[12.6+1.8*i for i in range(8)]; ys=[27.9,25.7]
slots=[(x,y) for y in ys for x in xs]
for r,(x,y) in zip(grp,slots): put(F[r],x,y,90)
# U14 MIC_FEED load switch group, B side just below the J11 group (short MIC_FEED to J11 pin 3)
for r,x,y,rot in [('U14',19.8,22.3,0),('C53',16.4,22.1,0),('C54',23.2,22.1,0),('R45',23.2,23.7,0),('R46',16.4,23.7,0)]: put(F[r],x,y,rot)
F['J10'].SetFPID(P.LIB_ID('Connector_JST','JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal'))
for t in ('TP1','TP2'): F[t].SetExcludedFromBOM(False)
P.SaveBoard(K,B); print('B-side J11 group:',['U13','D4','D5']+grp)
