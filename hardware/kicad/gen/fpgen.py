import re, os, uuid
from sexp import parse, dump
OUT='/workspace/pocketmate/hardware/kicad/PocketMate.pretty'; os.makedirs(OUT,exist_ok=True)
U=lambda: str(uuid.uuid4())
def head(name,descr,ref_y=-3,val_y=3):
    return f'''(footprint "{name}" (version 20241229) (generator "pocketmate_fpgen") (generator_version "9.0") (layer "F.Cu")
 (descr "{descr}") (attr smd)
 (property "Reference" "REF**" (at 0 {ref_y} 0) (layer "F.SilkS") (uuid "{U()}") (effects (font (size 0.8 0.8) (thickness 0.12))))
 (property "Value" "{name}" (at 0 {val_y} 0) (layer "F.Fab") (uuid "{U()}") (effects (font (size 0.8 0.8) (thickness 0.12))))
'''
def rect(layer,x1,y1,x2,y2,w=0.1):
    return f' (fp_rect (start {x1:.3f} {y1:.3f}) (end {x2:.3f} {y2:.3f}) (stroke (width {w}) (type solid)) (fill no) (layer "{layer}") (uuid "{U()}"))\n'
def pad(n,x,y,w,h,shape='roundrect',layers='"F.Cu" "F.Paste" "F.Mask"',extra=''):
    rr=' (roundrect_rratio 0.25)' if shape=='roundrect' else ''
    return f' (pad "{n}" smd {shape} (at {x:.4f} {y:.4f}) (size {w:.3f} {h:.3f}) (layers {layers}){rr}{extra} (uuid "{U()}"))\n'
def write(name,body): open(f'{OUT}/{name}.kicad_mod','w').write(body+')\n')
# ---- CM5 B2B split from Raspberry Pi CM5IO rev2 KiCad footprint (RP-008099-DD-1) ----
src=open('/workspace/pocketmate/hardware/kicad/ref/cm5io/CM5IO.pretty/Raspberry-Pi-5-Compute-Module.kicad_mod').read()
fp=parse(src)[0]
pads=[x for x in fp if isinstance(x,list) and x[0]=='pad' and x[1].strip('"').isdigit()]
for nm,(lo,hi) in {'CM5_B2B_10164227_Pins1-100':(1,100),'CM5_B2B_10164227_Pins101-200':(101,200)}.items():
    sel=[p for p in pads if lo<=int(p[1].strip('"'))<=hi]
    def at(p): a=[z for z in p if isinstance(z,list) and z[0]=='at'][0]; return float(a[1]),float(a[2])
    def sz(p): a=[z for z in p if isinstance(z,list) and z[0]=='size'][0]; return float(a[1]),float(a[2])
    xs=[at(p)[0] for p in sel]; ys=[at(p)[1] for p in sel]
    cx=(min(xs)+max(xs))/2; cy=(min(ys)+max(ys))/2
    b=head(nm,f'Amphenol BerkStak 10164227-1001A1RLF carrier-side B2B, CM5 pins {lo}-{hi}. Pads copied 1:1 from Raspberry Pi CM5IO rev2 footprint Raspberry-Pi-5-Compute-Module (RP-008099-DD-1), re-origined at connector centre (offset in CM5IO footprint: {cx:.3f},{cy:.3f}).')
    for p in sel:
        x,y=at(p); w,h=sz(p); n=p[1].strip('"')
        ang=[z for z in p if isinstance(z,list) and z[0]=='at'][0]
        if len(ang)>3 and round(float(ang[3]))%180==90: w,h=h,w   # source pads are rotated 90/270: bake rotation into size
        b+=pad(n,x-cx,y-cy,w,h,shape='rect')
    hw=(max(xs)-min(xs))/2+1.0; hh=(max(ys)-min(ys))/2+0.9
    b+=rect('F.Fab',-1.4,-11.25,1.4,11.25)+rect('F.CrtYd',-1.65,-11.5,1.65,11.5,0.05)
    pin1=[at(p) for p in sel if int(p[1].strip('"'))==lo][0]
    b+=f' (fp_circle (center {pin1[0]-cx+(2.0 if pin1[0]-cx>0 else -2.0):.3f} {pin1[1]-cy:.3f}) (end {pin1[0]-cx+(2.15 if pin1[0]-cx>0 else -1.85):.3f} {pin1[1]-cy:.3f}) (stroke (width 0.3) (type solid)) (fill yes) (layer "F.SilkS") (uuid "{U()}"))\n'
    write(nm,b); print(nm,len(sel),'centre in CM5IO fp',round(cx,3),round(cy,3),'span',round(max(xs)-min(xs),3),round(max(ys)-min(ys),3))
# ---- TPS61088 RHL0020A, TI land pattern 4207830-3/H (SLVSCM8A p.29), top view ----
b=head('TI_RHL0020A_VQFN-20_3.5x4.5mm_TPS61088','TI RHL (R-PVQFN-N20) 4.5x3.5mm, example board layout 4207830-3/H from TPS61088 datasheet SLVSCM8A; EP=pin21 PGND incl. 4 end tabs',-3,3)
for i,n in enumerate(range(2,10)): b+=pad(n,-1.75+0.5*i,1.725,0.28,0.85)
for i,n in enumerate(range(12,20)): b+=pad(n,1.75-0.5*i,-1.725,0.28,0.85)
b+=pad(1,-2.275,0.75,0.75,0.23); b+=pad(20,-2.275,-0.75,0.75,0.23); b+=pad(10,2.275,0.75,0.75,0.23); b+=pad(11,2.275,-0.75,0.75,0.23)
b+=pad(21,0,0,3.05,2.05,'rect','"F.Cu" "F.Mask"')
for sx in(-1,1):
    for sy in(-1,1): b+=pad(21,sx*2.0,sy*0.275,1.3,0.2,'rect','"F.Cu" "F.Mask"')
for sx in(-1,1):
    for sy in(-1,1): b+=pad('',sx*0.81,sy*0.56,1.32,0.82,'rect','"F.Paste"')
b+=rect('F.Fab',-2.25,-1.75,2.25,1.75)+rect('F.CrtYd',-2.9,-2.4,2.9,2.4,0.05)
b+=f' (fp_circle (center -2.7 1.4) (end -2.55 1.4) (stroke (width 0.3) (type solid)) (fill yes) (layer "F.SilkS") (uuid "{U()}"))\n'
write('TI_RHL0020A_VQFN-20_3.5x4.5mm_TPS61088',b)
# ---- MAX17055 TDFN-10-EP 2.0x2.5mm P0.4mm (T102A2+1C), outline 21-100013 rev C, land pattern 90-100007 rev B ----
NM='Maxim_TDFN-10-1EP_2x2.5mm_P0.4mm_EP1.4x1.3mm_MAX17055'
b=head(NM,'MAX17055ETB+ TDFN-10-EP 2.0(X)x2.5(Y)mm P0.4mm, ADI/Maxim outline 21-100013C, land pattern 90-100007B: pads 0.20x0.65 at 0.40 pitch, rows at 2.45 c-c (inner edge 0.90 = lead inner edge D/2-L, toe 0.30), EP 1.40x1.30 (=CSP). Pin1 bottom-left (top view).',-2.0,2.0)
for i in range(5): b+=pad(i+1,-0.8+0.4*i,1.225,0.20,0.65,'rect')
for i in range(5): b+=pad(6+i,0.8-0.4*i,-1.225,0.20,0.65,'rect')
b+=pad(11,0,0,1.40,1.30,'rect','"F.Cu" "F.Mask"')
b+=pad('',0,0,1.10,1.00,'rect','"F.Paste"')
b+=rect('F.Fab',-1.0,-1.25,1.0,1.25)+rect('F.CrtYd',-1.3,-1.8,1.3,1.8,0.05)
b+=f' (fp_circle (center -1.15 1.75) (end -1.02 1.75) (stroke (width 0.25) (type solid)) (fill yes) (layer "F.SilkS") (uuid "{U()}"))\n'
write(NM,b)
# ---- VEML7700-TT, Vishay 84286 rev1.8 p.10 proposed pad layout (top view) ----
b=head('Vishay_VEML7700','Vishay VEML7700-TT 6.8x2.35x3.0mm, proposed pad layout top view: 4x 0.7x1.6mm, pitch 1.27mm (doc 84286 p.10, drawing 6.550-5300.02-4). Pin order VERIFIED vs 84286 p.1 pinning photo: 1 SCL, 2 VDD, 3 GND, 4 SDA, left to right seen from the pad (lead) edge (leads on +Y edge of body outline)',-2.2,2.2)
for i in range(4): b+=pad(i+1,-1.905+1.27*i,0,0.7,1.6,'rect')
b+=rect('F.Fab',-3.4,-1.175,3.4,1.175)+rect('F.CrtYd',-3.65,-1.45,3.65,1.45,0.05)
b+=f' (fp_circle (center -2.6 1.2) (end -2.45 1.2) (stroke (width 0.25) (type solid)) (fill yes) (layer "F.SilkS") (uuid "{U()}"))\n'
write('Vishay_VEML7700',b)
# ---- Flex-tail 16P 0.5mm gold fingers (placeholder, for FH12 0.3mm-thick FPC). Pin n mates J11 pin n ----
NM='FlexTail_16P_P0.50mm'
b=head(NM,'PLACEHOLDER flex tail: 16 exposed fingers 0.30x3.0mm at 0.5mm pitch, stiffener 0.3mm total thickness for Hirose FH12 (0.5mm). Pin 1 at -X.',-2.8,2.8)
for i in range(16): b+=pad(i+1,-3.75+0.5*i,0,0.30,3.0,'rect','"F.Cu" "F.Mask"')
b+=rect('F.Fab',-4.5,-1.5,4.5,1.5)+rect('F.CrtYd',-4.6,-1.75,4.6,1.75,0.05)
write(NM,b)
# ---- Molex Pico-Lock 2.00 205338-0005 (5 ckt, SMT R/A). Not in KiCad lib: interpolated 1:1 from stock 205338-0004/-0006
#      (same generator / Molex SD 2053380000-SD): signal pads 1.1x1.45 @2.00, row Y-3.36; MP 1.35x2.9 at X +-(N+3.79)... ----
NM='Molex_Pico-Lock_205338-0005_1x05-1MP_P2.00mm_Horizontal'
b=head(NM,'Molex Pico-Lock 2.00mm 205338-0005, 5 circuits, SMT right angle, mated height 2.60mm (Molex 2053380000-SD). Interpolated from KiCad stock 205338-0004/-0006.',-5.4,5.4)
for i in range(5): b+=pad(i+1,-4+2*i,-3.36,1.1,1.45)
b+=pad('MP',-6.895,2.635,1.35,2.9); b+=pad('MP',6.895,2.635,1.35,2.9)
b+=rect('F.Fab',-6.975,-3.435+0.0,6.975,4.165)+rect('F.CrtYd',-8.07,-4.59,8.07,4.67,0.05)
b+=f' (fp_circle (center -4 -4.6) (end -3.85 -4.6) (stroke (width 0.25) (type solid)) (fill yes) (layer "F.SilkS") (uuid "{U()}"))\n'
write(NM,b)
open('/workspace/pocketmate/hardware/kicad/fp-lib-table','w').write('(fp_lib_table (version 7)\n (lib (name "PocketMate")(type "KiCad")(uri "${KIPRJMOD}/PocketMate.pretty")(options "")(descr "PocketMate project footprints"))\n)\n')
