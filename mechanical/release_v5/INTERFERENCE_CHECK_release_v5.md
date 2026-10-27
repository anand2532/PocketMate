# Release v5.1 – interference check output (auto-generated: check_release_v5.py -> make_interference_md.py)

Parts: 76 enclosure parts/volumes + 144 carrier solids from the KiCad export of PocketMate.kicad_pcb (md5 126f5c6c…, read-only copy). Estimated-height boxes for parts without 3D models: TP1, TP2, U1, J9, J5.

Threshold: common volume > 0.01 mm³. CLASH = real; other classes are intended / variant / envelope pairs.

| A | B | common mm³ | class | overlap bbox (X0,X1,Y0,Y1,Z0,Z1) |
|---|---|---|---|---|
| Vol_CM5 | PCB:J8 | 0.531 | CLASH | [35.8, 36.2, -17.28, -11.8, 9.23, 9.94] |
| Vol_J4_FH12_22 | PCB:Q2 | 0.262 | CLASH | [29.35, 32.65, 0.95, 1.05, 11.54, 12.34] |
| Vol_J4_FH12_22 | PCB:C6 | 0.226 | CLASH | [33.83, 34.83, 1.09, 1.59, 11.54, 12.04] |
| Vol_J12_FanHdr_DNP | PCB:R3 | 0.023 | CLASH | [30.72, 31.72, -26.57, -26.5, 11.54, 11.88] |
| Al_Unibody | Vol_ThermalPad | 4.5 | contact(face) | [7.0, 37.0, -28.0, 2.0, 4.0, 4.0] |
| Al_Unibody | Vol_CM5 | 0.323 | contact(face) | [0.0, 53.0, -29.0, 9.0, 5.0, 5.0] |
| Vol_CM5 | Vol_J1_B2B | 94.5 | intended(B2B mated) | [17.75, 40.25, 5.6, 8.4, 8.44, 9.94] |
| Vol_CM5 | Vol_J2_B2B | 94.5 | intended(B2B mated) | [17.75, 40.25, -28.4, -25.6, 8.44, 9.94] |
| Vol_UFL | Vol_Pigtail | 1.98 | intended(coax mate) | [51.4, 52.9, 0.4, 1.6, 1.9, 3.0] |
| Vol_LTE_UFL_GNSS | Coax_GNSS | 1.84 | intended(coax mate) | [-47.0, -45.4, 14.7, 15.85, 13.3, 14.3] |
| Vol_LTE_UFL_Main | Coax_Main | 1.897 | intended(coax mate) | [-51.6, -49.95, 12.85, 14.0, 13.3, 14.3] |
| Vol_LTE_DB_Conn_FH12_22 | LTE_Flex_22P | 4.875 | intended(flex in connector) | [-5.6, -5.0, -12.75, -0.25, 12.3, 12.95] |
| Vol_J14_FH12_22_Courtyard | LTE_Flex_22P | 15.844 | intended(flex in connector) | [-0.95, 1.0, -12.75, -0.25, 12.3, 12.95] |
| LTE_Flex_22P | PCB:J14 | 11.416 | intended(flex in connector) | [-0.41, 1.0, -12.75, -0.25, 12.3, 12.95] |
| Vol_J7_Molex205338 | Vol_J7_Housing205341 | 43.24 | intended(mated) | [-0.91, 0.26, 16.13, 30.68, 11.6, 14.14] |
| Bezel_DisplayFrame_PC | Vol_Antenna_Keepout | 0.72 | keepout-ok(non-metal/own feed) | [54.4, 54.5, -25.0, 11.0, 15.8, 16.0] |
| Vol_Antenna_FPC | Vol_Antenna_Keepout | 91.8 | keepout-ok(non-metal/own feed) | [59.6, 59.9, -24.0, 10.0, 5.5, 14.5] |
| Vol_Antenna_Keepout | Vol_Pigtail | 5.76 | keepout-ok(non-metal/own feed) | [57.0, 59.6, 0.4, 1.6, 4.0, 6.6] |
| Vol_Ant_LTE_Main_Keepout | Coax_Main | 11.811 | keepout-ok(non-metal/own feed) | [-60.2, -55.0, 12.85, 14.0, 10.0, 14.45] |
| Vol_Ant_GNSS_PatchOpt_Envelope | Vol_Ant_GNSS_Keepout | 288.8 | keepout-ok(non-metal/own feed) | [-58.8, -55.6, 17.5, 27.0, 2.5, 12.0] |
| Vol_Ant_GNSS_Keepout | Coax_GNSS | 1.087 | keepout-ok(non-metal/own feed) | [-58.8, -58.1, 17.0, 17.45, 11.0, 14.45] |
| Vol_Cell_Prod_62 | Vol_Cell_Proto_Akyga | 22134.0 | other-variant | [-53.75, -2.75, -33.5, 28.5, 2.3, 9.3] |
| Vol_Cell_Prod_62 | Vol_Leads_ProtoAkyga | 119.196 | other-variant | [-27.4, -12.58, 18.1, 28.5, 9.3, 10.8] |
| Vol_Cell_Prod_62 | Liner_PET_Proto | 290.77 | other-variant | [-53.5, -3.0, -33.3, 28.5, 9.3, 9.4] |
| Vol_Cell_Prod_62 | Foam_Proto_2p0 | 2922.92 | other-variant | [-51.7, -5.3, -31.7, 16.7, 9.4, 10.8] |
| Vol_Cell_Proto_Akyga | Vol_Leads_Prod62 | 43.274 | other-variant | [-27.4, -19.4, 28.5, 32.0, 5.75, 9.3] |
| Vol_Leads_Prod62 | Vol_Leads_ProtoAkyga | 41.538 | other-variant | [-25.8, -8.84, 18.5, 32.02, 9.3, 13.67] |
| Vol_Leads_ProtoAkyga | Liner_PET_Prod | 5.508 | other-variant | [-26.99, -12.29, 18.21, 28.3, 10.8, 10.9] |
| Liner_PET_Prod | Foam_Proto_2p0 | 208.78 | other-variant | [-51.7, -5.3, -31.7, 16.7, 10.8, 10.9] |
| Foam_Prod_0p5 | Foam_Proto_2p0 | 1043.9 | other-variant | [-51.7, -5.3, -31.7, 16.7, 10.9, 11.4] |
| Vol_Ant_GNSS_Envelope | Vol_Ant_GNSS_PatchOpt_Envelope | 144.4 | other-variant(GNSS chip vs patch option) | [-60.4, -58.8, 17.5, 27.0, 2.5, 12.0] |
| Vol_Battery | Vol_Cell_Prod_62 | 26877.0 | pocket-envelope | [-53.75, -2.75, -33.5, 28.5, 2.3, 10.8] |
| Vol_Battery | Vol_Cell_Proto_Akyga | 23383.5 | pocket-envelope | [-53.75, -2.75, -33.5, 32.0, 2.3, 9.3] |
| Vol_Battery | Vol_Leads_Prod62 | 69.394 | pocket-envelope | [-27.4, -16.06, 18.51, 32.03, 5.75, 11.3] |
| Vol_Battery | Vol_Leads_ProtoAkyga | 206.416 | pocket-envelope | [-27.4, -11.11, 18.1, 33.5, 5.0, 11.3] |
| Vol_Battery | Liner_PET_Prod | 311.08 | pocket-envelope | [-53.5, -3.0, -33.3, 28.3, 10.8, 10.9] |
| Vol_Battery | Foam_Prod_0p5 | 835.12 | pocket-envelope | [-51.7, -5.3, -31.7, 16.7, 10.9, 11.3] |
| Vol_Battery | Liner_PET_Proto | 300.98 | pocket-envelope | [-53.5, -3.0, -33.3, 31.8, 9.3, 9.4] |
| Vol_Battery | Foam_Proto_2p0 | 3966.82 | pocket-envelope | [-51.7, -5.3, -31.7, 16.7, 9.4, 11.3] |
| Vol_J6_CarrierTab | PCB:CarrierBoard | 18.901 | same-board | [8.3, 18.7, -35.3, -34.0, 9.94, 11.45] |
| Vol_CamFPC | PCB:CarrierBoard | 2.114 | same-board | [29.0, 43.0, 10.4, 10.5, 9.94, 11.45] |
| Vol_J3_FH12_22 | PCB:J3 | 46.63 | same-part | [11.64, 25.02, 20.5, 23.5, 11.69, 13.54] |
| Vol_J4_FH12_22 | PCB:J4 | 39.34 | same-part | [29.32, 42.69, 6.3, 8.85, 11.69, 13.54] |
| Vol_J11_FH12_16 | PCB:J11 | 36.203 | same-part | [13.82, 24.19, 30.8, 33.8, 11.69, 13.54] |
| Vol_LTE_EC25_Shield | Vol_LTE_U1_Courtyard | 52.7 | same-part | [-51.3, -20.3, -22.5, 11.5, 12.2, 12.25] |
| Vol_J14_FH12_22_Courtyard | PCB:J14 | 46.63 | same-part | [-0.41, 2.6, -13.18, 0.19, 11.69, 13.54] |
| Vol_Display | Vol_LTE_SIM_LidSwing | 167.648 | service(lid swing needs bezel+display off) | [-17.75, -5.35, -31.6, -29.0, 16.8, 22.0] |

## Clearances < 1.0 mm

| A | B | gap mm |
|---|---|---|
| LTE_Daughterboard_PCB | Al_Unibody | 0.0 |
| LTE_Daughterboard_PCB | Vol_LTE_EC25_Shield | 0.0 |
| LTE_Daughterboard_PCB | Vol_LTE_U1_Courtyard | 0.0 |
| LTE_Daughterboard_PCB | Vol_LTE_UFL_GNSS | 0.0 |
| LTE_Daughterboard_PCB | Vol_LTE_UFL_Main | 0.0 |
| LTE_Daughterboard_PCB | Vol_LTE_NanoSIM_Hinged | 0.0 |
| LTE_Daughterboard_PCB | Vol_LTE_DB_Conn_FH12_22 | 0.0 |
| LTE_Daughterboard_PCB | Foam_Prod_0p5 | 0.0 |
| LTE_Daughterboard_PCB | Foam_Proto_2p0 | 0.0 |
| Vol_LTE_EC25_Shield | Vol_LTE_U1_Courtyard | 0.0 |
| Vol_LTE_EC25_Shield | ThermalPad_Shield_0p5 | 0.0 |
| Vol_LTE_UFL_GNSS | Coax_GNSS | 0.0 |
| Vol_LTE_UFL_Main | Coax_Main | 0.0 |
| Vol_LTE_NanoSIM_Hinged | Vol_LTE_SIM_LidSwing | 0.0 |
| Vol_LTE_SIM_LidSwing | Vol_Display | 0.0 |
| Vol_LTE_DB_Conn_FH12_22 | LTE_Flex_22P | 0.0 |
| Vol_J14_FH12_22_Courtyard | LTE_Flex_22P | 0.0 |
| Vol_J14_FH12_22_Courtyard | PCB:J14 | 0.0 |
| LTE_Flex_22P | PCB:J14 | 0.0 |
| Liner_PET_Prod | Vol_Battery | 0.0 |
| Liner_PET_Prod | Vol_Cell_Prod_62 | 0.0 |
| Liner_PET_Prod | Vol_Leads_ProtoAkyga | 0.0 |
| Liner_PET_Prod | Foam_Prod_0p5 | 0.0 |
| Liner_PET_Prod | Foam_Proto_2p0 | 0.0 |
| Foam_Prod_0p5 | Vol_Battery | 0.0 |
| Foam_Prod_0p5 | Foam_Proto_2p0 | 0.0 |
| Liner_PET_Proto | Vol_Battery | 0.0 |
| Liner_PET_Proto | Vol_Cell_Prod_62 | 0.0 |
| Liner_PET_Proto | Vol_Cell_Proto_Akyga | 0.0 |
| Liner_PET_Proto | Foam_Proto_2p0 | 0.0 |
| Foam_Proto_2p0 | Vol_Battery | 0.0 |
| Foam_Proto_2p0 | Vol_Cell_Prod_62 | 0.0 |
| ThermalPad_Shield_0p5 | HeatSpreader_Cu_0p5 | 0.0 |
| HeatSpreader_Cu_0p5 | Al_Unibody | 0.0 |
| HeatSpreader_Cu_0p5 | ThermalPad_Post_0p3 | 0.0 |
| ThermalPad_Post_0p3 | Al_Unibody | 0.0 |
| RFWindow_LTE_Main_L_PC | Al_Unibody | 0.0 |
| RFWindow_GNSS_TL_PC | Al_Unibody | 0.0 |
| Vol_Ant_LTE_Main_FPC_40x15 | Vol_Ant_LTE_Main_Keepout | 0.0 |
| Vol_Ant_LTE_Main_FPC_40x15 | Coax_Main | 0.0 |
| Vol_Ant_LTE_Main_Keepout | Coax_Main | 0.0 |
| Vol_Ant_GNSS_Envelope | Vol_Ant_GNSS_PatchOpt_Envelope | 0.0 |
| Vol_Ant_GNSS_Envelope | Vol_Ant_GNSS_Keepout | 0.0 |
| Vol_Ant_GNSS_Keepout | Vol_Ant_GNSS_PatchOpt_Envelope | 0.0 |
| Vol_Ant_GNSS_Keepout | Coax_GNSS | 0.0 |
| Vol_Pigtail | Vol_UFL | 0.0 |
| Vol_Pigtail | Vol_Antenna_FPC | 0.0 |
| Vol_Pigtail | Vol_Antenna_Keepout | 0.0 |
| RFWindow_LTE_Main_L_PC | Vol_Ant_LTE_Main_FPC_40x15 | 0.013 |
| RFWindow_GNSS_TL_PC | Vol_Ant_GNSS_Envelope | 0.013 |
| RFWindow_GNSS_TL_PC | Vol_Ant_GNSS_PatchOpt_Envelope | 0.013 |
| Vol_Ant_LTE_Main_FPC_40x15 | Al_Unibody | 0.039 |
| Vol_Ant_GNSS_Envelope | Al_Unibody | 0.039 |
| Vol_Ant_GNSS_PatchOpt_Envelope | Al_Unibody | 0.039 |
| LTE_Daughterboard_PCB | Bezel_DisplayFrame_PC | 0.05 |
| Vol_Ant_GNSS_Envelope | Coax_GNSS | 0.05 |
| Vol_Ant_GNSS_PatchOpt_Envelope | Coax_GNSS | 0.05 |
| Vol_Ant_LTE_Main_Keepout | Al_Unibody | 0.058 |
| Vol_J14_FH12_22_Courtyard | PCB:CarrierBoard | 0.09 |
| LTE_Daughterboard_PCB | Vol_Battery | 0.1 |
| LTE_Daughterboard_PCB | LTE_Flex_22P | 0.1 |
| Vol_LTE_UFL_Main | Coax_GNSS | 0.1 |
| Foam_Prod_0p5 | Vol_Cell_Prod_62 | 0.1 |
| Foam_Proto_2p0 | Vol_Cell_Proto_Akyga | 0.1 |
| HeatSpreader_Cu_0p5 | Bezel_DisplayFrame_PC | 0.1 |
| Coax_GNSS | SideKey_Flex | 0.15 |
| Vol_LTE_EC25_Shield | HeatSpreader_Cu_0p5 | 0.2 |
| RFWindow_LTE_Main_L_PC | Vol_Ant_LTE_Main_Keepout | 0.2 |
| Vol_LTE_U1_Courtyard | Vol_LTE_UFL_Main | 0.25 |
| Vol_LTE_EC25_Shield | Bezel_DisplayFrame_PC | 0.3 |
| Liner_PET_Prod | Al_Unibody | 0.3 |
| Liner_PET_Prod | Vol_Leads_Prod62 | 0.3 |
| Liner_PET_Proto | Al_Unibody | 0.3 |
| RFWindow_LTE_Main_L_PC | Coax_Main | 0.3 |
| Vol_Ant_LTE_Main_Keepout | Vol_NTC_Case | 0.3 |
| Coax_Main | Al_Unibody | 0.3 |
| HeatSpreader_Cu_0p5 | Vol_Display | 0.4 |
| Vol_J14_FH12_22_Courtyard | PCB:C61 | 0.417 |
| LTE_Daughterboard_PCB | Liner_PET_Prod | 0.5 |
| Vol_Ant_LTE_Main_Keepout | Bezel_DisplayFrame_PC | 0.5 |
| Vol_Ant_GNSS_Keepout | Al_Unibody | 0.5 |
| ThermalPad_Shield_0p5 | Bezel_DisplayFrame_PC | 0.55 |
| LTE_Daughterboard_PCB | Vol_J7_Housing205341 | 0.56 |
| Vol_Pigtail | Al_Unibody | 0.566 |
| Vol_Ant_GNSS_Keepout | Bezel_DisplayFrame_PC | 0.583 |
| LTE_Daughterboard_PCB | Vol_Speaker | 0.6 |
| LTE_Daughterboard_PCB | Vol_Cell_Prod_62 | 0.6 |
| HeatSpreader_Cu_0p5 | Vol_Speaker | 0.6 |
| ThermalPad_Post_0p3 | Bezel_DisplayFrame_PC | 0.6 |
| ThermalPad_Post_0p3 | Vol_Speaker | 0.6 |
| Liner_PET_Proto | Vol_Leads_Prod62 | 0.622 |
| Liner_PET_Prod | Vol_NTC_Rise | 0.65 |
| Liner_PET_Proto | Vol_NTC_Rise | 0.65 |
| Vol_J14_FH12_22_Courtyard | PCB:R56 | 0.668 |
| Liner_PET_Proto | Vol_Leads_ProtoAkyga | 0.676 |
| Liner_PET_Prod | Vol_J7_Housing205341 | 0.7 |
| Vol_Ant_LTE_Main_Keepout | Coax_GNSS | 0.7 |
| Coax_Main | Coax_GNSS | 0.7 |
| Vol_J14_FH12_22_Courtyard | PCB:R57 | 0.705 |
| Vol_LTE_EC25_Shield | Foam_Prod_0p5 | 0.8 |
| Vol_LTE_EC25_Shield | Foam_Proto_2p0 | 0.8 |
| Vol_LTE_U1_Courtyard | Foam_Prod_0p5 | 0.8 |
| Vol_LTE_U1_Courtyard | Foam_Proto_2p0 | 0.8 |
| Vol_LTE_UFL_GNSS | Foam_Prod_0p5 | 0.8 |
| Vol_LTE_UFL_GNSS | Foam_Proto_2p0 | 0.8 |
| Vol_LTE_UFL_Main | Foam_Prod_0p5 | 0.8 |
| Vol_LTE_UFL_Main | Foam_Proto_2p0 | 0.8 |
| Vol_LTE_NanoSIM_Hinged | Foam_Prod_0p5 | 0.8 |
| Vol_LTE_NanoSIM_Hinged | Foam_Proto_2p0 | 0.8 |
| Vol_LTE_SIM_LidSwing | Bezel_DisplayFrame_PC | 0.8 |
| Vol_LTE_DB_Conn_FH12_22 | Foam_Prod_0p5 | 0.8 |
| Vol_LTE_DB_Conn_FH12_22 | Foam_Proto_2p0 | 0.8 |
| Vol_Ant_GNSS_Keepout | SideKey_Flex | 0.8 |
| Vol_LTE_U1_Courtyard | Vol_Speaker | 0.85 |
| LTE_Flex_22P | PCB:CarrierBoard | 0.85 |
| Foam_Prod_0p5 | Bezel_DisplayFrame_PC | 0.85 |
| Foam_Proto_2p0 | Bezel_DisplayFrame_PC | 0.85 |
| Foam_Prod_0p5 | Vol_J7_Housing205341 | 0.883 |
| Foam_Proto_2p0 | Vol_J7_Housing205341 | 0.883 |
| Vol_J14_FH12_22_Courtyard | PCB:C16 | 0.895 |
| Vol_LTE_EC25_Shield | Vol_Battery | 0.9 |
| Vol_LTE_EC25_Shield | Vol_LTE_UFL_Main | 0.9 |
| Vol_LTE_U1_Courtyard | Vol_Battery | 0.9 |
| Vol_LTE_UFL_GNSS | Vol_Battery | 0.9 |
| Vol_LTE_UFL_Main | Vol_Battery | 0.9 |
| Vol_LTE_NanoSIM_Hinged | Vol_Battery | 0.9 |
| Vol_LTE_DB_Conn_FH12_22 | Vol_Battery | 0.9 |
| LTE_Flex_22P | Foam_Prod_0p5 | 0.9 |
| LTE_Flex_22P | Foam_Proto_2p0 | 0.9 |
| ThermalPad_Shield_0p5 | Vol_Display | 0.9 |
| Vol_Pigtail | RFWindow_PC | 0.9 |
| Vol_J14_FH12_22_Courtyard | PCB:C62 | 0.916 |
