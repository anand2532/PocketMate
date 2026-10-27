# kicad-lte PCB stub: 4-layer, 0.8 mm finished, outline over the cell (mech frame Y up -> KiCad Y = -y).
import pcbnew as P
M = P.FromMM
B = P.CreateEmptyBoard() if hasattr(P, 'CreateEmptyBoard') else P.BOARD()
B.SetCopperLayerCount(4)
ds = B.GetDesignSettings()
ds.SetBoardThickness(M(0.8))
# Outline: 44 x 44 mm, mech X -52..-8, Y -30..14, 2 mm corner radius
X1, X2, Y1, Y2, r = -52.0, -8.0, -30.0, 14.0, 2.0
def V(x, y): return P.VECTOR2I(M(x), M(-y))
def seg(a, b):
    s = P.PCB_SHAPE(B); s.SetShape(P.SHAPE_T_SEGMENT); s.SetStart(V(*a)); s.SetEnd(V(*b)); s.SetLayer(P.Edge_Cuts); s.SetWidth(M(0.1)); B.Add(s)
def arc(c, a, m, b):
    s = P.PCB_SHAPE(B); s.SetShape(P.SHAPE_T_ARC); s.SetArcGeometry(V(*a), V(*m), V(*b)); s.SetLayer(P.Edge_Cuts); s.SetWidth(M(0.1)); B.Add(s)
seg((X1 + r, Y1), (X2 - r, Y1)); seg((X2, Y1 + r), (X2, Y2 - r)); seg((X2 - r, Y2), (X1 + r, Y2)); seg((X1, Y2 - r), (X1, Y1 + r))
k = r * (1 - 0.70710678)
arc(None, (X2 - r, Y1), (X2 - k, Y1 + k), (X2, Y1 + r)); arc(None, (X2, Y2 - r), (X2 - k, Y2 - k), (X2 - r, Y2))
arc(None, (X1 + r, Y2), (X1 + k, Y2 - k), (X1, Y2 - r)); arc(None, (X1, Y1 + r), (X1 + k, Y1 + k), (X1 + r, Y1))
# U1 module: centre at mech (-33.75, -12.0); J1 link connector at the carrier-facing (+X) edge
u = P.FootprintLoad('/workspace/pocketmate/hardware/kicad-lte/kicad-lte.pretty', 'Quectel_EC25_EC200U_LGA-144_32x29mm')
u.SetReference('U1'); u.SetValue('EC25-E / EC200U-CN'); u.SetPosition(V(-33.75, -12.0)); B.Add(u)
j = P.FootprintLoad('/usr/share/kicad/footprints/Connector_FFC-FPC.pretty', 'Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal')
j.SetReference('J1'); j.SetValue('FH12-22S-0.5SH(55) to carrier J14'); j.SetOrientationDegrees(90); j.SetPosition(V(-13.0, -10.0)); B.Add(j)
t = P.PCB_TEXT(B); t.SetText('kicad-lte stub: 4L 0.8 mm (JLC04081H-3313 class). U1 placeholder position; J1 mates carrier J14 1:1 via 22p 0.5 mm FFC (confirm Type A/B for pin sense)')
t.SetLayer(P.Cmts_User); t.SetPosition(V(-51, 16)); t.SetTextSize(P.VECTOR2I(M(0.8), M(0.8))); B.Add(t)
B.Save('/workspace/pocketmate/hardware/kicad-lte/kicad-lte.kicad_pcb')
STACK = """  (stackup
   (layer "F.SilkS" (type "Top Silk Screen"))
   (layer "F.Paste" (type "Top Solder Paste"))
   (layer "F.Mask" (type "Top Solder Mask") (thickness 0.01))
   (layer "F.Cu" (type "copper") (thickness 0.035))
   (layer "dielectric 1" (type "prepreg") (thickness 0.0994) (material "PP 3313") (epsilon_r 4.1) (loss_tangent 0.02))
   (layer "In1.Cu" (type "copper") (thickness 0.0152))
   (layer "dielectric 2" (type "core") (thickness 0.5008) (material "FR4") (epsilon_r 4.6) (loss_tangent 0.02))
   (layer "In2.Cu" (type "copper") (thickness 0.0152))
   (layer "dielectric 3" (type "prepreg") (thickness 0.0994) (material "PP 3313") (epsilon_r 4.1) (loss_tangent 0.02))
   (layer "B.Cu" (type "copper") (thickness 0.035))
   (layer "B.Mask" (type "Bottom Solder Mask") (thickness 0.01))
   (layer "B.Paste" (type "Bottom Solder Paste"))
   (layer "B.SilkS" (type "Bottom Silk Screen"))
   (copper_finish "ENIG")
   (dielectric_constraints no)
  )
"""
f='/workspace/pocketmate/hardware/kicad-lte/kicad-lte.kicad_pcb'; t=open(f).read()
i=t.index('(setup')+len('(setup'); t=t[:i]+'\n'+STACK+t[i:]
open(f,'w').write(t)
b2=P.LoadBoard(f); b2.Save(f)
print('saved', P.ToMM(b2.GetDesignSettings().GetBoardThickness()), b2.GetCopperLayerCount())
