"""v5.1: fit check of Layout's 47 x 50 mm LTE board (hardware/kicad-lte/kicad-lte.kicad_pcb md5 34c2eb67..., read via /tmp copy)
against the release-v5.1 enclosure. Component bodies = footprint bbox x height table (estimated unless noted)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cadquery as cq
from OCP.BRepTools import BRepTools
from OCP.TopoDS import TopoDS_Shape
from OCP.BRep import BRep_Builder
from OCP.BRepExtrema import BRepExtrema_DistShapeShape as DSS
from stepio import load_named
HERE = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(HERE, 'work')
idx = json.load(open(os.path.join(W, 'index.json')))
def rd(n):
    s = TopoDS_Shape(); BRepTools.Read_s(s, os.path.join(W, n + '.brep'), BRep_Builder()); return cq.Shape.cast(s)
P = {n: rd(n) for n in idx['names']}
for k, v in load_named(os.path.join(HERE, 'ref', 'carrier_kicad_export_126f5c6c.step')).items():
    P['PCB:' + k] = cq.Shape.cast(v).translate(cq.Vector(0, 0, 9.94))
OURS_LTE = [n for n in P if n.startswith('Vol_LTE') or n in ('LTE_Daughterboard_PCB', 'ThermalPad_Shield_0p5', 'Foam_Prod_0p5', 'Foam_Proto_2p0')]
ENV = {n: s for n, s in P.items() if n not in OURS_LTE and n != 'Vol_Carrier'}
FP = json.load(open(os.path.join(HERE, 'ref', 'lte_stub_footprints_34c2eb67.json')))
Z0, Z1 = 11.4, 12.2
H = {'U1': 2.4, 'J5': 1.4, 'J1': 2.0, 'J2': 2.1, 'J3': 2.1, 'J4': 2.1, 'C4': 2.1, 'C5': 2.1, 'U4': 1.45, 'U6': 0.9, 'FL1': 1.0}
def h(r):
    if r in H: return H[r]
    if r.startswith('Q'): return 1.1
    if r.startswith('TP'): return 0.1
    return 0.9                                     # 0402/0603 passives, small ICs
def box(x0, x1, y0, y1, z0, z1): return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))
def rrect(x0, x1, y0, y1, r):
    return cq.Workplane('XY', origin=(0, 0, Z0)).center((x0+x1)/2, (y0+y1)/2).rect(x1-x0, y1-y0).extrude(Z1-Z0).edges('|Z').fillet(r).val()
def dist(a, b):
    d = DSS(a.wrapped, b.wrapped); d.Perform(); return d.Value()
def body(o):
    if o['ref'] == 'U1':                           # EC25 body 32 x 29 centred on pos (rot 0: 32 in X)
        x, y = o['pos']; return box(x-16, x+16, y-14.5, y+14.5, Z1, Z1+2.4)
    x0, x1, y0, y1 = o['pads'] if o['ref'].startswith(('TP',)) else o['bbox']
    return box(x0, x1, y0, y1, Z1, Z1 + h(o['ref']))
def run(tag, outline, dx=0.0, drop=()):
    B = {'LTE47:PCB': outline}
    for o in FP:
        if o['ref'] in drop: continue
        B['LTE47:' + o['ref']] = body(o).translate(cq.Vector(dx, 0, 0))
    res = []
    for a, sa in B.items():
        ba = sa.BoundingBox()
        for n, sb in ENV.items():
            bb = sb.BoundingBox()
            if ba.xmax < bb.xmin - 1 or bb.xmax < ba.xmin - 1 or ba.ymax < bb.ymin - 1 or bb.ymax < ba.ymin - 1 or ba.zmax < bb.zmin - 1 or bb.zmax < ba.zmin - 1: continue
            try:
                v = sa.intersect(sb).Volume()
            except Exception: v = 0
            if v > 0.01:
                ib = sa.intersect(sb).BoundingBox()
                res.append(dict(a=a, b=n, vol=round(v, 2), bbox=[round(t, 2) for t in (ib.xmin, ib.xmax, ib.ymin, ib.ymax, ib.zmin, ib.zmax)]))
            elif a == 'LTE47:PCB' or a.endswith(('U1', 'J5', 'J1')):
                g = dist(sa, sb)
                if g < 1.0: res.append(dict(a=a, b=n, gap=round(g, 2)))
    print(f'== {tag}')
    for r in sorted(res, key=lambda r: -r.get('vol', 0)): print('  ', r)
    return res
OUT = {}
# A: Layout board exactly as drawn (X -52..-5, Y -32..18, R2), parts as placed
OUT['A_as_drawn'] = run('A: Layout 47x50 as drawn', rrect(-52, -5, -32, 18, 2))
# strip test: only the extra 3 mm (X -8..-5) of bare PCB + any parts in it
strip = box(-8.0, -5.0, -32, 18, Z0, Z1)
OUT['strip_-8_-5'] = [dict(b=n, vol=round(strip.intersect(s).Volume(), 3)) for n, s in ENV.items() if strip.intersect(s).Volume() > 0.001]
print('== strip X-8..-5 bare PCB vs enclosure', OUT['strip_-8_-5'])
for n in ('Vol_J7_Housing205341', 'Vol_Speaker', 'Vol_Battery', 'Vol_Cell_Prod_62', 'Vol_Leads_Prod62', 'Vol_Leads_ProtoAkyga', 'LTE_Flex_22P',
          'Vol_J14_FH12_22_Courtyard', 'PCB:J14', 'Bezel_DisplayFrame_PC', 'Al_Unibody', 'SideKey_Flex', 'HeatSpreader_Cu_0p5'):
    if n in ENV: print('   gap strip ->', n, round(dist(strip, ENV[n]), 2))
json.dump(OUT, open(os.path.join(W, 'lte47_fit.json'), 'w'), indent=1)
