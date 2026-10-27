"""O10 check: FFC bow vs v5.1 geometry. Reads work/*.brep + read-only carrier export. Writes work/ffc_fit.json."""
import sys, os, json; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cadquery as cq, numpy as np
from OCP.BRepTools import BRepTools; from OCP.TopoDS import TopoDS_Shape; from OCP.BRep import BRep_Builder
from stepio import load_named
from ffc_geom import ffc_solid
HERE = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(HERE, 'work')
idx = json.load(open(os.path.join(W, 'index.json')))
def rd(n):
    s = TopoDS_Shape(); BRepTools.Read_s(s, os.path.join(W, n + '.brep'), BRep_Builder()); return cq.Shape.cast(s)
P = {n: rd(n) for n in idx['names'] if n not in ('LTE_Flex_22P', 'Vol_LTE_FFC_BowMax')}
B = load_named(os.path.join(HERE, 'ref', 'carrier_kicad_export_126f5c6c.step'))
J14 = cq.Shape.cast(B['J14']).translate(cq.Vector(0, 0, 9.94))
P['PCB:J14(real model)'] = J14
P['PCB:CarrierBoard'] = cq.Shape.cast([v for k, v in B.items() if k.startswith('=>')][0]).translate(cq.Vector(0, 0, 9.94))
# J1 real body = J14 model mirrored about x=-2.975 (courtyards -12.95..-5.0 vs -0.95..7.04) and raised 0.75 (DB top 12.2 vs carrier top 11.45)
P['J1(mirrored FH12 model)'] = J14.mirror('YZ', (-2.975, 0, 0)).translate(cq.Vector(0, 0, 0.75))
TARGETS = ['Vol_Display', 'Bezel_DisplayFrame_PC', 'Vol_LTE_EC25_Shield', 'HeatSpreader_Cu_0p5', 'Vol_Cell_Prod_62', 'Vol_Cell_Proto_Akyga',
           'Liner_PET_Prod', 'Foam_Prod_0p5', 'Foam_Proto_2p0', 'LTE_Daughterboard_PCB', 'PCB:CarrierBoard', 'PCB:J14(real model)',
           'J1(mirrored FH12 model)', 'Al_Unibody', 'Vol_Battery', 'Vol_LTE_NanoSIM_Hinged', 'Vol_DSI_FPC_b', 'Vol_J7_Housing205341', 'Vol_Leads_Prod62']
TARGETS = [t for t in TARGETS if t in P]
out = {}
for L in [14.0, 14.2, 14.5, 14.8, 15.0, 15.3]:
    F = ffc_solid(L); bb = F.BoundingBox(); r = {'bbox': [round(v, 3) for v in (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax)]}
    for t in TARGETS:
        try: ov = F.intersect(P[t]).Volume()
        except Exception: ov = float('nan')
        r[t] = dict(gap=round(F.distance(P[t]), 3), overlap=round(ov, 4))
    out[L] = r
    print(L, r['bbox'], {t: (v['gap'], v['overlap']) for t, v in r.items() if t != 'bbox'})
# free space along the route: everything intersecting the slab X -5.55..-0.40, Z 11.7..17 over all Y
slab = cq.Solid.makeBox(5.15, 80, 5.3, cq.Vector(-5.55, -40, 11.7))
free = {}
for n, s in P.items():
    b = s.BoundingBox()
    if b.xmax < -5.55 or b.xmin > -0.40 or b.zmax < 11.7 or b.zmin > 17: continue
    try:
        c = s.intersect(slab)
        if c.Volume() < 1e-6: continue
        cb = c.BoundingBox(); free[n] = [round(v, 2) for v in (cb.xmin, cb.xmax, cb.ymin, cb.ymax, cb.zmin, cb.zmax)]
    except Exception: pass
out['route_slab_occupants'] = free
for n, v in sorted(free.items(), key=lambda kv: kv[1][2]): print('slab', n, v)
json.dump(out, open(os.path.join(W, 'ffc_fit.json'), 'w'), indent=1)
