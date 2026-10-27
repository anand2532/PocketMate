import uuid, os, re, json, copy
from sexp import *
OUT='/workspace/pocketmate/hardware/kicad'
PROJ='PocketMate'
U=lambda: str(uuid.uuid4())
F='(effects (font (size 1.27 1.27)))'
FH='(effects (font (size 1.27 1.27)) (hide yes))'
FL='(effects (font (size 1.27 1.27)) (justify left))'
# ---------------- custom symbols ----------------
CUSTOM={}  # name -> (sexp list, pins)
def mksym(name, left, right, ref='U', fp='', ds='', desc='', top=None, bot=None):
    top=top or []; bot=bot or []
    n=max(len(left),len(right),1); h=(n+1)*2.54/2
    h=round(h/2.54+0.5)*2.54
    w=max(10.16, 2.54*round((max([len(p[1]) for p in left+right]+[4])*1.27*2+5)/2.54/2+0.5))
    w=max(w, 2.54*(max(len(top),len(bot))+1))
    pins=[]
    def P(num,nm,typ,x,y,a): pins.append(f'(pin {typ} line (at {x:g} {y:g} {a}) (length 2.54) (name "{nm}" {F}) (number "{num}" {F}))')
    for i,(num,nm,typ) in enumerate(left): P(num,nm,typ,-w-2.54,h-2.54*(i+1),0)
    for i,(num,nm,typ) in enumerate(right): P(num,nm,typ,w+2.54,h-2.54*(i+1),180)
    for i,(num,nm,typ) in enumerate(top): P(num,nm,typ,-w+2.54*(i+1),h+2.54,270)
    for i,(num,nm,typ) in enumerate(bot): P(num,nm,typ,-w+2.54*(i+1),-h-2.54,90)
    s=f'''(symbol "{name}" (pin_names (offset 1.016)) (exclude_from_sim no) (in_bom yes) (on_board yes)
 (property "Reference" "{ref}" (at {-w:g} {h+1.27:g} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
 (property "Value" "{name}" (at {w:g} {h+1.27:g} 0) (effects (font (size 1.27 1.27)) (justify right bottom)))
 (property "Footprint" "{fp}" (at 0 0 0) {FH})
 (property "Datasheet" "{ds}" (at 0 0 0) {FH})
 (property "Description" "{desc}" (at 0 0 0) {FH})
 (symbol "{name}_0_1" (rectangle (start {-w:g} {h:g}) (end {w:g} {-h:g}) (stroke (width 0.254) (type default)) (fill (type background))))
 (symbol "{name}_1_1" {' '.join(pins)}))'''
    CUSTOM[name]=s
pas,pin,pout,bid,inp,oc,nc='passive','power_in','power_out','bidirectional','input','open_collector','no_connect'
# CM5 connectors from RP-008180-DS-7 section 4.2
cm5=dict(l.split()[:2] for l in open(OUT+'/ref/cm5_pins.txt') if re.match(r'^\d+ \S',l) and not l.startswith('101 to'))
PO={'84','88'}
def cmtyp(nm):
    return pas
for a,(lo,hi) in {'CM5_B2B_A':(1,100),'CM5_B2B_B':(101,200)}.items():
    L=[(str(i),cm5[str(i)].replace('CM5_3.3V','CM5_3V3').replace('CM5_1.8V','CM5_1V8'),(pout if str(i) in PO else cmtyp(cm5[str(i)]))) for i in range(lo,hi+1,2)]
    R=[(str(i),cm5[str(i)].replace('CM5_3.3V','CM5_3V3').replace('CM5_1.8V','CM5_1V8'),(pout if str(i) in PO else cmtyp(cm5[str(i)]))) for i in range(lo+1,hi+1,2)]
    mksym(a,L,R,'J','','https://pip-assets.raspberrypi.com/categories/944-raspberry-pi-compute-module-5/documents/RP-008180-DS-7-cm5-datasheet.pdf','CM5 B2B connector pins %d-%d (Amphenol 10164227-1001A1RLF), pin names per CM5 datasheet 4.2'%(lo,hi))
mksym('MAX17055ETB',[('10','BATT',pin),('9','THRM',pas),('2','AIN',inp),('7','REG',pout)],[('4','SDA',bid),('3','SCL',inp),('8','ALRT',oc),('5','CSN',inp),('1','NC',nc)],'U','' ,'https://www.analog.com/media/en/technical-documentation/data-sheets/max17055.pdf','MAX17055 ModelGauge m5 fuel gauge TDFN-10',bot=[('6','CSP',pin),('11','EP',pas)])
mksym('TPS61088RHL',[('9','VIN',pin),('2','EN',inp),('13','MODE',inp),('10','SS',pas),('3','FSW',pas),('19','ILIM',pas),('1','VCC',pout)],[('4','SW',pas),('5','SW',pas),('6','SW',pas),('7','SW',pas),('8','BOOT',pas),('14','VOUT',pout),('15','VOUT',pas),('16','VOUT',pas),('17','FB',inp),('18','COMP',pas)],'U','','https://www.ti.com/lit/ds/symlink/tps61088.pdf','TPS61088 10A sync boost, VQFN-20 RHL',bot=[('20','AGND',pin),('21','PGND',pas),('11','NC',pas),('12','NC',pas)])
mksym('VEML7700',[('2','VDD',pin),('3','GND',pin)],[('4','SDA',bid),('1','SCL',inp)],'U','','https://www.vishay.com/docs/84286/veml7700.pdf','Vishay VEML7700 ambient light sensor, I2C addr 0x10')
mksym('TPS7A0233PDBV',[('1','IN',pin),('3','EN',inp)],[('5','OUT',pout),('2','GND',pin),('4','NC',nc)],'U','Package_TO_SOT_SMD:SOT-23-5','https://www.ti.com/lit/ds/symlink/tps7a02.pdf','TPS7A02 3.3V 25nA Iq LDO, SOT-23-5 DBV (SBVS277 Table 5-1: 1 IN, 2 GND, 3 EN, 4 NC, 5 OUT)')
mksym('TLV62585DRL',[('3','VIN',pin),('4','EN',inp)],[('2','SW',pout),('5','FB',inp),('6','NC',nc)],'U','Package_TO_SOT_SMD:SOT-563','https://www.ti.com/lit/ds/symlink/tlv62585.pdf','TLV62585 3A 1.5MHz sync buck, SOT-563 (DRL). Pinout per SLVSDE5F sec.5',bot=[('1','GND',pin)])
os.makedirs(OUT,exist_ok=True)
open(OUT+'/PocketMate.kicad_sym','w').write('(kicad_symbol_lib (version 20241209) (generator "pocketmate_gen") (generator_version "9.0")\n'+'\n'.join(CUSTOM.values())+'\n)\n')
open(OUT+'/sym-lib-table','w').write('(sym_lib_table (version 7)\n (lib (name "PocketMate")(type "KiCad")(uri "${KIPRJMOD}/PocketMate.kicad_sym")(options "")(descr "PocketMate custom symbols (datasheet-derived)"))\n)\n')
def custom_pins(name):
    e=parse(CUSTOM[name])[0]; r=[]
    for x in e:
        if isinstance(x,list) and x[0]=='symbol':
            for y in x[2:]:
                if isinstance(y,list) and y[0]=='pin':
                    at=y[3]; r.append(dict(num=y[6][1].strip('"'),name=y[5][1].strip('"'),type=y[1],x=float(at[1]),y=float(at[2]),ang=int(at[3]),unit=1))
    return r
def getpins(l,s):
    if l=='PocketMate': return custom_pins(s)
    ps=pins(l,s)
    e=resolved(l,s)
    # add angle
    def walk(x,acc):
        for y in x:
            if isinstance(y,list):
                if y[0]=='pin':
                    at=[z for z in y if isinstance(z,list) and z[0]=='at'][0]
                    num=[z for z in y if isinstance(z,list) and z[0]=='number'][0][1].strip('"')
                    acc[num]=int(float(at[3])) if len(at)>3 else 0
                elif y[0]=='symbol': walk(y,acc)
    acc={}; walk(e,acc)
    for p in ps: p['ang']=acc[p['num']]
    return ps
def embed(l,s):
    if l=='PocketMate':
        return CUSTOM[s].replace(f'(symbol "{s}"',f'(symbol "PocketMate:{s}"',1)
    e=copy.deepcopy(resolved(l,s)); e[1]=f'"{l}:{s}"'
    return dump(e)
# ---------------- design ----------------
SHEETS={}
cur=None
def sheet(name,file,title): 
    global cur; cur=dict(name=name,file=file,title=title,parts=[]); SHEETS[name]=cur
def part(lib,sym,ref,val,fp,conn,dnp=False,units=None,**props):
    cur['parts'].append(dict(lib=lib,sym=sym,ref=ref,val=val,fp=fp,conn=conn,dnp=dnp,props=props))
cnt={}
def nref(p):
    cnt[p]=cnt.get(p,0)+1; return f'{p}{cnt[p]}'
R0402='Resistor_SMD:R_0402_1005Metric'; C0402='Capacitor_SMD:C_0402_1005Metric'; C0603='Capacitor_SMD:C_0603_1608Metric'; C0805='Capacitor_SMD:C_0805_2012Metric'
def R(v,a,b,fp=R0402,**k): part('Device','R',nref('R'),v,fp,{'1':a,'2':b},**k)
def C(v,a,b='GND',fp=C0402,**k): part('Device','C',nref('C'),v,fp,{'1':a,'2':b},**k)
def L(v,a,b,fp): part('Device','L',nref('L'),v,fp,{'1':a,'2':b})
def FLAG(net): part('power','PWR_FLAG','#FLG','PWR_FLAG','',{'1':net})
# ===== Sheet: CM5 =====
sheet('CM5','cm5.kicad_sch','CM5 module B2B connectors')
A={}
# connector A
na={'77':'+5V_CM5','79':'+5V_CM5','81':'+5V_CM5','83':'+5V_CM5','85':'+5V_CM5','87':'+5V_CM5',
 '84':'CM5_3V3','86':'CM5_3V3','88':'CM5_1V8','90':'CM5_1V8','78':'CM5_3V3',
 '58':'I2C1_SDA','56':'I2C1_SCL','55':'UART0_TX','51':'UART0_RX',
 '49':'I2S_BCLK','26':'I2S_LRCLK','27':'I2S_DIN','25':'I2S_DOUT',
 '54':'MCU_IRQ_N','50':'MUTE_STATUS_IO','48':'AMP_SD_MODE','46':'HAPTIC_EN','47':'CM5_ALIVE',
 '36':'DSI_I2C_SDA','35':'DSI_I2C_SCL','80':'CAM_I2C_SCL','82':'CAM_I2C_SDA',
 '97':'CAM_GPIO0','100':'CAM_GPIO1','92':'CM5_PWR_BUTTON','99':'CM5_PMIC_EN','93':'CM5_NRPIBOOT','94':'USB_CC1_CM5','96':'USB_CC2_CM5','16':'FAN_TACH','19':'FAN_PWM'}
conn={}
for i in range(1,101):
    nm=cm5[str(i)]
    if nm=='GND': conn[str(i)]='GND'
    elif str(i) in na: conn[str(i)]=na[str(i)]
for k in ('94','96'): conn.pop(k)   # CC1/CC2 unused: PD handled by STUSB4500
part('PocketMate','CM5_B2B_A','J1','10164227-1001A1RLF','PocketMate:CM5_B2B_10164227_Pins1-100',conn,MPN='Amphenol 10164227-1001A1RLF')
nb={'103':'USB_DM','105':'USB_DP',
 '115':'CSI_D0_N','117':'CSI_D0_P','121':'CSI_D1_N','123':'CSI_D1_P','127':'CSI_C_N','129':'CSI_C_P',
 '175':'DSI_D0_N','177':'DSI_D0_P','181':'DSI_D1_N','183':'DSI_D1_P','187':'DSI_C_N','189':'DSI_C_P',
 '133':'CSI_D2_N','135':'CSI_D2_P','139':'CSI_D3_N','141':'CSI_D3_P','193':'DSI_D2_N','195':'DSI_D2_P','194':'DSI_D3_N','196':'DSI_D3_P'}
conn={}
for i in range(101,201):
    nm=cm5[str(i)]
    if nm=='GND': conn[str(i)]='GND'
    elif str(i) in nb: conn[str(i)]=nb[str(i)]
part('PocketMate','CM5_B2B_B','J2','10164227-1001A1RLF','PocketMate:CM5_B2B_10164227_Pins101-200',conn,MPN='Amphenol 10164227-1001A1RLF')
for _ in range(2): C('22uF','+5V_CM5',fp=C0805)
for _ in range(2): C('100nF','+5V_CM5')
C('10uF','CM5_3V3',fp=C0603); C('100nF','CM5_3V3')
FLAG('+5V_CM5')
R('2.2k','I2C1_SDA','CM5_3V3',dnp=True); R('2.2k','I2C1_SCL','CM5_3V3',dnp=True)
# Micro-blower fan header (DNP): JST SH 4p 1.0mm. Fan_PWM = CM5 open-drain (direct, as CM5IO); Fan_Tacho has 1.8k internal pull-up to CM5_3V3.
part('Connector_Generic','Conn_01x04','J12','Fan 5V/GND/PWM/TACH','Connector_JST:JST_SH_SM04B-SRSS-TB_1x04-1MP_P1.00mm_Horizontal',{'1':'+5V_CM5','2':'GND','3':'FAN_PWM','4':'FAN_TACH'},dnp=True,MPN='JST SM04B-SRSS-TB')
R('10k','FAN_TACH','CM5_3V3',dnp=True); C('1uF','+5V_CM5',dnp=True)
part('Connector','TestPoint',nref('TP'),'nRPIBOOT','TestPoint:TestPoint_Pad_D1.0mm',{'1':'CM5_NRPIBOOT'})
part('Connector','TestPoint',nref('TP'),'GND','TestPoint:TestPoint_Pad_D1.0mm',{'1':'GND'})
# ===== Display & camera =====
sheet('DisplayCamera','display_camera.kicad_sch','DSI display (Waveshare 4.3in) and CSI camera (IMX708 / Camera Module 3)')
def fpc22(ref,val,pre,i2c_scl,i2c_sda,p17,p18):
    c={'1':'GND','2':pre+'D0_N','3':pre+'D0_P','4':'GND','5':pre+'D1_N','6':pre+'D1_P','7':'GND','8':pre+'C_N','9':pre+'C_P','10':'GND','11':pre+'D2_N','12':pre+'D2_P','13':'GND','14':pre+'D3_N','15':pre+'D3_P','16':'GND','19':'GND','20':i2c_scl,'21':i2c_sda,'22':'+3V3_PERIPH'}
    if p17: c['17']=p17
    if p18: c['18']=p18
    part('Connector_Generic','Conn_01x22',ref,val,'Connector_FFC-FPC:Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal',c)
fpc22('J3','DSI1 22p 0.5mm FH12-22S-0.5SH (Pi5 DSI pinout)','DSI_','DSI_I2C_SCL','DSI_I2C_SDA','DSI_PIN17',None)
R('2.2k','DSI_PIN17','+3V3_PERIPH')
fpc22('J4','CSI0 22p 0.5mm FH12-22S-0.5SH (Pi5 CSI pinout)','CSI_','CAM_I2C_SCL','CAM_I2C_SDA','CAM_GPIO0','CAM_GPIO1')
C('10uF','+3V3_PERIPH',fp=C0603); C('100nF','+3V3_PERIPH'); C('10uF','+3V3_PERIPH',fp=C0603); C('100nF','+3V3_PERIPH')
R('4.7k','DSI_I2C_SDA','CM5_3V3'); R('4.7k','DSI_I2C_SCL','CM5_3V3')
# ===== Audio =====
sheet('Audio','audio.kicad_sch','MAX98357A amp; mic data/mute-status interface to the side-key flex')
# Mics, mute switch and LED live on the SideFlex sheet. Carrier side, near J11:
R('33R','MIC_DATA_GATED','I2S_DIN')
# MIC_SW_LIVE (J11-11) = +3V3_PERIPH via SW5 pole 1 when LIVE, open when muted. Inverter -> MUTE_STATUS_IO high = muted (CM5 up), independent of PA11
R('100k','MIC_SW_LIVE','GND')
part('Transistor_FET','2N7002','Q6','2N7002','Package_TO_SOT_SMD:SOT-23',{'1':'MIC_SW_LIVE','3':'MUTE_STATUS_IO','2':'GND'})
R('10k','MUTE_STATUS_IO','CM5_3V3')
part('Audio','MAX98357A','U1','MAX98357AETE+','Package_DFN_QFN:TQFN-16-1EP_3x3mm_P0.5mm_EP1.23x1.23mm',
 {'1':'I2S_DOUT','16':'I2S_BCLK','14':'I2S_LRCLK','4':'AMP_SD_MODE','3':'GND','11':'GND','15':'GND','17':'GND','7':'+5V_CM5','8':'+5V_CM5','9':'SPK_P','10':'SPK_N'})
R('1M','AMP_SD_MODE','GND')
C('10uF','+5V_CM5',fp=C0603); C('100nF','+5V_CM5')
part('Connector_Generic','Conn_01x02','J5','Speaker 8R 1W','Connector_JST:JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal',{'1':'SPK_P','2':'SPK_N'})
# ===== USB-C / PD / charger / gauge =====
sheet('PowerInput','power_input.kicad_sch','USB-C, STUSB4500 PD sink, BQ25895 charger, MAX17055 gauge, battery')
# HRO TYPE-C-31-M-12 (LCSC C165948): 16P USB2.0 receptacle; D+/D- pairs tied, via U2 USBLC6 to CM5 USB2 (J2 103/105). SBU A8/B8 unused.
part('Connector','USB_C_Receptacle_USB2.0_16P','J6','TYPE-C-31-M-12','Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12',
 {'S1':'GND','A1':'GND','A12':'GND','B1':'GND','B12':'GND','A4':'VBUS_C','A9':'VBUS_C','B4':'VBUS_C','B9':'VBUS_C','A5':'USB_CC1','B5':'USB_CC2','A6':'USB_DP','B6':'USB_DP','A7':'USB_DM','B7':'USB_DM'})
part('Power_Protection','USBLC6-2SC6','U2','USBLC6-2SC6 (D+/D-)','Package_TO_SOT_SMD:SOT-23-6',{'1':'USB_DP','6':'USB_DP','3':'USB_DM','4':'USB_DM','2':'GND','5':'+3V3_AON'})
part('Power_Protection','USBLC6-2SC6','U3','USBLC6-2SC6 (CC1/CC2)','Package_TO_SOT_SMD:SOT-23-6',{'1':'USB_CC1','6':'USB_CC1','3':'USB_CC2','4':'USB_CC2','2':'GND','5':'+3V3_AON'})
part('Device','D_TVS','D2','SMF15A (VBUS TVS)','Diode_SMD:D_SOD-123F',{'1':'GND','2':'VBUS_C'})
FLAG('VBUS_C')
part('Interface_USB','STUSB4500QTR','U4','STUSB4500QTR','Package_DFN_QFN:QFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm',
 {'2':'USB_CC1','1':'USB_CC1','4':'USB_CC2','5':'USB_CC2','18':'PD_VBUS_VS','7':'MCU_I2C_SCL','8':'MCU_I2C_SDA','19':'PD_ALERT_N','12':'GND','13':'GND','6':'GND',
  '24':'VBUS_C','22':'GND','10':'GND','25':'GND','21':'PD_VREG_1V2','23':'PD_VREG_2V7','16':'VBUS_EN_SNK','9':'PD_DISCH'})
C('1uF','PD_VREG_1V2'); C('1uF','PD_VREG_2V7'); C('1uF','VBUS_C',fp=C0603)
R('1k','PD_VBUS_VS','VBUS_C',fp='Resistor_SMD:R_0603_1608Metric'); R('220R','PD_DISCH','VBUS_CHG',fp='Resistor_SMD:R_0603_1608Metric')
# PMOS sink power switch controlled by VBUS_EN_SNK
part('Transistor_FET','DMP3013SFV','Q1','DMP3013SFV','Package_SON:Diodes_PowerDI3333-8',{'1':'VBUS_C','2':'VBUS_C','3':'VBUS_C','5':'VBUS_CHG','4':'VBUS_EN_SNK'})
R('100k','VBUS_EN_SNK','VBUS_C')
FLAG('VBUS_CHG')
part('Battery_Management','BQ25895RTW','U5','BQ25895RTWR','Package_DFN_QFN:Texas_RTW_WQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm_ThermalVias',
 {'1':'VBUS_CHG','10':'CHG_ILIM','4':'CHG_STAT','6':'MCU_I2C_SDA','5':'MCU_I2C_SCL','7':'CHG_INT_N','8':'GND','9':'GND','12':'BQ_QON_N',
  '17':'GND','18':'GND','25':'GND','23':'CHG_PMID','19':'CHG_SW','20':'CHG_SW','21':'CHG_BTST','15':'VSYS','16':'VSYS','13':'VBAT','14':'VBAT','22':'CHG_REGN','11':'CHG_TS'})
C('1uF','VBUS_CHG',fp=C0603); C('10uF','CHG_PMID',fp=C0805); C('47nF','CHG_BTST','CHG_SW'); C('4.7uF','CHG_REGN',fp=C0603)
L('1uH XAL4020-102ME','CHG_SW','VSYS','Inductor_SMD:L_Coilcraft_XAL4020-XXX')
C('22uF','VSYS',fp=C0805); C('22uF','VSYS',fp=C0805); C('10uF','VBAT',fp=C0805)
R('130R 1%','CHG_ILIM','GND')
R('5.23k','CHG_REGN','CHG_TS'); R('30.1k','CHG_TS','GND')
R('2.2k','CHG_STAT_LED','CHG_REGN'); part('Device','LED','D3','GREEN charge','LED_SMD:LED_0402_1005Metric',{'2':'CHG_STAT_LED_A','1':'CHG_STAT'})
cur['parts'][-2]['conn']={'1':'CHG_REGN','2':'CHG_STAT_LED_A'}
FLAG('VSYS'); FLAG('VBAT')
# QON wake: power button via Schottky (no MCU in path)
part('Device','D_Schottky','D4','RB521S30 (QON wake)','Diode_SMD:D_SOD-523',{'1':'BTN_PWR_N','2':'BQ_QON_N'})
# Battery
# Battery: Molex Pico-Lock 2.00 205338-0005 (mates 205341-0005 housing + 205342 crimp, AWG20: 5.0 A/pin @5ckt). Order: power pairs adjacent, NTC at the end
part('Connector_Generic','Conn_01x05','J7','Molex 205338-0005 (BAT+,BAT+,BAT-,BAT-,NTC)','PocketMate:Molex_Pico-Lock_205338-0005_1x05-1MP_P2.00mm_Horizontal',{'1':'VBAT','2':'VBAT','3':'BAT_N','4':'BAT_N','5':'CHG_TS'},MPN='Molex 2053380005')
FLAG('BAT_N')
# MAX17055 low-side sense
R('10m 1% 1206 0.5W','BAT_N','GND',fp='Resistor_SMD:R_1206_3216Metric')
part('PocketMate','MAX17055ETB','U6','MAX17055ETB+','PocketMate:Maxim_TDFN-10-1EP_2x2.5mm_P0.4mm_EP1.4x1.3mm_MAX17055',
 {'10':'VBAT','2':'BAT_N','7':'GAUGE_REG','4':'MCU_I2C_SDA','3':'MCU_I2C_SCL','8':'GAUGE_ALRT_N','5':'GND','6':'BAT_N','11':'BAT_N'})
C('100nF','VBAT','BAT_N'); C('470nF','GAUGE_REG','BAT_N')
R('4.7k','MCU_I2C_SDA','+3V3_AON'); R('4.7k','MCU_I2C_SCL','+3V3_AON')
R('10k','PD_ALERT_N','+3V3_AON'); R('10k','CHG_INT_N','+3V3_AON'); R('10k','GAUGE_ALRT_N','+3V3_AON')
# ===== Regulators =====
sheet('Regulators','regulators.kicad_sch','Always-on LDO, TPS61088 5V boost, CM5 5V load switch')
part('PocketMate','TPS7A0233PDBV','U7','TPS7A0233PDBVR','Package_TO_SOT_SMD:SOT-23-5',{'1':'VBAT','3':'VBAT','5':'+3V3_AON','2':'GND'},MPN='TI TPS7A0233PDBVR')
C('1uF','VBAT'); C('1uF','+3V3_AON'); C('100nF','+3V3_AON')
part('PocketMate','TPS61088RHL','U8','TPS61088RHLR','PocketMate:TI_RHL0020A_VQFN-20_3.5x4.5mm_TPS61088',
 {'9':'VSYS','2':'BOOST_EN','10':'BST_SS','3':'BST_FSW','19':'BST_ILIM','1':'BST_VCC','4':'BST_SW','5':'BST_SW','6':'BST_SW','7':'BST_SW','8':'BST_BOOT',
  '14':'+5V_BOOST','15':'+5V_BOOST','16':'+5V_BOOST','17':'BST_FB','18':'BST_COMP','20':'GND','21':'GND','11':'GND','12':'GND'})
L('1uH XAL5030-102ME','VSYS','BST_SW','Inductor_SMD:L_Coilcraft_XAL5030-XXX')
C('22uF','VSYS',fp=C0805); C('100nF','VSYS'); C('2.2uF','BST_VCC',fp=C0603); C('100nF','BST_BOOT','BST_SW'); C('47nF','BST_SS')
R('150k 1%','BST_FSW','BST_SW'); R('127k 1%','BST_ILIM','GND')
R('182k 1%','+5V_BOOST','BST_FB'); R('56k 1%','BST_FB','GND')
R('10k','BST_COMP','BST_COMP_RC'); C('2.7nF','BST_COMP_RC'); C('18pF','BST_COMP')
for _ in range(3): C('22uF','+5V_BOOST',fp=C0805)
R('100k','BOOST_EN','GND')
# Peripheral 3V3 buck: TLV62585DRLR from VSYS; enabled by CM5_3V3 (on only while CM5 rails are up -> no back-powering of CM5 I/O)
part('PocketMate','TLV62585DRL','U12','TLV62585DRLR','Package_TO_SOT_SMD:SOT-563',{'3':'VSYS','4':'BUCK3V3_EN','2':'BUCK3V3_SW','5':'BUCK3V3_FB','1':'GND'},MPN='TI TLV62585DRLR',LCSC='C485117')
C('10uF','VSYS',fp=C0603); C('100nF','VSYS')
L('1uH DFE252012F-1R0M','BUCK3V3_SW','+3V3_PERIPH','Inductor_SMD:L_1008_2520Metric')
R('100k 1%','+3V3_PERIPH','BUCK3V3_FB'); R('22.1k 1%','BUCK3V3_FB','GND')
C('22uF','+3V3_PERIPH',fp=C0805); C('22uF','+3V3_PERIPH',fp=C0805)
R('10k','CM5_3V3','BUCK3V3_EN'); R('100k','BUCK3V3_EN','GND')
FLAG('+3V3_PERIPH')
# 5V load switch (high-side PMOS + NMOS driver) -- TPS61088 is not true-disconnect
part('Transistor_FET','DMP3013SFV','Q2','DMP3013SFV','Package_SON:Diodes_PowerDI3333-8',{'1':'+5V_BOOST','2':'+5V_BOOST','3':'+5V_BOOST','5':'+5V_CM5','4':'LSW_GATE'})
R('100k','LSW_GATE','+5V_BOOST'); C('10nF','LSW_GATE','+5V_BOOST')
part('Transistor_FET','2N7002','Q3','2N7002','Package_TO_SOT_SMD:SOT-23',{'1':'CM5_5V_EN','3':'LSW_GATE','2':'GND'})
R('100k','CM5_5V_EN','GND')
# ===== MCU =====
sheet('MCU','mcu.kicad_sch','STM32U031 always-on supervisor, buttons, CM5 power control')
part('MCU_ST_STM32U0','STM32U031K8Ux','U9','STM32U031K8U6','Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.45x3.45mm',
 {'1':'+3V3_AON','17':'+3V3_AON','5':'+3V3_AON','16':'GND','32':'GND','33':'GND',
  '4':'MCU_NRST','23':'SWDIO','24':'SWCLK',
  '6':'BTN_PWR_N','7':'BTN_ACTION_N','10':'BTN_VOLUP_N','11':'BTN_VOLDN_N',
  '8':'MCU_TX','9':'MCU_RX','12':'CM5_PWRBTN_DRV','13':'CM5_PMIC_OFF_DRV',
  '25':'BOOST_EN','15':'CM5_5V_EN','14':'NTC_ADC','22':'NTC_BIAS','31':'MCU_BOOT0','26':'MCU_IRQ_N','27':'CM5_ALIVE','28':'CHG_INT_N','18':'GAUGE_ALRT_N','19':'PD_ALERT_N',
  '29':'MCU_I2C_SCL','30':'MCU_I2C_SDA','20':'MUTE_STATUS_IO','21':'MIC_PWR_EN'})
C('100nF','+3V3_AON'); C('100nF','+3V3_AON'); C('1uF','+3V3_AON'); C('100nF','MCU_NRST')
R('10k','MCU_BOOT0','GND')
# skin NTC (off-board, back plate) on JST SH 2p; divider biased from GPIO PA12 only while sampling
R('10k 1%','NTC_BIAS','NTC_ADC'); C('100nF','NTC_ADC')
part('Connector_Generic','Conn_01x02','J10','Skin NTC 10k B3435','Connector_JST:JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal',{'1':'NTC_ADC','2':'GND'})
R('1k','MCU_TX','UART0_RX'); R('1k','MCU_RX','UART0_TX')
R('10k','MCU_IRQ_N','CM5_3V3')
for n in ['BTN_PWR_N','BTN_ACTION_N','BTN_VOLUP_N','BTN_VOLDN_N']:
    R('100k',n,'+3V3_AON'); C('10nF',n)
# ESD for the flex lines: TPD4E05U06 on the 4 buttons, D5 on the mute-status line
part('Power_Protection','TPD4E05U06DQA','U13','TPD4E05U06DQAR (flex buttons ESD)','Package_SON:USON-10_2.5x1.0mm_P0.5mm',{'1':'BTN_PWR_N','2':'BTN_ACTION_N','4':'BTN_VOLUP_N','5':'BTN_VOLDN_N','3':'GND','8':'GND'})
part('Device','D_TVS','D5','PESD5V0S1BB (ESD, MIC_SW_LIVE)','Diode_SMD:D_SOD-523',{'1':'GND','2':'MIC_SW_LIVE'})
# Carrier J11: side-key flex, Hirose FH12-16S-0.5SH. Placement: carrier top edge X 22..35, Y 27..31
# pin 2 = always-on (ALS on MCU bus); pin 3 = MIC_PWR (gated, = +3V3_PERIPH: on only with CM5) feeds the mute switch/mics/LED
# Recording-indicator load switch: MIC_FEED = (+3V3_PERIPH AND SW5 live, via flex) AND MIC_PWR_EN (MCU PA11); QOD tied to VOUT (150R fast discharge)
part('Power_Management','TPS22917DBV','U14','TPS22917DBVR','Package_TO_SOT_SMD:SOT-23-6',{'1':'MIC_SW_LIVE','2':'GND','3':'MIC_PWR_EN','6':'MIC_FEED','5':'MICSW_QOD'},MPN='TI TPS22917DBVR',LCSC='C2681320')
R('0R','MICSW_QOD','MIC_FEED')  # QOD->VOUT: 0R = fastest (150R internal); fit R to slow fall time
C('100nF','MIC_SW_LIVE'); C('100nF','MIC_FEED'); FLAG('MIC_SW_LIVE')  # driven from +3V3_PERIPH through SW5 on the flex (switch contact); R('100k','MIC_PWR_EN','GND')
SIDEFLEX={'1':'GND','2':'+3V3_AON','3':'MIC_FEED','4':'I2S_BCLK','5':'GND','6':'I2S_LRCLK','7':'MIC_DATA_GATED','8':'GND','9':'MCU_I2C_SDA','10':'MCU_I2C_SCL','11':'MIC_SW_LIVE','12':'BTN_PWR_N','13':'BTN_VOLUP_N','14':'BTN_VOLDN_N','15':'+3V3_PERIPH','16':'BTN_ACTION_N'}
part('Connector_Generic','Conn_01x16','J11','FH12-16S-0.5SH(55)','Connector_FFC-FPC:Hirose_FH12-16S-0.5SH_1x16-1MP_P0.50mm_Horizontal',SIDEFLEX,MPN='Hirose FH12-16S-0.5SH(55)')
# CM5 PWR_Button / PMIC_Enable open-drain (CM5 pulls these to 5V internally)
part('Transistor_FET','2N7002','Q4','2N7002','Package_TO_SOT_SMD:SOT-23',{'1':'CM5_PWRBTN_DRV','3':'CM5_PWR_BUTTON','2':'GND'})
part('Transistor_FET','2N7002','Q5','2N7002','Package_TO_SOT_SMD:SOT-23',{'1':'CM5_PMIC_OFF_DRV','3':'CM5_PMIC_EN','2':'GND'})
R('100k','CM5_PWRBTN_DRV','GND'); R('100k','CM5_PMIC_OFF_DRV','GND')
part('Connector_Generic','Conn_01x05','J8','SWD (TC2030 pads)','Connector_PinHeader_1.27mm:PinHeader_1x05_P1.27mm_Vertical',{'1':'+3V3_AON','2':'SWDIO','3':'SWCLK','4':'MCU_NRST','5':'GND'})
# ===== Sensors & haptics =====
sheet('Sensors','sensors_haptics.kicad_sch','DRV2605L haptic (DNP), I2C1 pull-ups (VEML7700 is on the side-key flex)')
part('Driver_Haptic','DRV2605LDGS','U11','DRV2605LDGSR','Package_SO:VSSOP-10_3x3mm_P0.5mm',
 {'3':'I2C1_SDA','2':'I2C1_SCL','4':'GND','5':'HAPTIC_EN','6':'VSYS','10':'VSYS','8':'GND','7':'LRA_P','9':'LRA_N','1':'HAPTIC_REG'},dnp=True)
C('1uF','VSYS',dnp=True); C('1uF','HAPTIC_REG',dnp=True); R('100k','HAPTIC_EN','GND',dnp=True)
part('Connector_Generic','Conn_01x02','J9','LRA motor','Connector_JST:JST_SH_SM02B-SRSS-TB_1x02-1MP_P1.00mm_Horizontal',{'1':'LRA_P','2':'LRA_N'},dnp=True)
part('Device','R','R_ALS_I2C','DNP','',{})  # placeholder removed below
cur['parts'].pop()
R('2.2k','I2C1_SDA','CM5_3V3'); R('2.2k','I2C1_SCL','CM5_3V3')
# ===== Side-key flex (separate flex PCB; J13 tail mates with carrier J11, pin n = pin n) =====
sheet('SideFlex','side_flex.kicad_sch','Side-key flex: Power/Vol buttons, Action, hardware mic mute (DPDT + red LED), 2x SPH0645 mics, VEML7700')
part('Connector_Generic','Conn_01x16','J13','Flex tail to carrier J11 (placeholder)','PocketMate:FlexTail_16P_P0.50mm',SIDEFLEX)
part('Switch','SW_Push','SW1','POWER','Button_Switch_SMD:SW_SPST_PTS810',{'1':'BTN_PWR_N','2':'GND'})
part('Switch','SW_Push','SW2','ACTION','Button_Switch_SMD:SW_SPST_PTS810',{'1':'BTN_ACTION_N','2':'GND'})
part('Switch','SW_Push','SW3','VOL+','Button_Switch_SMD:SW_SPST_PTS810',{'1':'BTN_VOLUP_N','2':'GND'})
part('Switch','SW_Push','SW4','VOL-','Button_Switch_SMD:SW_SPST_PTS810',{'1':'BTN_VOLDN_N','2':'GND'})
part('Sensor_Audio','SPH0645LM4H','MK1','SPH0645LM4H-B (Left, SEL=GND)','Sensor_Audio:Knowles_SPH0645LM4H-6_3.5x2.65mm',{'5':'MIC_FEED','3':'GND','2':'GND','1':'I2S_LRCLK','4':'I2S_BCLK','6':'MIC_SD_L'})
part('Sensor_Audio','SPH0645LM4H','MK2','SPH0645LM4H-B (Right, SEL=VDD)','Sensor_Audio:Knowles_SPH0645LM4H-6_3.5x2.65mm',{'5':'MIC_FEED','3':'GND','2':'MIC_FEED','1':'I2S_LRCLK','4':'I2S_BCLK','6':'MIC_SD_R'})
# 0R per mic (tri-state outputs share the line; lets one mic be isolated for debug)
R('0R','MIC_SD_L','MIC_SD'); R('0R','MIC_SD_R','MIC_SD')
C('100nF','MIC_FEED'); C('100nF','MIC_FEED'); R('100k','MIC_SD','GND')
# DPDT mute (hardware only). Pole 1: +3V3_PERIPH (J11-15) -> MIC_SW_LIVE (J11-11, to carrier U14 IN, live) / red LED (muted).
# Pole 2: common MIC_DATA_GATED (out) <- MIC_SD (live) / GND (muted).
part('Switch','SW_DPDT_x2','SW5','MIC MUTE (DPDT slide)','Button_Switch_SMD:SW_DPDT_CK_JS202011JCQN',{'2':'+3V3_PERIPH','1':'MIC_SW_LIVE','3':'MUTE_LED_PWR','5':'MIC_DATA_GATED','4':'MIC_SD','6':'GND'})
R('1k','MUTE_LED_PWR','MUTE_LED_A')
part('Device','LED','D1','RED mic-muted','LED_SMD:LED_0402_1005Metric',{'2':'MUTE_LED_A','1':'GND'})
# VEML7700 on the always-on MCU I2C bus (addr 0x10); firmware keeps ALS_SD=1 (0.5 uA) when idle
part('PocketMate','VEML7700','U10','VEML7700-TT','PocketMate:Vishay_VEML7700',{'2':'+3V3_AON','3':'GND','4':'MCU_I2C_SDA','1':'MCU_I2C_SCL'})
C('100nF','+3V3_AON'); C('1uF','MIC_FEED')
# REC indicator: lit whenever MIC_FEED (the mic supply itself) is powered -> exact indication
R('1.3k','MIC_FEED','REC_LED_A')
part('Device','LED','D6','GREEN REC (APTD1608LZGCK)','LED_SMD:LED_0603_1608Metric',{'2':'REC_LED_A','1':'GND'})
# ===== LTE daughterboard link (kicad-lte, Option D of layout/lte_placement_study.md) =====
# Carrier J14 = Hirose FH12-22S-0.5SH, 22p 0.5 mm FPC to the LTE board (EC25-E / EC200U-CN). Appended last so no existing ref renumbers.
# Signals are CM5 3.3 V GPIO domain; 1.8 V translation + PWRKEY/RESET_N open-drain drivers live on the LTE board.
# USB2: CM5 USB3-0 port's USB2 pair (J2 134 DP / 136 DM), 90R diff. LTE_USB_VBUS = +5V_CM5 (EC200U needs USB_VBUS >= 3.5 V, so not VSYS).
sheet('LTE','lte_link.kicad_sch','LTE daughterboard link J14 (FH12-22S, 22p 0.5mm): VSYS, USB2 (CM5 USB3-0 DP/DM), control GPIOs')
for k,v in {'134':'LTE_USB_DP','136':'LTE_USB_DM'}.items():
    SHEETS['CM5']['parts'][[q['ref'] for q in SHEETS['CM5']['parts']].index('J2')]['conn'][k]=v
for k,v in {'34':'LTE_PWR_EN','30':'LTE_PWRKEY','28':'LTE_RESET','24':'LTE_W_DISABLE_N','29':'LTE_STATUS','31':'LTE_RI','41':'LTE_AP_READY'}.items():
    SHEETS['CM5']['parts'][[q['ref'] for q in SHEETS['CM5']['parts']].index('J1')]['conn'][k]=v
LTEFLEX={'1':'VSYS','2':'VSYS','3':'VSYS','4':'VSYS','5':'VSYS','6':'VSYS','7':'GND','8':'GND','9':'GND',
 '10':'LTE_USB_DM','11':'LTE_USB_DP','12':'GND','13':'LTE_USB_VBUS','14':'GND',
 '15':'LTE_PWR_EN','16':'LTE_PWRKEY','17':'LTE_RESET','18':'LTE_W_DISABLE_N','19':'LTE_STATUS','20':'LTE_RI','21':'LTE_AP_READY','22':'GND'}
part('Connector_Generic','Conn_01x22','J14','LTE link FH12-22S-0.5SH(55)','Connector_FFC-FPC:Hirose_FH12-22S-0.5SH_1x22-1MP_P0.50mm_Horizontal',LTEFLEX,MPN='Hirose FH12-22S-0.5SH(55)')
R('0R','+5V_CM5','LTE_USB_VBUS')          # USB_VBUS detect feed (uA load); DNP to hide the module from USB
R('100k','LTE_PWR_EN','GND')              # LTE load switch off while CM5 GPIO floats / CM5 off
C('22uF','VSYS',fp=C0805); C('100nF','VSYS')  # carrier-side VSYS decoupling at J14 (2 A burst feed, bulk is on the LTE board)
# GND flag
SHEETS['CM5']['parts'].append(dict(lib='power',sym='PWR_FLAG',ref='#FLG',val='PWR_FLAG',fp='',conn={'1':'GND'},dnp=False,props={}))
# ---------------- emit ----------------
netsheets={}
for s in SHEETS.values():
    for p in s['parts']:
        for n in p['conn'].values(): netsheets.setdefault(n,set()).add(s['name'])
NS=uuid.UUID('6f1b0c1e-2b6d-4a51-9a3e-5c0de0a1b2c3')
DU=lambda k: str(uuid.uuid5(NS,k))
ROOT=DU('root'); pwr=[0]
def emit_sheet(s,suuid,page):
    items=[]; libs={}
    # ---- layout pass: choose smallest paper that fits ----
    blocks=[]
    for p in s['parts']:
        ps=getpins(p['lib'],p['sym'])
        libs[(p['lib'],p['sym'])]=embed(p['lib'],p['sym'])
        units=sorted(set(q['unit'] for q in ps if q['unit']>0)) or [1]
        for un in units:
            up=[q for q in ps if q['unit'] in (0,un)]
            xs=[q['x'] for q in up] or [0]; ys=[q['y'] for q in up] or [0]
            lab=max([len(n) for n in p['conn'].values()]+[3])*1.05+5
            top=any(q['ang']==270 and q['num'] in p['conn'] for q in up); bot=any(q['ang']==90 and q['num'] in p['conn'] for q in up)
            vert2=all(abs(q['x'])<0.01 for q in up) and len(up)<=3
            wl=-min(xs)+(lab if any(q['ang']==0 for q in up) else 3)
            wr=max(xs)+(lab if any(q['ang']==180 for q in up) else 3)
            if vert2: wr=max(wr,3+len(p['val'])*1.0); wl=max(wl,4)
            tl=(lab if top else 0)+(0 if vert2 else 7); bl=(lab if bot else 0)+(0 if vert2 else 7)
            if not vert2: wr=max(wr,min(xs)+max(len(p['val']),len(p['ref']))*1.1+3)
            blocks.append((p,un,up,xs,ys,wl,wr,tl,bl,vert2))
    for paper,PW,PH in (('A3',420,297),('A2',594,420),('A1',841,594)):
        x0,y0=20.32,30.48; x,y=x0,y0; rowh=0; W=PW-20; pos=[]
        for (p,un,up,xs,ys,wl,wr,tl,bl,vert2) in blocks:
            ht=tl+max(ys)-min(ys)+bl+6
            if x+wl+wr>W: x=x0; y+=rowh; rowh=0
            X=round((x+wl)/2.54)*2.54; Y=round((y+tl+max(ys))/2.54)*2.54
            x+=wl+wr+2.54; rowh=max(rowh,ht); pos.append((X,Y))
        if y+rowh<PH-45: break
    s['paper']=paper
    for (p,un,up,xs,ys,wl,wr,tl,bl,vert2),(X,Y) in zip(blocks,pos):
        if True:
            pw=p['lib']=='power'
            ref=p['ref']
            if pw: pwr[0]+=1; ref=f"#FLG0{pwr[0]}"
            if vert2: rx,ry,vx,vy=X+2.54,Y-1.27,X+2.54,Y+1.27
            else: rx,ry,vx,vy=X+min(xs),Y-max(ys)-tl+2.54,X+min(xs),Y-min(ys)+bl-2.54
            pinuu=' '.join(f'(pin "{q["num"]}" (uuid "{U()}"))' for q in up)
            props=''.join(f' (property "{k}" "{v}" (at {X:g} {Y:g} 0) {FH})' for k,v in p['props'].items())
            items.append(f'''(symbol (lib_id "{p['lib']}:{p['sym']}") (at {X:g} {Y:g} 0) (unit {un}) (exclude_from_sim no) (in_bom {'no' if pw else 'yes'}) (on_board {'no' if pw else 'yes'}) (dnp {'yes' if p['dnp'] else 'no'}) (uuid "{DU(s['name']+':'+ref+':'+str(un))}")
 (property "Reference" "{ref}" (at {rx:g} {ry:g} 0) {FH if pw else FL}) (property "Value" "{p['val']}" (at {vx:g} {vy:g} 0) {FH if pw else FL})
 (property "Footprint" "{p['fp']}" (at {X:g} {Y:g} 0) {FH}) (property "Datasheet" "~" (at {X:g} {Y:g} 0) {FH}){props}
 {pinuu} (instances (project "{PROJ}" (path "/{ROOT}/{suuid}" (reference "{ref}") (unit {un})))))''')
            seen=set()
            for q in up:
                px=round(X+q['x'],2); py=round(Y-q['y'],2)
                if (px,py) in seen: continue
                seen.add((px,py))
                n=p['conn'].get(q['num'])
                if n is None:
                    if not pw: items.append(f'(no_connect (at {px:g} {py:g}) (uuid "{U()}"))')
                    continue
                if n=='GND' and not pw:
                    pwr[0]+=1
                    libs[('power','GND')]=embed('power','GND')
                    items.append(f'''(symbol (lib_id "power:GND") (at {px:g} {py:g} {({0:270,180:90,270:180}).get(q['ang'],0)}) (unit 1) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (uuid "{U()}")
 (property "Reference" "#PWR0{pwr[0]}" (at {px:g} {py+6:g} 0) {FH}) (property "Value" "GND" (at {px:g} {py+3.8:g} 0) {FH})
 (property "Footprint" "" (at {px:g} {py:g} 0) {FH}) (property "Datasheet" "" (at {px:g} {py:g} 0) {FH}) (pin "1" (uuid "{U()}"))
 (instances (project "{PROJ}" (path "/{ROOT}/{suuid}" (reference "#PWR0{pwr[0]}") (unit 1)))))''')
                    continue
                a={0:180,180:0,90:270,270:90}[q['ang']]
                j={0:'left',180:'right',90:'left',270:'right'}[a]
                if len(netsheets[n])>1 or n=='GND':
                    items.append(f'(global_label "{n}" (shape passive) (at {px:g} {py:g} {a}) (fields_autoplaced yes) (effects (font (size 1.27 1.27)) (justify {j})) (uuid "{U()}") (property "Intersheetrefs" "${{INTERSHEET_REFS}}" (at {px:g} {py:g} 0) {FH}))')
                else:
                    items.append(f'(label "{n}" (at {px:g} {py:g} {a}) (effects (font (size 1.27 1.27)) (justify {j} bottom)) (uuid "{U()}"))')
    txt=f'''(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0") (uuid "{suuid}") (paper "{s['paper']}")
 (title_block (title "PocketMate - {s['name']}") (comment 1 "{s['title']}") (date "2026-10-21") (rev "0.1") (company "PocketMate"))
 (lib_symbols {' '.join(libs.values())})
 {chr(10).join(items)}
 (text "{s['title']}. Connections are by net label at pin endpoints; global labels cross sheets." (exclude_from_sim no) (at 20.32 20.32 0) (effects (font (size 2 2)) (justify left bottom)) (uuid "{U()}"))
)
'''
    open(f"{OUT}/{s['file']}",'w').write(txt)
blocks=[]
for i,s in enumerate(SHEETS.values()):
    su=DU('sheet:'+s['name']); emit_sheet(s,su,i+2)
    bx=25.4+(i%4)*60.96; by=40.64+(i//4)*40.64
    blocks.append(f'''(sheet (at {bx:g} {by:g}) (size 50.8 25.4) (exclude_from_sim no) (in_bom yes) (on_board yes) (dnp no) (fields_autoplaced yes) (stroke (width 0.1524) (type solid)) (fill (color 0 0 0 0)) (uuid "{su}")
 (property "Sheetname" "{s['name']}" (at {bx:g} {by-0.7:g} 0) (effects (font (size 1.27 1.27)) (justify left bottom)))
 (property "Sheetfile" "{s['file']}" (at {bx:g} {by+26:g} 0) (effects (font (size 1.27 1.27)) (justify left top)))
 (instances (project "{PROJ}" (path "/{ROOT}" (page "{i+2}")))))''')
open(f'{OUT}/{PROJ}.kicad_sch','w').write(f'''(kicad_sch (version 20250114) (generator "eeschema") (generator_version "9.0") (uuid "{ROOT}") (paper "A3")
 (title_block (title "PocketMate CM5 carrier - top level") (date "2026-10-21") (rev "0.1") (company "PocketMate"))
 (lib_symbols)
 {chr(10).join(blocks)}
 (text "PocketMate CM5 carrier v0.1 - see hardware/block-diagram.md for block diagram, power tree and power states" (exclude_from_sim no) (at 25.4 25.4 0) (effects (font (size 2.54 2.54)) (justify left bottom)) (uuid "{U()}"))
 (sheet_instances (path "/" (page "1")))
)
''')
if not os.path.exists(f'{OUT}/{PROJ}.kicad_pro'):
    open(f'{OUT}/{PROJ}.kicad_pro','w').write(json.dumps({"meta":{"filename":"PocketMate.kicad_pro","version":3},"schematic":{"legacy_lib_dir":"","legacy_lib_list":[]},"sheets":[],"boards":[],"libraries":{"pinned_footprint_libs":[],"pinned_symbol_libs":[]}},indent=2))
json.dump({n:sorted(v) for n,v in netsheets.items()},open(OUT+'/gen/nets.json','w'),indent=1)
print('ok',{k:len(v['parts']) for k,v in SHEETS.items()})
