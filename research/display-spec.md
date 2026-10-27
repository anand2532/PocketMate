# PocketMate display and camera FPC sourcing spec (v1, 2026-10-21)
Mechanical basis: `mechanical/keepouts_v4_22c.md` (DSI tail drop into **J3 = Hirose FH12-22**, 22-pin, 0.5 mm; camera into **J4 = FH12-22**).

## 1. Display tail requirements (J3)
| Item | Requirement | Basis |
|---|---|---|
| Interface at J3 | **MIPI DSI, 22-pin 0.5 mm, Raspberry Pi 22-pin DSI pinout**, direct to CM5 DSI (no bridge board inside the enclosure) | carrier J3 FH12-22 |
| FPC thickness in the bend zones | **≤ 0.15 mm** (0.12 mm PI design value) | keepouts_v4_22c: the S-bend into J3 needs R1 + R2 + t = 1.56 for 0.12 mm. A 0.2 mm tail fails (needs 2.6 mm) |
| Contact-end thickness | Per the FH12 mating spec (stiffened contact end). **Stiffener only inside the connector** (Y < 24.05 in the carrier frame) | keepouts_v4_22c: "a 0.5 mm stiffened section cannot bend here" |
| Free length (glass edge to J3 mouth) | **≥ 16.5 mm**, including a **flat service Z-fold of ≥ 2.5 mm** on the run (3 layers, about 0.36 mm, at Z 15.0..15.5) | keepouts_v4_22c: 14.0 mm without the fold is < 15 mm, so it fails |
| Fold at the glass edge | 180°, R ≥ 0.72 (6t for 0.12 PI) | keepouts_v4_22c |
| Components on the tail | **None in the bend/run zones** (Y 24.05..35.0) | clearance over J11 is 1.36–1.86 mm |

## 2. Candidate panels vs spec
| Panel | What the source shows | Meets the J3 spec? | Custom tail? |
|---|---|---|---|
| **Waveshare 4.3inch DSI LCD**. Bare glass per its panel spec ([4.3inch IPS(P) spec](https://files.waveshare.com/upload/1/16/4.3inch_IPS%EF%BC%88P%EF%BC%89%281%29.pdf), outline drawing p.4) | **Panel interface is 24-bit parallel RGB, not DSI**: pins 5–28 R0–B7, DCLK/HSYNC/VSYNC/DE (§6.3). **40-pin FPC, 0.50 ± 0.03 mm pitch**, finger width 0.35 ± 0.03, span 19.50 ± 0.07, tail width 20.50 ± 0.1. **Tail 46.00 ± 0.5 mm** from the glass. **Contact-end thickness 0.30 ± 0.03 mm**. Stiffener/finger zone 3.50 ± 0.30 at the contact end. **A component area on the FPC up to 1.35 mm high** (bridge/LED parts). Glass module 2.80 ± 0.20 thick. The bend-zone base film thickness is not dimensioned. Pins 37–40 are XR/YD/XL/YU (resistive-touch lines on this sheet; the product uses CTP, VERIFY). **The DSI conversion is on Waveshare's adapter PCB** (its 15/22-pin DSI connector), not on the panel | ❌ **No.** Wrong interface at the glass (RGB 40-pin). A component zone sits on the tail. The 0.30 mm contact end is double our bend limit. Using it needs Waveshare's bridge PCB inside the device | Waveshare sells finished modules. **No custom-tail offer found** |
| **Ronbo MPI4303** ([listing](https://ronboelectronics.en.made-in-china.com/product/YOgGSAkPhacj/China-Mipi-Dsi-Input-4-3-Inch-IPS-800X480-Raspberry-Pi-4b-3b-Capacitive-Touch-LCD-Screen.html)) | "MIPI DSI", 800 × 480 IPS, 400 cd/m², CTP 5-point. **Module PCB size 106.0 × 68.0 mm**: it is a panel on a driver PCB, connected "directly to Raspberry Pi … by an FFC cable". **No FPC thickness, pin count, pitch, tail length or connector is published.** Prices now **$20.50 (2–99), $19.50 (100–499), $18.50 (500+)**. Ready sample ≤ 1 wk; custom sample 1–2 wk; MP 3–4 wk | **Unknown → likely no** as stock: FFC-to-PCB architecture, Pi-4-style connector (VERIFY) | **Yes, vendor states "custom solution if standard products couldn't meet requirements"** and "Customization: Available" |

**Note on cost:** `bom.md` used $17.50 at 1k for MPI4303 from an earlier listing. The listing now shows $18.50 at 500+, with no 1k break. **Re-quote.**

**Verdict and ask:** neither stock part meets the J3 spec. Send Ronbo (and Lida as alternate) a **custom-tail RFQ**:
- DSI glass (a native-DSI driver IC on glass, or a COG/COF with DSI) with an FPC tail ending in a **22-pin 0.5 mm RPi-DSI pinout** for FH12-22
- PI ≤ 0.15 mm total in the bend zones
- Stiffener only on the contact end, sized for FH12 insertion
- No components on the tail
- Free length ≥ 16.5 mm, including a ≥ 2.5 mm flat Z-fold
- CTP on a separate, also-thin tail or combined into the 22-pin I2C lines
- Request the drawing, stack-up and the driver IC / DT overlay

## 3. Camera FPC (J4, CM5 CSI)
| Item | Requirement / finding | Source |
|---|---|---|
| Module | Haozhou **HZ-OV5647AF S1.0**, OV5647, MIPI CSI, $2.5–3, MOQ 1, 7–15 workdays | [ChinaX listing](https://www.chinax.com/cmoscameramodules/c2042731-raspberry-pi-camera-module) |
| Module connector (stock) | **15-pin MIPI CSI connector** (Pi 1–4 style, 1.0 mm) on the Haozhou family listing. "Autofocus/fixed focus … support customization" | [Haozhou OV5647 listing](https://www.cmoscameramodules.com/sale-53445134-5mp-mipi-camera-module-ov5647-raspberry-pi-camera-module-ff-1080p-wide-angle-mipi-csi.html) |
| Required at J4 | **22-pin, 0.5 mm pitch FPC (RPi 22-pin CSI standard, as on Pi 5 / Zero / CM IO boards)**, about **14 mm** long, U-fold per keepouts_v4_22c (1.55 mm available ≥ 0.9 needed) | keepouts_v4_22c J4 row |
| 22-pin pinout | Use the **Raspberry Pi 22-pin camera standard**: 2-lane/4-lane D-PHY pairs with interleaved GND, plus CAM GPIO, I2C SCL/SDA and 3.3 V. **See §4 (VERIFIED from the CM5 IO Board KiCad files)**. The OV5647 uses 2 data lanes | RPi CM5 IO board schematic (to fetch) |
| Impedance | MIPI D-PHY differential pairs: **100 Ω differential** nominal is the D-PHY norm. **VERIFIED (§5): CM5 datasheet §2.5.2 requires 100 Ω differential, P/N matched within 0.15 mm**. Keep pairs length-matched and GND-shielded on a 1-layer + GND or 2-layer FPC | to cite from the CM5 datasheet |
| Sources | (a) **Vendor custom:** Haozhou says customization is supported. Ask for the AF module with a 22-pin 0.5 mm × about 14 mm tail directly. (b) **Separate jumper:** a stock 15-to-22-pin adapter FPC (e.g. the type Waveshare specifies for Pi 5 22-pin connectors, [Waveshare note](https://www.waveshare.com/catalog/product/view/id/3595/s/rpi-ir-cut-camera-b/category/37/)). Its length and thickness are unlikely to fit the 14 mm U-fold, so **prototype only** | listings |

**Camera verdict:** the stock module (15-pin) does **not** plug into J4. Order the **vendor-custom 22-pin 0.5 mm, about 14 mm tail** (preferred). Use a 15→22 jumper only on the bench.

## 4. VERIFIED: RPi 22-pin MIPI connector pinout (resolves the VERIFY above)
**Source:** Raspberry Pi Ltd, *CM5 IO Board, revision 2, KiCAD files* (RP-008099-DD-1, [pip.raspberrypi.com Design Files](https://pip.raspberrypi.com/categories/1098-design-files), updated 6 Oct 2025).
- Sheet **CM5_HighSpeed, sheet 2/4, "Rev: 1"** in the title block. Sheet-1 labels: "CSI/DSI 0" (J5) and "CSI/DSI 1" (J16).
- Pinout taken from the netlist I exported with kicad-cli 9 from `CM5IO.kicad_sch`.
- Connector **J5, J16 = Hirose FH12-22S-0.5SH(55)** (Mouser 798-FH12-22S-0.5SH55). That is 22-position, 0.5 mm, **bottom contact**, SMT right-angle. The 22-pin standard is identical for CSI and DSI: the CM5 MIPI0/1 ports are dual-purpose.

| Pin | Signal | Pin | Signal |
|---|---|---|---|
| 1 | GND | 12 | D2_P |
| 2 | D0_N | 13 | GND |
| 3 | D0_P | 14 | D3_N |
| 4 | GND | 15 | D3_P |
| 5 | D1_N | 16 | GND |
| 6 | D1_P | 17 | CAM_GPIO0 (J5) / 2.2 kΩ pull-up to 3V3 (J16, via R8) |
| 7 | GND | 18 | CAM_GPIO1 (J5) / NC (J16) |
| 8 | C_N (clock) | 19 | GND |
| 9 | C_P (clock) | 20 | SCL (SCL0 on J5 / SCL1 on J16) |
| 10 | GND | 21 | SDA (SDA0 on J5 / SDA1 on J16) |
| 11 | D2_N | 22 | +3.3 V |

Signal names are DPHYx_*. For a 2-lane device (OV5647, 2-lane DSI panel), D2/D3 are unused and can be left open or grounded on the device side.

## 5. VERIFIED: impedance
*Raspberry Pi Compute Module 5 Datasheet*, Release 3 (build 08/06/2026), §2.5.2 "MIPI (CSI and DSI)", p.10: **"The MIPI signals must be routed as 100 Ω differential pairs. Within a pair, the signals should be length-matched within 0.15 mm."**
- This applies to our carrier traces and to custom FPC tails.
- The datasheet sets no tolerance. Proposed ±10%, a common fab default (EST).

## 6. Vendor contacts
| Vendor | Contact | Verified? |
|---|---|---|
| **Ronbo Electronics Ltd** (primary) | **agatha@ronboe.com**, +86 13760194392 (Mon–Fri 9:00–18:00 CST). 15H2, Block A, Guanghao International Center, Minzhi, Longhua, Shenzhen. [ronboe.com/contact](https://www.ronboe.com/contact/) | ✅ Fetched live from ronboe.com on 2026-10-21. The site footer also lists rongfa.chen@ronboe.com (search index only, not re-checked). Store: [MIC](https://ronboelectronics.en.made-in-china.com/) |
| **Shenzhen Lida Screen Co., Ltd** (alternate; LD043DSI 4.3" DSI, "can customize FPC pin sequence") | **No published email found.** Use the "Contact Now" form on the official store [lida-screen.en.made-in-china.com](https://www.made-in-china.com/showroom/lida-screen/product-detailmFwTsDCAkSVk/China-4-3inch-Mipi-Dsi-LCD-Module-800X480-with-Capacitive-Touch-for-Raspberry-Pi.html). Address: No. 35 Baomin 2nd Rd, Liutang, Xixiang, Shenzhen | ⚠️ Email **UNVERIFIED / none**. The contact page is JS-rendered and could not be read. Do not confuse with *Nanyang* Lida Optic-electronics (lida@lida-oe.com.cn), a different company |

## 7. Display RFQ (paste-ready, not sent)
**To:** agatha@ronboe.com (Ronbo). The same text goes to Lida Screen via the MIC form.
**Subject:** RFQ: custom 4.3" 800×480 IPS MIPI-DSI CTP module with thin 22-pin tail (PocketMate, samples / 1k / 10k yr)

> Dear Ronbo team,
>
> We are developing PocketMate, a handheld device on the Raspberry Pi Compute Module 5. We would like a quotation for a custom version of your 4.3" DSI display (ref. MPI4303).
>
> **Panel:** 4.3" 800×480 IPS, **native MIPI DSI, 2-lane** (DSI driver IC on glass/COF, no bridge PCB). Capacitive touch (5-point) over **I2C**. Please state the driver IC and touch IC and supply a Linux DT/panel init sequence.
>
> **Custom FPC tail (mandatory):**
> 1. Ends in a **22-pin, 0.5 mm pitch** contact for a Hirose **FH12-22S-0.5SH** (bottom-contact) on our board.
> 2. **Raspberry Pi 22-pin DSI pinout:** 1 GND, 2 D0_N, 3 D0_P, 4 GND, 5 D1_N, 6 D1_P, 7 GND, 8 CLK_N, 9 CLK_P, 10 GND, 11 D2_N, 12 D2_P, 13 GND, 14 D3_N, 15 D3_P, 16 GND, 17 GPIO0, 18 GPIO1, 19 GND, 20 SCL, 21 SDA, 22 +3.3 V. D2/D3 unused (2-lane). Touch on pins 20/21. Touch INT/RST on 17/18 if needed: please propose.
> 3. **Total FPC thickness ≤ 0.15 mm** in all bend and run zones.
> 4. **Stiffener only on the contact end, inside the connector.** No stiffener elsewhere.
> 5. **Nothing mounted on the tail** (no components or bridge parts).
> 6. **Free length ≥ 16.5 mm** from the glass edge to the connector contact start. It must include a **flat service Z-fold of ≥ 2.5 mm** and survive a 180° fold at the glass edge (R ≥ 0.72 mm).
> 7. MIPI pairs **100 Ω differential**, P/N matched within 0.15 mm, ground-referenced.
>
> **Quantities:** 5–10 samples; 1,000 pcs; 10,000 pcs/year.
>
> **Please provide:**
> - Outline and FPC drawing with stack-up
> - Price breaks at the above quantities
> - Tooling/NRE
> - Sample and mass-production lead times
> - MOQ and datasheet
>
> Best regards,
> Anand Mohan Pandey
> PocketMate
