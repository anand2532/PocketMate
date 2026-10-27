import sys; sys.path.insert(0,'.')
import cadquery as cq, json
from OCP.BRepTools import BRepTools
from OCP.TopoDS import TopoDS_Shape
from OCP.BRep import BRep_Builder
from OCP.BRepExtrema import BRepExtrema_DistShapeShape as D
from stepio import load_named
def rd(n):
    s=TopoDS_Shape(); BRepTools.Read_s(s,'work/'+n+'.brep',BRep_Builder()); return cq.Shape.cast(s)
idx=json.load(open('work/index.json')); P={n:rd(n) for n in idx['names']}
for k,v in load_named('ref/carrier_kicad_export_126f5c6c.step').items(): P['PCB:'+k]=cq.Shape.cast(v).translate(cq.Vector(0,0,9.94))
pairs=[('Vol_LTE_EC25_Shield','Vol_Display'),('HeatSpreader_Cu_0p5','Vol_Display'),('Vol_LTE_EC25_Shield','Bezel_DisplayFrame_PC'),('HeatSpreader_Cu_0p5','Bezel_DisplayFrame_PC'),
('LTE_Daughterboard_PCB','Vol_Leads_Prod62'),('LTE_Daughterboard_PCB','Vol_Leads_ProtoAkyga'),('LTE_Daughterboard_PCB','Vol_J7_Housing205341'),('LTE_Daughterboard_PCB','Vol_Speaker'),('Vol_LTE_EC25_Shield','Vol_Speaker'),('HeatSpreader_Cu_0p5','Vol_Speaker'),
('LTE_Daughterboard_PCB','Vol_Battery'),('LTE_Daughterboard_PCB','Vol_Cell_Prod_62'),('LTE_Daughterboard_PCB','SideKey_Flex'),('Bezel_DisplayFrame_PC','Vol_Leads_Prod62'),
('Coax_GNSS','SideKey_Flex'),('Coax_Main','SideKey_Flex'),('Coax_GNSS','Vol_LTE_UFL_Main'),('Vol_Ant_GNSS_Keepout','Vol_ALS_VEML7700'),('Vol_Ant_LTE_Main_Keepout','Vol_ALS_VEML7700'),('RFWindow_GNSS_TL_PC','Vol_ALS_VEML7700'),
('Vol_Ant_GNSS_Keepout','SideKey_Flex'),('Vol_Ant_LTE_Main_Keepout','SideKey_Flex'),('Vol_Ant_LTE_Main_Keepout','Vol_NTC_Case'),('Vol_Ant_LTE_Main_FPC_40x15','Vol_Cell_Prod_62'),('Vol_Ant_LTE_Main_FPC_40x15','Vol_Cell_Proto_Akyga'),
('Vol_Ant_LTE_Main_FPC_40x15','Vol_Leads_Prod62'),('Vol_Ant_GNSS_Envelope','Vol_Leads_Prod62'),('Vol_Ant_LTE_Div_FPC','Vol_Speaker'),('Vol_Ant_LTE_Div_FPC','Vol_J6_USBC_HRO'),('RFWindow_LTE_Div_BL_PC','Vol_J6_USBC_HRO'),
('Vol_Ant_LTE_Main_FPC_40x15','Vol_Antenna_FPC'),('Vol_Ant_LTE_Main_FPC_40x15','RFWindow_PC'),('Vol_LTE_NanoSIM_Hinged','Vol_LTE_EC25_Shield'),('Vol_LTE_DB_Conn_FH12_22','Vol_LTE_NanoSIM_Hinged'),
('LTE_Flex_22P','PCB:J7'),('LTE_Flex_22P','Vol_J7_Housing205341'),('Vol_J14_FH12_22_Courtyard','PCB:H3'),('PCB:J14','PCB:C61'),('PCB:J14','PCB:J10'),('Vol_Pigtail','Al_Unibody'),('Vol_Pigtail','Vol_CM5'),('Vol_Pigtail','PCB:CarrierBoard')]
P['PCB:CarrierBoard']=[v for k,v in P.items() if k.startswith('PCB:=>')][0]
out={}
for a,b in pairs:
    if a not in P or b not in P: print('missing',a,b); continue
    d=D(P[a].wrapped,P[b].wrapped); d.Perform(); out[f'{a} | {b}']=round(d.Value(),2); print(f'{a:32s} {b:28s} {d.Value():6.2f}')
json.dump(out,open('work/key_gaps.json','w'),indent=1)
