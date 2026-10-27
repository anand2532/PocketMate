# RFQ: Custom 1S Li-Po pouch cell for PocketMate

> **Scope (Rev D):** this RFQ is for the PRODUCTION custom cell only (≤8.5×50.5×62.0 mm incl. PCM, ≥3000 mAh rated / 3100 target, ≥2C continuous, 3C/10 s peak). The PROTOTYPE cell is the off-the-shelf Akyga LP655063 (3000 mAh, 1C / 3 A max, 65.5×51×7.0 mm max pack, 10k NTC beta unstated). It is not part of this RFQ. See components.md for it and its B3950 trip estimates ("Akyga LP655063 datasheet" section, about line 424–442).
**Issued by:** PocketMate hardware team (Anand Mohan Pandey) · **Date:** 2026-10-21 · **Rev:** D (staggered lead lengths, Enclosure v4_22c). Rev C was sent to iBorn, Grepow and THOR; Rev D goes as a follow-up
**Product:** PocketMate, a handheld personal AI companion (Raspberry Pi CM5). **Market:** India first (BIS mandatory), then global.

## 1. Mechanical
| Item | Requirement |
|---|---|
| Max envelope (finished pack incl. PCM, Kapton/tape, label) | **T ≤ 8.5 × W ≤ 50.5 × L ≤ 62.0 mm** (Rev C). Product pocket is 51.5 × 67 × 9.0 mm. **The ≥ 5 mm between the pack and the pocket end is reserved for the lead bend** |
| Measurement | Thickness at 300 gf, 25 °C, at 50% SOC or shipping SOC (state which). State tolerances |
| PCM location | Folded onto the **50 mm short edge**, inside the 62.0 mm length |
| Swelling | ≤ 8% thickness growth (≤ 9.0 mm absolute) after 500 cycles. ≤ 5% after 7 days at 60 °C storage at 100% SOC. Pack must never exceed 9.0 mm in any condition. Report your actual figures |
| Weight | Report |

## 2. Electrical (cell)
| Item | Requirement |
|---|---|
| Rated capacity | **≥ 3000 mAh minimum rated, target ≥ 3100 mAh** at **0.2C discharge to 3.0 V, 25 °C**, after standard charge (0.5C CC to 4.2 V, CV to 0.02C). Also report typical capacity, and capacity at 1C and 2C |
| Nominal / charge voltage | 3.7 V nominal. **4.20 V ± 0.03 V** charge |
| Discharge cut-off | 3.0 V (report if 2.75 V) |
| Continuous discharge | **≥ 2C continuous (≥ 6.0 A at 3.0 Ah; system need about 6.5 A, so state your figure) at 25 °C.** Report cell surface temperature rise at 2C |
| Peak discharge | **≥ 3C (≥ 9.0 A) for ≥ 10 s** (state your rating) |
| Max charge current | ≥ 1C. Our charger is **TI BQ25895, 3.0 A max CC**. Confirm 3 A charge (about 1.0C at 3.0 Ah) is acceptable at 10–45 °C, and state any JEITA current/voltage reductions you require |
| Internal resistance | Report AC IR (1 kHz) of cell and pack (≤ 60 mΩ pack target) |
| Cycle life | **≥ 500 cycles to ≥ 80%** at 0.5C/0.5C, 25 °C. Also report at 1C charge / 1C discharge |
| Temperatures | **Charge 0–45 °C. Discharge −20 to 60 °C.** Storage per your spec |
| Self-discharge / shipping SOC | Report. Shipping at 30–50% SOC per UN38.3 |

## 3. Protection circuit module (PCM)
| Item | Requirement |
|---|---|
| Overcharge (OVP) | 4.275–4.30 V detect, with release and delay stated |
| Over-discharge (UVP) | 2.5–2.8 V detect, with release and delay stated |
| Over-current (OCP) | **6–8 A discharge** (must not trip at 6.5 A continuous). State delay |
| Short circuit | Required. Auto-recovery or load-removal release (state which). State delay (µs) |
| Charge over-current | State |
| MOSFET Rds(on), PCM | Report (≤ 20 mΩ target) |
| Quiescent current | ≤ 5 µA, report |
| Thermistor | **10 kΩ ±1% at 25 °C, B25/85 = 3435 K ±1% (Semitec 103AT-equivalent, which TI's BQ25895 divider values assume). State your B25/50 as well**, on a separate wire (not in series with the power path), bonded to the cell body |

## 4. Termination (Rev B, PM decision 2026-10-21: J7 = Molex Pico-Lock 2.00 mm, 5-pos)
| Item | Requirement |
|---|---|
| Housing (cable side) | **Molex 205341-0205**: 2.00 mm Pico-Lock receptacle crimp housing, 5 circuits, black, PA UL94V-0 ([Molex 205341 series chart](https://www.molex.com/en-us/products/series-chart/205341)). Note: the part number is 205341-02**05**, not "-0501" |
| Crimp terminal | **Molex 205342-5028**: female crimp, **AWG 20–22**, gold, copper alloy, 20 mΩ max ([RS 201-7496](https://no.rs-online.com/web/p/crimp-contacts/2017496)). The 205342 series covers AWG 20–26 overall ([Molex datasheet 987650-9061](https://www.molex.com/content/dam/molex/molex-dot-com/en_us/pdf/datasheets/987650-9061.pdf)) |
| Mating PCB header (carrier J7) | **Molex 205338-0005**: right-angle SMT, gold, positive lock, 5 circuits, **mated height 2.60 mm** ([205338 series chart](https://www.molex.com/en-us/products/series-chart/205338)). The 205338 series chart lists **right-angle SMT only. No vertical header was found** in the 2.00 mm Pico-Lock family |
| Wire | **AWG20** for the 4 power leads, UL1007/UL1571 (state type and insulation OD). NTC lead: AWG20 preferred for one terminal type, or AWG22 (same terminal 205342-5028) |
| Lead length | **Staggered per §4d (Rev D)**. Supersedes "about 40 mm" |
| Wire exit | From the PCM on the **50 mm edge**, routed per §4c |

### 4a. Pinout (the schematic is master, Rev C)
| Pin | Signal | Wire | Colour |
|---|---|---|---|
| 1 | VBAT+ | AWG20 | Red |
| 2 | VBAT+ | AWG20 | Red |
| 3 | GND (pack −, after PCM) | AWG20 | Black |
| 4 | GND (pack −, after PCM) | AWG20 | Black |
| 5 | NTC (10k B3435; other end to pack − at the PCM) | AWG20/22 | Yellow |

### 4b. Current rating (Molex 987650-9061 derating table, 2.00 mm pitch, ≤ 30 °C rise at the crimp barrel, all circuits powered)
| AWG | 2-ckt | 3-ckt | 4-ckt | **5-ckt** | 6-ckt |
|---|---|---|---|---|---|
| 20 | 6.5 A | 5.5 A | 5.5 A | **5.0 A** | 5.0 A |
| 22 | 5.0 | 5.0 | 4.5 | 4.5 | 4.0 |

- **4 power circuits loaded in a 5-pos housing:** use **5.0 A per pin** (conservative 5-circuit figure). The 4-circuit figure is 5.5 A. Molex does not publish an exact "4 of 5 loaded" value.
- **Per rail with 2 pins in parallel: about 10 A, which is ≥ 6.5 A ✅.** About 6.5 A continuous, if shared evenly, is 3.25 A per pin. That holds even with ±30% current imbalance.
- **Vendor:** wire both VBAT pins and both GND pins to the PCM output pads with **equal-length leads**. Confirm the PCM pad and trace rating for at least 8 A.

### 4c. Mechanical fit (Rev C, vendor drawing to confirm)
- **Housing:** 205341-0205 is 14.55 × 9.1 × 2.54 mm ([Arrow](https://www.arrow.de/products/2053410205/molex)). Header mated height is 2.60 mm (Molex).
  - It fits easily within the 50 mm edge, and at about 2.5 mm thick it sits **well inside the 9 mm pocket ✅**.
- **Length budget:** pack ≤ 62.0 mm in a 67 mm pocket leaves **≥ 5.0 mm at the exit end for the AWG20 lead bend ✅** (PM decision Rev C, accepting about −5% capacity).
  - Leads exit flat from the PCM in the cell mid-plane and turn in that ≥ 5 mm zone.
  - AWG20 UL1007 OD is about 1.5–1.6 mm (EST; vendor to state the actual OD).
  - Vendor and Enclosure team to confirm the bend radius on the drawing.
- **No lead crosses the cell face** (8.5 + about 1.6 mm would exceed 9.0 mm).
- **PCM pads:** 4 × AWG20 plus NTC. Vendor to confirm pad size, solder method and ≥ 8 A pad/trace rating.

### 4d. Staggered lead lengths (Rev D, from Enclosure `mechanical/keepouts_v4_22c.md` and `build_v4_22c.py`)
| J7 pin | Signal | Housing cavity position | Production pack (mm) | Akyga re-termination (mm) |
|---|---|---|---|---|
| 1 | VBAT | Y 27.7 | **22.1** | **24.2** |
| 2 | VBAT | Y 25.7 | **24.5** | **26.6** |
| 3 | BAT_N | Y 23.7 | **26.9** | **29.0** |
| 4 | BAT_N | Y 21.7 | **29.4** | **31.5** |
| 5 | NTC (CHG_TS) | Y 19.7 | **31.8** | **34.0** |

- **Pin mapping confirmed by Layout (2026-10-21):** pins 1–5 are at Y 27.7 → 19.7, X 7.12 in the Layout frame, with the cable mouth facing −X. Lead *i* in Enclosure's model (`build_v4_22c.py`) is therefore pin *i*.
  - Note: Enclosure's model puts the housing mouth at X −8.88, which is a different X datum from Layout's 7.12. The Y values agree. Enclosure and Layout should confirm the frame offset so the lengths still hold.
- **Definition:** these are Enclosure's model wire centreline lengths (`W.Length`) from the pack exit point to the housing mouth face (X −8.88).
  - Model wire OD is 1.6 mm, and the leads exit the pack edge at 1.6 mm pitch.
  - **Vendor to confirm** whether they quote lead length to the housing face or to the crimp. Our figures are to the **housing face**.
- **Tolerance: TBC.** No harness-length tolerance is given in the Enclosure files, and I have no sourced standard figure to cite.
  - Proposed for vendor comment: **±0.5 mm** per lead. The leads step by 2.4–2.5 mm, so ±0.5 mm keeps the order unambiguous.
  - Vendor to state their capability. Enclosure to confirm the slack available in the U-turn.

## 5. Compliance and documents (deliverables)
- **IEC 62133-2:2017** test report (cell and pack), from a CB-scheme lab
- **UN38.3** test summary and report. **MSDS/SDS**. RoHS and REACH
- **BIS IS 16046 (Part 2): R-number for the cell AND the pack**, registered under your name (or a named Indian AIR, Authorised Indian Representative) before pilot shipment. State the current R-numbers you already hold, and your timeline and cost for this model
- Dimensioned **drawing** (pack incl. PCM, wire exit, connector pinout), full **datasheet**, PCM schematic and BOM, NTC part number, and cell maker/grade if not in-house

## 6. Quantities and commercial
| Phase | Qty | Need by |
|---|---|---|
| Engineering samples | **10–20 pcs** | ASAP; state lead time |
| Pilot | **1,000 pcs** | state lead time |
| Production | **10,000 pcs/yr** (forecast) | state lead time and capacity |

Quote: unit price at 20 / 1k / 5k / 10k, tooling/NRE (if any), MOQ, Incoterms (FOB Shenzhen and DAP India), payment terms, warranty, sample lead time, mass-production lead time, and UN38.3 shipping class.

## 7. Questions for the vendor
1. Max capacity you can deliver at ≤ 8.5 × 50.5 × 62 mm and 2C. If below 3.0 Ah, state your best figure.
2. Is the cell stacked or wound? Cathode chemistry?
3. 2C discharge curve and temperature rise. Peak-current pulse capability.
4. Is the BQ25895 3 A charge acceptable? Recommended JEITA settings?
5. Existing BIS R-numbers (cell/pack) and the timeline for this model.
6. Termination per §4: confirm the 205341-0205 / 205342-5028 harness, AWG20, the PCM pad rating ≥ 8 A, and the fit option from §4c (a/b/c).

## 8. Vendor contact routes (from each vendor's own website)
| Vendor | Email | Phone | RFQ route | Verified |
|---|---|---|---|---|
| **Grepow** (Shenzhen Grepow Battery Co., Ltd.) | **info@grepow.com** (global). US: info@genstattu.com. DE: info@genspow.de | **+86-755-88376378** (CN, HQ / Intl Marketing Center). +1-925-364-7166 (US). +49-(0)218-25700755 (DE) | [grepow.com/contact-us.html](https://www.grepow.com/contact-us.html) | ✅ text from the official contact page via search index. ⚠ the box got HTTP 522/timeouts on grepow.com, so the page did not load live |
| **THOR Power** (Dengzhou Xinju New Energy) | **sales@thorbattery.com** | **+86 180 2916 9106** (WhatsApp/Tel) | [thorbattery.com/contact-us/](https://thorbattery.com/contact-us/). Product pages have a "Request a Quote" button (form URL not captured) | ✅ fetched live (HTTP 200). Email and phone on contact and product pages |
| **iBorn** (ibornbattery.com) | **info@ibornbattery.com** | **+86 0755 2998 5193** (office). **+86 182 1924 2308** (mobile) | [ibornbattery.com/pages/contact-us](https://ibornbattery.com/pages/contact-us) | ✅ fetched live (HTTP 200). RFQ form fields not inspected |

## 9. Quote comparison checklist
| Check | Grepow | THOR | iBorn |
|---|---|---|---|
| Pack T × W × L incl. PCM (max) ≤ 8.5 × 50.5 × 62.0 | | | |
| Rated capacity (mAh) @ 0.2C / typical | | | |
| Continuous discharge (A) ≥ 6.5. Peak (A, s) | | | |
| OCP setting 6–8 A. Short-circuit delay | | | |
| 10k B3435 NTC, separate wire | | | |
| Termination: 205341-0205 + 205342-5028, AWG20, 2+2+1 pinout; fit option §4c a/b/c | | | |
| BQ25895 3 A charge OK. JEITA notes | | | |
| Cycle life (cycles @ conditions → 80%) | | | |
| Swelling % (cycle / 60 °C storage) | | | |
| IEC 62133-2 / UN38.3 / MSDS available | | | |
| BIS IS 16046-2 R-number (cell / pack): existing or timeline and cost | | | |
| Sample lead time / price | | | |
| Pilot 1k and 10k/yr price, MOQ, NRE | | | |
| Drawing + datasheet supplied | | | |

## Rev D follow-up delta (paste into vendor emails)
> **Subject: PocketMate 1S Li-po RFQ: Rev D delta (lead lengths)**
> Further to our Rev C RFQ, only §4 termination changes:
> 1. **Lead lengths are now staggered**, measured from the pack exit to the Molex 205341-0205 housing face. Pins 1–5: **22.1 / 24.5 / 26.9 / 29.4 / 31.8 mm**. They replace "about 40 mm".
> 2. **Pin-to-length mapping (pin 1 at the +Y end of the 5-way housing):** pin 1 VBAT 22.1, pin 2 VBAT 24.5, pin 3 GND 26.9, pin 4 GND 29.4, pin 5 NTC 31.8 mm. Please quote the harness as staggered, 5 × AWG20 (UL1007/UL1571), 205342-5028 terminals.
> 3. **Proposed length tolerance ±0.5 mm per lead.** Please confirm your capability, and whether you measure to the housing face or the crimp.
>
> All other Rev C requirements are unchanged: ≤ 8.5 × 50.5 × 62.0 mm incl. PCM; ≥ 3.0 Ah rated (target 3.1 Ah) at 0.2C; 2C; PCM OCP 6–8 A; 10k B25/85 = 3435 NTC; pinout 1 VBAT, 2 VBAT, 3 GND, 4 GND, 5 NTC; IEC 62133-2, UN38.3, MSDS, and BIS IS 16046-2 R-number.

> **Note (2026-10-21 23:16 IST, from Layout):** Enclosure moved J7 0.3 mm toward -Y. The pins stay at X 7.12, and the new Y positions are: pin 1 VBAT 27.4, pin 2 VBAT 25.4, pin 3 BAT_N 23.4, pin 4 BAT_N 21.4, pin 5 NTC 19.4. The §4d lead lengths came from Enclosure v4_22c, before the move. Enclosure needs to confirm whether they change, and also resolve the X reference mismatch (Layout X 7.12 vs the Enclosure housing face at X −8.88), before the Rev D follow-up goes out.

## 4e. Final lead spec (Enclosure v4_22e, 2026-10-21 23:18 IST): supersedes the §4d lengths
- 5x AWG20 leads exit the 50 mm edge at the PCM end, at 1.6 mm pitch at the exit, into a Molex 205341-0205 housing with 205342-5028 terminals.
- Length is measured from the cell exit to the housing face, tolerance ±1 mm.
- Pin 1 is furthest toward the pack's +X side (exit X −20.2), and pins 2–5 step toward −X.

| Pin | Signal (schematic master) | Production pack (≤62 mm) | Akyga prototype |
|---|---|---|---|
| 1 | VBAT | 22.1 mm | 24.2 mm |
| 2 | VBAT | 24.5 mm | 26.6 mm |
| 3 | GND (BAT_N) | 26.9 mm | 29.0 mm |
| 4 | GND (BAT_N) | 29.4 mm | 31.5 mm |
| 5 | NTC | 31.9 mm | 34.0 mm |

> **RESOLVED (23:19 IST):** Enclosure confirmed the schematic is master (1–2 VBAT, 3–4 BAT_N, 5 NTC/CHG_TS). The lengths stand, with pin 5 at 31.9 mm. Cleared to send as the Rev D follow-up.
