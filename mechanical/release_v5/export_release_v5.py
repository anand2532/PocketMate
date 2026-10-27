"""Release v5 exports: assembly STEP, per-part STEP, STL, 2D drawings (PDF + DXF)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cadquery as cq
from OCP.BRepTools import BRepTools
from OCP.TopoDS import TopoDS_Shape
from OCP.BRep import BRep_Builder
HERE = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(HERE, 'work')
idx = json.load(open(os.path.join(W, 'index.json')))
def rd(n):
    s = TopoDS_Shape(); BRepTools.Read_s(s, os.path.join(W, n + '.brep'), BRep_Builder()); return cq.Shape.cast(s)
P = {n: rd(n) for n in idx['names']}
for d in ('step_parts', 'stl', 'drawings'): os.makedirs(os.path.join(HERE, d), exist_ok=True)
PHYS = [n for n in P if not n.startswith('Vol_')]
COL = lambda n: (cq.Color(0.75, 0.76, 0.78) if n == 'Al_Unibody' else cq.Color(0.72, 0.45, 0.2) if 'Cu' in n else
                 cq.Color(0.1, 0.45, 0.15) if 'PCB' in n else cq.Color(0.85, 0.9, 1.0, 0.5) if n.endswith('_PC') else
                 cq.Color(0.9, 0.6, 0.6, 0.25) if n.startswith('Vol_') else cq.Color(0.3, 0.3, 0.3))
A = cq.Assembly(name='PocketMate_release_v5')
for n in P: A.add(cq.Workplane().add(P[n]), name=n, color=COL(n))
A.save(os.path.join(HERE, 'pocketmate_assembly_release_v5.step'), exportType='STEP')
E = cq.Assembly(name='PocketMate_release_v5_envelopes')
for n in P:
    if n.startswith('Vol_'): E.add(cq.Workplane().add(P[n]), name=n, color=COL(n))
E.save(os.path.join(HERE, 'step_parts', 'envelopes_and_keepouts_release_v5.step'), exportType='STEP')
for n in PHYS:
    cq.exporters.export(cq.Workplane().add(P[n]), os.path.join(HERE, 'step_parts', n + '_release_v5.step'))
STL = ['Al_Unibody', 'Bezel_DisplayFrame_PC', 'ActionCap_PC', 'RFWindow_PC', 'RFWindow_LTE_Main_L_PC', 'RFWindow_GNSS_TL_PC',
       'GripInlay_L', 'GripInlay_R', 'CameraWindow_PC', 'HeatSpreader_Cu_0p5', 'LTE_Daughterboard_PCB']
for n in STL:
    cq.exporters.export(cq.Workplane().add(P[n]), os.path.join(HERE, 'stl', n + '_release_v5.stl'), tolerance=0.01, angularTolerance=0.1)
print('exported', len(PHYS), 'part STEPs,', len(STL), 'STLs')
