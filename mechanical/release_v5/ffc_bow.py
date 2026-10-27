"""v5.1 O10: LTE FFC (22P 0.5 mm Type A) bow study between DB J1 and carrier J14.
Clamped-clamped planar elastica (inextensible, horizontal tangent at both actuator lips), solved by shooting.
Geometry from the read-only KiCad J14 model (Hirose FH12-22S-0.5SH): slot Z 11.725..12.05 (FFC centre 11.89),
FFC stop X 2.55, body face X 0.60, actuator lip X -0.40; J1 = mirror about the J1/J14 courtyard pair (x' = -5.95 - x), +0.75 Z (DB top 12.2 vs carrier top 11.45)."""
import numpy as np, json
from scipy.integrate import solve_ivp
from scipy.optimize import fsolve
ZC14, ZC1 = 11.89, 12.64
X_LIP14, X_LIP1 = -0.40, -5.55
TIP14, TIP1 = 2.55, -8.50
STIFF = 3.0                                  # stiffener (insertion end) length each end
from scipy.integrate import solve_bvp
def solve(s_len, cx, dz, prev=None):
    t = np.linspace(0, 1, 401)
    if prev is None:
        h = np.sqrt(max(s_len - cx, 1e-3) * 4 * cx) / np.pi
        x = cx * t; z = dz * t + h / 2 * (1 - np.cos(2 * np.pi * t))
        th = np.arctan2(np.gradient(z), np.gradient(x)); k = np.gradient(th) / np.gradient(t) / s_len
        y0 = np.vstack([th, k, x, z]); p0 = [-4 * np.pi**2 / s_len**2, 0.0]
    else:
        y0, p0 = prev
    def f(tt, y, p):
        a, b = p; th, k, x, z = y
        return s_len * np.vstack([k, a * np.sin(th) + b * np.cos(th), np.cos(th), np.sin(th)])
    def bc(ya, yb, p): return np.array([ya[0], ya[2], ya[3], yb[0], yb[2] - cx, yb[3] - dz])
    r = solve_bvp(f, bc, t, y0, p=p0, tol=1e-7, max_nodes=200000)
    return r
out = {}
cx = X_LIP14 - X_LIP1; dz = ZC14 - ZC1
prev = None; Ls = np.round(np.arange(11.30, 16.01, 0.05), 2)
for L in Ls:
    sl = L - (X_LIP1 - TIP1) - (TIP14 - X_LIP14)
    r = solve(sl, cx, dz, prev)
    if not r.success: print(L, 'fail', r.message); prev = None; continue
    tt = np.linspace(0, 1, 801); Y = r.sol(tt); prev = (r.sol(np.linspace(0,1,401)), r.p)
    x = X_LIP1 + Y[2]; z = ZC1 + Y[3]; R = 1 / np.max(np.abs(Y[1]))
    if round(L*100) % 50 == 0 or round(L*100) in (1420, 1480, 1530):
        out[float(L)] = dict(free_len=round(sl,3), z_top_centreline=round(z.max(),3), z_top_outer=round(z.max()+0.05,3),
                  bow_height_above_J1_slot=round(z.max()-ZC1,3), bow_height_above_J14_slot=round(z.max()-ZC14,3), x_min=round(x.min(),3), x_max=round(x.max(),3),
                  x_at_top=round(x[np.argmax(z)],3), z_min=round(z.min(),3), min_bend_radius=round(R,3), R_over_t=round(R/0.1,1),
                  pts=[[round(a,4), round(b,4)] for a, b in zip(x[::4], z[::4])])
        print(L, {k: v for k, v in out[float(L)].items() if k != 'pts'})
json.dump(out, open('work/ffc_bow.json', 'w'), indent=1)
