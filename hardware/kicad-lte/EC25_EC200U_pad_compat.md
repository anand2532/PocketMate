# EC25 / EC200U-CN shared LGA-144 land pattern: pad check (2026-10-27)

Sources: Quectel EC25 Hardware Design V2.2 (§3.2, Fig.45 module bottom, Fig.46 recommended footprint) and EC200U Series Hardware Design V1.0 (§3.2, Fig.39/40). PDFs and renders are in `ref/`. The Quectel *EC200x&EC2x Compatible Design* note confirms the two modules share the package.

## Geometry (footprint `kicad-lte:Quectel_EC25_EC200U_LGA-144_32x29mm`)
- Bodies: EC25 is 32.0 x 29.0 mm and EC200U is 31.0 x 28.0 mm. With both bodies centred, **all 144 pad centres coincide**. Checks: LCC pitch 1.3 (6x1.3 + 1.8 gap + 12x1.3 per side, 19x1.3 per row, rows start 3.85 mm from the EC25 left edge = 3.35 from the EC200U left edge); signal LGA columns at x = -13.0 / -11.0 on a 2.0 pitch; GND LGA columns at 3.2/3.4/3.2/3.4/3.2 and rows at 4.8 pitch; centre cluster 4x3 at 1.6 pitch.
- LCC pads are 0.8 x 2.65 mm. The heel is flush with the module pad heel: |x| = 14.5 and |y| = 13.0 on both modules. The toe goes to |x| = 17.15 and |y| = 15.65. That gives EC200U its recommended 1.65 mm toe and EC25 1.15 mm (EC25 recommends 1.0).
- Signal LGA pads 117-140 are 1.1 x 1.1. GND LGA pads 85-112 are 2.0 x 3.0, with a pin-1 chamfer on pad 108.
- Courtyard is **35.3 x 32.3 mm** (+-17.65 x +-16.15 about the module centre). Quectel asks for about 3 mm to other parts for rework.
- 132 copper pads.

## EC200U-only pads: 73-84 (centre 4x3 cluster)
- EC25: these are RESERVED and "should not be designed in schematic and PCB decal … served as a keepout area" (HD V2.2 §3.2 note 9 and the Fig.46 keepout).
- EC200U: 73/74 LOUDSPK_P/N, 75/77 MIC_P/N, 78/79/80 KEYIN1/2/3, 83/84 KEYOUT0/1, 76 GND, 81/82 RESERVED.
- **Main footprint: pads 73-84 are NOT copper.** They are drawn on Dwgs.User and labelled "EC200U-only". A rule area on F.Cu and In1.Cu (cluster +0.5 mm) blocks tracks, vias, pads and pour.
- PocketMate uses none of the analog audio or keypad functions, so EC200U loses nothing. Its pad 76 GND just sits on mask.
- An EC200U-only variant, `..._EC200U-full` (144 pads, no keepout), is in the lib. **Do not fit an EC25 on it.**

## Shared pads whose function differs (same copper, schematic must suit both)
| Pad | EC25 | EC200U | Design rule for the shared board |
|---|---|---|---|
| 3 | RESERVED | SLEEP_IND (out) | NC |
| 35 | ANT_DIV (LTE Rx-div) | ANT_BT/WIFI_SCAN | Diversity feed through a 0R/pi-match. For EC200U, fit the match only if Wi-Fi scan is wanted |
| 37-40 | BT UART | SPI | NC |
| 43 | RESERVED | ADC2 | NC |
| 113/114 | RESERVED | KEYOUT2/3 | NC |
| 117-139 | WLAN SDIO / SGMII / COEX | LCD, SDIO2, WLAN ctl, AUX UART | NC |
| 128 | SGMII | USIM2_VDD (out) | NC |
| 140 | RESERVED | ISINK (current-sink input, 200 mA) | **NC**: never tie to a rail |
| 141/142 | RESERVED | I2C2 | NC |
| 143/144 | RESERVED | GRFC1/2 | NC |
| 13 | USIM_PRESENCE | USIM_DET | Same use |

## Electrical differences on pads we use
- **USB_VBUS (71):** EC25 needs 3.0-5.25 V, EC200U needs 3.5-5.25 V. It is fed from carrier +5V_CM5 via J14-13 and R56 0R, not from VSYS.
- **PWRKEY (21) / RESET_N (20):** EC25 is 0.8 V / 1.8 V domain, EC200U is VBAT domain. Drive both with an open-drain NMOS to GND only, never push-pull. This works on both modules.
- **STATUS (61):** EC25 is open drain, EC200U is push-pull. Pull it up to VDD_EXT (1.8 V, pad 7) with 10k-47k, then level-shift.
- **VDD_EXT (7):** 1.8 V, 50 mA on both. Use it as the module-side reference for translators.
- Same function and level on both: VBAT_BB 59/60, VBAT_RF 57/58 (3.3-4.3 V), USB_DP/DM 69/70, USIM 10/14-17, AP_READY 2, W_DISABLE# 4, RI 62, NET_STATUS 6, ANT_MAIN 49, ANT_GNSS 47, USB_BOOT 115, GND (EC200U adds 76).
