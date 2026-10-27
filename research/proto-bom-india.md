# PocketMate: prototype BOM, qty 1, Indian stockists (v1, 2026-10-27, 22:15 IST)

**Scope.** This covers every line of `research/bom.md` §3, the LTE daughterboard (`hardware/kicad-lte/kicad-lte_BOM.csv`), and carrier parts that are already fixed in `hardware/power-config.md`, `cm5-config.md` and `PocketMate.net`. All prices and stock figures were read on 2026-10-27 between about 19:00 and 22:15 IST. Nothing has been ordered.

**GST basis.**
- **incl.** means the page shows GST-inclusive pricing (Robocraze "Incl. GST"; Evelta inc/ex both shown; Syntronix; Robu).
- **ex.** means element14 India, Mouser India or LionCircuits list prices. These show pre-tax unit prices, so add 18 % IGST at checkout. **VERIFY** at the cart.
- **?** means Silverline: the store renders both "Incl. GST" and "+ GST" labels, so check at the cart.

**Link check.**
- ✅ means the page was fetched and showed stock today.
- ◐ means the page resolves and shows schema `InStock`, but no live count was readable. LionCircuits is an aggregator with 7–10 day dispatch, so treat its stock as **VERIFY**.
- ⚠ means the figure comes only from a search-index snapshot, because the site blocks the fetcher (Mouser.in, DigiKey.in and Robu return 403; IndiaMART returns 429).

---

## 0. FOR SCHEMATIC: substitutions that touch the schematic or footprint
| # | Line | Designed part | Prototype part (why) | Schematic change? | Footprint change? | Action |
|---|---|---|---|---|---|---|
| S1 | LTE module U1 | EC25-E (EC25EFA-512-STD) | **EC200U-CN (EC200UCNAA)**. No verified qty-1 EC25-E stock in India today: Rhydolabz is out of stock, the Evelta page is 404, and LionCircuits is out of stock. | **Yes, pin-function deltas.** The LTE board symbol is already dual-labelled `EC25-E / EC200U-CN`. Re-check these pins against the EC200U HW design guide: USB_VBUS, PWRKEY timing, STATUS, RI, AP_READY, W_DISABLE#, and **J3 = DIV (EC25) vs BT/Wi-Fi-scan (EC200U)**. EC200U is Cat-1 (10/5 Mbps). | No. Same `Quectel_EC25_EC200U_LGA-144_32x29mm`. **VERIFY** EC200U pads that EC25 leaves NC. | Keep the dual footprint. If Voltiro confirms EC25EFA stock (see §2), fit EC25-E instead |
| S2 | CM5 | CM5104032 (4 GB / 32 GB) | **CM5108032** (8 GB / 32 GB). CM5104032 shows `available=false` at Silverline. | No | No | none. +₹4,900 |
| S3 | Display | Ronbo MPI4303 with a custom 22-pin tail | **Waveshare 4.3" DSI (Rev 2.2+)** plus the official 22p→15p Pi 5 display cable. Ronbo has no Indian stock. | No. J3 is unchanged (cm5-config.md §3 already specifies this panel and cable) | No | Bench and fit only. It does not fit the enclosure (the driver PCB is on the back). See §3 |
| S4 | Camera | HZ-OV5647AF with a custom 22-pin tail | **OV5647 5 MP fixed-focus module, 15-pin**, plus a 22p→15p cable. | No. J4 is unchanged. `dtoverlay=ov5647`; no AF/VCM. | No | Firmware: overlay only |
| S5 | Battery | LP705060 custom (PCM + 10k B3435 NTC, Pico-Lock 5-pin) | **Bench supply** for LTE bring-up, or an out-of-envelope **25C RC LiPo + external 103AT-2 NTC + BQ29700 PCM** (§4) | No. J7 pinout is kept: 1-2 VBAT, 3-4 BAT_N, 5 CHG_TS. | No. A pigtail is made to the 205338 mate. | Harness only |
| S6 (alt only) | Fuel gauge | MAX17055**EWL+T** (WLP-9) | **Fit the exact part** (LionCircuits). The only element14 stock is MAX17055**ETB+T** (TDFN-10). | If ETB+T is used: pin numbers change | **Yes, WLP-9 → TDFN-10** | Avoid unless LionCircuits fails |
| S7 (alt only) | CM5 B2B ×2 | Amphenol 10164227-1001A1RLF | Exact part at LionCircuits (◐). The fallback is **Hirose DF40C-100DS-0.4V(51)**, element14, 21,487 in stock. It is the native Hirose mate of the CM5's DF40 plugs. | No | **VERIFY** the land pattern (same 0.4 mm 2×50 family, 1.5 mm stack) | Only if Amphenol slips |
| S8 (alt only) | Speaker | CMS-15118D-L100 | Exact part at LionCircuits. Fallbacks at element14: CMS-15118C-SP (15×11×4.2) or CMS-151125-078S-67 (15×11×2.5) | Wiring/terminal type | **Yes** (pads/spring vs wire) | Only if needed |
| S9 (alt only) | Charger | BQ25895RTWR | Mouser India (⚠). The element14 alternative is BQ25890RTWT. | BQ25890 is the same RTW-24 family. **VERIFY the pin-for-pin match.** BQ25896 is **not** pin-compatible (power-config.md). | VERIFY | Only if Mouser fails |
| — | Haptic driver | DRV2605LDGSR | DGSR (LionCircuits) or **DGST** (element14). These differ only in reel size. | No | No | — |

**Net effect for Schematic with the primary choices below: only S1 (EC200U pin deltas) needs a schematic review.** S2–S5 are cable, firmware or harness changes. S6–S9 apply only if the exact part fails to arrive.

---

## 1. Carrier lines (bom.md §3 + fixed carrier parts)
| # | Ref / line | Part (fit this) | Source (qty 1) | INR qty 1 | GST | Stock / ship | Substitute |
|---|---|---|---|---|---|---|---|
| 1 | Compute | **CM5108032** (8 GB/32 GB/Wi-Fi) | [Silverline](https://www.silverlineelectronics.in/products/raspberry-pi-compute-module-5-8gb-ram-32gb-emmc-2-4-5-0ghz-wi-fi-bluetooth-5-0-cm5108032-s) | **19,900** | ? | ✅ `available=true` (Shopify) | CM5104032 ₹15,000: **sold out** ([page](https://www.silverlineelectronics.in/products/raspberry-pi-official-compute-module-5-4gb-ram-with-32gb-emmc-2-4-5-0ghz-wi-fi-bluetooth-5)). CM5102032 ₹9,690 and CM5104016 ₹6,000 are both sold out |
| 2 | J1/J2 B2B ×2 | Amphenol 10164227-1001A1RLF | [LionCircuits](https://www.lioncircuits.com/parts/10164227-1001A1RLF) | 220.02 ×2 = **440.04** | ex. | ◐ InStock, 7–10 days | element14 order code 4137104 ₹192.24: **no stock** (from 12/1/2027). Hirose DF40C-100DS-0.4V(51), element14 [2427679](https://in.element14.com/search?st=DF40C-100DS-0.4V%2851%29), ₹239.05, ✅ 21,487, 3–5 days (S7) |
| 3 | Display (J3) | Waveshare 4.3" DSI capacitive 800×480 (**Rev 2.2+**, cm5-config.md) | [Robocraze](https://robocraze.com/products/waveshare-4-3inch-dsi-lcd-capacitive-touch-display-800-480-for-raspberry-pi) | **3,525** | incl. | ✅ available | Ronbo MPI4303 sample $18.50 (bom.md), import only (§3) |
| 3a | Display cable | Official Pi 5 display FPC 22p→15p, 200 mm | [Silverline](https://www.silverlineelectronics.in/products/raspberry-pi-5-display-official-fpc-cable-200mm) | **82** | ? | ✅ available | — |
| 4 | Camera (J4) | "Raspberry Pi 5MP Camera Module with Cable" (OV5647 class, fixed focus; **VERIFY the sensor** on the listing) | [Robocraze](https://robocraze.com/products/raspberry-pi-5mp-camera-module) | **295** | incl. | ✅ available | Camera Module 3 (IMX708 AF) ₹2,600, [Silverline](https://www.silverlineelectronics.in/products/test-3), ✅. This matches the current cm5-config.md overlay. Waveshare RPi Camera (M) ₹2,619 (fisheye) |
| 4a | Camera cable | 22p→15p (the same official Pi 5 FPC as 3a; the camera and display cables share this spec, **VERIFY** contact side) | Silverline (as 3a) | **82** | ? | ✅ | — |
| 5 | Mics ×2 | TDK ICS-43434 (NRND) | [element14 2911502](https://in.element14.com/search?st=ICS-43434) | 316.90 ×2 = **633.80** | ex. | List view: stock not shown (**VERIFY**) | [LionCircuits](https://www.lioncircuits.com/parts/ICS-43434) ₹511.48 ◐ |
| 6 | Amp | MAX98357AETE+T | [element14 2949165](https://in.element14.com/analog-devices/max98357aete-t/audio-power-amp-d-40-to-85deg/dp/2949165) | **390.67** | ex. | ✅ 23,382, 4–6 days (UK) | — |
| 7 | Speaker (J5) | Same Sky CMS-15118D-L100 | [LionCircuits](https://www.lioncircuits.com/parts/CMS-15118D-L100) | **594.50** | ex. | ◐ InStock, 7–10 days | element14 CMS-15118C-SP 4814260 ₹346.81; CMS-151125-078S-67 4893088 ₹239.52 (S8) |
| 8 | Charger | TI BQ25895RTWR | [Mouser India](https://www.mouser.in/c/semiconductors/power-management-ics/battery-management/?m=Texas+Instruments&series=BQ25895) | **294.68** | ex. | ⚠ 5,069 (search snapshot; Mouser blocks the fetch) | [LionCircuits](https://www.lioncircuits.com/parts/BQ25895RTWR) ₹428.22 ◐. element14 BQ25890RTWT 3008742 ₹497.76, 14 in stock (S9) |
| 9 | Boost | TI TPS61088RHLR | [Evelta](https://evelta.com/tps61088rhlr-2-7v-12v-10a-high-efficiency-boost-converter-ic-vqfn-20/) | **112.10** (95.00 ex.) | incl. | ✅ 20 in stock, ships in 24 h (Mumbai) | — |
| 10 | Gauge | ADI MAX17055EWL+T | [LionCircuits](https://www.lioncircuits.com/parts/MAX17055EWL%2BT) | **469.55** | ex. | ◐ InStock, 7–10 days | element14 MAX17055ETB+T 2857995 ₹445.27 (**footprint change**, S6) |
| 11 | PD sink | ST STUSB4500QTR | [element14 2980889](https://in.element14.com/search?st=STUSB4500QTR) | **226.95** | ex. | ✅ 5,554, 4–6 days | — |
| 12 | AON MCU | ST STM32U031K8U6 | [element14 4355939](https://in.element14.com/search?st=STM32U031K8U6) | **309.41** | ex. | ✅ **1 in stock**, 4–6 days. Order today. | Same footprint: STM32U031K6U6/K4U6 (less flash), **VERIFY** stock |
| 13 | Haptic driver | TI DRV2605LDGSR | [LionCircuits](https://www.lioncircuits.com/parts/DRV2605LDGSR) | **286.77** | ex. | ◐ InStock, 7–10 days | element14 DRV2605LDGST 3123356 ₹359.23 (reel variant only) |
| 14 | LRA | Vybronics VG0832012 | [LionCircuits](https://www.lioncircuits.com/parts/VG0832012) | **438.70** | ex. | ◐ InStock, 7–10 days | Not at element14 IN or Evelta |
| 15 | J7 cell header | Molex 205338-0005 | [element14 3470893](https://in.element14.com/search?st=205338-0005) | **265.61** | ex. | ✅ 5,894 | The mating 5-way Pico-Lock housing and crimps for the pigtail are **TBC** (not priced) |
| 16 | F1 LTE fuse | Littelfuse 0466004.NR (4 A, 1206) | [LionCircuits](https://www.lioncircuits.com/parts/0466004.NR) | **171.18** | ex. | ◐ | — |
| 17 | USB-C ESD ×2 | ST USBLC6-2SC6 (block-diagram: ×2) | [LionCircuits](https://www.lioncircuits.com/parts/USBLC6-2SC6) | 66.11 ×2 = **132.22** | ex. | ◐ | — |
| 18 | AON LDO | TI TPS7A0233 (block-diagram) | [LionCircuits TPS7A0233PDQNR](https://www.lioncircuits.com/parts/TPS7A0233PDQNR) | **101.19** | ex. | ◐ | **VERIFY** the package against the carrier footprint (DQN X2SON vs DBV SOT-23-5) |
| 19 | J3, J4, J14 FPC ×3 | Hirose FH12-22S-0.5SH(55) | [LionCircuits](https://www.lioncircuits.com/parts/FH12-22S-0.5SH%2855%29) | 327.55 ×3 = **982.65** | ex. | ◐ InStock, 7–10 days | Not at element14 IN (only FH12-20S ₹143.08 / FH12-24S, which are **not** drop-in) |
| 20 | Passives, buttons, misc | bom.md "EST $6" (excluding the connectors above) | — | **528 EST** ($6 × ₹88) | — | — | Mostly Evelta 0402/0603 at ₹0.70–1.30 each ex. |
| 21 | Thermal pad + spreader | bom.md "EST $2" | — | **176 EST** | — | — | — |
| 22 | PCB + assembly (carrier 4-layer + LTE 0.8 mm 4-layer) | — | RFQ (e.g. LionCircuits, PCB Power) | **RFQ, not in total** | — | — | The bom.md $12 is a 1k-volume EST and does not apply at qty 1 |
| 23 | Enclosure (CNC Al unibody + PC parts) | — | RFQ to a CNC shop | **RFQ, not in total** | — | — | The bom.md $9 is a moulded-volume EST |
| 24 | Cell | LP705060 custom | see §4 | in the §4 subtotal | | | |

**Carrier subtotal (lines 1–21): ₹29,734.02**

## 2. 4G block (LTE daughterboard, `kicad-lte_BOM.csv`)
| Ref | Part | Source (qty 1) | INR qty 1 | GST | Stock / ship | Substitute / note |
|---|---|---|---|---|---|---|
| U1 | **Quectel EC200U-CN** (LGA-144, Cat-1, LTE-FDD B1/3/5/8 + TDD B34/38/39/40/41; [Quectel EC200U spec V1.8](https://developer.quectel.com/en/wp-content/uploads/sites/2/2024/11/Quectel_EC200U_Series_LTE_Standard_Module_Specification_V1.8.pdf)), which covers India B1/3/5/8/40/41 | [Syntronix](https://syntronix.in/product/quectel-ec200u-cn-lte-cat-1-4g-lte-module/) | **590** | incl. | ✅ schema InStock | Evelta ₹1,156.40 incl.: **sold out**. **Preferred EC25-E:** [Voltiro via IndiaMART, EC25EFA-512-STD](https://www.indiamart.com/proddetail/ec25-efa-512-std-quectel-module-2854133916888.html), ₹1,670, "In Stock, ships from Noida". This is ⚠ from the search index only (IndiaMART returns 429), so **phone them to confirm the -512-STD LGA and a genuine source**. Rhydolabz EC25-E ₹2,499 ex.: **out of stock**. LionCircuits EC25EFA: out of stock |
| U2 | TI TPS22965DSGR | [element14 3008911](https://in.element14.com/search?st=TPS22965DSGR) | **84.79** | ex. | ✅ 6,745 | — |
| J1 | Hirose FH12-22S-0.5SH(55) | LionCircuits (as line 19) | **327.55** | ex. | ◐ | — |
| (link) | 22-way 0.5 mm FFC, J1↔J14, free span 4.05 mm (release_v5) | — | **TBC** | | | A stock FFC this short is unlikely. Order a custom length or a 30–50 mm Type-A/Type-B (contact side **VERIFY**) for bench |
| J2, J4 | Hirose U.FL-R-SMT-1(10) ×2 (Main, GNSS; **J3 DIV not fitted**, release_v5) | [LionCircuits](https://www.lioncircuits.com/parts/U.FL-R-SMT-1%2810%29) | 212.84 ×2 = **425.68** | ex. | ◐ | element14 1688077 ₹62.09 at **MOQ 10** (₹620.90) |
| J5 | Same Sky (CUI) NSIM-2-C (BOM part) | [LionCircuits](https://www.lioncircuits.com/parts/NSIM-2-C) | **90.48** | ex. | ◐ | element14 has it only as a full reel (1,500). GCT SIM8060-6-1-14-00-A, element14 3221422, ₹140.22, ✅ 9,429. This is a **different footprint**, so don't swap it in |
| U3, U5 | TI TPD4E05U06DQAR ×2 | [LionCircuits](https://www.lioncircuits.com/parts/TPD4E05U06DQAR) | 93.92 ×2 = **187.84** | ex. | ◐ | — |
| Q1–Q6 | Diodes DMG1012T-7 ×6 | [LionCircuits](https://www.lioncircuits.com/parts/DMG1012T-7) | 18.22 ×6 = **109.32** | ex. | ◐ | — |
| C4, C5 | KEMET T520B107M006ATE070 ×2 | [LionCircuits](https://www.lioncircuits.com/parts/T520B107M006ATE070) | 119.92 ×2 = **239.84** | ex. | ◐ | — |
| D1 | Willsemi WS4.5D3HV | — | **TBC** (in passives EST) | | not searched | — |
| ANT main | Abracon **AANI-FB-0173-1** (40×15×0.2, 698–960 / 1710–2690 MHz, u.FL, 66 mm Ø1.13) | [element14 4751751](https://in.element14.com/search?st=AANI-FB-0173) | **278.14** | ex. | ✅ 910, 4–6 days | LionCircuits ₹362.46 ◐ |
| ANT GNSS | Johanson **1575AT43A0040001E** chip (7.0×2.0×0.8) on a 9.5×12.5 carrier with a u.FL pigtail | [element14 4397877](https://in.element14.com/search?st=1575AT43A0040) | **104.86** | ex. | ✅ 963, 4–6 days | Abracon APAKN0904-S1575-T patch: [LionCircuits](https://www.lioncircuits.com/parts/APAKN0904-S1575-T) ₹339.02 ◐. The carrier PCB and pigtail are **TBC** |
| ANT div | none (release_v5 PM decision) | — | 0 | | | — |

**4G subtotal (priced lines): ₹2,438.50** (with EC200U-CN; **+₹1,080** if the Voltiro EC25-E at ₹1,670 is confirmed)

## 3. Prototype workarounds for custom items
- **Display tail (Ronbo MPI4303 with a custom 22-pin tail):**
  - Bring up on the **Waveshare 4.3" DSI** (same 800×480 class, 15-pin 1.0 mm on the panel) with the official 22p→15p cable into J3. This is exactly the configuration in cm5-config.md, so there is no schematic change.
  - It does not fit the 125×75×22 shell (the driver PCB is on the back), so run it on the bench outside the enclosure.
  - For an in-enclosure fit, order a Ronbo **sample with its stock tail** ($18.50, bom.md) and bridge it with a short 0.5 mm FFC adapter. Its tail pinout must match J3's 22-pin DSI map (**VERIFY**: Ronbo drawing).
- **Camera tail (HZ-OV5647AF with a custom 22-pin tail):**
  - Use a stock 15-pin OV5647 module plus the 22p→15p cable into J4. The sensor driver is the same, but there is **no autofocus**.
  - If you want IMX708 AF instead, fit Camera Module 3 (₹2,600) and keep the current overlay.
  - Custom tail length and fold are then only a mechanical item for EVT.
- **Custom cell (LP705060 with PCM, B3435 NTC and Pico-Lock):** see §4.
  - Without LTE, any ≥3000 mAh 1S pack with PCM can be pigtailed to a 205338 mate. Keep the governor cap of 2.5 A (power-config.md item 3).
  - The Akyga LP655063 named in power-config.md is a Polish (Ropla) item and was **not found in India**.

## 4. (B) LTE prototype battery
**Requirement:** 1S LiPo, ≥3C (≥9 A continuous), about 3000 mAh, ≤8.5 × 50.5 × 62 mm, NTC, qty 1 in India.

**Result: no pack meeting all five was found in Indian stock.** RC/drone 1S packs of 3000 mAh class at ≥25C are all long and thin. Packs that fit the envelope state no C-rate.

| Candidate | Size (mm) | C / A | NTC / PCM | INR | Source | Verdict |
|---|---|---|---|---|---|---|
| Robu **Pro-Range 3.7 V 3300 mAh 25C 1S** | 133 × 43 × 8 | 25C (≈82 A, maker claim) | none / none | **1,218** incl. | [Robu](https://robu.in/product/pro-range-3-7v-3300mah-25c-1s/), ⚠ snippet: "low stock" (Robu blocks the fetcher) | Electrically OK. **Out of envelope (133 mm)**, so use it tethered outside the shell |
| Orange 1S 2500 mAh 25C | 135 × 45 × 8 | 25C | none | not captured | Robu (snippet) | Out of envelope |
| Orange 1S 2200 mAh 25C | 99 × 40 × 5 | 25C | none | not captured | Robu (snippet) | Out of envelope (99 mm) |
| Orange 1S 1500 mAh 25C | 70 × 35 × 10 | 25C | none | not captured | Robu (snippet) | Too thick and long |
| ComponentsTree KP-505060 3000 mAh | 5 × 50 × 60 (as listed) | **not stated** | not stated | 279 | ComponentsTree (snippet) | Fits, but the C-rate is unknown, and 3000 mAh in 5 mm is implausible. **Do not use for LTE** |

**Recommended path:**
1. Use the **bench supply** (below) for LTE bring-up, RF and power-budget tests.
2. Use the **Pro-Range 3300 25C, tethered**, for untethered field and roaming tests.
3. The production 2C/3C-peak cell stays with the battery RFQ.

**NTC / PCM workaround for an RC LiPo:**
- **NTC:** Semitec **103AT-2** (10 kΩ, B 3435 K, the thermistor TI recommends in SLUSC88 line 271). Get it from [LionCircuits](https://www.lioncircuits.com/parts/103AT-2): **₹73.92** ex., ◐ InStock.
  - Alternative: Vishay NTCLE413E2103F102L (3435 K), [LionCircuits](https://www.lioncircuits.com/parts/NTCLE413E2103F102L) ₹187.69.
  - Kapton-tape it to the cell face centre, wire it to **J7 pin 5 (CHG_TS) and pins 3/4 (BAT_N)**, and keep **RT1 5.23 k / RT2 30.1 k** (power-config.md, B3435 row: trips at 0.5 °C and 44.9 °C).
  - Evelta's MF52 10K is **3977 K**. With it, fit 4.42 k / 19.6 k (power-config.md B3950 row) or don't use it.
- **PCM:** [7Semi BQ29700D 1S Li-ion/LiPo protection module](https://evelta.com/7semi-bq29700d-battery-protection-module/), Evelta, **₹230.10** incl. (₹195 ex.), ✅ 15 in stock, ships in 24 h.
  - **Its continuous/OCD current rating is not stated**, because BQ29700 trips on FET V_DS.
  - **VERIFY ≥10 A on the bench before using it with LTE**, or swap its FETs.
  - The "18650 protection 12V/10A" boards (Evelta ₹364, Robocraze ₹50) are **3S**, not 1S, so don't use them. Robocraze "1S 3.7V 5A" (₹46) is under-rated.
  - A verified ≥10 A 1S PCM at qty 1 in India is **TBC**.
  - Fit an inline 10 A fuse (EST class; TBC) on the cell + lead in any case.
- Charge the RC pack only through the BQ25895 at **VREG 4.208 V** (≤4.24 V with LTE fitted). Do not use a hobby balance charger set to HV (4.35 V).

**Bench-supply option:**
- **Supply:** OWON **SPE3102** 30 V / 10 A programmable, **₹10,099** incl., [Robocraze](https://robocraze.com/products/owon-spe3102-30v-10a-programmable-dc-power-supply), ✅ available.
  - Remote sense is **not confirmed**: check the manual. If it has none, use the short-lead method below.
  - Alternative: SPE6103 60 V / 10 A, ₹12,915.
  - This is test equipment, so it is **not in the BOM total**.
- **Settings:**
  - Set **4.20 V**, with the current limit at 10 A. Use the 3.0–4.35 V range only for sweeps. **Never exceed 4.24 V** with an LTE board fitted (EC25 VBAT max 4.3 V; power-config.md). power-config.md's earlier "3.8 V" is a valid nominal point too.
  - Connect **+ to J7 pins 1+2 (VBAT) and − to J7 pins 3+4 (BAT_N)**, so the MAX17055 sense resistor still sees the current.
- **Leads and decoupling:**
  - Use ≤15 cm of ≥16 AWG twisted pair, soldered to a 205338 mate or to pads at J7.
  - Without remote sense, add about 2 × 470 µF low-ESR plus 100 µF at J7. The LTE peaks of 7.8–8.4 A (power-config.md v0.4) are faster than a lab supply's loop.
  - Measure VBAT at J7 with a scope during a TX burst and keep it ≥3.55 V (the LTE TX gate in power-config.md).
- **Emulate the NTC:** fit a **10 kΩ resistor from J7-5 to J7-3/4** (this reads as 25 °C). Otherwise TS is out of range and charging is suspended (SLUSC88 line 271: "Charge suspends when either TS pin is out of range").

**How the BQ25895 behaves without a real cell** (TI SLUSC88C, Oct 2022):
- **Supply only on BAT, no USB-C:**
  - POR occurs, and I²C becomes active once BAT > VBAT_UVLOZ (§8.2.1).
  - BAT > VBAT_DPLZ (2.35–2.7 V) turns on the BATFET to SYS (§8.2.2).
  - The BATFET over-current trip **IBAT(FET_OCP) = 9 A** (line 594) latches BATFET_DIS until VBUS returns.
  - LTE is fed **before** the BATFET (F1 → J14), so LTE peaks don't count toward this 9 A. Only SYS (CM5 and the rest) does.
- **USB-C plugged in while on the bench supply:**
  - The charger sees a "battery" at 4.20 V and tries to charge toward VREG 4.208 V.
  - A source-only lab supply can't sink current, so the node floats up to about VREG and the charger terminates (§8.2.7.3).
  - This is harmless at VREG 4.208 V, but for clean measurements **disable charging (CHG_CONFIG = 0)** or leave USB-C unplugged.
  - Expect the MAX17055 SOC to be meaningless.
- **USB-C only, no cell at all:**
  - "Instant-on works with no battery" (line 51). SYS is regulated from VBUS (VSYSMIN loop), so the CM5 can boot.
  - **LTE will not work**: LTE_VBAT is taken from the BAT node, which has no reservoir, and the charger's battery-detect cycling will brown out the module.
  - Use this mode only for non-LTE bring-up.

**Battery subtotal (Pro-Range + 103AT-2 + BQ29700D module): ₹1,522.02** (bench supply excluded)

## 5. Total
| Block | INR |
|---|---|
| Carrier (lines 1–21, incl. ₹704 EST) | 29,734.02 |
| 4G block (EC200U-CN) | 2,438.50 |
| LTE prototype battery kit | 1,522.02 |
| **Total, as listed (mixed GST basis)** | **₹34,398.54** |
| + 18 % GST on the ₹7,660.34 of ex-GST lines (element14/Mouser/LionCircuits) | +1,378.86 → **≈ ₹35,777 incl. GST** |
| If Silverline's ₹20,064 is also ex-GST | **≈ ₹39,389** (worst case) |
| If EC25-E (Voltiro ₹1,670) replaces EC200U-CN | +₹1,080 |
| CM5104032 instead of CM5108032 (if restocked) | −₹4,900 |
| **Not in total (RFQ/TBC):** PCB fab + assembly ×2 boards, CNC enclosure, J1–J14 FFC, J7 mating housing/crimps, GNSS carrier PCB/pigtail, D1, 10 A fuse, Ronbo sample import, shipping charges, bench supply (₹10,099) | — |

**Lead-time critical path:**
- LionCircuits lines take 7–10 days and element14 lines (UK stock) 4–6 days.
- Evelta, Robocraze and Silverline ship in about 1–3 days.
- **Order STM32U031K8U6 now (1 left at element14).**
