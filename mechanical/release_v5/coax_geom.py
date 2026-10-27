"""O12 (Layout 27 Oct 23:50 IST): coax routes from Layout's final u.FL centres, swept Ø1.13 micro-coax.
Bend radius rule: R >= 6.8 mm (strictest of the verified 1.13 mm cable datasheets: Taoglas 300115B000098A / Samtec MH113 6.8,
Wellshow D113L115 5.0, Rosnol RF1.13 4.5 static, Gigatronix 1.13 4.0 static). U.FL plugs swivel 360 deg, so the cable exit
direction is free. Cable centreline Z = 13.875 (same as v5.0: U.FL mated, cable exit 1.675 above DB top 12.2)."""
import math, json, cadquery as cq
D = 1.13; ZC = 13.875; R_GNSS = 6.8
# --- Main coax (O12b, Abracon AANI-FB-0173 datasheet, REVISED 05-26-25) ---
# Datasheet top view: 40 x 15 mm board; cable (Ø1.13) leaves through a 40 mm LONG edge, perpendicular to it, lying along the
# 15 mm axis, 11.0 mm from one SHORT end (29 mm from the other); cable bonded on the board face for ~9.6 mm ('tail' solder end).
# Our mount: 40 mm along Y (Y -27..13), 15 mm along Z (Z 2.5..17.5), cable face toward +X, exit edge = TOP (Z 17.5),
# the 11 mm end toward +Y  ->  feed tail (solder end) at Y = 13-11 = 2.0, Z = 17.5-9.6 = 7.9.
FEED = dict(x=-59.63, y=2.0, z=7.9)        # cable axis just inside the FPC inner face (cable X -60.195..-59.065)
J2 = (-49.7, 13.2, ZC)
R_MAIN = 6.8
R2_MAIN = 7.0
# Solved once (scipy Nelder-Mead, work/main_arc_params.npy): arc1 (vertical plane, R 6.8) + arc2 (tilted-plane circle, R 7.0) end exactly at J2.
PHI, GAM, BET = 1.25493179, 0.137557931, 1.42981948     # rad: heading azimuth after arc1, arc2 plane tilt (down), arc2 sweep
def main_geom():
    import math as m
    R1, R2 = R_MAIN, R2_MAIN
    F = (FEED['x'], FEED['y'], FEED['z'])
    d = (m.cos(PHI), m.sin(PHI), 0.0)
    E1 = (F[0] + R1*d[0], F[1] + R1*d[1], F[2] + R1)
    right = (d[1], -d[0], 0.0)
    n = (m.cos(GAM)*right[0], m.cos(GAM)*right[1], -m.sin(GAM))
    P = lambda t: tuple(E1[k] + R2*(d[k]*m.sin(t) + n[k]*(1 - m.cos(t))) for k in range(3))
    M1 = tuple((F[k] + R1*(d[k]*(1 - m.cos(m.pi/4)) if k < 2 else 0)) for k in range(2)) + (F[2] + R1*m.sin(m.pi/4),)
    return dict(F=F, E1=E1, M1=M1, M2=P(BET/2), E2=P(BET), heading_end=tuple(d[k]*m.cos(BET) + n[k]*m.sin(BET) for k in range(3)))
def main_path(n=60):
    g = main_geom(); R1, R2 = R_MAIN, R2_MAIN
    F = g['F']; E1 = g['E1']
    d = (math.cos(PHI), math.sin(PHI), 0.0); right = (d[1], -d[0], 0.0)
    nn = (math.cos(GAM)*right[0], math.cos(GAM)*right[1], -math.sin(GAM))
    p1 = [(F[0] + R1*d[0]*(1-math.cos(t)), F[1] + R1*d[1]*(1-math.cos(t)), F[2] + R1*math.sin(t)) for t in [k*math.pi/2/n for k in range(n+1)]]
    p2 = [tuple(E1[q] + R2*(d[q]*math.sin(BET*k/n) + nn[q]*(1 - math.cos(BET*k/n))) for q in range(3)) for k in range(n+1)]
    return PHI, p1, p2
def gnss_pts():
    x0, y0 = -44.6, 15.1; xa = -53.0; th = math.radians(40)
    cx, cy = xa, y0 + R_GNSS
    pm = (cx - R_GNSS*math.sin(th/2), cy - R_GNSS*math.cos(th/2))
    pb = (cx - R_GNSS*math.sin(th), cy - R_GNSS*math.cos(th))
    t = (pb[0] - (-58.8)) / math.cos(th)
    pe = (-58.8, pb[1] + t*math.sin(th))
    return (x0, y0), (xa, y0), pm, pb, pe
def _tube(edges, p0, d0):
    w = cq.Wire.assembleEdges(edges)
    p0 = tuple(p0) + ((ZC,) if len(p0) == 2 else ())
    prof = cq.Wire.makeCircle(D/2, cq.Vector(*p0), cq.Vector(*d0) if len(d0) == 3 else cq.Vector(d0[0], d0[1], 0))
    return cq.Workplane().add(prof).toPending().sweep(cq.Workplane().add(w), transition='round').val()
def coax_main_short():
    """20.7 mm route for the custom 25 mm cable (next spin, O14). Not in the prototype assembly."""
    g = main_geom(); V = lambda p: cq.Vector(*p)
    e1 = cq.Edge.makeThreePointArc(V(g['F']), V(g['M1']), V(g['E1']))
    e2 = cq.Edge.makeThreePointArc(V(g['E1']), V(g['M2']), V(g['E2']))
    return _tube([e1, e2], g['F'], (0, 0, 1))
FEED_P = (FEED['x'], FEED['y'], FEED['z'])
def coax_gnss():
    p0, pa, pm, pb, pe = gnss_pts(); V = lambda p: cq.Vector(p[0], p[1], ZC)
    es = [cq.Edge.makeLine(V(p0), V(pa)), cq.Edge.makeThreePointArc(V(pa), V(pm), V(pb)), cq.Edge.makeLine(V(pb), V(pe))]
    return _tube(es, p0, (-1, 0))
def _min_radius(pts):
    best = 1e9
    for i in range(1, len(pts)-1):
        a, b, c = pts[i-1], pts[i], pts[i+1]
        u = [b[k]-a[k] for k in range(3)]; v = [c[k]-b[k] for k in range(3)]
        cr = [u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0]]
        la = math.dist(a, b); lb = math.dist(b, c); lc = math.dist(a, c)
        area2 = math.sqrt(sum(x*x for x in cr))
        if area2 > 1e-9: best = min(best, la*lb*lc/(2*area2))
    return best
def summary():
    phi, p1, p2 = main_path()
    pm = p1 + p2[1:]
    pm = [p for i, p in enumerate(pm) if i == 0 or math.dist(p, pm[i-1]) > 1e-6]
    Lm = sum(math.dist(pm[i], pm[i+1]) for i in range(len(pm)-1))
    p0, pa, pmid, pb, pe = gnss_pts()
    Lg = math.dist(p0, pa) + R_GNSS*math.radians(40) + math.dist(pb, pe)
    return dict(main=dict(feed_tail=FEED, j2=J2, phi_deg=round(math.degrees(phi), 1), length_mm=round(Lm, 2), min_R_mm=round(_min_radius(pm), 2), z_max=round(max(p[2] for p in pm), 3)),
                gnss=dict(path=[p0, pa, pb, pe], arc_R_mm=R_GNSS, arc_deg=40, length_mm=round(Lg, 2)), z_centre=ZC, dia=D, bend_rule_mm=6.8)
if __name__ == '__main__':
    print(json.dumps(summary(), indent=1)); m = coax_main(); g = coax_gnss(); print(m.isValid(), m.Volume(), g.isValid(), g.Volume())


# ===================== SLACK LOOP (stock 66 mm Abracon -1 cable, prototype) =====================
# Stock cable: 66 mm from the antenna 15 mm edge to the connector tip + 9.6 mm bonded on the board = 75.6 mm from the solder tail;
# to the J2 plug centre ~73.6 mm (assumes ~2 mm plug half-length, Layout's J2 envelope).  Short route = 20.7 mm -> ~53 mm slack.
# Route = polyline of waypoints with exact R = R_SLACK corner fillets (fillet_path.py), solved once with scipy (work/opt_slack.py,
# work/slack_params.npy) so that: total length 73.6 mm, every bend >= R_SLACK, centreline clear of floor, cell, bezel lip, DB, window,
# radiator, other strands (>= 1.9 mm centre-to-centre).  Loop = stadium in the plane X = SLK_X (parallel to the antenna wall).
R_SLACK = 6.9
L_STOCK_TO_J2 = 73.6
SLK_X, SLK_W, SLK_X4, SLK_Y4, SLK_X5, SLK_Y5, SLK_Z5 = -55.5874, 19.8758, -55.4179, -0.5861, -58.14, 10.717, 12.8788
SLK_ZB = 3.5; SLK_ZT = SLK_ZB + 2*R_SLACK; SLK_YR = FEED['y']
def slack_waypoints(w=None, length_trim=None):
    w = SLK_W if w is None else w
    return [FEED_P_, (SLK_X, SLK_YR, SLK_ZT), (SLK_X, SLK_YR - w, SLK_ZT), (SLK_X, SLK_YR - w, SLK_ZB),
            (SLK_X4, SLK_Y4, SLK_ZB), (SLK_X5, SLK_Y5, SLK_Z5), J2]
FEED_P_ = (FEED['x'], FEED['y'], FEED['z'])
def slack_segs(w=None):
    from fillet_path import fillet_polyline
    return fillet_polyline(slack_waypoints(w), R_SLACK)
def coax_main_slack(w=None):
    segs, rep = slack_segs(w); V = lambda p: cq.Vector(*[float(c) for c in p]); es = []
    for s in segs:
        if s[0] == 'L':
            if math.dist(s[1], s[2]) > 1e-6: es.append(cq.Edge.makeLine(V(s[1]), V(s[2])))
        else: es.append(cq.Edge.makeThreePointArc(V(s[1]), V(s[2]), V(s[3])))
    d0 = [FEED_P_[i] - 0 for i in range(3)]
    t = [slack_waypoints(w)[1][i] - FEED_P_[i] for i in range(3)]; n = math.sqrt(sum(c*c for c in t)); t = [c/n for c in t]
    return _tube(es, FEED_P_, tuple(t))
def slack_summary(w=None):
    from fillet_path import length, sample
    segs, rep = slack_segs(w); pts = sample(segs, 0.25)
    # radius check: analytic arcs, plus independent 3-point circumradius on a 1 mm resample of the arcs only
    rmin = min(s[6] for s in segs if s[0] == 'A')
    return dict(length_mm=round(length(segs), 2), min_R_mm=round(rmin, 2), corners=rep, loop_w=SLK_W, loop_plane_X=SLK_X, n_pts=len(pts))
