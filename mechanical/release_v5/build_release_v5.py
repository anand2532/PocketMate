"""PocketMate release v5 builder (CadQuery/OCP).
Source: ../pocketmate_assembly_v4_22e.step (named solids, read-only).
Board:  ../../hardware/kicad/PocketMate.kicad_pcb (read-only; exported to STEP from a /tmp copy by kicad-cli).
Frame:  origin body centre, +X right, +Y top edge, Z from outer back.  Y_ours = -Y_kicad.
Writes only inside release_v5/.
"""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cadquery as cq
from stepio import load_named
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '..', 'pocketmate_assembly_v4_22e.step')

def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))
def fuse(*s):
    r = s[0]
    for t in s[1:]: r = r.fuse(t)
    return r.clean()
def poly_prism(pts, z0, z1):
    w = cq.Workplane('XY', origin=(0, 0, z0)).polyline(pts).close().extrude(z1-z0)
    return w.val()

src = {k: cq.Shape.cast(v) for k, v in load_named(SRC).items()}
P = dict(src)                      # name -> shape (release set)
NEW = []                           # names added in v5

# ---------------- LTE daughterboard stack (option D, Layout study) ----------------
DB_Z0, DB_Z1 = 11.4, 12.2          # 0.8 mm 4-layer PCB
SH_TOP = 15.5                      # shield top (user spec)
# outline: X -52..-8.6, Y -32..17, speaker notch, J7-housing corner notch, two mounting ears
db_pts = [(-34.4, -32.0), (-27.0, -32.0), (-27.0, -35.0), (-22.5, -35.0), (-22.5, -32.0),
          (-13.0, -32.0), (-13.0, -35.0), (-10.0, -35.0), (-10.0, -32.0), (-5.0, -32.0),
          (-5.0, 15.5), (-9.4, 15.5), (-9.4, 17.0), (-52.0, 17.0), (-52.0, -23.4), (-34.4, -23.4)]
# v5.1: right edge -8.0 -> -5.0 = Layout's 47 mm width (hardware/kicad-lte md5 34c2eb67); Y top kept at 17 (Y18 leaves 0.1 to the production cell leads)
P['LTE_Daughterboard_PCB'] = poly_prism(db_pts, DB_Z0, DB_Z1)
P['Vol_LTE_EC25_Shield'] = box(-51.3, -20.3, -22.5, 11.5, DB_Z1, SH_TOP)      # 31x34 height keep-out; U1 EC25 (32x29x2.4) ROTATED 90 deg, centre (-35.8,-5.5)
P['Vol_LTE_U1_Courtyard'] = box(-51.95, -19.65, -23.15, 12.15, DB_Z1, DB_Z1 + 0.05)   # Quectel LGA-144 courtyard 35.3x32.3 rotated (PCB-level marker)
# O12 (Layout 27 Oct 23:50 IST): final u.FL positions, both rot 90; mated-plug envelopes
P['Vol_LTE_UFL_GNSS'] = box(-45.7, -43.5, 14.0, 16.2, DB_Z1, DB_Z1 + 2.1)     # J4 centre (-44.6,15.1)
P['Vol_LTE_UFL_Main'] = box(-50.8, -48.6, 12.1, 14.3, DB_Z1, DB_Z1 + 2.1)     # J2 centre (-49.7,13.2); body Y 11.9..14.5
# v5.1: diversity antenna dropped (PM) -> no DIV u.FL / coax / window / FPC
P['Vol_LTE_NanoSIM_Hinged'] = box(-17.75, -5.35, -31.6, -17.6, DB_Z1, DB_Z1 + 1.4)    # v5.1: CUI/Same Sky NSIM-2-C 12.4 x 14 x 1.4 (verified), 2.4 from U1 pad toes
P['Vol_LTE_SIM_LidSwing'] = box(-17.75, -5.35, -31.6, -29.0, DB_Z1 + 1.4, DB_Z1 + 1.4 + 12.0)  # lid opening sweep (display/bezel removed)
P['Vol_LTE_DB_Conn_FH12_22'] = box(-12.95, -5.0, -15.07, 2.08, DB_Z1, DB_Z1 + 2.0)   # v5.1: FH12-22S rot 90, mouth +X at the X-5 edge
P['Vol_J14_FH12_22_Courtyard'] = box(-0.95, 7.04, -15.095, 2.095, 11.54, 13.54)    # J14 as placed by Layout (reserve_j14.py), rot 270, cable from -X, contacts centred Y -6.5
# v5.1 O10 (Layout 27 Oct 22:15 IST): custom 22P 0.5 mm Type A FFC, J14 unmoved. Elastica bow (ffc_bow.py) -> ffc_geom.py.
from ffc_geom import ffc_solid
P['LTE_Flex_22P'] = ffc_solid(14.5)                     # nominal 14.5 tip-to-tip, 11.5 wide, 0.1 film, 3.0 x 0.3 stiffened ends seated in J1/J14
P['Vol_LTE_FFC_Bow_MaxTol_15p3'] = ffc_solid(15.3)     # worst-case long cable (15.0 +0.3) bow envelope
# ---------------- cell insulation ----------------
P['Liner_PET_Prod'] = box(-53.5, -3.0, -33.3, 28.3, 10.80, 10.90)
P['Foam_Prod_0p5'] = poly_prism([(-34.1, -31.7), (-5.3, -31.7), (-5.3, 15.2), (-9.7, 15.2), (-9.7, 16.7),
                                 (-51.7, 16.7), (-51.7, -23.1), (-34.1, -23.1)], 10.90, DB_Z0)
P['Liner_PET_Proto'] = box(-53.5, -3.0, -33.3, 31.8, 9.30, 9.40)
_lp = src['Vol_Leads_ProtoAkyga'].BoundingBox()
_lpcut = box(_lp.xmin - 0.5, _lp.xmax + 0.5, _lp.ymin - 0.5, _lp.ymax + 0.5, 0, 20)
P['Liner_PET_Proto'] = P['Liner_PET_Proto'].cut(_lpcut).clean()     # relief around the Akyga leads
P['Foam_Proto_2p0'] = poly_prism([(-34.1, -31.7), (-5.3, -31.7), (-5.3, 15.2), (-9.7, 15.2), (-9.7, 16.7),
                                  (-51.7, 16.7), (-51.7, -23.1), (-34.1, -23.1)], 9.40, DB_Z0)
# ---------------- thermal path: shield -> pad -> Cu spreader -> pad -> Al post ----------------
P['ThermalPad_Shield_0p5'] = box(-50.5, -21.1, -22.0, 11.0, SH_TOP, 15.9)
P['HeatSpreader_Cu_0p5'] = fuse(box(-50.9, -20.7, -22.3, 11.3, 15.9, 16.4),       # plate (X min held 0.15 off the left bezel lip)
                                box(-34.4, -28.4, -22.7, -22.3, 15.9, 16.4),     # bridge
                                box(-34.4, -28.4, -24.5, -22.7, 15.2, 16.4),     # joggle (0.2 off shield)
                                box(-34.4, -28.4, -35.5, -24.5, 15.2, 15.7))     # tab onto the Al post
P['ThermalPad_Post_0p3'] = box(-34.4, -28.4, -35.5, -33.6, 14.9, 15.2)
# ---------------- unibody: post, ledges, RF windows ----------------
U = src['Al_Unibody']
post = box(-34.4, -28.4, -35.6, -33.6, 1.0, 14.9)
ledge1 = box(-27.0, -22.5, -35.6, -33.6, 1.0, DB_Z0)
ledge2 = box(-13.0, -10.0, -35.6, -33.6, 1.0, DB_Z0)
U = fuse(U, post, ledge1, ledge2)
win = {
  'RFWindow_LTE_Main_L_PC': box(-62.7, -60.4, -28.0, 14.0, 2.0, 18.0),
  'RFWindow_GNSS_TL_PC':    box(-62.7, -60.4, 17.0, 27.5, 2.0, 15.5),
}
for n, c in win.items():
    P[n] = U.intersect(c).clean()
    U = U.cut(c).clean()
P['Al_Unibody'] = U
# Wi-Fi pigtail re-routed (v4_22e envelope rose through the CM5/carrier and dipped into the floor rib)
P['Vol_Pigtail'] = fuse(box(51.4, 58.2, 0.4, 1.6, 1.9, 3.1), box(57.0, 58.2, 0.4, 1.6, 1.9, 6.6), box(57.0, 59.6, 0.4, 1.6, 5.4, 6.6))
# antenna envelopes + keep-outs (no metal / copper)
P['Vol_Ant_LTE_Main_FPC_40x15'] = box(-60.4, -60.2, -27.0, 13.0, 2.5, 17.5)   # Abracon AANI-FB-0173 class 40x15x0.2
P['Vol_Ant_LTE_Main_Keepout'] = box(-60.2, -55.0, -28.0, 14.0, 2.2, 18.0)   # floor fillet ends at Z 2.1
P['Vol_Ant_GNSS_Envelope'] = box(-60.4, -58.8, 17.5, 27.0, 2.5, 15.0)           # v5.1 GNSS kept: chip antenna on <=9.5(Y) x 12.5(Z) carrier, 0.8 PCB + 0.8 chip (Johanson 1575AT43A0040001E class)
P['Vol_Ant_GNSS_PatchOpt_Envelope'] = box(-60.4, -55.6, 17.5, 27.0, 2.5, 12.0)  # option: 9x9x4 patch (Abracon APAKN0904-S1575-T class) on 9.5x9.5x0.8 carrier, kept below the side-key flex riser (Z12)
P['Vol_Ant_GNSS_Keepout'] = box(-58.8, -55.0, 17.0, 27.5, 2.0, 15.5)
# coax routes (Ø1.13 mini-coax, modelled as 1.3 mm square runs)
from coax_geom import coax_main_slack, coax_gnss   # O12: swept Ø1.13, R>=6.8 (see coax_geom.py); O15: stock 66 mm cable with slack loop
P['Coax_Main'] = coax_main_slack()
P['Coax_GNSS'] = coax_gnss()

# ---- O15 (PM 28 Oct): stock 66 mm Abracon cable on the prototype -> defined slack zone + printed floor clips ----
import math as _m
import coax_geom as _cg
from fillet_path import fillet_polyline as _fp
_segs, _rep = _cg.slack_segs()
def _frame_box(cx, cy, z0, z1, ang, a0, a1, l0, l1):
    """box in a local frame rotated by ang (rad, about Z) around (cx,cy): along-axis a in [a0,a1], lateral l in [l0,l1], Z z0..z1"""
    b = box(a0, a1, l0, l1, z0, z1)
    return b.rotate(cq.Vector(0, 0, 0), cq.Vector(0, 0, 1), _m.degrees(ang)).translate(cq.Vector(cx, cy, 0))
# bottom straight of the loop = 3rd straight run; find it from the waypoints (BL corner -> W4), straight part between the two fillets
_W = _cg.slack_waypoints(); _BL, _W4 = _W[3], _W[4]
_u = [(_W4[i]-_BL[i]) for i in range(3)]; _n = _m.sqrt(sum(c*c for c in _u)); _u = [c/_n for c in _u]
_t3 = _rep[2][2]; _t4 = _rep[3][2]
_s0, _s1 = _t3, _n - _t4                       # straight run along BL->W4 (distance from BL waypoint)
_sm = _s1 - 1.45                               # clip A at the +Y end of the straight (keeps clear of the NTC case Y -12..-8)
_cxA, _cyA = _BL[0] + _u[0]*_sm, _BL[1] + _u[1]*_sm; _angA = _m.atan2(_u[1], _u[0])   # strand heading azimuth
_ZB = _cg.SLK_ZB; _FLOOR = 1.5      # Al unibody floor top in the antenna slab is Z 1.5 (probed)
# Clip A: floor saddle (PA12 / printed resin, bonded with adhesive transfer film): base 1.2 thick (Z 1.5..2.7), two 0.5 prongs flanking the cable (0.1 gap each side)
_g = _cg.D/2 + 0.10
P['Clip_Slack_Saddle_A'] = fuse(_frame_box(_cxA, _cyA, _FLOOR, _FLOOR+1.20, _angA, -1.3, 1.3, -_g-0.5, _g+0.5),
                                _frame_box(_cxA, _cyA, _FLOOR, _ZB+0.45, _angA, -1.3, 1.3, -_g-0.5, -_g),
                                _frame_box(_cxA, _cyA, _FLOOR, _ZB+0.45, _angA, -1.3, 1.3, _g, _g+0.5))
# Clip B: retainer post outside the left arc of the loop (left-most cable point Y = SLK_YR - SLK_W - R - D/2), two flanking prongs at Z 8.9..12.0
_yl = _cg.SLK_YR - _cg.SLK_W - _cg.D/2                      # cable surface at the left-most point of the arc (Y)
_xc = _cg.SLK_X; _gp = _cg.D/2 + 0.10
_TOL = 1.5                                                   # loop can grow 1.5 mm in width (= +3 mm cable) before it butts the post
_py1, _py0 = _yl - _TOL - 0.30, _yl - _TOL - 0.30 - 1.20     # back plate Y range
_Zl = _ZB + _cg.R_SLACK                                    # left-most point of the arc is at this Z
P['Clip_Slack_Post_B'] = fuse(box(_xc-_gp-0.5, _xc+_gp+0.5, _py0, _py1, _FLOOR, _Zl+1.6),
                              box(_xc-_gp-0.5, _xc-_gp, _py1-0.01, _yl + _cg.D*0.55, _Zl-1.5, _Zl+1.6),
                              box(_xc+_gp, _xc+_gp+0.5, _py1-0.01, _yl + _cg.D*0.55, _Zl-1.5, _Zl+1.6))
# slack-zone envelope (keep-in for the stock-cable loop; loop width can change by +/-1.5 mm for cable length tolerance +/-3 mm)
_zy0, _zy1 = _py0 - 0.25, _cg.SLK_YR+0.9
P['Vol_Coax_SlackZone'] = fuse(box(_cg.SLK_X-1.25, _cg.SLK_X+1.2, _zy0, _zy1, 1.9, 15.5),      # lower part (Z 1.9 = NTC case top; clip bases Z 1.5..2.7 stand in the floor recess)
                               box(_cg.SLK_X-1.25, _cg.SLK_X+0.85, _zy0, _zy1, 15.4, 18.0))   # upper part stays 0.2 clear of the bezel lip X -54.5
# ---------------- bezel: clamp posts over ears + two finger clamps from the side-key rib ----------------
Bz = src['Bezel_DisplayFrame_PC']
Bz = fuse(Bz, box(-24.0, -22.5, -34.6, -32.6, 12.25, 15.85), box(-12.5, -10.5, -34.6, -32.6, 12.25, 15.85),
          box(-41.0, -38.0, 16.0, 32.45, 12.25, 13.25), box(-32.0, -29.0, 16.0, 32.45, 12.25, 13.25))
# v4_22e had blind holes only (unibody O2.2 open at top, bezel O3.2 open at bottom): no screw path. v5: front-entry M2 countersunk.
# v4_22e bezel = 2 bodies (frame Z19..22 and inner skirt Z11.5..19) with ~0.5 gap between skirt top and frame underside
# (shared area 3.9 mm^2).  v5 bridges them so the bezel prints/machines as ONE part.
sol = sorted(Bz.Solids(), key=lambda t: t.BoundingBox().zmin)
skirt, frame = sol[0], sol[1]
bridge = skirt.intersect(box(-70, 70, -40, 40, 18.2, 19.0)).translate(cq.Vector(0, 0, 0.8))   # Z19.0..19.8 over the skirt top ring
bridge = bridge.cut(src['Vol_Display']).cut(src['Al_Unibody'])
Bz = skirt.fuse(frame).fuse(bridge).clean()
print('bezel solids after bridge', len(Bz.Solids()))
for cx in (-57.5, 57.5):
    for cy in (-31.5, 31.5):
        Bz = Bz.cut(cq.Solid.makeCylinder(1.2, 3.2, cq.Vector(cx, cy, 18.9)))                       # O2.4 clearance
        Bz = Bz.cut(cq.Solid.makeCone(1.2, 2.05, 0.85, cq.Vector(cx, cy, 21.15)))                   # 90 deg csk O4.1 at Z22 (ISO 7046 M2, dk 3.8)
        Bz = Bz.cut(cq.Solid.makeCylinder(2.05, 0.2, cq.Vector(cx, cy, 22.0)))
        U = U.fuse(cq.Solid.makeCylinder(1.1, 17.9, cq.Vector(cx, cy, 1.1)))                         # refill v4 O2.2 blind hole
        U = U.cut(cq.Solid.makeCylinder(1.05, 7.0, cq.Vector(cx, cy, 12.0)))                         # O2.1 x 7 for M2 helical insert (STI)
Bz = Bz.clean(); U = U.clean()
# v5.1 (O1 fix): the v4_22b action-button hole (Y14.6..25.4, Z~8.0..19.0) was tangent to the top face (Z19) at Y20 -> zero-thickness
# lintel / non-manifold edge.  Close the hole top to a flat Z 18.45 => 0.55 mm Al lintel; cap through-portion top is Z 18.25 -> 0.20 clear.
U = U.fuse(box(60.5, 62.5, 14.5, 25.5, 18.45, 19.0), box(60.45, 60.5, 14.5, 25.5, 18.8, 19.0)).clean()
P['Al_Unibody'] = U
P['Bezel_DisplayFrame_PC'] = Bz
NEW = ['LTE_Daughterboard_PCB','Vol_LTE_EC25_Shield','Vol_LTE_U1_Courtyard','Vol_LTE_UFL_GNSS','Vol_LTE_UFL_Main',
       'Vol_LTE_NanoSIM_Hinged','Vol_LTE_SIM_LidSwing','Vol_LTE_DB_Conn_FH12_22','Vol_J14_FH12_22_Courtyard','LTE_Flex_22P','Vol_LTE_FFC_Bow_MaxTol_15p3',
       'Liner_PET_Prod','Foam_Prod_0p5','Liner_PET_Proto','Foam_Proto_2p0','ThermalPad_Shield_0p5','HeatSpreader_Cu_0p5',
       'ThermalPad_Post_0p3','RFWindow_LTE_Main_L_PC','RFWindow_GNSS_TL_PC',
       'Vol_Ant_LTE_Main_FPC_40x15','Vol_Ant_LTE_Main_Keepout','Vol_Ant_GNSS_Envelope','Vol_Ant_GNSS_Keepout',
       'Vol_Ant_GNSS_PatchOpt_Envelope','Coax_Main','Coax_GNSS','Vol_Pigtail','Vol_Coax_SlackZone','Clip_Slack_Saddle_A','Clip_Slack_Post_B']
if __name__ == '__main__':
    import pickle
    from OCP.BRepTools import BRepTools
    os.makedirs(os.path.join(HERE, 'work'), exist_ok=True)
    for k, s in P.items():
        BRepTools.Write_s(s.wrapped, os.path.join(HERE, 'work', k + '.brep'))
    json.dump({'names': list(P), 'new': NEW}, open(os.path.join(HERE, 'work', 'index.json'), 'w'), indent=1)
    for k in NEW + ['Al_Unibody', 'Bezel_DisplayFrame_PC']:
        b = P[k].BoundingBox(); print(k, round(P[k].Volume(), 1), [round(v, 2) for v in (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)])
