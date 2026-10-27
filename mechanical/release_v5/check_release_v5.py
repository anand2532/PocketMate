"""Full interference + clearance check for release v5 (all enclosure parts, volumes, and every carrier footprint)."""
import os, sys, json, itertools
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cadquery as cq
from OCP.BRepTools import BRepTools
from OCP.TopoDS import TopoDS_Shape
from OCP.BRep import BRep_Builder
from stepio import load_named
HERE = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(HERE, 'work')
idx = json.load(open(os.path.join(W, 'index.json')))
def rd(n):
    s = TopoDS_Shape(); BRepTools.Read_s(s, os.path.join(W, n + '.brep'), BRep_Builder()); return cq.Shape.cast(s)
P = {n: rd(n) for n in idx['names']}
# carrier components from the read-only KiCad export (Z: board bottom -> 9.94)
B = {}
for k, s in load_named(os.path.join(HERE, 'ref', 'carrier_kicad_export_126f5c6c.step')).items():
    sh = cq.Shape.cast(s).translate(cq.Vector(0, 0, 9.94))
    B['PCB:' + (k if not k.startswith('=>') else 'CarrierBoard')] = sh
fps = json.load(open(os.path.join(HERE, 'ref', 'carrier_footprints_126f5c6c.json')))
EST_H = {'JST_SH_SM02B': 2.95, 'TQFN-16': 0.8, 'TestPoint': 0.05}
est = []
for o in fps:
    if o['models'] and not any(m for m in o['models'] if any(t in m for t in ('JST', 'USB_C', 'TQFN'))): continue
    if o['ref'].startswith('H') or o['ref'] in ('J1', 'J2', 'J6', 'J7', 'J12', 'J10'): continue   # holes / modelled as Vol_*
    h = next((v for t, v in EST_H.items() if t in o['fp']), None)
    if h is None: continue
    x0, x1, y0, y1 = o['bb']
    B['PCB:' + o['ref'] + '(est)'] = cq.Solid.makeBox(x1-x0, y1-y0, h, cq.Vector(x0, -y1, 11.54)); est.append(o['ref'])
ALL = {k: v for k, v in P.items() if k != 'Vol_Carrier'}; ALL.update(B)   # real board solid replaces the box envelope
SAME = {'PCB:J14': 'Vol_J14_FH12_22_Courtyard', 'PCB:J3': 'Vol_J3_FH12_22', 'PCB:J4': 'Vol_J4_FH12_22', 'PCB:J11': 'Vol_J11_FH12_16'}
METAL = lambda n: not (n.endswith('_PC') or n.startswith('Vol_Ant') or n.startswith('Foam') or n.startswith('Liner')
                       or n.startswith('ThermalPad') or n.startswith('Clip_Slack') or n in ('GripInlay_L', 'GripInlay_R', 'Bezel_DisplayFrame_PC', 'ActionCap_PC', 'Vol_LTE_SIM_LidSwing'))
def classify(a, b):
    s = {a, b}
    if any(n.startswith('PCB:') for n in s) and ('Vol_Carrier' in s or 'PCB:CarrierBoard' in s): return 'same-board'
    for k, v in SAME.items():
        if s == {k, v}: return 'same-part'
    if 'PCB:CarrierBoard' in s and 'Vol_Carrier' in s: return 'same-part'
    var = lambda n: 'prod' if ('Prod' in n) else ('proto' if ('Proto' in n) else None)
    va, vb = var(a), var(b)
    if va and vb and va != vb: return 'other-variant'
    if s == {'Vol_Ant_GNSS_Envelope', 'Vol_Ant_GNSS_PatchOpt_Envelope'}: return 'other-variant(GNSS chip vs patch option)'
    if va and vb and va == vb and ('Cell' in a or 'Cell' in b) and ('Leads' in a or 'Leads' in b): return 'intended(lead on cell)'
    if 'Vol_Battery' in s: return 'pocket-envelope'
    if 'BattPad_NTCpocket' in s and any('Cell' in n or 'Vol_NTC_Batt' in n for n in s): return 'intended(pad)'
    if 'Vol_Coax_SlackZone' in s:   # O15: slack-zone envelope (keep-in for stock-cable loop + clips)
        o = (s - {'Vol_Coax_SlackZone'}).pop()
        if o == 'Coax_Main' or o.startswith('Clip_Slack'): return 'intended(slack zone contents)'
        if o == 'Vol_Ant_LTE_Main_Keepout': return 'intended(zone lies inside LTE keep-out; non-metal cable+clips only)'
    if any(n.startswith('Clip_Slack') for n in s) and 'Al_Unibody' in s: return 'intended(clip seated on unibody floor)'
    if any('Keepout' in n for n in s):
        o = (s - {n for n in s if 'Keepout' in n}).pop() if len(s) > 1 else a
        if any(t in o for t in ('Coax', 'Vol_Ant', 'Pigtail', 'UFL')) or not METAL(o): return 'keepout-ok(non-metal/own feed)'
        return 'KEEPOUT-VIOLATION'
    if any('Coax' in n for n in s) and any(('UFL' in n) or ('Vol_Ant' in n) for n in s): return 'intended(coax mate)'
    if s == {'LTE_Flex_22P', 'Vol_LTE_FFC_Bow_MaxTol_15p3'}: return 'other-variant(FFC nominal vs max-length bow)'
    if s & {'LTE_Flex_22P', 'Vol_LTE_FFC_Bow_MaxTol_15p3'} and any(('Conn' in n) or ('J14' in n) for n in s): return 'intended(FFC stiffener seated in FH12)'
    if 'Vol_LTE_U1_Courtyard' in s and (s & {'LTE_Daughterboard_PCB', 'Vol_LTE_EC25_Shield', 'ThermalPad_Shield_0p5'}): return 'same-part'
    if 'Vol_LTE_SIM_LidSwing' in s: return 'service(lid swing needs bezel+display off)'
    return 'CLASH'
names = list(ALL); bbs = {n: ALL[n].BoundingBox() for n in names}
def ov(a, b, g=0.0):
    A, Bb = bbs[a], bbs[b]
    return A.xmin < Bb.xmax + g and Bb.xmin < A.xmax + g and A.ymin < Bb.ymax + g and Bb.ymin < A.ymax + g and A.zmin < Bb.zmax + g and Bb.zmin < A.zmax + g
res = []
for a, b in itertools.combinations(names, 2):
    if a.startswith('PCB:') and b.startswith('PCB:'): continue
    if not ov(a, b): continue
    try: v = ALL[a].intersect(ALL[b]).Volume()
    except Exception: v = -1
    if v > 0.01 or v < 0:
        c = classify(a, b)
        try:
            cb = ALL[a].intersect(ALL[b]).BoundingBox(); ext = [round(t, 2) for t in (cb.xmin, cb.xmax, cb.ymin, cb.ymax, cb.zmin, cb.zmax)]
            if c == 'CLASH' and min(cb.xlen, cb.ylen, cb.zlen) < 0.02: c = 'contact(face)'
        except Exception: ext = None
        if c == 'CLASH' and {a, b} & {'Vol_CM5'} and any('B2B' in n for n in (a, b)): c = 'intended(B2B mated)'
        if c == 'CLASH' and {a, b} == {'Vol_J7_Molex205338', 'Vol_J7_Housing205341'}: c = 'intended(mated)'
        if c == 'CLASH' and 'Vol_UFL' in (a, b) and 'Vol_Pigtail' in (a, b): c = 'intended(coax mate)'
        if c == 'CLASH' and 'Vol_Antenna_FPC' in (a, b) and 'Vol_Pigtail' in (a, b): c = 'intended(coax mate)'
        res.append(dict(a=a, b=b, vol=round(v, 3), cls=c, bbox=ext))
# clearances for the release-v5 additions vs everything nearby (gap < 1.0 mm)
NEWS = idx['new'] + ['Al_Unibody', 'Bezel_DisplayFrame_PC']
gaps = []
for a in idx['new']:
    for b in names:
        if b == a or not ov(a, b, 1.0): continue
        d = ALL[a].distance(ALL[b]) if hasattr(ALL[a], 'distance') else None
        try:
            from OCP.BRepExtrema import BRepExtrema_DistShapeShape
            dd = BRepExtrema_DistShapeShape(ALL[a].wrapped, ALL[b].wrapped); dd.Perform(); d = dd.Value()
        except Exception: d = None
        if d is not None and d < 1.0:
            gaps.append(dict(a=a, b=b, gap=round(d, 3)))
json.dump(dict(clashes=res, gaps=gaps, est=est, n_parts=len(P), n_board=len(B)), open(os.path.join(HERE, 'work', 'check.json'), 'w'), indent=1)
print('parts', len(P), 'board solids', len(B), 'estimated', est)
for r in res:
    if r['cls'] in ('CLASH', 'KEEPOUT-VIOLATION'): print(r)
print('--- non-clash classes:', sorted(set(r['cls'] for r in res)))
