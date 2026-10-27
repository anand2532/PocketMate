# kicad-lte: PocketMate LTE daughterboard (Option D)

- `kicad-lte.kicad_pro` / `kicad-lte.kicad_pcb`: board stub, **4 copper layers, 0.8 mm**. The stackup is in Board Setup (JLC04081H-3313 class; confirm with the fab):
  - F.Mask 0.01
  - F.Cu 0.035
  - PP 3313 0.0994 (Er 4.1)
  - In1.Cu 0.0152
  - core 0.5008 (Er 4.6)
  - In2.Cu 0.0152
  - PP 3313 0.0994
  - B.Cu 0.035
  - B.Mask 0.01
  - ENIG finish
  - Suggested use: L2 is solid GND under the RF and USB. 50 ohm CPWG and 90 ohm USB on L1 over a 0.0994 dielectric; run `pocketmate/hardware/layout/fd_impedance.py` for the widths.
- Outline is 44 x 44 mm at mech X -52..-8, Y -30..14 (KiCad Y = -mech Y), inside the over-cell zone in `lte_placement_study.md`.
  - U1 is at mech (-33.75, -12.0). J1 (FH12-22S, mouth +X, toward carrier J14) is at (-13.0, -10.0).
  - Placeholder positions; no nets yet.
- `kicad-lte.pretty/`: the shared EC25/EC200U footprint, plus an EC200U-only variant. See `EC25_EC200U_pad_compat.md`.
- `tools/gen_fp.py` and `tools/make_pcb_stub.py` regenerate both.

## Link: carrier J14 <-> LTE J1 (22p 0.5 mm FFC, FH12-22S-0.5SH(55) both ends)
| Pin | Net (carrier) | Notes |
|---|---|---|
| 1-6 | VSYS | BQ25895 SYS; 6 x 0.5 A. LTE board load switch + 2x100 uF + 2x22 uF |
| 7-9, 12, 14, 22 | GND | 12 and 14 guard the USB pair |
| 10 / 11 | LTE_USB_DM / LTE_USB_DP | CM5 J2-136 / J2-134 (USB3-0 port's USB2 pair), 90 ohm diff |
| 13 | LTE_USB_VBUS | +5V_CM5 via R56 0R (EC200U needs >= 3.5 V) |
| 15 | LTE_PWR_EN | CM5 GPIO5 (J1-34), R57 100k pull-down: LTE load switch |
| 16 | LTE_PWRKEY | CM5 GPIO6 (J1-30) -> NMOS on LTE board |
| 17 | LTE_RESET | CM5 GPIO13 (J1-28) -> NMOS on LTE board |
| 18 | LTE_W_DISABLE_N | CM5 GPIO26 (J1-24) |
| 19 | LTE_STATUS | CM5 GPIO16 (J1-29) |
| 20 | LTE_RI | CM5 GPIO12 (J1-31) |
| 21 | LTE_AP_READY | CM5 GPIO25 (J1-41) |

Control signals are 3.3 V (CM5 bank) on the flex. The 1.8 V translation is on the LTE board. Pin n = pin n assumes a same-side-contact (Type A) FFC with both connectors facing the same way; if the cable is Type B, mirror J1 on the LTE board.
