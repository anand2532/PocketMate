# Quectel EC25 / EC200U-CN shared LGA-144 footprint (top view, origin = module centre, KiCad Y down).
# Geometry: EC25 HD V2.2 Fig.45 (module bottom) + Fig.46 (recommended footprint); EC200U HD V1.0 Fig.39/40.
# All 144 pad centres coincide once both bodies are centred (EC25 32.0x29.0, EC200U 31.0x28.0).
# Pads 73-84 (centre 4x3 cluster) are EC25 RESERVED/keepout (HD 3.2 note 9) but EC200U audio/keypad pads.
import sys
FULL = '--ec200u-full' in sys.argv   # variant with pads 73-84 copper (EC200U only; NOT for EC25)
name = 'Quectel_EC25_EC200U_LGA-144_32x29mm' + ('_EC200U-full' if FULL else '')
pads = []   # (num, x, y, w, h, extra)
P = 1.3
# LCC pads: 0.8 wide; inner end flush with module pad heel (|x|=14.5 sides, |y|=13.0 top/bottom),
# toe to 17.15 / 15.65 = EC200U's 1.65 mm toe (EC25 needs 1.0, gets 1.15)
SX_IN, SX_OUT = 14.5, 17.15; SY_IN, SY_OUT = 13.0, 15.65
sx = (SX_IN + SX_OUT) / 2; sl = SX_OUT - SX_IN
sy = (SY_IN + SY_OUT) / 2
colY = [-12.6 + P * k for k in range(7)] + [-3.0 + P * k for k in range(13)]
left = list(range(1, 8)) + [141, 142] + list(range(8, 19))            # top -> bottom
right = list(range(54, 47, -1)) + [144, 143] + list(range(47, 36, -1))  # top -> bottom
rowX = [-12.15 + P * k for k in range(20)]
top = [114, 113] + list(range(72, 54, -1))      # left -> right
bot = [116, 115] + list(range(19, 37))          # left -> right
for n, y in zip(left, colY): pads.append((n, -sx, y, sl, 0.8, ''))
for n, y in zip(right, colY): pads.append((n, sx, y, sl, 0.8, ''))
for n, x in zip(top, rowX): pads.append((n, x, -sy, 0.8, sl, ''))
for n, x in zip(bot, rowX): pads.append((n, x, sy, 0.8, sl, ''))
assert len(pads) == 80
# inner signal LGA 1.1 x 1.1, 2.0 pitch: outer col x=-13.0 (129-140), inner col x=-11.0 (117-128), rows y=-11..+11
for k in range(12):
    pads.append((129 + k, -13.0, -11 + 2 * k, 1.1, 1.1, ''))
    pads.append((117 + k, -11.0, -11 + 2 * k, 1.1, 1.1, ''))
# GND LGA 2.0 x 3.0
GX = [-8.2, -5.0, -1.6, 1.6, 5.0, 8.2]; GY = [-9.6, -4.8, 0, 4.8, 9.6]
rows = [[108, 103, 99, 95, 90, 85], [109, 104, 100, 96, 91, 86], [110, 105, None, None, 92, 87],
        [111, 106, 101, 97, 93, 88], [112, 107, 102, 98, 94, 89]]
for r, y in zip(rows, GY):
    for n, x in zip(r, GX):
        if n: pads.append((n, x, y, 2.0, 3.0, 'chamfer' if n == 108 else ''))
# centre cluster 73-84 (EC200U-only function), 1.1 sq, 1.6 pitch
CL = [[82, 79, 76, 73], [83, 80, 77, 74], [84, 81, 78, 75]]
CX = [-2.4, -0.8, 0.8, 2.4]; CY = [-1.6, 0, 1.6]
cluster = [(n, x, y) for r, y in zip(CL, CY) for n, x in zip(r, CX)]
if FULL:
    for n, x, y in cluster: pads.append((n, x, y, 1.1, 1.1, ''))
nums = sorted(p[0] for p in pads)
assert nums == sorted(set(nums))
assert len(pads) == (144 if FULL else 132), len(pads)
L = []
A = L.append
A(f'(footprint "{name}"\n (version 20241229) (generator "kicad-lte_gen_fp") (generator_version "9.0") (layer "F.Cu")')
A(' (descr "Quectel EC25 series (32.0x29.0) and EC200U series (31.0x28.0) shared LGA-144 land pattern. 80 LCC + 64 LGA. '
  + ('Pads 73-84 PRESENT (EC200U-only variant: do not fit EC25). ' if not FULL and False else '')
  + ('Pads 73-84 present: EC200U-only, violates EC25 keepout. ' if FULL else 'Pads 73-84 omitted (EC25 keepout); they carry EC200U-only audio/keypad. ')
  + 'Refs: EC25 HD V2.2 7.1-7.2, EC200U HD V1.0 6.1-6.2")')
A(' (tags "Quectel EC25 EC200U EC21 EG25 LTE LGA-144")')
A(' (property "Reference" "U1" (at 0 -17.2 0) (layer "F.SilkS") (effects (font (size 1 1) (thickness 0.15))))')
A(f' (property "Value" "{name}" (at 0 17.2 0) (layer "F.Fab") (effects (font (size 1 1) (thickness 0.15))))')
A(' (attr smd)')
def rect(x1, y1, x2, y2, layer, w):
    A(f' (fp_rect (start {x1:g} {y1:g}) (end {x2:g} {y2:g}) (stroke (width {w}) (type solid)) (fill no) (layer "{layer}"))')
def line(x1, y1, x2, y2, layer, w, t='solid'):
    A(f' (fp_line (start {x1:g} {y1:g}) (end {x2:g} {y2:g}) (stroke (width {w}) (type {t})) (layer "{layer}"))')
def text(s, x, y, layer, sz=0.6):
    A(f' (fp_text user "{s}" (at {x:g} {y:g} 0) (layer "{layer}") (effects (font (size {sz} {sz}) (thickness {sz*0.15:.3f}))))')
# Fab: both bodies
rect(-16, -14.5, 16, 14.5, 'F.Fab', 0.1)
rect(-15.5, -14.0, 15.5, 14.0, 'F.Fab', 0.05)
line(-16, -13.5, -15, -14.5, 'F.Fab', 0.1)
text('EC25 32.0x29.0 (outer) / EC200U 31.0x28.0 (inner)', 0, -15.2, 'F.Fab', 0.5)
# Courtyard: pad toes +0.5
CX_, CY_ = SX_OUT + 0.5, SY_OUT + 0.5
rect(-CX_, -CY_, CX_, CY_, 'F.CrtYd', 0.05)
# Silk: corner L marks outside pads + pin-1 dot
s = 0.12; ox, oy = SX_OUT + 0.25, SY_OUT + 0.25
for gx in (-1, 1):
    for gy in (-1, 1):
        line(gx * ox, gy * oy, gx * (ox - 1.2), gy * oy, 'F.SilkS', s)
        line(gx * ox, gy * oy, gx * ox, gy * (oy - 1.2), 'F.SilkS', s)
A(f' (fp_circle (center {-ox+0.3:g} {-oy-0.6:g}) (end {-ox+0.55:g} {-oy-0.6:g}) (stroke (width 0.25) (type solid)) (fill yes) (layer "F.SilkS"))')
# EC200U-only cluster marking (User.Drawings + F.Fab), keepout rule area per EC25 Fig.46 (cluster +0.5 mm)
kx1, ky1, kx2, ky2 = -2.95 - 0.5, -2.15 - 0.5, 2.95 + 0.5, 2.15 + 0.5
for n, x, y in cluster:
    rect(x - 0.55, y - 0.55, x + 0.55, y + 0.55, 'Dwgs.User', 0.05)
    text(str(n), x, y, 'Dwgs.User', 0.4)
rect(kx1, ky1, kx2, ky2, 'Dwgs.User', 0.1)
text('EC200U-only 73-84 (LOUDSPK/MIC/KEYPAD, 76=GND, 81/82=RES)', 0, ky2 + 0.7, 'Dwgs.User', 0.45)
text('EC25: KEEPOUT - no pads/tracks/vias' if not FULL else 'EC200U-ONLY VARIANT: pads fitted', 0, ky1 - 0.6, 'Dwgs.User', 0.45)
text('Pin 3 / 35 / 37-40 / 43 / 117-144 functions differ EC25 vs EC200U - see kicad-lte/EC25_EC200U_pad_compat.md', 0, 16.3, 'Dwgs.User', 0.4)
if not FULL:
    A(f''' (zone (net 0) (net_name "") (layers "F.Cu" "In1.Cu") (hatch edge 0.5) (connect_pads (clearance 0)) (min_thickness 0.25) (filled_areas_thickness no)
  (keepout (tracks not_allowed) (vias not_allowed) (pads not_allowed) (copperpour not_allowed) (footprints allowed))
  (fill (thermal_gap 0.5) (thermal_bridge_width 0.5))
  (polygon (pts (xy {kx1:g} {ky1:g}) (xy {kx2:g} {ky1:g}) (xy {kx2:g} {ky2:g}) (xy {kx1:g} {ky2:g}))))''')
for n, x, y, w, h, ex in sorted(pads):
    if ex == 'chamfer':
        A(f' (pad "{n}" smd roundrect (at {x:g} {y:g}) (size {w:g} {h:g}) (layers "F.Cu" "F.Paste" "F.Mask") (roundrect_rratio 0) (chamfer_ratio 0.2) (chamfer top_left))')
    else:
        A(f' (pad "{n}" smd rect (at {x:g} {y:g}) (size {w:g} {h:g}) (layers "F.Cu" "F.Paste" "F.Mask"))')
A(')')
open(f'/workspace/pocketmate/hardware/kicad-lte/kicad-lte.pretty/{name}.kicad_mod', 'w').write('\n'.join(L) + '\n')
print(name, len(pads), 'courtyard', round(2 * CX_, 2), 'x', round(2 * CY_, 2))
