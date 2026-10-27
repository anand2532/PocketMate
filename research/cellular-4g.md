# PocketMate 4G cellular option (Quectel, LGA only). v1, 2026-10-21

**Cat-4 vs the ₹3,000 (~$35) cap:**
- The only Cat-4 part covering all India bands (B1/3/5/8/40/41) is **EC25-E**.
- It is under the cap **only on Indian reseller listings**: ₹1,670 (Voltiro/IndiaMART), ₹2,500 (Thinksemi), ₹2,695 ex-GST (Evelta, sold out).
- **No authorised-distributor volume price under $35 was found.** The cheapest non-India price is $41.50 (Nice-IC).
- **Best Cat-1 fallback: EC200U-CN**, ₹590 incl. GST (Syntronix) to ₹620 (Voltiro). Quectel states it is footprint-compatible with the EC25 series.

FX for comparison only: ₹88 ≈ $1 (EST, as in compute-options.md). Prices were taken from the web on 2026-10-21. "qty" is as listed.

## 1. Ranked table (LGA parts only)
| Rank | Part (exact variant) | Cat | India bands B1/3/5/8/40/41 (Quectel spec) | LGA size (mm) | Best price found (qty, source) | vs ₹3,000 cap |
|---|---|---|---|---|---|---|
| **1** | **EC25-E** (EC25EFA-512-STD) | **4** (150/50) | ✅ FDD B1/3/5/7/8/20, TDD B38/40/41. Region "EMEA/South Korea/Thailand/**India**" ([EC25 spec V3.0](https://www.quectel.com/content/uploads/2026/03/Quectel_EC25_Series_LTE_Standard_Module_Specification_V3.0.pdf)) | 29.0 × 32.0 × 2.4, 144 pads | ₹1,670/pc, qty n/s ([IndiaMART Voltiro](https://www.indiamart.com/proddetail/ec25-efa-512-std-quectel-module-2854133916888.html)). ₹2,500 ([Thinksemi/aajjo](https://www.aajjo.com/product/quectel-ec25efa-512-std-for-industrial-in-chengalpattu-thinksemi-infotech-limited)). ₹2,695 ex-GST, 1 pc, sold out ([Evelta](https://evelta.com/quectel-ec25-e-lte-category-4-module/)). $41.50 (Nice-IC, via search index) | ⚠️ **Under the cap on India reseller listings only.** Not authorised. **Get an authorised quote (Quectel India) at 1k** |
| ✗ | EC25-EUX / EC25-EU | 4 | ❌ **No B5** (FDD B1/3/7/8/20/28A + TDD 38/40/41) (same spec) | 29 × 32 | n/a | Dropped (band gap) |
| ✗ | EC25-AU/AUX, EC25-J | 4 | ❌ AU: TDD B40 only, no B41. J: no B5/B40 (Quectel EC25 brief) | 29 × 32 | EC25-AUX mPCIe $44.48 @10 (LCSC C46609529), not LGA | Dropped |
| ✗ | EG25-G (EG25GLGD-128-SGNS) | 4 | ✅ (global) | 29 × 32 | **$47.54 @10** ([LCSC C28695029](https://www.lcsc.com/product-detail/C28695029.html)) | ❌ **Over the cap** (~₹4,180) |
| ✗ | EC20 R2.1 | 4 | not verified (not checked) | 29 × 32 | ₹2,245 for "EC20 CE FILG" ([robotskull](https://www.robotskull.ai/categories/quectel-modules/2440060000000958266)). CE is a China variant; India bands **unverified** | ⚠️ Flag; not recommended |
| ✗ | EG21-G (EG21GLGD-128-SGNS) | **1** (not 4) | ✅ global | 29 × 32 | Mouser $39.60 @250 (0 stock). Avnet $35.94 @4,000 ([OEMsTrade](https://www.oemstrade.com/search/eg21g)) | ❌ Over the cap, and only Cat-1 |
| **F1** | **EC200U-CN** | 1bis | ✅ FDD B1/3/5/8, TDD B34/38/39/40/41. Region "China/India" ([EC200U spec V1.6](https://www.quectel.com/content/uploads/2024/03/Quectel_EC200U_Series_LTE_Standard_Specification_V1.6.pdf?wpId=123500)) | 28.0 × 31.0 × 2.4. EC25-compatible footprint (Quectel EC200U spec V1.1) | ₹590 incl. GST ([Syntronix](https://syntronix.in/product/quectel-ec200u-cn-lte-cat-1-4g-lte-module/)). ₹620 ([Voltiro/TradeIndia](https://www.tradeindia.com/products/ec200u-cn-4g-quectel-module-c12827677.html)). ₹1,200 (robotskull) | ✅ Far under |
| F2 | EG915U-CN | 1 | ✅ FDD B1/3/5/8 + TDD B34/38/39/40/41, "China/India" ([EG915U spec V1.3](https://developer.quectel.com/en/wp-content/uploads/sites/2/2024/11/Quectel_EG915U_Series_LTE_Standard_Module_Specification_V1.3.pdf)). (EU/LA variants: **no TDD**) | 23.6 × 19.9 × 2.4, 126 pins | CN price not found. EU: $24.71 ([YCICT](https://www.ycict.com/eg915u-eu-lga.html)) | ✅ (EU price) |
| F3 | EG800G-CN (EG800GCNGB-I05-SGNDA) | 1bis | ✅ FDD B1/3/5/8 + TDD B34/38/39/40/41 (EG800G spec V1.2, via search). EU: no TDD | 17.7 × 15.8 | **$7.26 @10** ([LCSC C49056359](https://www.lcsc.com/product-detail/C49056359.html)) | ✅ |
| F4 | EC800M-CN (EC800MCNGB-I05-SGNSA) | 1bis | ✅ TDD B34/38/39/40/41, FDD B1/3/5/8 (verify in spec), "China/India" | 17.7 × 15.8 × 2.4 | **$6.23 @100** ([LCSC C53243597](https://www.lcsc.com/product-detail/C53243597.html)) | ✅ |
| F5 | EG800K-CN | 1bis | ✅ FDD B1/3/5/8 + TDD 34/38/39/40/41 ([EC800K/EG800K HW V1.0](https://developer.quectel.com/en/wp-content/uploads/sites/2/2025/06/Quectel_EC800KEG800K_Series_QuecOpenQuecPython_Hardware_Design_V1.0.pdf)). EU: no TDD | 17.7 × 15.8 × 2.4 | CN not found. EU $4.83 @100 (LCSC C44008839) | ✅ |
| F6 | **EG800Q-IN** (India variant, Qualcomm QCX216) | 1bis | ✅ FDD B1/3/5/8 + TDD B40/41 ([EG800Q spec V1.9 prelim](https://www.quectel.com/content/uploads/2024/03/Quectel_EG800Q_Series_LTE_Standard_Module_Specification_V1.9_Preliminary.pdf)) | 17.7 × 15.8 × 2.4 | IN price not found. EU €10.98 @5 (EXC) | ✅ (likely) |
| F7 | EG912U-GL (EG912UGLAC-I05) | 1 | B5/40/41 confirmed. **B1/3/8 to verify** ([EG912U-GL spec](https://developer.quectel.com/en/wp-content/uploads/sites/2/2024/11/Quectel_EG912U-GL_LTE_Standard_Specification_V1.2.pdf)) | 29.0 × 25.0 × 2.4 | $12.68 @10 ([LCSC C7472750](https://www.lcsc.com/product-detail/C7472750.html)) | ✅ |
| F8 | EC200A-CN | 4? / 1? **verify** | TDD B34/38/39/40/41 (EC200A spec V1.6, via search). FDD not verified | 29 × 32 class (verify) | no price found | TBC |
| — | EC800G / EC800N / EG915N | 1 / 1bis | Not checked (EG915N-EU on LCSC $9.35 @10, EU variant) | — | — | Not ranked |

## 2. Recommendation
- **Lay out one EC25-footprint LGA site, 29 × 32 mm.**
  - **Primary SKU part: EC25-E** (Cat-4, full India bands), subject to an **authorised Quectel India quote ≤ ₹3,000 at 1k**.
  - **Cost-down / fallback: EC200U-CN** (Cat-1bis, ₹590–620) on the same footprint, per Quectel's EC25-compatibility statement. **Verify pin-compatibility against both HW guides before layout freeze.**
- **Make it a separate "PocketMate 4G" SKU**, for four reasons:
  - **Cost:** about ₹1.7–2.7k for the module, plus SIM holder, two antennas and RF shield (EST ₹300–600). Plus the end-product MTCTE test cost.
  - **Power:** EC25-E draws 774 mA at 23.5 dBm on B3. That is **≈ 2.9 W at 3.8 V**, against the **≈ 1.6–1.85 W** whole-device passive budget (thermal_v2.md). So sustained uplink must be duty-limited. Idle is 30.8 mA (USB connected) ≈ 0.12 W (EC25 HW V2.4.2, Table 34).
  - **Thermal:** the above means firmware must cap uplink, or the 4G SKU must use a lower CM5 clock.
  - **Certification:** a cellular SKU triggers MTCTE for the end product (see §6). Keeping it a separate SKU keeps the Wi-Fi base model's certification path unchanged.

## 3. Interface, power and thermal (LGA candidates)
| Item | EC25-E | EC200U-CN | Source |
|---|---|---|---|
| Host interface | USB 2.0 HS (no PCIe needed) | USB 2.0 | specs |
| CM5 USB | CM5 has **1× USB 2.0 + 2× USB 3.0** (CM5 datasheet R3 §2.4). Use the **USB 2.0 port**, or the USB2 pair of a USB3 port, whichever the carrier leaves free (**Layout to confirm**) | | CM5 datasheet |
| VBAT | 3.3–4.3 V, typ. 3.8 V. Must **never drop below 3.3 V**. Supply **≥ 2.0 A**. VBAT_RF burst up to 1.8 A | 3.3–4.3 V | EC25 HW V2.4.2 §3.6 |
| Sleep / idle | LTE-FDD PF128 sleep 1.90 mA. Idle 20.7 mA (USB off) / 30.8 mA (on) | Sleep 1.4 mA (PF128). Idle 28.7 / 12.7 mA | HW Table 34; EC200U spec |
| Active (max power) | B3 774 mA, B5 762, B40 432, B41 480 mA @ ~23 dBm | not extracted (TBC) | HW Table 34 |
| PSM / eDRX | not verified here (TBC) | TBC | — |

- **Battery impact:** the prototype Akyga LP655063 is rated 1C (≈ 3 A).
  - CM5 peak plus a 2 A modem burst can exceed it, so **prototype with the 4G radio duty-limited or bench-powered.**
  - The production RFQ pack (2C continuous, 3C peak) covers it.

## 4. SIM, antennas, Linux
- **SIM:** EC25-E: 1× (U)SIM, 1.8/3.0 V. **eSIM optional** per the EC25 spec V3.0. EC200U-CN: 2× (U)SIM (SIM2 optional).
  - A push-push nano-SIM holder fits, but the MPN is TBC.
  - An MFF2 eSIM footprint is optional; it needs an operator eSIM profile in India (TBC).
- **Antennas:** EC25-E has ANT_MAIN, ANT_DIV and ANT_GNSS (50 Ω). EC200U has main, GNSS (optional) and BT/Wi-Fi-scan.
  - **The aluminium unibody needs an RF window** (plastic or glass end-cap, or slot) for the LTE main (698–2690 MHz), diversity and GNSS antennas. Antenna part numbers and sizes are **TBC** (no supplier verified this pass).
- **Linux on CM5:**
  - **EC25:** QMI/RmNet, Linux `qmi_wwan`, plus USB serial (`option`); ECM optional (EC25 spec V3.0 / EC25 brief). Supported by ModemManager over QMI (EST; widely used, verify on Pi OS).
  - **EC200U / EG915U (Unisoc):** **USB RNDIS / ECM and USB serial only; no QMI** (EC200U spec V1.6, EG915U spec V1.3, Linux 2.6–6.7). ModemManager support for the Unisoc parts is **VERIFY**.

## 5. Board requirements (Schematic and Layout). Forward verbatim
**Basis:**
- Quectel *EC25 Series Hardware Design* V2.4.2 (Preliminary, 2021-04-08) ([copy](https://www.3jtech.com.tw/storage/system/PDF/Quectel_EC25_Series_Hardware_Design_V2_4_2_Preliminary_20210408.pdf)), referred to as [HW].
- The EC200U-CN fallback must be cross-checked against the *EC200U Hardware Design* (not yet read: **TBC**).

**5.1 VBAT (pins 57/58 VBAT_RF, 59/60 VBAT_BB)**
- Range 3.3–4.3 V (typ. 3.8). **Minimum 3.3 V including the burst drop.** Source must supply **≥ 2.0 A**; VBAT_RF bursts up to 1.8 A [HW §3.6, Table 6].
- **Bulk and decoupling:**
  - Per rail: about **100 µF low-ESR (ESR ≈ 0.7 Ω)** bulk, plus an MLCC array of **100 nF, 33 pF and 10 pF**, all close to the VBAT_BB/VBAT_RF pins.
  - A TVS on VBAT (V_RWM ≈ 4.5 V; reference part WS4.5D3HV) [HW §3.6.2].
- **Routing:**
  - Single source, star-split into VBAT_BB and VBAT_RF.
  - **VBAT_BB ≥ 1 mm and VBAT_RF ≥ 2 mm** trace width; wider for longer runs [HW §3.6.2].
- **Source:**
  - Quectel prefers an LDO when the headroom is small, or a buck when the voltage difference is large [HW §3.6.3].
  - Our proposal: **feed from the BQ25895 SYS node** (tracks VBAT, about 3.5–4.35 V; **VERIFY VSYSMIN and SYS max ≤ 4.3 V in the BQ25895 datasheet**), through a load switch (≥ 2.5 A, for SKU/power gating), with the 100 µF bulk at the module.
  - Alternative: a dedicated 3.8 V buck-boost (≥ 2.5 A) if SYS can fall below 3.4 V under CM5 load (**TBC by power budget**).
  - Do **not** feed from 3.3 V.

**5.2 USB 2.0 (USB_DP pin 69, USB_DM pin 70, USB_VBUS pin 71)**
- **90 Ω differential**, ground-surrounded, preferably on an inner layer with GND above and below. Do not route under crystals, magnetics or RF [HW §3.10].
- Common-mode choke footprint (L1) near the module. 0 Ω test-point stubs (DNP). ESD on D+/D− **< 2 pF**, placed near the connector or test point.
- USB_VBUS: VBUS sense input, Vmin 3.0 V [HW pin table]. Drive it from a CM5-side switched 3.3/5 V so the host can drop VBUS to allow sleep when USB suspend is unused [HW §3.5.1, Fig. 6].
- Connect to the free CM5 **USB 2.0** port (CM5 datasheet R3 §2.4.2: USB 2.0 pairs **must not be P/N swapped**).

**5.3 RF**
- ANT_MAIN (pin 49), ANT_DIV and ANT_GNSS (pin 47): **50 Ω** CPWG to u.FL or antenna feed pads.
- **π-match** (series 0 Ω, two shunt DNP) on main and diversity, placed close to the antenna [HW §5.1, R1/C1/C2, R2/C3/C4].
- GNSS: passive antenna directly. For an active antenna, add an external LDO bias through an inductor, as in [HW Fig. 38 and its notes].
- Keep RF traces short, with GND via fence. Antennas sit behind the unibody RF window.

**5.4 (U)SIM**
- USIM_VDD (pin 14, 1.8/3.0 V auto), USIM_DATA/CLK/RST, and USIM_PRESENCE (pin 13, 1.8 V, card detect).
- Series 0 Ω on each line. **33 pF** to GND on DATA/CLK/RST (EGSM900 filter).
- TVS array **≤ 15 pF**. Bypass on USIM_VDD **< 1 µF**, placed at the holder.
- Trace length **< 200 mm**. Keep DATA and CLK apart, GND-shielded, and away from RF/VBAT [HW §3.9].
- Optional MFF2 eSIM wired in parallel behind 0 Ω options (EC25-E has 1 SIM interface, so it is either the holder or the eSIM).

**5.5 Control from the STM32U0**
- Module IO is the **1.8 V domain** (VDD_EXT, pin 7, 1.8 V output).
- **PWRKEY (pin 21):** drive through an **open-drain NPN/NMOS** (Quectel ref: 4.7 kΩ / 47 kΩ, 10 nF). Low **≥ 500 ms** to turn on.
  - Wait **≥ 30 ms after VBAT is stable** before asserting.
  - Release after STATUS goes low. USB is active **≥ 13 s** after PWRKEY [HW §3.7.1, Fig. 10/12].
- **RESET_N (pin 20):** open-drain, low **150–460 ms**. Use it only if AT+QPOWD and PWRKEY fail. No large capacitance on either pin [HW §3.8].
- **STATUS:** open-drain output. Pull up to the **STM32 IO rail**.
- **RI** (and WAKEUP_IN / AP_READY if used) is 1.8 V push-pull. Use a **1.8 V↔3.3 V level shifter** (or a 1.8 V-tolerant STM32 IO domain: **TBC by STM32U0 VDDIO2**).

**5.6 Footprint and mechanicals**
- EC25: **(29.0 ± 0.15) × (32.0 ± 0.15) × (2.4 ± 0.2) mm**. **144 pads = 80 LCC + 64 LGA** [HW §1/§2].
- Land pattern and stencil from [HW Ch. 7] (stencil 0.18–0.20 mm per the HW revision notes). Reserved pins must be footprinted but left as **keepout** [HW pin notes].
- **Dual-footprint check:** EC200U-CN is 28.0 × 31.0. Confirm the pad map overlaps from both HW guides. **TBC.**
- Allow for a **board-level RF shield can** over the module and RF match (EST; required by the EMC plan, not by Quectel).
- **Thermal:** solid GND copper under the module with a via array to inner GND. Pad the module (or can) to the aluminium chassis with a thermal gap pad. Per [HW §6.8 "Thermal Consideration"] (not yet extracted, so values are TBC).

## 6. India certification
- **TEC MTCTE:** the search-index synthesis of TEC's *MTCTE Procedure* (3 Apr 2024) says **modules/components are excluded** and the **end product** is certified. No Quectel module MTCTE certificate was found. **VERIFY on the [MTCTE certified list](https://tec.gov.in/public/Equipment-certified-under-MTCTE).**
  - Quectel's spec sheets list SRRC/CCC for the -CN variants and CE/GCF for EC25-E. **No India certification is listed.**
- **WPC ETA** for the end product (LTE plus Wi-Fi/BT): VERIFY.
- **BIS CRS:** applies to the end product/adapter as for the base SKU (bom.md).

## 7. Layout follow-up (2026-10-21, 23:56 IST): daughterboard plan
### 7.1 Is EC25-E "EU-only"? **No.**
- Quectel's *EC25 Series LTE Standard Module Specification* V3.0 (2026-03) lists **EC25-E**:
  - Region/Operator: **"EMEA/South Korea/Thailand/India"**
  - LTE-FDD **B1/3/5/7/8/20**; LTE-TDD **B38/40/41**; WCDMA B1/5/8; GSM B3/8
- It therefore **covers all of India's B1/3/5/8/40/41**.
- Quectel's own EC25 variant brief groups **EC25-E** under "Variants for EMEA/Korea/Thailand/India".
  - No separate "EC25-IN" exists.
  - Quectel's India-specific variants are Cat-1bis (e.g. EG800Q-**IN**; EC200U/EG915U/EG800K/EG800G **-CN**, region "China/India").
- Variants that do **not** fit India:
  - EC25-EU/EUX: no B5
  - EC25-AU/AUX: B40 only
  - EC25-J: no B5/B40

### 7.2 CM5 USB2 hosts available for the module
Source: *CM5 Datasheet* R3, pinout table and §2.4. All pins are on the **high-speed connector (J2, pins 101–200)**.

| Port | D+ / D− pins | Note |
|---|---|---|
| USB 2.0 (USB_P / USB_N) | 105 / 103 | **Used by the carrier USB-C.** Datasheet: USB 2.0 needs `dtoverlay=dwc2,dr_mode=host` |
| **USB3-0** USB2 pair (USB3-0-DP / -DM) | **134 / 136** | Datasheet labels these "USB 2.0 signal" |
| **USB3-1** USB2 pair (USB3-1-DP / -DM) | **163 / 165** | as above |

- **Can they run USB2-only?** Each USB 3.0 port includes its own USB 2.0 HS pair (DP/DM), so the SuperSpeed TX/RX pairs can be left unconnected.
  - A USB2-only device such as the EC25 then enumerates on that pair.
  - This is standard USB 3.x host behaviour and how Pi 5 USB3 ports serve USB2 devices. EST: the datasheet does not state "USB2-only" explicitly. **Bench-verify on the CM5 IO board.**
- **Recommendation:** route the **USB3-1 DP/DM (163/165)** pair to the flex.
  - 90 Ω differential, P/N matched ≤ 0.15 mm, **no P/N swap** on USB 2.0 pairs (datasheet §2.4).
  - Leave the USB3-1 RX/TX pairs NC. Use VBUS_EN or a GPIO-switched rail for module USB_VBUS sense.
- **Note on CM4-to-CM5 migration:** these pins were CAM0/DSI0 on CM4 (datasheet pin-change table). The carrier must not use them for MIPI.
- **USB2 across the ~22-pin flex:** keep the pair as a GND-flanked coplanar pair (G-D+-D−-G) at 90 Ω on the flex stack-up. Assign several flex pins to VSYS/GND for the 2 A bursts (EST: ≥ 4 + 4 pins at 0.5 A/pin, **check the connector rating**).

### 7.3 Antennas (behind the plastic windows)
| Role | Part | Size (mm) | Bands | Connector | Price / source | Notes |
|---|---|---|---|---|---|---|
| **LTE main** | **Taoglas FXUB63.07.0150C** | 96 × 21 × 0.2 | 600–6000 MHz. Datasheet efficiency: 824–960 57%, 1710–2200 67.5%, **2300–2690 (B40/41) 74%**, 698–806 only 25% | I-PEX MHF I (U.FL), 150 mm Ø1.37 | $3.41 (Aztek), $3.50 (Westward Sales). Mouser stocks the series (price not read) | [datasheet](https://www.taoglas.com/datasheets/FXUB63.07.0150C.pdf). Peel-and-stick on plastic/glass. **96 mm long: fits only along the 125 mm length (left end + bottom-left window). Check window size** |
| **LTE diversity** | **Molex 146185** series (quad-band flex) | **84 × 15 × 0.10** | 824–960 MHz, 1.71–2.7 GHz (covers B1/3/5/8/40/41), 3–6 GHz. Eff. > 60% / > 65% | Micro-coax (mates 73412-0110 / U.FL type) | Price not found (TBC; Mouser/DigiKey) | [Molex flex brochure](https://services.dac-group.com/marketing/documents/molex/molex-flexible-cellular-antennas.pdf). Shorter, suits the bottom-left window |
| alt. diversity | Molex 105263 (6-band flex) | 106.6 × 13 × 0.10 | 824–960, 1.71–2.70 GHz | micro-coax | TBC | same brochure |
| GNSS | **TBC**: not sourced in this pass (candidates: Taoglas FXP passive flex, Quectel YC/YF series) | — | L1 1575 MHz | U.FL | — | EC25 GNSS input is passive-antenna capable [HW §5.2] |

- **Placement:**
  - Main on the left-end window. Diversity on the bottom-left window, ≥ 1/4 λ apart where possible and orthogonal to the main.
  - Both away from the right-end Wi-Fi.
- **Keepout:** no Al within about 5–10 mm of the radiator (EST, **antenna vendor to confirm in tuning**). Budget a matching/tuning session with Taoglas or Molex in the final enclosure.
- The ~2.4 GHz Wi-Fi must be isolated from LTE B40 (2300–2400 MHz). Keep the antennas at opposite ends (the current plan). Coexistence filtering is TBC.

### 7.4 Thickness check (Enclosure v4_22c model, `pocketmate_enclosure_v4_22c.FCStd`, bounding boxes read with FreeCAD)
| Item | Z (mm) |
|---|---|
| Battery pocket `Vol_Battery` | **2.3 .. 11.3 (9.0 mm)** |
| Production cell (8.5 mm) | 2.3 .. 10.8 (0.5 mm swell margin) |
| Akyga prototype (7.0 mm) | 2.3 .. 9.3 |
| Display `Vol_Display` underside | **16.8** |
| Bezel/display frame (PC) | starts at 11.5 |

- **Inside the 9 mm pocket: does NOT fit.** 8.5 cell + 0.8 PCB + 2.4 EC25 + about 0.3 shield (EST) ≈ **12.0 mm > 9.0 mm**.
- **On top of the pocket** (board on a ledge at Z 11.3, not loading the cell):
  - Z 11.3 → 12.1 (PCB) → 14.5 (EC25) → about 14.8–15.0 (shield can, EST 0.3–0.5 over the module).
  - That leaves **≈ 1.8–2.0 mm** under the display (16.8). It **fits in Z**, with these conditions:
  1. **Bottom-side components are not allowed** (the board sits 0.5 mm over a swelling cell). Keep the 100 µF bulk caps topside, ≤ 2.4 mm tall.
  2. **XY clashes in the proposed outline X −52..−8, Y −32..18:**
     - **Speaker** `Vol_Speaker` at X −50..−35, Y −35..−24, Z 12..15.5: overlaps. Trim the board to Y > −24 in that X range, or move the speaker.
     - **Battery leads** at X −28.3..−8.9, Y 17.2..35.2, Z up to 13.7: overlap the strip Y 17.2..18. Trim to Y < 17.
     - **Side-key flex** at Y ≥ 15, Z 12..17: overlaps Y 15..18. Trim to Y < 15, or check the exact flex outline.
     - **Bezel frame** (Z ≥ 11.5): local ribs not sampled. **Enclosure to confirm** a clear Z 11.3..15.0 volume over the cell.
  3. Swell clearance: the 0.5 mm pocket margin is the only gap between the cell and the board. An IEC-type swelling allowance (typically about 8–10% of thickness, EST) would need **≈ 0.7–0.85 mm**. **Flag this to Enclosure/Battery:** consider a 0.3 mm stiffener-free gap or lowering the board ledge budget.
  4. Thermal: the board sits directly over the cell, so EC25 heat (up to ≈ 2.9 W in bursts) warms the cell. Thermal-pad the shield to the bezel or Al, not into the cell.
