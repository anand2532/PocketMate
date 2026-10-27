"""LTE FFC solid (v5.1 O10) from the elastica centreline in work/ffc_bow.json.
22P 0.5 mm Type A FFC, width 11.5 (= (N+1) x 0.5), conductor-film 0.1 thick, 0.3 thick stiffened ends (Hirose FH12 mating t=0.3+-0.05), 3.0 long."""
import json, os, numpy as np
import cadquery as cq
HERE = os.path.dirname(os.path.abspath(__file__))
Y0, Y1 = -12.25, -0.75
T, TS, LS = 0.10, 0.30, 3.0
ZC14, ZC1, TIP14, TIP1 = 11.89, 12.64, 2.55, -8.50
def box(x0, x1, y0, y1, z0, z1): return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0, y0, z0))
def ffc_solid(L):
    d = json.load(open(os.path.join(HERE, 'work', 'ffc_bow.json')))
    key = min(d, key=lambda k: abs(float(k) - L)); assert abs(float(key) - L) < 1e-6, (L, list(d))
    p = np.array(d[key]['pts'])
    t = np.gradient(p, axis=0); t /= np.linalg.norm(t, axis=1)[:, None]
    n = np.c_[-t[:, 1], t[:, 0]]
    up = p + n * T / 2; lo = p - n * T / 2
    ring = list(up) + list(lo[::-1])
    w = cq.Wire.makePolygon([cq.Vector(x, Y0, z) for x, z in ring], close=True)
    band = cq.Solid.extrudeLinear(cq.Face.makeFromWires(w), cq.Vector(0, Y1 - Y0, 0))
    s1 = box(TIP1, TIP1 + LS, Y0, Y1, ZC1 - TS/2, ZC1 + TS/2)
    s14 = box(TIP14 - LS, TIP14, Y0, Y1, ZC14 - TS/2, ZC14 + TS/2)
    return band.fuse(s1).fuse(s14).clean()
