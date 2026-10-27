"""2D drawings for release v5: planar sections of the real B-rep -> PDF (matplotlib) + DXF (ezdxf) with critical dimensions."""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cadquery as cq, ezdxf
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from OCP.BRepTools import BRepTools
from OCP.TopoDS import TopoDS_Shape
from OCP.BRep import BRep_Builder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir
HERE = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(HERE, 'work'); D = os.path.join(HERE, 'drawings')
idx = json.load(open(os.path.join(W, 'index.json')))
def rd(n):
    s = TopoDS_Shape(); BRepTools.Read_s(s, os.path.join(W, n + '.brep'), BRep_Builder()); return cq.Shape.cast(s)
P = {n: rd(n) for n in idx['names']}
AX = {'Z': ((0, 0, 1), 0, 1), 'X': ((1, 0, 0), 1, 2), 'Y': ((0, 1, 0), 0, 2)}
def section(shape, axis, val):
    n, i, j = AX[axis]; o = [0, 0, 0]; o[' XYZ'.index(axis) - 1] = val
    sec = BRepAlgoAPI_Section(shape.wrapped, gp_Pln(gp_Pnt(*o), gp_Dir(*n))); sec.Build()
    out = []
    for e in cq.Shape.cast(sec.Shape()).Edges():
        L = e.Length(); k = max(2, int(L / 0.2) + 1)
        pts = [e.positionAt(t / (k - 1)) for t in range(k)]
        out.append([(p.toTuple()[i], p.toTuple()[j]) for p in pts])
    return out
class Sheet:
    def __init__(s, title, sub):
        s.t, s.sub, s.layers, s.dims, s.notes = title, sub, [], [], []
    def add(s, polys, layer, color): s.layers.append((polys, layer, color))
    def dim(s, p1, p2, off, txt=None, horiz=True):
        s.dims.append((p1, p2, off, txt, horiz))
    def note(s, t): s.notes.append(t)
    def render(s, pdf, fname):
        fig, ax = plt.subplots(figsize=(16.5, 11.7))
        for polys, layer, c in s.layers:
            for pl in polys:
                xs, ys = zip(*pl); ax.plot(xs, ys, '-', color=c, lw=0.7)
        doc = ezdxf.new('R2010', setup=True); msp = doc.modelspace()
        for polys, layer, c in s.layers:
            if layer not in doc.layers: doc.layers.add(layer)
            for pl in polys: msp.add_lwpolyline(pl, dxfattribs={'layer': layer})
        for p1, p2, off, txt, horiz in s.dims:
            if horiz:
                y = p1[1] + off; L = abs(p2[0] - p1[0]); t = txt or f'{L:.2f}'
                ax.annotate('', (p1[0], y), (p2[0], y), arrowprops=dict(arrowstyle='<->', lw=0.6, color='b'))
                ax.plot([p1[0], p1[0]], [p1[1], y], 'b:', lw=0.4); ax.plot([p2[0], p2[0]], [p2[1], y], 'b:', lw=0.4)
                ax.text((p1[0] + p2[0]) / 2, y + 0.3, t, color='b', fontsize=7, ha='center')
                d = msp.add_linear_dim(base=(p1[0], y), p1=p1, p2=p2, angle=0, override={'dimtxt': 1.0, 'dimasz': 0.8}, text=txt or '<>')
            else:
                x = p1[0] + off; L = abs(p2[1] - p1[1]); t = txt or f'{L:.2f}'
                ax.annotate('', (x, p1[1]), (x, p2[1]), arrowprops=dict(arrowstyle='<->', lw=0.6, color='b'))
                ax.plot([p1[0], x], [p1[1], p1[1]], 'b:', lw=0.4); ax.plot([p2[0], x], [p2[1], p2[1]], 'b:', lw=0.4)
                ax.text(x + 0.3, (p1[1] + p2[1]) / 2, t, color='b', fontsize=7, rotation=90, va='center')
                d = msp.add_linear_dim(base=(x, p1[1]), p1=p1, p2=p2, angle=90, override={'dimtxt': 1.0, 'dimasz': 0.8}, text=txt or '<>')
            d.render()
        ax.set_aspect('equal'); ax.grid(True, lw=0.2)
        ax.set_title(f'{s.t}\n{s.sub}', fontsize=10)
        ax.text(0.01, 0.01, '\n'.join(s.notes + ['PocketMate release v5.1 (27 Oct 2026) - units mm - origin body centre, +X right, +Y top edge, Z from outer back',
                                                  'General tol. ISO 2768-mK unless noted; critical dims per README']),
                transform=ax.transAxes, fontsize=7, va='bottom', family='monospace')
        pdf.savefig(fig); plt.close(fig)
        y = -60
        for t in s.notes: msp.add_text(t, height=1.2, dxfattribs={'insert': (-60, y)}); y -= 2
        doc.saveas(os.path.join(D, fname))
U, Bz = P['Al_Unibody'], P['Bezel_DisplayFrame_PC']
WIN = ['RFWindow_LTE_Main_L_PC', 'RFWindow_GNSS_TL_PC', 'RFWindow_PC']
sheets = []
s = Sheet('UNIBODY 6061-T6 - plan section Z=10.0 (cell/CM5 level) and Z=14.0 (LTE shelf level)', 'Al_Unibody_release_v5.step')
s.add(section(U, 'Z', 10.0), 'U_Z10', 'k'); s.add(section(U, 'Z', 14.0), 'U_Z14', '0.55')
for w in WIN: s.add(section(P[w], 'Z', 10.0) + section(P[w], 'Z', 14.0), 'WINDOWS', 'r')
s.dim((-62.5, -37.5), (62.5, -37.5), -6); s.dim((-62.5, -37.5), (-62.5, 37.5), -6, horiz=False)
s.dim((-34.4, -35.6), (-28.4, -35.6), -3.5, 'POST 6.0'); s.dim((-27.0, -35.6), (-22.5, -35.6), -2.0, 'LEDGE 4.5')
s.dim((-13.0, -35.6), (-10.0, -35.6), -2.0, 'LEDGE 3.0'); s.dim((-62.5, -28), (-62.5, 14), -3, 'LTE MAIN WIN 42.0', horiz=False)
s.dim((-62.5, 17), (-62.5, 27.5), -3, 'GNSS WIN 10.5', horiz=False)
s.note('POST X-34.4..-28.4 Y-35.6..-33.6 top Z14.90 +0/-0.05 (thermal; flat 0.05)')
s.note('LEDGES X-27.0..-22.5 & -13.0..-10.0, Y-35.6..-33.6, top Z11.40 +0/-0.05 (daughterboard seat)')
sheets.append((s, 'unibody_plan_sections_release_v5.dxf'))
for ax_, val, name, ttl in [('X', -61.5, 'left_end', 'LEFT END WALL - section X=-61.5 (looking +X) - LTE main + GNSS windows'),
                            ('Y', -36.5, 'bottom_wall', 'BOTTOM WALL - section Y=-36.5 - plain Al (v5.1: diversity window deleted)'),
                            ('Y', 36.5, 'top_wall', 'TOP WALL - section Y=36.5 (unchanged from v4_22e)'),
                            ('X', 61.5, 'right_end', 'RIGHT END WALL - section X=61.5 - Wi-Fi window (unchanged)')]:
    s = Sheet(ttl, 'Al_Unibody + RF windows'); s.add(section(U, ax_, val), 'UNIBODY', 'k')
    for w in WIN: s.add(section(P[w], ax_, val), 'WINDOWS', 'r')
    if name == 'left_end':
        s.dim((-28, 2), (14, 2), -3, '42.0 +0.1/0'); s.dim((-28, 2), (-28, 18), -3, '16.0 +0.1/0', horiz=False)
        s.dim((17, 2), (27.5, 2), -3, '10.5 +0.1/0'); s.dim((27.5, 2), (27.5, 15.5), 3, '13.5 +0.1/0', horiz=False)
        s.dim((14, 18), (17, 18), 2, 'WEB 3.0'); s.note('Windows: through-pocket in 2.1 wall, slot corners R0.5 max (EDM/0.8 end mill: plug corners to match)')
    if name == 'bottom_wall':
        s.note('v5.1: no diversity window - bottom wall is continuous 6061 between USB-C and speaker ports')
    sheets.append((s, f'unibody_{name}_release_v5.dxf'))
s = Sheet('BEZEL / DISPLAY FRAME (PC) - plan sections Z=13.0 (clamps, fingers) and Z=16.4 (lips)', 'Bezel_DisplayFrame_PC_release_v5.step')
s.add(section(Bz, 'Z', 13.0), 'BEZ_Z13', 'k'); s.add(section(Bz, 'Z', 16.4), 'BEZ_Z16', '0.55')
s.dim((-24.0, -34.6), (-22.5, -34.6), -2, 'CLAMP 1.5'); s.dim((-12.5, -34.6), (-10.5, -34.6), -2, 'CLAMP 2.0')
s.dim((-41, 32.45), (-38, 32.45), 2, 'FINGER 3.0'); s.dim((-32, 32.45), (-29, 32.45), 2, 'FINGER 3.0')
s.note('Clamp posts bottom Z12.25 (0.05 nominal gap to daughterboard 12.20: 0.2 thick foam tape on post tip gives preload)')
s.note('Fingers Y16.0..32.45, Z12.25..13.25, bear on daughterboard top edge Y16..17')
sheets.append((s, 'bezel_plan_release_v5.dxf'))
for w in WIN:
    b = P[w].BoundingBox(); s = Sheet(f'RF WINDOW {w} - SLA clear/tough resin (NO metal-filled resin)', f'stl/{w}_release_v5.stl')
    thin = min((b.xlen, 'X'), (b.ylen, 'Y'), (b.zlen, 'Z'))[1]; mid = {'X': (b.xmin + b.xmax) / 2, 'Y': (b.ymin + b.ymax) / 2, 'Z': (b.zmin + b.zmax) / 2}[thin]
    s.add(section(P[w], thin, mid), 'WINDOW', 'r')
    i, j = AX[thin][1], AX[thin][2]; lo = (b.xmin, b.ymin, b.zmin); hi = (b.xmax, b.ymax, b.zmax)
    s.dim((lo[i], lo[j]), (hi[i], lo[j]), -2); s.dim((lo[i], lo[j]), (lo[i], hi[j]), -2, horiz=False)
    s.note(f'Thickness ({thin}) {min(b.xlen, b.ylen, b.zlen):.2f}; print -0.05/side vs slot; bond with 2-part epoxy; 0.3x45 outer chamfer')
    sheets.append((s, f'window_{w}_release_v5.dxf'))
# flat patterns
for n, note in [('Foam_Prod_0p5', 'PE/PU closed-cell foam 0.5 (production cell) - die/laser cut'),
                ('Foam_Proto_2p0', 'PE/PU closed-cell foam 2.0 (Akyga proto cell)'),
                ('Liner_PET_Prod', 'PET/polyimide 0.1 insulating liner, adhesive one side, onto cell top'),
                ('Liner_PET_Proto', 'PET/polyimide 0.1 liner, Akyga cell; relief around leads'),
                ('ThermalPad_Shield_0p5', 'Gap pad 0.5, >=3 W/mK, 29.4 x 33.0'),
                ('ThermalPad_Post_0p3', 'Gap pad 0.3, >=3 W/mK, 6.0 x 1.9'),
                ('HeatSpreader_Cu_0p5', 'C1100 Cu 0.5, Ni plate; joggle 0.7 down at Y-22.7/-24.5; Kapton 0.05 on top face (display side)')]:
    sh = P[n]; b = sh.BoundingBox(); s = Sheet(f'FLAT PATTERN {n}', note)
    s.add(section(sh, 'Z', (b.zmin + b.zmax) / 2 if 'Heat' not in n else 16.1), 'OUTLINE', 'k')
    if 'Heat' in n: s.add(section(sh, 'Z', 15.45), 'TAB', '0.5'); s.note('Developed length tab+joggle+plate approx 46.0 (bend allowance 0.7 offset joggle); cut flat then form')
    s.dim((b.xmin, b.ymin), (b.xmax, b.ymin), -3); s.dim((b.xmin, b.ymin), (b.xmin, b.ymax), -3, horiz=False)
    sheets.append((s, f'flat_{n}_release_v5.dxf'))
# daughterboard outline for Layout
s = Sheet('LTE DAUGHTERBOARD OUTLINE (Edge.Cuts proposal for hardware/kicad-lte) - 0.8 mm 4L', 'mech coords; KiCad Y = -mech Y')
s.add(section(P['LTE_Daughterboard_PCB'], 'Z', 11.8), 'Edge.Cuts', 'g'); s.add(section(P['Vol_LTE_EC25_Shield'], 'Z', 13), 'U1_SHIELD', 'r')
s.add(section(P['Vol_LTE_NanoSIM_Hinged'], 'Z', 12.5), 'SIM', 'm'); s.add(section(P['Vol_LTE_DB_Conn_FH12_22'], 'Z', 13), 'J1', 'b')
for u in ('Vol_LTE_UFL_Main', 'Vol_LTE_UFL_GNSS'): s.add(section(P[u], 'Z', 13), 'UFL', 'c')
s.dim((-52, -32), (-5, -32), -5, '47.0'); s.dim((-52, -23.4), (-52, 17), -3, horiz=False); s.dim((-34.4, -23.4), (-34.4, -32), -2, 'NOTCH 8.6', horiz=False)
s.note('U1 EC25/EC200U ROTATED 90 deg, centre (-35.8,-5.5); J1 FH12-22 rot 90 mouth +X at X-5.0, contacts centred Y-6.5 (aligns with carrier J14)')
s.note('v5.1: 47 mm wide (X-52..-5) per Layout; keep speaker notch X<-34.4/Y<-23.4 and J7 notch X>-9.4/Y>15.5; NSIM-2-C at X-17.75..-5.35 Y-31.6..-17.6'); s.note('Ears X-27..-22.5 and -13..-10 to Y-35.0 sit on Al ledges; bezel clamp posts above. No screws (no room over the cell).')
sheets.append((s, 'lte_daughterboard_outline_release_v5.dxf'))
with PdfPages(os.path.join(HERE, 'drawings', 'pocketmate_drawings_release_v5.pdf')) as pdf:
    for s, f in sheets: s.render(pdf, f)
print(len(sheets), 'sheets')
