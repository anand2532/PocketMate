# PocketMate: BOM v2, India-first (2026-10-21)
**Targets (PM/Anand):** retail under ₹30,000 (about $350), BOM about **$120–150 at volume**. Prices come from the cited pages. **EST** marks estimates. FX used only for totals: ₹88 ≈ $1, £1 ≈ $1.33, CHF 1 ≈ $1.25, €1 ≈ $1.16 (**all FX are estimates**).

## 1. Compute module and Raspberry Pi volume path
| Option | Price found | Source |
|---|---|---|
| CM5104032 (4GB/32GB eMMC/Wi-Fi), **India** | **₹15,000** (in stock) | [Silverline Electronics](https://www.silverlineelectronics.in/collections/raspberry-pi-compute-module-5) |
| CM5104032, US/EU | **$140 official list** ([RPi product brief RP-008181-DS-11, Sept 2026](https://pip-assets.raspberrypi.com/categories/944-raspberry-pi-compute-module-5/documents/RP-008181-DS-11-cm5-product-brief.pdf)). Resellers: $129 DFRobot, $134.99 Central Computer ([listing](https://www.centralcomputer.com/raspberry-pi-cm5104032-compute-module-cm5-4gb-ram-32gb-emmc-wireless.html)), €152 incl. VAT / €148.20 at 250+ ([Welectron](https://www.welectron.com/Raspberry-Pi-Compute-Module-CM5104032-32GB-4-GB-RAM-WiFi)) | see §0 price note |
| CM5102032 (2GB/32GB/Wi-Fi), India | ₹9,690 | Silverline |
| CM5102000 (2GB Lite/Wi-Fi), India | ₹7,145 | Silverline |
| CM5104016 (4GB/16GB/Wi-Fi) | listed at Silverline, price not captured | Silverline |
| CM5004000 (4GB Lite, **no wireless**) | $100 | [PiShop](https://www.pishop.us/product-category/raspberry-pi/raspberry-pi-boards/compute-modules/compute-module-5/) |

**Volume quote path:**
1. **Silverline Electronics, Bengaluru.** It describes itself as "the only Approved Raspberry Pi channel partner in India" ([site](https://www.silverlineelectronics.in/)). Ask for a 1k CM5104016/CM5104032 quote, delivered and GST-invoiced.
2. **Raspberry Pi direct for business.** Raspberry Pi says business buyers can purchase certain products directly ([reseller page](https://www.raspberrypi.com/resellers/?country=1&q=india)). Submit an OEM enquiry for 1k–10k.
3. **element14 India.** It sells CM5 ([element14 IN](https://in.element14.com/authorised-resellers)), but its approved status was not confirmed.
4. **Robu.in** says it is an "official distributor" but does not appear in the results from the official reseller list ([Robu](https://robu.in/product-category/raspberry-pi-microcontroller-development-board/)). Confirm before buying.
5. **Raspberry Pi Design Partners:** no India-based partner was found. Check raspberrypi.com/partners (not fetched).

## 2. Cost-down substitutions
| Item | v1 | v2 (cost-down) | Fit / risk |
|---|---|---|---|
| Display | Waveshare $34.97 at 100+ | **Ronbo MPI4303** 4.3" 800×480 IPS DSI, 5-point CTP, 400 cd/m², 106.0 × 68.0 mm: **$17.50 at 1k**, $18.50 sample ([Made-in-China](https://ronboelectronics.en.made-in-china.com/product/YOgGSAkPhacj/China-Mipi-Dsi-Input-4-3-Inch-IPS-800X480-Raspberry-Pi-4b-3b-Capacitive-Touch-LCD-Screen.html)). Alternate: Lida LD043DSI, 106 × 68 × 8 mm, 500 cd/m², $22–23 ([Lida](https://www.made-in-china.com/showroom/lida-screen/product-detailmFwTsDCAkSVk/China-4-3inch-Mipi-Dsi-LCD-Module-800X480-with-Capacitive-Touch-for-Raspberry-Pi.html)) | 68 mm is under 75 ✅ (matches the PM's 67.8 mm glass decision). Glass-only panels at $3.50–3.90 exist but use an MCU interface, not DSI ([listing](https://laserlcd.en.made-in-china.com/product/UERpzycOqAYr/China-Custom-Mipi-Dsi-480X800-IPS-TFT-Display-Screen-4-3-Inch-Touch-LCD-Display.html)). Driver-IC overlay on CM5 needs validation |
| Camera | Camera Module 3 (IMX708 AF) $25 | **OV5647 AF module, Shenzhen Haozhou HZ-OV5647AF S1.0**, MIPI CSI, **$2.50–3.00**, MOQ 1 ([listing](https://www.chinax.com/cmoscameramodules/c2042731-raspberry-pi-camera-module)). Arducam B0176 (OV5647 software AF), price not shown ([Arducam](https://www.arducam.com/arducam-ov5647-standard-raspberry-pi-camera-b0033.html)) | 5 MP vs 12 MP and no PDAF, so OCR quality drops. libcamera supports `ov5647`, but autofocus VCM support needs testing (VERIFY) |
| Battery | LP684875, quote needed | **RESKY LP705060**, 3000 mAh, 7 × 50 × 60 mm, MOQ 100, price negotiable ([listing](https://www.lithiumbatteriescell.com/sale-54125060-rechargeable-lipo-batteries-cell-705060-3000mah-3-7v-11-1wh-power-li-ion-polymer-battery-pack.html)). Indian-assembled packs: not found | Discharge only 0.5 C continuous, so get the 1–2 C version. **Quote required.** BIS IS 16046 registration is likely needed for sale in India (VERIFY) |
| Charger | BQ25895 (DigiKey 0) | **BQ25895 via LCSC** (5,634 in stock, $1.22 at 1k). Second source **BQ25896** ($1.65 at 1k) | see components.md "Charger/gauge alternates" |
| Gauge | BQ27441 (DigiKey 0) | **MAX17055** (LCSC 5,890, $0.99 at 1k) or **BQ27220** (LCSC 23,096, $0.34 at 1k) | same section |

## 3. Volume BOM (~1k)
**CM5 price note (resolved 2026-10-21).** The $70 figure was the Nov 2024 launch-era price; launch list ran $45 (no wireless/2GB/Lite) to $95 (wireless/8GB/64GB), per RPi staff on the [launch post](https://www.raspberrypi.com/news/compute-module-5-on-sale-now/). The current official brief (Sept 2026) lists **CM5104032 $140, CM5104016 $130, CM5104000 (Lite) $105, CM5004032 (no wireless) $135, CM5102032 $107.50, CM5102000 $72.50**. This BOM uses the current list.

| Item | ~1k USD | Basis |
|---|---|---|
| CM5104032 | **140.00** (official list, Sept 2026 brief). India: ₹15,000 ≈ $170 EST FX, qty 1 | no published volume price, quote via path above |
| 2× Amphenol 10164227-1001A1RLF | 1.90 | Findchips 5k |
| Display, Ronbo MPI4303 | 17.50 | 1k price |
| Camera, OV5647 AF | 3.00 | top of $2.5–3 range |
| 2× I2S mic (ICS-43434, NRND) | 6.19 | DigiKey 10k |
| MAX98357A | 1.45 | ADI 1k list |
| CMS-15118D-L100 speaker | 2.10 | CHF 1.676 at 1k |
| BQ25895RTWR | 1.22 | LCSC 1k |
| TPS61088RHLR | 1.36 | DigiKey |
| MAX17055EWL+T | 0.99 | LCSC 1k |
| STUSB4500QTR | 1.22 | ST at 500 |
| STM32U031K8U6 | 1.50 | ST at 500 |
| DRV2605L + VG0832012 LRA (from best pass) | 0.76 + LRA (no price) | LCSC 1k |
| Battery LP705060 | **quote** | – |
| Passives, connectors, buttons, antenna | **EST 6** | estimate |
| PCB + assembly | **EST 12** | estimate. JLCPCB 4L $91/m² fab rate ([JLCPCB](https://jlcpcb.com/v)) |
| Enclosure (injection moulded, tooling not amortized) | **EST 9** | estimate |
| Thermal pad + spreader | **EST 2** | estimate |
| **Total, excluding battery and LRA** | **≈ $208** (was $197 at $129) | |

**Against the $120–150 target: missed by about $58–88.** The CM5 alone ($140) is 93–117% of the target. Everything else costs about $68.
- **Using CM5102032 (2GB/32GB/Wi-Fi, $107.50 official list; ₹9,690 India)** would cut $32.50. Total ≈ $175. CM5104016 (4GB/16GB/Wi-Fi, $130) saves $10 if 16 GB eMMC is enough. But 2 GB rules out gemma-1b plus STT plus UI headroom (gemma3:1b alone is about 1.4 GB).
- **Hitting about $150 needs a CM5 4GB at about $82 or less.** Only a Raspberry Pi OEM quote can confirm whether that is possible. Otherwise move to $150–200 and price at the top of the ₹30k band.
- **Retail check:** ₹30,000 including 18% GST is ₹25,424 ex-GST ≈ $289 EST FX. A $208 BOM is **72%** of net retail, which leaves no channel or warranty margin. A typical BOM of about 30–40% of net retail would be $87–116.

## 4. India import duty + GST (estimates, confirm with a customs broker or CA)
| Goods | HS | BCD | SWS | IGST | Source |
|---|---|---|---|---|---|
| Processors/controllers, memories, amplifier ICs | 8542 31/32/33 | **0%** | 0 | 18% | [Cybex](https://www.cybex.in/indian-custom-duty/electronic-integrated-circuits-microassemblies-hs-code-8542) |
| ICs "other" (8542 39) | 8542 39 00 | 7.5% | 10% of BCD | 18% | same |
| Mobile-phone PCBA, camera-module and connector inputs | various | NIL since 2025-02-02 (was 2.5%), mobile-phone end use only | – | 18% | [Notif. 10/2025-Cus](https://taxguru.in/custom-duty/budget-2025-changes-bcd-rates-mobile-parts.html), [Indian Express](https://indianexpress.com/article/technology/tech-news-technology/union-budget-2025-import-duties-smartphone-sub-parts-9811924/) |
| Li-ion cells/packs | 8507 60 00 | **15%** (TradePrep) or 20% (Comercinate), sources disagree | 10% of BCD | 18% | [TradePrep](https://tradeprep.in/hs/85076000) ("total effective 37.47%"), [Comercinate](https://comercinate.com/hsn-code/85076000/) |
| Finished device as a portable computer (if classified there) | 8471 30 10 | 0% | – | 18% | [TariffCheck](https://www.tariffcheck.in/hs/84713010). **Classification is uncertain**: a voice-assistant device may fall under 8517/8543 at higher BCD |
| Display open cells | – | 5% (open cells for IFPD/TV context) | – | 18% | Indian Express above. A complete 4.3" LCM is likely classified differently, so VERIFY |

**Effect on BOM (EST):**
- With assembly in India and parts imported: most ICs are at 0% BCD. The CM5 module itself needs classification (likely 8471 50/8473 30, VERIFY).
- The battery adds about 16.5–22% landed duty (BCD + SWS). On an EST $5–8 cell that is about $1–2.
- IGST at 18% is an input tax credit for a GST-registered manufacturer and is offset against the 18% output GST (general GST rule, confirm with a CA).
- **Net duty uplift on the BOM: EST about 1–3%**, if the CM5 and display land at 0–5% BCD.
- **Importing the finished device instead** would be 18% IGST, plus BCD from 0% to 20% depending on classification.
- Compliance costs that are not priced here: BIS CRS (battery and adapter), WPC/ETA (Wi-Fi/BT), TEC if classified as telecom.

---
## 5. Finished-unit import vs local assembly (India)
| Route | Duty basis | Source |
|---|---|---|
| **Import finished units** | **PM market input: 40–50% total duty on finished devices.** If the device can be classified as a portable ADP machine (HS 8471 30 10), the published rate is **0% BCD + 18% IGST** ([TariffCheck](https://www.tariffcheck.in/hs/84713010)). Classifying it as an AI/voice device under 8517/8543 is where higher BCD would apply. **Conflict between the two figures: get a classification ruling (CAAR) before deciding** | PM / TariffCheck |
| **Local assembly in India** | Imported ICs: 0% BCD + 18% IGST, creditable ([Cybex](https://www.cybex.in/indian-custom-duty/electronic-integrated-circuits-microassemblies-hs-code-8542)). Li-ion cell: 15–20% BCD + SWS ([TradePrep](https://tradeprep.in/hs/85076000)) | §4 |

**Worked example** on the §3 BOM of ≈ $197 (computed at the old $129 CM5; at the $140 list the BOM is ≈ $208 and duty figures scale by about +6%), 18% IGST creditable in both cases. Factory and EMS costs are not included:
- Import finished at 40%: about +$79 per unit. At 50%: about +$99. Duty is on the CIF value of the finished unit, so real-world it is higher than this.
- Local assembly: about 1–3% ≈ +$2–6 (EST), plus Indian EMS labour (not priced).

**Verdict: assemble in India** (SKD/CKD kit or full local SMT). The duty saving is about $70–95 per unit, which is larger than any part-level saving found. It also helps any later PLI or "Make in India" positioning (not evaluated).

## 6. BIS registration (CRS, Scheme-II)
| Item | Standard | Fees | Timeline | Source |
|---|---|---|---|---|
| Li-ion **cell** and **battery pack** (registered separately) | IS 16046 (Part 2):2018 | Government fees since 2026-02-25: ₹1,000 application, **₹25,000 per year** processing, ₹20,000 per additional test report, ₹30,000 per post-grant request. MSME concession up to 80% until May 2029 | **20 working days** after a complete application. Lab testing comes first and is not included | [BIS FAQ](https://www.crsbis.in/BIS/app_srv/tdc/gl/docs/FAQs-Cells-and-Batteries-14-Nov.pdf), [BIS how-to](https://www.crsbis.in/BIS/howtoapply.do), [fee summary](https://www.techbydr.com/compliance-watch/2026-02-25-crs-scheme-ii-fees-msme-concession-2029/) |
| Consultant quote, battery | – | ₹62,540 per fresh application (outside India, incl. GST). Inclusion ₹35,400 | 20–25 working days | [ASC Group](https://www.ascgroup.in/bis-crs-certification-for-sealed-secondary-cells-batteries-containing-alkaline-or-non-acid-electrolytes/) |
| **Power adapter** (only if bundled) | IS/IEC 62368-1:2023 ("Power Adaptors for IT Equipments") | same CRS fees | same | [BIS Scheme-II](https://www.bis.gov.in/product-certification/products-under-compulsory-certification/scheme-ii-registration-scheme/?lang=en) |
| The device itself | Likely IS/IEC 62368-1 if classed as ADP machine or tablet (VERIFY scope) | same | same | same |

- Notes: registration lasts 2 years, then renewal. Foreign applicants need an Authorized Indian Representative. Lab test costs were not found.
- **Recommendations:**
  - **Ship without an adapter** (USB-C PD, user-supplied) to avoid a second registration.
  - Use a cell and pack vendor that **already holds an IS 16046 registration**, so you only do a model inclusion.
- **Budget (EST):** about ₹1–2 lakh plus lab testing per registered item. Allow 2–3 months including testing (EST).

## 7. Thermal analysis at 45 °C ambient (Indian summer)
**Sourced facts:**
- **CM5 throttling:** soft throttling of the ARM cores from 80 °C, by 100 MHz per °C (a Raspberry Pi engineer on the forum). Hard throttling of ARM and GPU at 85 °C. Firmware holds the SoC below 85 °C ([RPi docs](https://github.com/raspberrypi/documentation/blob/master/documentation/asciidoc/computers/raspberry-pi/frequency-management.adoc), [forum](https://forums.raspberrypi.com/viewtopic.php?t=368073)).
- **CM5 has less heat-sinking copper than a Pi 5.** Operating range is −20 to +85 °C, and Wi-Fi works best at 75 °C or below ([CM5 datasheet](https://pip-assets.raspberrypi.com/categories/944-raspberry-pi-compute-module-5/documents/RP-008180-DS-7-cm5-datasheet.pdf?disposition=inline)).
- Raspberry Pi advises against relying on protective throttling and recommends underclocking where airflow is limited ([CM5 thermal white paper](https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-009520-WP-1-Thermal%20modelling%20of%20Raspberry%20Pi%20Compute%20Module%205.pdf)).
- **Passive cooling is insufficient for heavy loads beyond 200–300 s** on a Pi 5 at room temperature ([RPi blog](https://www.raspberrypi.com/news/heating-and-cooling-raspberry-pi-5/)).
- **Skin limits** (IEC 62368-1 TS1, from ISO 13732-1): **48 °C for contact over 1 min, 43 °C for over 8 h**, for both metal and plastic ([UL brief](https://japan.ul.com/wp-content/uploads/sites/27/2014/06/1_techbrief_touchtemp.pdf)). The Japanese mobile guideline MCPC TR-023 uses metal 51 °C/1 min, 48 °C/10 min, 43 °C/8 h, tested at **35 °C ambient** ([MCPC](https://www.mcpc-jp.org/news/doclist/(3)TR-023_Ver.3.00.pdf)).
- **JEITA:** no charging below 0 °C or **above 45 °C** cell temperature. Between 40 and 45 °C, charge with reduced voltage and current ([TI SLYT365](https://www.ti.com/lit/an/slyt365/slyt365.pdf)). The BQ25895 has TS/JEITA NTC support ([datasheet](https://www.ti.com/lit/ds/symlink/bq25895.pdf)).

**Dissipation estimate (EST, my calculation, not sourced; validate with a thermal prototype):**
- Enclosure surface is 2 × (125 × 75) + 2 × (125 + 75) × 20 mm² ≈ **0.027 m²**.
- Assumed combined natural convection plus radiation h ≈ **8–10 W/m²·K** (typical textbook range for still air; an assumption).
- Even with a perfect pad to the aluminium frame, the frame cannot be cooler than the case skin. So **sustained power ≈ h × A × (T_skin − T_ambient)**.

| Ambient | Skin limit | ΔT | Sustained power (EST) |
|---|---|---|---|
| 25 °C | 43 °C (8 h) | 18 K | ≈ 3.9–4.9 W |
| 35 °C (MCPC test) | 48 °C (>1 min) | 13 K | ≈ 2.8–3.5 W |
| **45 °C** | **48 °C (>1 min)** | **3 K** | **≈ 0.6–0.8 W** |
| 45 °C | 43 °C (8 h) | −2 K | **0 W.** The limit is below ambient, so any heat breaks it |

**Implications:**
- At 45 °C ambient, the hand-held skin limit, not CM5 throttling, is what limits the device. Sustained CM5 compute (LLM inference at several watts) cannot stay within 48 °C skin while held.
- The SoC itself (limit 85 °C) has about 40 K of headroom above ambient, so it will run, just throttled.
- **Charging:** at 45 °C ambient the cell will be at or above 45 °C, so **JEITA blocks charging**. Even at 40–45 °C, charging is derated.

**Recommendations:**
1. Add a **thermal governor** in firmware. Use the case NTC plus SoC temperature to cap ARM frequency (`arm_freq` / cpufreq) so that skin stays at 48 °C or below. Run LLM and OCR in bursts of 30 s or less with cool-down periods, and offload to the cloud (with user consent) when hot.
2. **Place an NTC on the cell and one on the case.** Wire the cell NTC to the BQ25895 TS pin with the JEITA profile enabled. Show the user a "too hot to charge" state.
3. **Use the aluminium frame as a spreader, but keep the hand-contact areas plastic or rubber** (TS1 short-contact limits are higher for plastic: 60 °C for 10 s–1 min).
4. Rate the product **"operating 0–40 °C, charging 10–40 °C"** (EST rating, to be set after testing) and document the derating.
5. Before a design freeze, build a **45 °C chamber test**: SoC temperature, skin map and charge behaviour.

## 8. Lower SKU: ₹17,999–24,999
| Cost-out | Saving | User loses | Source |
|---|---|---|---|
| CM5104032 → **CM5102032** (2GB/32GB/Wi-Fi) | ₹15,000 → ₹9,690 = **₹5,310** | gemma3-1b (about 1.4 GB) plus STT plus UI is tight. Practically limited to qwen2.5-0.5B (about 400 MB, 33.8 tok/s on Pi 5 2GB) and tiny.en STT, so weaker answers. Less memory and search headroom | [Silverline](https://www.silverlineelectronics.in/collections/raspberry-pi-compute-module-5), llama.cpp #30069 |
| → **CM5102000** (2GB Lite/Wi-Fi) + microSD | ₹15,000 → ₹7,145 = **₹7,855** (minus the microSD cost, not priced) | Same as above, plus slower and less durable storage. The PRD allows eMMC or microSD | Silverline |
| Camera OV5647 AF (already in v2) | – (v1 to v2 saved about $22) | 5 MP, no PDAF. OCR on small print is worse | §2 |
| Smaller cell (e.g. 2000 mAh) | quote needed | Shorter runtime | – |
| No haptics | ≈ $0.76 + LRA | No tactile confirmation for push-to-talk and mute | LCSC |
| MAX17048 instead of MAX17055 | ≈ $0.99 → (MAX17048 has no 1k LCSC price; DigiKey is $1.79 at 10k, so no saving) | Loses mAh and time-to-empty readings | – |
| Cloud-first models | $0 | Needs network; weaker offline/privacy story | – |

- **Lower-SKU BOM (EST):** §3 ≈ $208 − CM5 saving (₹5,310–7,855 ≈ $60–89 EST FX) − haptics ≈ **$118–148**, battery excluded.
- At ₹17,999–24,999 including GST, net retail is ₹15,253–21,186, about $173–241 (EST FX). That puts BOM at roughly 57–62% of net retail at either end of the range: still thin, but closer.
- **Recommendation:** use the 2GB/32GB eMMC module for the lower SKU. Market it as "cloud-assisted", with offline notes, search, OCR and tiny-model voice. Keep the 4GB SKU at ₹29,999.
