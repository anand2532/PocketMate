# PocketMate: Component Research v1
Date: 2026-10-21 · Target: CM5 4GB (CM4 as the alternate) · Enclosure from the PRD: about 125 × 75 × 18–24 mm, 200–300 g. **Compactness is the priority.**

Rules: every part number, price and size below comes from the cited page. Anything I could not confirm says **VERIFY**. Prices are list or distributor prices as of the dates shown on those pages.

---
## 0. CM5 module and board-to-board connectors
- CM5 is 40 × 55 mm. The bare module is 4.6 mm deep. Mounted height is 4.94 mm or 7.44 mm, depending on the connector. PCB 1.24 mm. Four M2.5 holes, inset 3.5 mm. [CM5 datasheet](https://pip-assets.raspberrypi.com/categories/944-raspberry-pi-compute-module-5/documents/RP-008180-DS-7-cm5-datasheet.pdf?disposition=inline)

| Part (carrier side, 2 per board) | Stack height | Clearance under CM5 | Footprint (A × B) | Notes |
|---|---|---|---|---|
| Amphenol BerkStak **10164227-1001A1RLF** | 1.5 mm | none | – | Officially specified for CM5 and tested for CM5 current |
| Amphenol BerkStak **10164227-1004A1RLF** | 4.0 mm | 2.5 mm | – | Officially specified. Lets you place parts under the CM5 |
| Hirose **DF40C-100DS-0.4V(51/58)** | 1.5 mm | none | 22.6 × 19.6 mm | The CM4 part. Raspberry Pi engineers say it mates mechanically but was "not tested" for CM5 currents and they use it in development only ([forum](https://forums.raspberrypi.com/viewtopic.php?t=387843)) |
| Hirose **DF40HC(3.0)-100DS-0.4V(51/58)** | 3.0 mm | – | 22.6 × 19.6 mm | The CM4 tall option ([DF40 catalog](https://www.hirose.com/en/product/document?clcode=&documentid=en_DF40_CAT&documenttype=Catalog&lang=en&productname=&series=DF40)) |

**Recommendation:** use Amphenol 10164227-1001A1RLF (1.5 mm) to keep the stack thinnest. Use the Hirose DF40C only if you are reusing a CM4 carrier. Prices and stock: VERIFY at DigiKey or Mouser.

## 1. Display (4.3", 800×480+, IPS, capacitive, DSI)
| Candidate | Specs | Size | CM5 notes | Price |
|---|---|---|---|---|
| **Waveshare 4.3inch DSI LCD** ([wiki](https://www.waveshare.com/wiki/4.3inch_DSI_LCD), [product](https://www.waveshare.com/product/4.3inch-dsi-lcd.htm), [panel spec](https://files.waveshare.com/upload/1/16/4.3inch_IPS%EF%BC%88P%EF%BC%89%281%29.pdf)) | 800×480 IPS, 160°, 5-point capacitive touch (I2C), 6H glass, 60 Hz, software backlight | Bare panel 105.50 × 67.20 × 2.80 mm, active area 95.04 × 53.856 mm | Wiki lists Pi5/CM5 support and says it is driver-free. Connect to DSI1 with the 22-pin cable. CMs do not auto-detect DSI, so add `dtoverlay=vc4-kms-dsi-waveshare-panel,4_3_inch` (from an AskUbuntu report). On Pi 5 the DSI output sits on RP1, a separate DRM node | VERIFY |
| **Waveshare 4.3inch DSI QLED** ([wiki](https://www.waveshare.com/wiki/4.3inch_DSI_QLED)) | 800×480 QLED-IPS, 78% NTSC gamut vs 50% for IPS | Same family | Wiki lists Pi5/CM4. CM5 support is implied, VERIFY | VERIFY |
| **Waveshare 43H-800480-IPS (CT-B)** ([wiki](https://www.waveshare.com/wiki/43H-800480-IPS)) | 800×480, 300 cd/m², 1200:1 contrast, lightweight bare-module series | Display 105.42 × 67.07 × 2.90 mm. Touch versions 112.40 × 75.10 × 5.00 mm or 106.10 × 67.80 × 5.20 mm | Wiki lists Pi 4/CM3/CM4. Pi 5/CM5 not listed, VERIFY | VERIFY |
| Raspberry Pi Touch Display 2, 5" (reference) ([docs](https://www.raspberrypi.com/documentation/accessories/touch-display-2.html)) | 720×1280 TFT (not IPS on the 5"), 500 cd/m², overlay params `sizex`/`sizey`/`swapxy` | 91.5 × 143.5 × 16 mm | First-party and supported until 2030 or later | $40 list |

⚠ **Fit:** the 67 mm bare panel fits the 75 mm width. The 75.10 mm touch-glass variant does **not** fit inside 75 mm walls. Choose the 67.8 mm-tall glass, or make the enclosure about 80 mm wide.
**PM DECISION (2026-10-21): use the 106.10 × 67.80 × 5.20 mm touch-glass variant and keep the enclosure 75 mm wide.** Prototype: Waveshare 4.3inch DSI LCD, $35.39 at qty 1–9 and $34.97 at 100+ ([Waveshare](https://www.waveshare.com/product/4.3inch-dsi-lcd.htm)).

## 2. CSI autofocus camera
| Candidate | Specs | CM5 notes | Price |
|---|---|---|---|
| **Raspberry Pi Camera Module 3 (IMX708)** ([news](https://www.raspberrypi.com/news/new-autofocus-camera-modules/)) | 12 MP, 4608×2592, PDAF+CDAF, 5 cm minimum focus (10 cm on Wide), 66° or 102° HFoV, HDR, 1080p50 | Native libcamera support. Board is the same size as V2 (about 25 × 24 mm, VERIFY on the mechanical drawing). Needs a 22-pin mini FPC on CM5 | $25 standard, $35 wide |
| **Arducam 16MP IMX519 AF, SKU B0371** ([product](https://www.arducam.com/imx519-autofocus-camera-module-for-raspberry-pi-arducam-b0371.html), [docs](https://docs.arducam.com/Raspberry-Pi-Camera/Native-camera/16MP-IMX519/)) | 16 MP, 4656×3496, 1.22 µm, 1/2.53", PDAF+CDAF, 10 cm minimum focus | `camera_auto_detect=0` and `dtoverlay=imx519[,cam0]`. Autofocus control needs Arducam's libcamera build | $24.99 |

**Recommendation:** Camera Module 3 standard. It is first-party, has the closest minimum focus (helps document OCR) and needs no custom libcamera.

## 3. Dual digital MEMS microphones
| Candidate | Specs | Size | Pi notes | Price |
|---|---|---|---|---|
| **Knowles SPH0645LM4H** (I2S) on Adafruit #3421 ([product](https://www.adafruit.com/product/3421), [guide](https://cdn-learn.adafruit.com/downloads/pdf/adafruit-i2s-mems-microphone-breakout.pdf)) | 50 Hz–15 kHz, 1.6–3.6 V, bottom port, L/R select pin gives stereo on one data line | Chip: VERIFY on the datasheet | `dtoverlay=googlevoicehat-soundcard`, fixed 48 kHz. BCLK GPIO18, LRCL GPIO19, DOUT GPIO20 | $6.95 breakout |
| **TDK ICS-43434** (I2S) | Adafruit sells a breakout (guide above) | VERIFY | Same overlay | VERIFY |
| **PDM mic, Adafruit #3492** ([product](https://www.adafruit.com/product/3492)) | 1.8–3.3 V, 1–3.25 MHz clock, 0.6 mA, 61 dB SNR | Breakout 14.0 × 12.8 × 2.8 mm | The Linux PDM path on RP1/CM5 is not confirmed, VERIFY. Simpler options: route PDM to the companion MCU, or pick I2S mics | $4.95 |

⚠ Running an I2S mic and an I2S amp together: stock overlays conflict (whichever loads last wins, [forum](https://forums.raspberrypi.com/viewtopic.php?t=389717)). You need one custom combined overlay with shared BCLK/LRCLK, DIN on GPIO20 and DOUT on GPIO21.
**Recommendation:** two I2S mics (SPH0645LM4H or ICS-43434), set L/R, on one data line.

## 4. I2S class-D amp and speaker
| Candidate | Specs | Price |
|---|---|---|
| **Analog Devices MAX98357A** (Adafruit #3006, [product](https://www.adafruit.com/product/3006)) | Mono, 3.2 W into 4 Ω or 1.8 W into 8 Ω at 5 V, 2.7–5.5 V supply, 8–96 kHz, no MCLK needed, five selectable gains. `dtoverlay=max98357a` | $5.95 breakout |
| Second candidate (for example TAS2563 or MAX98360A) | Not researched in this pass. VERIFY | – |

Speaker: use a microspeaker of about 15–20 mm, 8 Ω, 1 W, under 4 mm thick. No specific part was verified yet. **Recommendation:** MAX98357A (the chip is a small WLP/TQFN, VERIFY the package) driving an 8 Ω microspeaker.

## 5. 1S charger with power-path
| Candidate | Specs | Notes |
|---|---|---|
| **TI BQ25895** ([datasheet](https://www.ti.com/lit/ds/symlink/bq25895.pdf), [checklist](https://e2e.ti.com/cfs-file/__key/communityserver-discussions-components-files/196/BQ25895_5F00_SchematicChecklist-V1p1.pdf)) | I2C, 3.9–14 V input, up to 5 A charge, power-path, boost OTG | Has no PD/CC stack, so pair it with §6. Set IINLIM after PD negotiation. Package size: VERIFY on the datasheet |

The CM5 wants a 5 V rail at up to about 5 A peak. From a 1S cell you need a 5 V boost or buck-boost after the charger. That part was not selected in this pass.

## 5b. Fuel gauges (separate parts)
| Part | Method | Package and size | Notes |
|---|---|---|---|
| **MAX17048** ([datasheet](https://media.digikey.com/pdf/Data%20Sheets/Maxim%20PDFs/MAX17048-49_Rev7_Nov2016.pdf)) | ModelGauge, no sense resistor | WLP 0.9 × 1.7 mm or TDFN 2 × 2 mm | 3 µA hibernate. Simplest option. Linux driver `max17040_battery` covers MAX17048 (VERIFY) |
| **TI BQ27441-G1** ([datasheet](https://www.ti.com/lit/ds/symlink/bq27441-g1.pdf)) | Impedance Track, 10 mΩ sense resistor | VSON-12, 2.5 × 4.0 mm | Most accurate, reports SoH. Mainline `bq27xxx_battery` driver |
| **onsemi LC709203F** ([datasheet](https://www.mouser.com/datasheet/2/308/1/LC709203F_D-2315014.pdf)) | HG-CVR, no sense resistor | WDFN8 3 × 4 mm or WLCSP9 1.60 × 1.76 mm | Adafruit breakouts exist |

**Recommendation:** BQ27441-G1 for accurate mAh and health reporting in the battery UI. Use MAX17048 if board area is tight.

## 6. USB-C PD sink
| Part | Specs |
|---|---|
| **ST STUSB4500** ([datasheet](https://www.st.com/resource/en/datasheet/stusb4500.pdf)) | Standalone auto-run sink up to 20 V/5 A, NVM PDOs, dead-battery support |
| **Hynetek HUSB238** ([datasheet](https://en.hynetek.com/uploadfiles/site/219/news/b038530d-67c0-4ba0-9269-de0e666cb35b.pdf)) | Standalone PD3.0 sink, legacy and Apple detection, I2C configuration. Small and cheap |

Package sizes and prices: VERIFY. **Recommendation:** STUSB4500 asking for 9 V, feeding the BQ25895.

## 7. Low-power companion MCU (always-on and wake)
| Part | Sleep current (source) | Notes |
|---|---|---|
| **ST STM32U0** ([series](https://www.st.com/en/microcontrollers-microprocessors/stm32u0-series.html)) | Marketed as best-in-class static consumption. Exact figure: VERIFY | Best fit for the power, button and RTC supervisor role |
| **Espressif ESP32-S3** ([datasheet](https://documentation.espressif.com/esp32-s3_datasheet_en.html)) | Deep sleep: VERIFY. The original ESP32 lists 10 µA | Includes Wi-Fi/BLE and a PDM input. Higher active power |
| **RP2040** ([whitepaper](https://pip-assets.raspberrypi.com/categories/685-app-notes-guides-whitepapers/documents/RP-004339-WP-1-Power%20switching%20RP2040%20for%20low%20standby%20current%20applications.pdf)) | About 180 µA typical in deep sleep | Not suitable for always-on unless you power-switch it |

**Recommendation:** STM32U0 handling the power button, CM5 enable/shutdown handshake, gauge alerts and the mic-mute LED.

## 8. Battery cell (enclosure 125 × 75 × ~20 mm)
Rough space budget: 125 mm length, minus about 70 mm under the display, leaves room beside or under the CM5. In practice the cell sits under the display and CM5. Plan for **about 60–70 × 50–60 × 6–8 mm** of space.

| Cell | Size | Capacity | Fit |
|---|---|---|---|
| **Adafruit #328** LiPo ([product](https://www.adafruit.com/product/328)) | 50 × 60 × 7.3 mm, 50 g | 2500 mAh, about 10 Wh, protected, JST-PH, 1.2 A max charge | ✅ Fits. Stack is about 7.3 mm cell + 1.6 mm PCB + 4.94 mm CM5 + 12.7 mm cooler, which is too tall when everything is stacked. Put the cell **beside** the CM5, not under it |
| **Adafruit #354** 2×18650 ([product](https://www.adafruit.com/product/354)) | 69 × 37 × 18 mm, 95 g | 4400 mAh | ❌ 18 mm thick. Fits only a 24 mm enclosure. Not compact, and the 2.2 A discharge limit is marginal |
| Generic 3000–4000 mAh pouch, about 6–8 × 60 × 70–90 mm (e.g. "606090" form) | – | – | Specific product not verified. VERIFY the vendor, protection board and discharge rating of at least 2 C |

CM5 draw from about 3.7 V may reach 2–3 A peak. Pick a cell rated for at least 1.5–2 C discharge. **Recommendation:** about a 3000 mAh, 7 mm pouch with a thermistor and PCM. Use Adafruit #328 for the prototype. Expect roughly 3–5 h of active use (an estimate, not measured).

## 9. Thermal
- **Raspberry Pi Cooler for CM5** ([product](https://www.raspberrypi.com/products/cooler/)): passive aluminium, 56 × 41 × 12.7 mm, silicone pad over the SoC, wireless module and PMIC, in production until 2036 or later. A review says sustained all-core load can still throttle ([bret.dk](https://bret.dk/raspberry-pi-compute-module-5-review-cooler-faster-better/)).
- **Compact alternative:** a 1–2 mm thermal pad plus a thin aluminium or copper spreader bonded to an aluminium back shell, using the case as the heatsink. This saves most of the 12.7 mm height. A 25–30 mm blower is optional (no part verified).
- **Recommendation:** bond the SoC to an aluminium mid-frame or back cover through a pad. Use the official Cooler only on the dev carrier. Cap sustained load with `arm_freq` and the governor, and keep inference bursts short.

## 10. Local models on CM5 4GB (Pi 5 figures, same BCM2712)
| Task | Model | Reported performance | Source |
|---|---|---|---|
| STT | faster-whisper tiny.en int8 | 1.15 s average latency on short clips (Pi 5 4GB) | [ACM paper](https://doi.org/10.1145/3769102.3774244) |
| STT | faster-whisper base.en int8 | 2.13 s on the same test. distil-small.en 4.90 s | same |
| TTS | Piper en_US-lessac-low | 0.53 s for one sentence (Pi 5 CPU) | [edge_tts_comparison](https://github.com/ktomanek/edge_tts_comparison) |
| TTS | Kokoro fp16 ONNX | 4.80 s for the same sentence, too slow for interactive use | same |
| LLM | Qwen2.5-0.5B Q4_0 (llama.cpp) | 33.8 tok/s generation, 290 tok/s prompt processing (Pi 5 2GB) | [llama.cpp #30069](https://github.com/ggml-org/llama.cpp/discussions/30069) |
| LLM | gemma3:1b Q4_K_M (Ollama) | 11.5 tok/s, about 1.4 GB RAM | [Stratosphere](https://stratospherelinuxips.readthedocs.io/en/develop/immune/research_rpi_llm_performance.html) |
| LLM | llama3.2:1b Q4_K_M | 11.2 tok/s | same |
| LLM | qwen2.5:1.5b Q4_K_M | 10.0 tok/s, about 1.85 GB | same |
| LLM | qwen2.5:3b Q4_K_M | 5.2 tok/s, about 3.0 GB (too tight on 4 GB) | same |
| OCR | Tesseract | 56 s cut to 4 s by resizing to 800 px wide (Raspberry Pi) | [derkuba.de](https://derkuba.de/posts/en/0625/tesseract-on-raspberry/) |
| OCR | PaddleOCR | 840 ms per plate on **Pi 4**. No Pi 5 figure found | [IEEE](https://doi.org/10.1109/comtech65062.2025.11034455) |
| Optional accelerator | Axera NPU (AXCL) on a Pi 5 host | Whisper-base RTF 0.11, Kokoro RTF 0.06, Qwen2.5-1.5B 16 tok/s | [AXCL docs](https://axcl-docs.readthedocs.io/en/latest/doc_guide_npu_benchmark.html) |

**Recommended local stack:** faster-whisper tiny.en/base.en int8, then gemma3-1b or qwen2.5-1.5b Q4 (llama.cpp), Piper TTS, and Tesseract or RapidOCR on cropped, resized camera frames. Cloud handles larger models when the user allows it.

---
## Summary BOM (recommended)
CM5 4GB + Amphenol 10164227-1001A1RLF ×2 · Waveshare 4.3" DSI 800×480 IPS (bare panel 105.5 × 67.2 × 2.8) · Pi Camera Module 3 · 2× SPH0645LM4H/ICS-43434 I2S · MAX98357A + 8 Ω microspeaker · STUSB4500 → BQ25895 → 5 V boost (not selected yet) · BQ27441-G1 (or MAX17048) · STM32U0 · about 3000 mAh 7 mm pouch (prototype: Adafruit #328) · SoC-to-frame thermal pad.

## Open VERIFY items (v1, see v2 closeout below)
Package sizes for BQ25895, STUSB4500, HUSB238 and MAX98357A · prices and stock at DigiKey/Mouser/LCSC · STM32U0 and ESP32-S3 sleep currents · CM5 Linux PDM support · CM5 display overlay on current Raspberry Pi OS · a specific about-3000 mAh pouch vendor · the 5 V boost part · speaker part.

---
# Charger/gauge alternates (2026-10-21, for the schematic engineer)
Design chain: STUSB4500 (PD sink) → charger VBUS → SYS → TPS61088 → 5 V to CM5. The charger's own OTG boost is not used, so OTG current does not matter.

**Key finding: BQ25895RTWR is in stock at LCSC.** 5,634 units at $2.1402 (qty 1) and $1.2188 (1k), part C80200 ([LCSC](https://www.lcsc.com/product-detail/C80200.html)). Only DigiKey is out of stock. **Keep BQ25895 as the primary part.** The alternates below are second sources.

## (a) Charger
| Part | Charge / input | Ship mode | Package | Stock / price | Differences vs BQ25895 |
|---|---|---|---|---|---|
| **BQ25895RTWR (primary)** | 5 A, 3.9–14 V | BATFET + QON | WQFN-24 4 × 4 mm | LCSC 5,634, $2.14 / $1.22 at 1k. DigiKey 0 | – |
| **BQ25896RTWR (alt 1, TI)** | **3 A**, 3.9–14 V, IINLIM 100 mA–3.25 A | BATFET ship mode, QON, 12 µA | WQFN-24 4 × 4 mm ([datasheet](https://www.ti.com/lit/gpn/BQ25896)) | LCSC 838, $2.94 / $1.65 at 1k ([LCSC](https://www.lcsc.com/product-detail/C181475.html)) | **Not pin-compatible.** BQ25896 has PSEL/ILIM pins where BQ25895 has D+/D−/DSEL. The register maps (REG00–REG14) are similar in structure but not interchangeable, so the driver needs per-part tables ([SensorLib map](https://lewisxhe.github.io/SensorLib/BQ25896Regs_8hpp.html)). Needs a separate footprint variant. 3 A meets the target |
| **Silergy SY6970QCC (alt 2)** | 5 A, 3.9–14 V, I2C, OTG | – (VERIFY BATFET/ship mode in datasheet) | QFN 4 × 4-24 | LCSC 32, $0.98 / $0.49 at 1k ([LCSC](https://www.lcsc.com/product-detail/C5357542.html)) | Commonly sold as a BQ25895-class replacement. **Pin and register compatibility is not confirmed by any source.** Get the datasheet before committing. Low stock |
| **SGMICRO SGM41513 / SGM41511** | 3 A, 3.9–13.5 V, I2C | BATFET (VERIFY) | TQFN-24 4 × 4 mm | LCSC SGM41513: 2,600, $1.27 / $0.71 at 100. SGM41511: 3,443, $1.27 ([LCSC](https://www.lcsc.com/brand/1005-280.html)) | A BQ25601-class part, not BQ2589x. **Different pinout and registers.** No D+/D− and no ADC (VERIFY) |
| SGM41542 | 3.78 A, BATFET ship mode via nQON ([datasheet](https://www.sg-micro.de/rect/assets/1e8de70b-657e-4156-be68-a64fdbe8e418/SGM41541_SGM41542.pdf)) | ✅ | TQFN-24 4 × 4 mm | **LCSC out of stock**, $1.70 | Rejected for now (stock) |
| TI BQ25611D | 3 A, 4–13.5 V, IINDPM up to 3.2 A | BATFET ship mode, 7 µA | WQFN-24 4 × 4 mm ([datasheet](https://www.ti.com/lit/ds/symlink/bq25611d.pdf)) | Stock not checked | Different family (BQ2560x registers). Input current limit 3.2 A at up to 13.5 V is fine with a 9 V PD source |
| BQ25890/92/98, BQ25601, BQ25672, ETA6973, IP2315 | not checked in this pass | | | | Open |

**Charger verdict:** Primary is **BQ25895** (LCSC stock). Second source is **BQ25896**: same family, 3 A, 4 × 4 footprint size. It needs its own pin-map variant and driver register table. Design the BQ25895 with D+/D− unused (STUSB4500 handles PD) so that a BQ25896 board variant is a small change. Tell firmware to set IINLIM after PD negotiation on either part.

## (b) Fuel gauge
| Part | Algorithm | Package | Stock / price | Differences vs BQ27441 |
|---|---|---|---|---|
| BQ27441DRZR-G1A (v1) | Impedance Track, 10 mΩ sense | VSON-12 2.5 × 4.0 mm | DigiKey 0 (due 2026-11-09) | – |
| **BQ27220YZFR** | CEDV coulomb counter, 10 mΩ sense, 50 µA normal / 9 µA sleep, SoH, external thermistor ([datasheet](https://www.ti.com/lit/ds/symlink/bq27220.pdf)) | DSBGA-9 1.62 × 1.58 mm | **LCSC 23,096**, $0.63 / $0.34 at 1k ([LCSC](https://www.lcsc.com/product-detail/C528617.html)) | Same TI I2C command style (0x55 address family, VERIFY). Different footprint (BGA). CEDV needs one full discharge to learn capacity. Parameters via GAUGEPARCAL/OTP. Linux `bq27xxx_battery` lists bq27220 (VERIFY on your kernel) |
| **MAX17055EWL+T** | ModelGauge m5 EZ: coulomb counter plus voltage model, 7 µA, no characterization needed, ageing reports ([ADI](https://www.analog.com/en/products/max17055.html)) | WLP-9 1.4 × 1.5 mm or TDFN-10 2 × 2.5 mm | **LCSC 5,890**, $1.39 / $0.99 at 1k ([LCSC](https://www.lcsc.com/product-detail/C2682627.html)) | Completely different register map from BQ27441. Needs a sense resistor. Mainline `max17042_battery` driver supports MAX17055 (VERIFY) |
| MAX17048G+T10 | ModelGauge (voltage only), no sense resistor, 3 µA hibernate | TDFN-8 2 × 2 mm | DigiKey 10,783, $5.02 / $1.79 at 10k | No current measurement, so it cannot report mAh, power draw or runtime-to-empty directly |
| BQ27421 | Impedance Track | – | not checked | Close relative of BQ27441, but chemistry must be checked with GPCCHEM ([TI E2E](https://e2e.ti.com/support/power-management-group/power-management/f/power-management-forum/1184042/bq27421-g1-differences-between-bq27421-and-bq27427)) |

**Is MAX17048 enough?** It is enough for a percentage battery icon and a low-battery alert. It is **not enough** for PocketMate's PRD goal of "battery monitoring" plus power and thermal tuning, because it measures no current and so gives no mAh, wattage or time-to-empty. **Pick: MAX17055** (in stock, needs no characterization, coulomb counting, ageing reports). **Alternate: BQ27220** (cheapest at $0.34, CEDV, BGA). MAX17048 remains a no-sense-resistor fallback.

---
# v2 closeout (2026-10-21)
Prices are as shown on the cited pages on that date. Currency is as listed (GBP/CHF/NOK come from regional DigiKey pages). Do not treat any of these as quotes.

## 5V boost (priority)
- **BQ25895's own boost is not suitable.** It gives 4.5–5.5 V at up to 3.1 A on PMID, but only in OTG/boost mode, which the device switches between with charge mode ([datasheet](https://www.ti.com/lit/ds/symlink/bq25895.pdf)). The CM5 is specified for 5 V at up to 5 A ([DFRobot spec](https://www.dfrobot.com/product-2893.html)).
- **Selected: TI TPS61088RHLR.** Synchronous boost with 10 A switch current, 2.7–12 V input, 4.5–12.6 V output, 1 µA shutdown current, VQFN-20 **4.50 × 3.50 mm**. It runs from the BQ25895 SYS rail ([datasheet](https://www.ti.com/lit/ds/symlink/tps61088.pdf)). DigiKey: 10,343 in stock, $1.364 ([Octopart](https://octopart.com/part/texas-instruments/TPS61088RHLR)).
- Design note: 3 A out at 5 V is about 15 W, which is about 4.5 A from the cell at 3.4 V. Set the peak current limit to suit the cell and limit CM5 USB current (`usb_max_current_enable` off, so peripherals are limited to 600 mA). Inductor and output capacitors are not yet selected.

## Speaker (priority)
- **Selected: Same Sky CMS-15118D-L100.** 15 × 11 × 3 mm, 8 Ω, 0.7 W rated (1 W max), 91 dB SPL at 0.7 W/0.1 m, 1.5 g, wire leads ([datasheet](https://www.sameskydevices.com/product/resource/cms-15118d-l100.pdf)). DigiKey 102-4343-ND: 327 in stock, CHF 3.59 at qty 1 and CHF 1.676 at 1k, 17-week lead time ([DigiKey CH](https://www.digikey.ch/en/products/detail/same-sky-formerly-cui-devices/CMS-15118D-L100/7404551)).
- Alternates on the same DigiKey listing: CMS-151135-078SP-67 (8 Ω, 700 mW), PUI AS01508AO-WP-R.
- Keep MAX98357A gain low. Into 8 Ω at 5 V it can deliver more than the speaker's 1 W limit (1.8 W at 10% THD).

## Battery cell (priority)
| Cell | Size | Capacity | Discharge | Protection | Source |
|---|---|---|---|---|---|
| **LiPol Battery LP684875 (selected)** | 6.8 × 48 × 75 mm | 3000 mAh, 11.1 Wh, about 60 g | 1.5 A standard, **3.0 A max**. PCM overcurrent trips at 4–4.5 A | PCM + 10 kΩ B3435 NTC, JST PHR-3 | [datasheet](https://www.lipoly-battery.com/wp-content/uploads/2024/05/LP684875-3000mAh-with-NTC-and-JST-PHR-3-lipo-battery-datasheet.pdf) |
| RESKY LP705060 | 7 × 50 × 60 mm, 65 g | 3000 mAh | 0.5 C continuous, 1 C max | PCM/NTC not stated | [listing](https://www.lithiumbatteriescell.com/sale-54125060-rechargeable-lipo-batteries-cell-705060-3000mah-3-7v-11-1wh-power-li-ion-polymer-battery-pack.html), MOQ 100, price negotiable |

- **Fit** (inside about 121 × 71 mm after 2 mm walls): lay the cell's 75 mm length along the enclosure's 125 mm axis. CM5 (40 along the length, 55 across) sits beside it: 75 + 40 = 115 mm, which is under 121 mm. Cross dimensions are 48 and 55 mm, both under 71 mm. ✅
- **Risk:** a 3 A maximum discharge, with about 4.5 A of cell current at a 15 W peak, is marginal. Either cap the CM5 load at about 10 W or ask the supplier for a 2 C cell in the same size. Price: **quote required** (none published).

## Package sizes, prices and stock
| Part | Package (size) | Qty 1 price | Volume price | Stock | Source |
|---|---|---|---|---|---|
| CM5104032 (4GB/32GB/Wi-Fi) | 55 × 40 × 4.7 mm module | $129 (DFRobot, limit 2). Seeed $140, out of stock. Welectron €152 incl. VAT | Welectron 250+: €148.20 | Limited | [DFRobot](https://www.dfrobot.com/product-2893.html), [Welectron](https://www.welectron.com/Raspberry-Pi-Compute-Module-CM5104032-32GB-4-GB-RAM-WiFi) |
| CM5004032 (no wireless) / CM5004000 (Lite) | same | $135 / $100 | – | Notify / in stock | [PiShop](https://www.pishop.us/product-category/raspberry-pi/raspberry-pi-boards/compute-modules/compute-module-5/) |
| Amphenol 10164227-1001A1RLF ×2 | 100-pos, 0.4 mm | Mouser $1.88. DigiKey NOK 15.81 | about $0.894–0.992 at 5k (other distributors) | DigiKey 151, Mouser 7,997 | [Findchips](https://www.findchips.com/search/10164227-1001A1RLF) |
| BQ25895RTWR | WQFN-24 4.00 × 4.00 mm | £2.52 | £1.338 at 3k | **DigiKey out of stock**, 2,964 due 2027-01-07 | [DigiKey UK](https://www.digikey.co.uk/en/products/detail/texas-instruments/BQ25895RTWR/5214018) |
| TPS61088RHLR | VQFN-20 4.50 × 3.50 mm | $1.364 | – | 10,343 | above |
| BQ27441DRZR-G1A | VSON-12 2.50 × 4.00 mm | £2.20 | £1.262 at 3k | **DigiKey out of stock**, due 2026-11-09 | [DigiKey UK](https://www.digikey.co.uk/en/products/detail/texas-instruments/BQ27441DRZR-G1A/4626408) |
| MAX17048G+T10 | TDFN-8 2 × 2 mm | $5.02 | $1.7875 at 10k | 10,783 | [DigiKey](https://www.digikey.com/en/products/detail/analog-devices-inc-maxim-integrated/MAX17048G-T10/3758921) |
| STUSB4500QTR | QFN-24 4 × 4 mm | LCSC $1.8317 | ST eStore $1.22 at 500 | ST in stock | [ST eStore](https://estore.st.com/en/products/interfaces-and-transceivers/usb.html) |
| HUSB238 | DFN-10 3 × 3 mm | LCSC from $0.5908 | – | – | search synthesis, VERIFY on LCSC |
| MAX98357AETE+T | TQFN-16 3 × 3 × 0.75 mm (WLP 1.345 × 1.435 mm available) | £3.07 | £1.671 at 2.5k. ADI 1k list $1.45 | 38,712 | [DigiKey UK](https://www.digikey.co.uk/en/products/detail/analog-devices-inc-maxim-integrated/MAX98357AETE-T/4936122), [ADI](https://www.analog.com/en/products/max98357a.html) |
| ICS-43434 ×2 | 3.50 × 2.65 × 0.98 mm | $5.71 | $3.094 at 10k | 79,514. **Marked obsolete/NRND** | [DigiKey AU](https://www.digikey.com.au/en/products/detail/tdk-invensense/ICS-43434/6140298) |
| STM32U031K8U6 | UFQFN-32 5 × 5 × 0.55 mm | $2.74 (ST). TME $2.51 | $1.50 at 500 | ST in stock, TME 395 | [ST](https://estore.st.com/en/stm32u031k8u6-cpn.html), [TME](https://www.tme.com/us/en-us/details/stm32u031k8u6/st-microcontrollers/stmicroelectronics/) |
| Camera Module 3 | V2 board size | $25 list | – | – | [RPi](https://www.raspberrypi.com/news/new-autofocus-camera-modules/) |
| CMS-15118D-L100 | 15 × 11 × 3 mm | CHF 3.59 | CHF 1.676 at 1k | 327 | above |

⚠ **Mic change:** ICS-43434 is NRND. Use SPH0645LM4H as the primary mic (its price and package are still open).

## Exact MCU sleep currents
- **STM32U031:** Stop 2 630 nA with RTC (515 nA without). Standby 160 nA with RTC (30 nA without). Shutdown 16 nA. VBAT 130 nA. 4 µs wake from Stop ([datasheet](https://www.st.com/resource/en/datasheet/stm32u031r6.pdf)). **Kept as the selected MCU.**
- **ESP32-S3:** deep sleep 7 µA (RTC memory only), 8 µA with RTC peripherals ([datasheet](https://documentation.espressif.com/esp32_s3_datasheet_en.pdf)).
- **RP2040:** about 180 µA (earlier whitepaper).

## Still open
SPH0645LM4H price and package · HUSB238 exact LCSC listing · LP684875 price and a 2 C variant · Pi Cooler price · CM5 Linux PDM support (no longer needed with I2S mics) · DSI overlay validation on hardware · TPS61088 inductor and capacitors.

---
# Battery cell options (2026-10-21, pocket max 51 × 64 × 7 mm)
Requirements: 1S LiPo, about 2.6–2.8 Ah, 1–2 C continuous, PCM, pigtail/connector, NTC preferred, BIS IS 16046 preferred. Dimensions are T × W × L.

| Option | Size | Capacity / Wh | Continuous discharge | PCM / NTC / lead | Price / MOQ | Fit | BIS |
|---|---|---|---|---|---|---|---|
| **Akyga LP655063** (distributor Ropla AKY2210, [listing + aky2210.pdf](https://www.elektronik.ropla.eu/en/magazyn/magazyn/?ic=AKY2210)) | 6.5 × 50 × 63 mm (listed package size; **VERIFY whether the PCM is included**), 46 g | 3000 mAh / 11.1 Wh (3.7 V × 3.0 Ah) | **1 C max (3 A)**, 0.2 C nominal | PCM + **10 kΩ NTC**, JST ZHR-3 (1.5 mm), 40 mm wires | Price not captured. Ropla tray of 12 | ✅ if 63 mm includes the PCM (1 mm spare) | Not verified |
| **THOR-655060** ([product page](https://thorbattery.com/product/thor-655060/)) | Bare cell 6.5 × 50 × 60 mm. **6.5 × 50 × 62 mm with PCM**. Tolerance ±0.2 T, ±0.5 W/L | 2700 mAh / 9.99 Wh, about 43.5 g | **1 C (2.7 A)**. "Higher discharge-rate designs available upon engineering review" | PCM standard. **NTC optional**. PH2.0 or Molex 1.25 | MOQ from 10 samples, production quoted per project | ✅ 1 mm W, 2 mm L, 0.5 mm T spare | Not verified (UN38.3/MSDS; IEC 62133-2 "for selected models") |
| **LiPol Battery LP605060** 2800 mAh ([datasheet](https://www.lipolbattery.com/LiPo-Battery-Datahseet/LiPo_Battery_LP605060_3.7V_2800mAh.pdf)) | 6.0 × 50 mm (±0.5). **Length with PCM not readable in the extract, VERIFY** (nominally 60 + PCM) | 2800 mAh min / 10.36 Wh, about 56 g | **1 C (2.8 A)**. PCM overcurrent trips at 3–4.5 A | PCM yes, **NTC no**. AWG22 wires (Molex 50-37-5023 variant [here](https://www.lipolbattery.com/LiPo-Battery-Datahseet/LiPo_Battery_LP605060_3.7V_2800mAh_50375023.pdf)) | Not published | ✅ T and W. L needs ≤ 64 to be confirmed | Not verified |
| RESKY LP705060 (from v2) | 7 × 50 × 60 mm bare (±0.5 T) | 3000 mAh | 0.5 C continuous, 1 C max | PCM/NTC not stated | MOQ 100, negotiable | 🟨 7.0 ± 0.5 mm can exceed the 7 mm pocket | Not verified |
| Rejected: LP605064 3000 mAh ([datasheet](https://www.lipo-battery.com/wp-content/uploads/2021/03/LP605064.pdf)) | 64 mm cell + PCM is over 64 | – | 1 C | PCM, no NTC | – | ❌ too long | – |
| Rejected: LP684875 (v2 pick) | 6.8 × 48 × 75 mm | 3000 mAh | 1 C | PCM + NTC | – | ❌ 75 mm is over 64 | – |

**Discharge gap:**
- No option found offers 2 C continuous. All are 1 C, which is about 2.7–3.0 A.
- CM5 at 5 V/3 A through the boost is about 4.5 A from the cell. So either:
  - (a) cap system power at about 9–10 W in firmware (≈ 2.7 A × 3.6 V × η), or
  - (b) order a custom 2 C build. THOR says on its product page that higher discharge-rate designs are available after engineering review.
- PCM overcurrent trip levels (3–5 A) must be confirmed above the boost peak.

**BIS status:**
- **None of these cells is verified as BIS-registered.** The BIS CRS database (crsbis.in, "Registered Manufacturers" / scope-of-licence pages, e.g. [this example record](https://www.crsbis.in/BIS/Lims_registrationc.do?hmode=getScopeofLicense&rNumber=PTBUUDMxME1CUlZUNDFFVk5CRE1wVlZRQnBWUlNCbmVQQlRNczFUUEFBWkVScHpPMDFsPT0%3D)) lists models per manufacturer. Searches found no IS 16046 (Part 2) record for Akyga, THOR (Dengzhou Xinju New Energy), LiPol Battery or RESKY.
- No vendor claimed a BIS registration on its page.
- **Action:** ask each shortlisted vendor for its **BIS R-number (R-41xxxxxx) and the exact model in scope**, then verify it on crsbis.in. Otherwise budget a new IS 16046 (Part 2) registration (fees in bom.md §6). Under BIS rules the **cell must be registered before the battery pack** ([G&M Compliance](https://www.gmcompliance.com/2019/06/05/india-bis-update-update-to-is-16046-part-22018iec-62133-22017/)). A vendor with an already-registered cell saves one registration.

**Recommendation:**
1. **Prototype: Akyga LP655063.** It is the only option found with PCM, NTC and a ready connector at 3000 mAh, and it is in distributor stock. First confirm from aky2210.pdf that 63 mm includes the PCM.
2. **Production: THOR-655060 custom build.** Confirmed 62 mm with PCM. Ask for NTC (10 kΩ B3435 to match the BQ25895 TS pin), **2 C continuous**, PCM overcurrent of at least 5 A, a JST/Molex pigtail, an IEC 62133-2 report and a BIS IS 16046 registration (or a commitment to register).
3. Fallback: LiPol LP605060 (6.0 mm, slimmest) if its length with PCM is ≤ 64 mm and you accept no NTC. In that case add a thermistor taped to the cell.

## Battery decisions + BIS verification (2026-10-21)
**PM DECISIONS:**
- **Prototype: Akyga LP655063**, with system power **capped at about 9 W in firmware**. This keeps cell current within its 1 C (3 A) rating.
- **Production: custom THOR-655060 with 2 C continuous discharge** (plus NTC, PCM overcurrent of at least 5 A, and a pigtail, per the recommendation above).

**BIS CRS database query, precisely what happened:**
- `https://www.crsbis.in/BIS/Lims_registrationc.do?hmode=getLimsData` (the public "registered products" search) **loads over curl** with HTTP 200 and 30,865 bytes. There is **no CAPTCHA**.
- Its Search button is jQuery JavaScript. It POSTs to `...?hmode=getLimsData&regNo=&prodCat=&models=&strBrand=`.
- Posting brand = AKYGA / THOR / LIPOL / RESKY and models = 655060 / LP655063 returned **the same empty 30,865-byte template with no result rows**.
- A control test with known R-numbers (R-41291978, R-41162671) also returned no rows, even with a session cookie and the page's `;TID=` token. **So the empty results say nothing about whether these vendors are registered.** The result table is apparently populated in a way a plain POST does not reproduce, probably by a JS DataTables/session flow.
- The scope pages `...?hmode=getScopeofLicense&rNumber=<encoded>` use an obfuscated R-number encoding, not plain base64. Plain base64 R-numbers return a 50,009-byte page with no manufacturer data. I did not try to reverse-engineer it.
- `ProductDetails.jsp` timed out (curl after 25 s; WebFetch returned 504). The BIS FAQ PDF failed with a TLS EOF over curl.
- **Next step:** run the search by hand in a real browser at the getLimsData URL, or ask vendors for R-numbers and open their scope page from the site's own link.

**Status per vendor (rule: verified only if the R-number was seen on crsbis.in itself):**
| Vendor / legal manufacturer | BIS IS 16046-2 status |
|---|---|
| Akyga (Akyga battery, Poland brand; cell maker unknown) | **Needs vendor R-number** |
| THOR (legal manufacturer per THOR's site: **Dengzhou Xinju New Energy**) | **Needs vendor R-number** |
| LiPol Battery Co., Ltd (China) | **Needs vendor R-number** |
| RESKY | **Needs vendor R-number** |

**Pouch makers with IS 16046-2 licence documents (vendor-published; not verified on crsbis.in):**
| Maker | Licence (from vendor PDF) | Scope | Fit for 50 × 63 × 6.5 mm, 2.7–3 Ah |
|---|---|---|---|
| Shenzhen Nova Technology Ltd (brand NovaBat) | **R-41291978**, cells, 28-Jun-2024 to **27-Jun-2026, now past expiry unless renewed** ([PDF](https://www.novabattery.com/upload/soft/260601/NovaLithiumBatteryBIScertificate.pdf)) | Models include 604060, 603450, 906090… | **No 655060-class model in scope.** Would need an inclusion (₹30k government fee) |
| Yj Power Group Limited, Shenzhen (brand YJ Power) | **R-41162671**, Li-ion polymer battery. Inclusion letter 20-01-2022, licence then valid to 24-08-2022 ([PDF](https://www.yjbattery.com/wp-content/uploads/2024/12/%E7%94%B5%E6%B1%A0BIS%E8%AF%81%E4%B9%A6.pdf)) | YJ603048, YJ753048, YJ802540… | No 655060 model. Current validity unknown |
| Dongguan NVT Technology Co., Ltd | crsbis.in scope page appeared **in a search-engine snippet** ([link](https://www.crsbis.in/BIS/Lims_registrationc.do?hmode=getScopeofLicense&rNumber=PTBUUDMxME1CUlZUNDFFVk5CRE1wVlZRQnBWUlNCbmVQQlRNczFUUEFBWkVScHpPMDFsPT0%3D)), IS 16046 (Part 2) | Samsung-brand phone packs only | Not a custom-pouch supplier for us. R-number not seen, so not verified |

**Conclusion:**
- **No verified IS 16046-2 registration was found for any 50 × 63 × 6.5 mm, 2.7–3 Ah cell.** None of the 2–3 qualifying makers requested could be confirmed.
- Practical path: ask THOR (production) for a BIS R-number, or make a new cell plus battery registration a contract deliverable. Alternatively, ask Nova or YJ Power to quote a 655060/655063 cell **and** to file a BIS model inclusion under their existing licence (after confirming the licence is still valid).

**PM AGREED (2026-10-21): the BIS IS 16046-2 R-number (cell + battery registration) is a THOR contract deliverable for the production cell.**

## Akyga LP655063: datasheet check (2026-10-21) ⚠ DOES NOT FIT
Source: AKYGA "Specification Approval Sheet" LP655063, Release 1, 2024-08-29 ([aky2210.pdf](https://www.elektronik.ropla.eu/pdf/stock/aky/aky2210.pdf)), §3.1, §3.2 and §6 drawing.
- **The 63 mm figure is the bare cell only:** 63 × 50 × 6.5 mm max, "not including tabs" (§3.1).
- **Assembled pack, including PCM, Kapton tape and the folded tab/PCM end: L 65.5 × W 51 × T 7 mm max** (§3.2, drawing §6). These are maximums measured at 300 gf, "not including battery drawing line" (that is, the wires).
- **Lead exit:** the red, black and yellow (NTC) AWG24 wires exit **axially from the PCM end**, the short 51 mm edge, at the bottom of the 65.5 mm length. In the drawing they come out of the face of the PCM end, offset toward the centre. Wire length is **40 mm** to a **JST ZHR-3** (1.5 mm pitch) connector. The pocket also needs wire-bend clearance beyond 65.5 mm at that end.
- **Against the pocket** (50 × 63 × 6.5 nominal + 0.5 mm per side, so 51 × 64 × 7.5 mm max):

| Dimension | Pack | Pocket max | Result |
|---|---|---|---|
| L | 65.5 | 64 | ❌ 1.5 mm over, plus wire exit |
| W | 51 | 51 | 🟨 zero margin |
| T | 7.0 | 7.5 | ✅ |

- **Implication for the PM decision:** the prototype choice of Akyga LP655063 **does not fit the current pocket**. Options:
  - (a) lengthen the pocket to at least 66 mm plus about 3–5 mm wire-bend space at the PCM end. That needs an Enclosure check of the 125 mm budget.
  - (b) prototype with **THOR-655060** instead (vendor states 62 mm with PCM, 6.5 × 50).
  - (c) a cell with a 60 mm body (for example 655060-class from another vendor) plus a PCM of 3 mm or less.
- Electrical figures confirmed: 3000 mAh at 0.2 C, 1 C max charge and discharge, 3.0 V cut-off, PCM + 10 kΩ NTC, charge 0–45 °C.

## Battery cell options, rev for the 22 mm body (2026-10-21)
**Pocket:** 51.5 × 67 × 9.0 mm. **Cell envelope limit, including PCM and tape:** ≤ 8.5 T × 51 W × 65.5 L mm. Wires must exit on the 51 mm edge.

**How LiPol labels sizes (from its own datasheets).** LiPol's drawings dimension the finished pack, with the PCM folded onto the end and Kapton tape applied, to the model number:
- LP605060: 6.0 ± 0.3 × 50 ± 0.5 × 60 ± 1.0 mm ([datasheet](https://www.lipolbattery.com/LiPo-Battery-Datahseet/LiPo_Battery_LP605060_3.7V_2800mAh.pdf)).
- LP855055: 8.5 ± 0.3 × 50 ± 0.5 × 55 ± 1.0 mm ([datasheet](https://li-polymer-battery.com/wp-content/uploads/2024/04/LiPo_Battery_LP855055_3.7V_2500mAh.pdf)).

Both drawings show the red/black wires leaving from the PCM end, on the 50 mm edge. The model number therefore gives pack size **including the PCM**, with a worst case of +0.3 T / +0.5 W / +1.0 L. This is unlike Akyga and THOR, which quote the bare cell and add +2 to +2.5 mm for the PCM.

**Standard discharge rating.** LiPol's standard packs are rated **1C continuous**: LP605060 is 2800 mA max continuous, with PCM over-current trip at 3–4.5 A. That falls short of the ≥ 2C / 3–5 A target. **A high-rate cell plus a 5–6 A PCM must be requested** on every option below.

| Option | Pack T × W × L (incl. PCM) | Worst case with tolerance | Capacity / Wh | Discharge | NTC | Connector / wire exit | Price / MOQ | Datasheet | Fits ≤ 8.5 × 51 × 65.5? | BIS |
|---|---|---|---|---|---|---|---|---|---|---|
| **LiPol LP755060** ⭐ | 7.5 × 50 × 60 | 7.8 × 50.5 × 61 | **3500 mAh / 12.95 Wh** (catalogue) | Standard is 1C; request 2C + 10k NTC | Option (vendor offers NTC on any pack) | Wires on the 50 mm PCM edge (LiPol standard). Connector to order (e.g. JST PHR-3 / ZHR-3) | MOQ **5 pcs** stocked. 6–7 wk mass production. Price on request | Model-specific datasheet not public. Catalogue listing at [lithium-polymer-battery.net 3000mAh+ table](https://www.lithium-polymer-battery.net/iec-62133-certified-lithium-polymer-battery-lp805060-3-7v-3000mah-11-1wh-with-pcm-wires-jst-achr-02v-s/) | ✅ yes, with 0.7 T / 0.5 W / 4.5 L margin | Needs vendor R-number |
| **LiPol LP834964** | 8.3 × 49 × 64 | 8.6 × 49.5 × 65 | 3500 mAh / 12.95 Wh (catalogue) | as above | option | as above | as above | catalogue (same table) | 🟨 L and W fit. T is 8.6 worst case (> 8.5, < 9.0 pocket) | Needs vendor R-number |
| **LiPol LP845053** | 8.4 × 50 × 53 | 8.7 × 50.5 × 54 | 3500 mAh / 12.95 Wh (catalogue) | as above | option | as above | as above | catalogue | 🟨 T is 8.7 worst case. Frees about 11 mm of length | Needs vendor R-number |
| LiPol LP745060 | 7.4 × 50 × 60 | 7.7 × 50.5 × 61 | 3250 mAh / 12.0 Wh EST (3.7 V × 3.25 Ah) | as above | option | as above | as above | catalogue | ✅ yes | Needs vendor R-number |
| LiPol LP755066 | 7.5 × 50 × 66 | 7.8 × 50.5 × 67 | 3750 mAh | – | – | – | – | catalogue | ❌ L 66 > 65.5 | – |
| LiPol LP805060 | 8 × 50 × 60 | 8.3 × 50.5 × 61 | 3000 mAh / 11.1 Wh. IEC 62133 claimed | 1C | **No** (as listed) | JST ACHR-02V-S | MOQ 5 | [listing](https://www.lithium-polymer-battery.net/iec-62133-certified-lithium-polymer-battery-lp805060-3-7v-3000mah-11-1wh-with-pcm-wires-jst-achr-02v-s/) | ✅ fits, but only 3.0 Ah | Needs vendor R-number |
| EEMB LP805065-PCM-LD | ≤ 8.3 × 50.5 × 66 (H ≤ 67 on the drawing) | – | 2800 mAh | 1C-class | No (2 wires, UL1007 AWG24) | wires | – | [EEMB spec](https://macrogroup.ru/upload/iblock/9cf/v8j1xd6s7wwio8oc79k4npeifqqe2yf7/LP805065.pdf) | ❌ L 66–67 | – |
| THOR-804864 | 8.0 × 48 × **66** with PCM | – | 3000 mAh / 11.1 Wh | per THOR standard | Optional | PH2.0 / Molex 1.25 | MOQ 10 samples | [THOR](https://thorbattery.com/product/thor-804864/) | ❌ L 66 | Needs vendor R-number |
| THOR-755068 | 7.5 × 50 × **70** with PCM | – | 3000 mAh | – | Optional | – | MOQ 10 | [THOR](https://thorbattery.com/product/thor-755068/) | ❌ L 70 | – |
| Akyga LP905060 | 9.0 × 50 × 60 (cell) | – | 3000 mAh. 1C | 1C | – | wires 100 mm | – | [Ropla AKY1785](https://www.elektronik.ropla.eu/en/magazyn/magazyn/?ic=AKY1785) | ❌ T 9.0 | – |
| THOR-105060 (reference) | 10 × 50 × 62 with PCM | – | 3500 mAh / 12.95 Wh. 1C (3.5 A) standard. "Higher discharge-rate designs available" | 1C | Optional | PH2.0 / Molex 1.25 | MOQ 10 | [THOR](https://thorbattery.com/product/thor-105060/) | ❌ T 10 | – |

**THOR catalogue check.** THOR's model list ([models](https://thorbattery.com/products/lipo-battery-models/)) has no 805060, 855060, 805065 or 855065 entry. Its nearest parts fail on length once the PCM is added. Staying with THOR, the contract vendor, therefore means a **custom 80–85 × 50 × ≤ 63 mm (bare) 2C cell**, which ends at ≤ 65.5 mm with the PCM. THOR's pages state custom size, capacity, PCM, NTC and connector are available. The **BIS R-number remains a THOR contract deliverable**.

**Recommendation**
1. **Production: custom THOR 2C cell, about 8.0 × 50 × 62 mm bare (≤ 65 mm with PCM).**
   - Specify ≥ 3.3–3.5 Ah, 2C (≥ 7 A) continuous, a 6 A PCM, a 10 kΩ B3435 NTC, 3 wires exiting the 50 mm PCM edge, and JST ZHR-3/PHR-3.
   - Ask THOR for a drawing that dimensions the finished pack.
   - THOR also supplies the BIS R-number under the contract.
2. **Prototype / second source: LiPol LP755060 (3500 mAh, 7.5 × 50 × 60 mm including PCM).**
   - Order it with the 2C/high-rate option, a 10k NTC and a JST 3-pin connector.
   - Request the model-specific datasheet and confirm the drawing before ordering.
   - It leaves about 1.2 mm of thickness and about 6 mm of length in the pocket for the wire bend.
   - If LiPol cannot do 2C, keep the 9 W firmware power cap from the Akyga decision.
3. No catalogue part was verified with both ≥ 2C and a 10k NTC in this envelope. Every option needs vendor confirmation, and the BIS status of every option is **"needs vendor R-number"**.

## Battery correction and re-source (2026-10-21, 22:44 IST) ⚠ supersedes the LP755060 recommendation above
### 0. LP755060 reconciliation: the "3500 mAh" figure was wrong to rely on
| Source | Type | Capacity | Discharge (continuous) | Size | URL status |
|---|---|---|---|---|---|
| LiPol catalogue table (lithium-polymer-battery.net, 3000mAh+ list) | Sales table, **not a datasheet** | **3500** (table row "LP755060 3500 60 50 7.5"; rated vs typical not given) | not stated | 7.5 × 50 × 60 | 200, [page](https://www.lithium-polymer-battery.net/iec-62133-certified-lithium-polymer-battery-lp805060-3-7v-3000mah-11-1wh-with-pcm-wires-jst-achr-02v-s/) |
| Akyga LP755060 spec sheet (Release 1, 2025-11-25) | **Datasheet** | **3000 mAh rated @ 0.1C** | **0.3C max (≈ 0.9 A)**; charge 0.3C | Cell 7.5 × 50 × 60.5. **Pack 8 × 51 × 62.5 max** | 200, [aky2747.pdf](https://elektronik.ropla.eu/pdf/stock/aky/aky2747.pdf), [Ropla AKY2747](https://www.elektronik.ropla.eu/en/magazyn/magazyn/?ic=AKY2747) (in stock) |
| iBorn LP755060-3000 | Vendor spec table | 3000 mAh nominal @ 0.2C | **1C continuous**, 2C peak | **7.5 × 50.5 × 62 max** | 200, [iBorn](https://ibornbattery.com/products/755060-37v-3000mah-lipo-battery-for-monitor) |
| BZ / UFX 755060 | Vendor spec table | 3000 mAh typical and minimum @ 0.2C | 1C continuous | 7.5 × 50 × 62 max | 200, [BZ](https://www.bzbattery.com/china-most-popular-battery-for-bluetooth-speaker-ufx-755060-3000mah-3-7v-rechargeable-li-polymer-battery.html) |
| FP Battery 755060 | Vendor page | ≥ 3000 mAh @ 0.2C | "1C (not continuous)" | – | 200, [FP](https://www.fpbattery.com/product/3-7v-3000mah-755060-lithium-polymer-battery/) |
| Crazell 755060 | Vendor page | 3000 mAh | 1C max | 7.0 × 50 × 60 | 200, [Crazell](https://www.crazell.com/product/755060-lipo-battery/) |

**Correction.**
- Every datasheet or vendor spec says a **755060 is a 3.0 Ah cell**. The 3500 mAh came from one LiPol sales-table row with no datasheet behind it, and it should not have been reported as the cell's capacity.
- I also applied LiPol's "model number = pack incl. PCM" rule to the LiPol catalogue rows. That rule is only shown on two LiPol datasheets (LP605060, LP855055) and is unverified for the others.
- The Akyga version is rated 0.3C and its pack is 8 × 51 × 62.5 mm, so it is **not usable**.
- **The LiPol LP755060 / LP834964 / LP845053 / LP745060 "3500 mAh" rows above are withdrawn.**

### 1. Prototype: 755060-class (≤ 7.8 × 50.5 × 61 incl. PCM), in stock, ≥ 1C
| Part | Datasheet capacity / discharge | Size | NTC | Price / stock | Verdict |
|---|---|---|---|---|---|
| **PKCELL LP785060 (2023 rev, AC307046)** | **2500 mAh typ / 2375 min. Max continuous 2500 mA (1C)**. PCM over-current 4–9 A ([datasheet](https://www.batterypkcell.com/uploads/LP785060-2500mAh-3.7V-AC307046-20230717.pdf), 200) | ≈ 60.5 × 50 × 7.8 (BerryBase listing). Datasheet appendix drawing not text-extractable, so **VERIFY whether it includes the PCM** | **No** (none in datasheet) | Welectron **€7.70** incl. VAT, "Orderable, 6–7 weeks" ([Welectron](https://www.welectron.com/PKCell-LP785060-LiPo-2500-mAh-PH-Connector), 200). BerryBase: **sold out** ([BerryBase](https://www.berrybase.de/en/lp-785060-lithium-polymer-lipo-battery-3.7v-2500mah-with-2-pin-jst-connector), 200). Tinytronics listing 403 from the box | ✅ best electrical match. ❌ not in stock today |
| Adafruit #328 (PKCELL LP785060, 2019 sheet) | 2500 typ / 2375 min. **Max continuous 1500 mA (0.6C)**. PCM over-current 2–5 A ([datasheet](https://cdn-shop.adafruit.com/product-files/328/LP785060+2500mAh+3.7V+20190510.pdf), 200) | 50 × 60 × 7.3 | **No** (Adafruit: "do not have thermistors") | **$14.95, in stock** ([Adafruit](https://www.adafruit.com/product/328), 200) | ❌ below 1C (bench use only) |
| iBorn LP755060-3000 | 3000 mAh @ 0.2C, **1C continuous**, 2C peak | 7.5 × 50.5 × **62** max | not listed (customisable) | Price not published. Sample lead time 14–15 days | 🟨 1 mm over the 61 limit, but fits the 67 mm pocket. Not stock |
| BZ/UFX 755060 | 3000 mAh, 1C continuous | 7.5 × 50 × 62 max | no | "$3.60, In stock". FOB $1.2–1.5/Ah, MOQ 1000 Ah | 🟨 62 mm. Factory "in stock" claim, not a retail shelf |
| Akyga LP755060 | 3000 mAh, **0.3C** | 8 × 51 × 62.5 | no | in stock at Ropla | ❌ |
| **Akyga LP655063** (fallback) | 3000 mAh, **1C**, PCM + **10k NTC** ([aky2210.pdf](https://www.elektronik.ropla.eu/pdf/stock/aky/aky2210.pdf)) | **7 × 51 × 65.5** max pack | **Yes, 10k** | Ropla: **2 pcs on stock** ([AKY2210](https://www.elektronik.ropla.eu/en/magazyn/magazyn/?ic=AKY2210)) | ✅ fits the new 51.5 × 67 × 9 pocket (not the 61 mm class) |
| Robu.in (India) | 1S range tops out at 2200 mAh (RC packs) ([Robu](https://robu.in/product-category/1-cell-lipo-3-7v-4-2v/)) | – | – | – | ❌ no 3 Ah 1C pouch found |

**Prototype recommendation.**
- Use the **Akyga LP655063**: in stock, 1C, 10k NTC, and it fits the 22 mm-body pocket. Keep the **9 W cap** (1C ≈ 3 A).
- If the 61 mm class is mandatory, order the **PKCELL LP785060 (2023 rev)** from Welectron (6–7 weeks) and add an external NTC on the cell face.

### 2. Production: about 3.5 Ah, ≤ 8.5 × 51 × 65.5 incl. PCM, 2C continuous
**Catalogue search result: none found.**

| Maker | Closest catalogue part | Why it fails | Source (status) |
|---|---|---|---|
| Grepow 1C list | **GRP8652065**: 3650 mAh, 3.65 A (1C), 8.2 × 52 × 66 | 1C only. W 52 > 51. L 66 > 65.5 | [Grepow 1C](https://www.grepow.com/lipo-battery/1c-discharge-rate-rechargeable-battery-cell.html) (search index OK; box curl timed out) |
| Grepow 3C list | No part with 50 mm width and ≤ 66 mm length. All 3C parts of 3 Ah or more are 85–98 mm long | size | [Grepow 3C](https://www.grepow.com/high-discharge-rate-battery/3c-high-discharge-lipo-cell.html) (522 from box; indexed) |
| Grepow 5C / 30C | All long and narrow (e.g. 3500 mAh 5C = 5.3 × 41.5 × 126.5) | size | [5C](https://www.grepow.com/high-discharge-rate-battery/5c-high-discharge-lipo-cell.html) (indexed) |
| EEMB LiPo catalogue | No 50 × 60–65 entry (closest LP505464, LP604765) | size | [EEMB](https://www.eemb.com/products-55) (200) |
| BZ 756060-2C | 3500 mAh 2C, but 60 mm wide | W | [BZ](https://www.bzbattery.com/chinese-lipo-cell-factory-professional-customize-bz-756060-2c-3-7v-3500mah-battery-for-3c-digital-product.html) |
| THOR | No 80–85 × 50 × 60–65 model (see above) | – | THOR models page |
| Great Power, AMP/Ufine | No public model table found in this pass | – | – |

**Realistic capacity (EST).** Grepow's 1C GRP8652065 reaches 3650 mAh in 8.2 × 52 × 66 mm. Trimming to 50 × ~62 mm bare and adding a 2C (stacked, lower density) design puts a realistic custom target at **about 3.0–3.3 Ah**. 3.5 Ah at 2C in this envelope is unlikely without going to 9 mm. This is an estimate, not a vendor figure.

**Production recommendation.** Issue a custom-cell RFQ with this spec:
- ≤ 8.5 × 50.5 × 65.5 mm including PCM and tape
- ≥ 3.2 Ah rated
- 2C (≥ 6.5 A) continuous
- 6–8 A PCM
- 10k B3435 NTC
- 3 wires exiting the 50 mm edge, JST ZHR-3

Send it to:
- **Grepow**, stacked high-rate. MOQ not published.
- **THOR** (MOQ 10 samples; production quoted per project). The BIS R-number is a THOR deliverable.
- **iBorn** (sample lead time 14–15 days, bulk 30–35 days).

BIS status of every option: **needs vendor R-number**.

## PM decision, battery (2026-10-21, 22:50 IST)
- **Prototype: Akyga LP655063.** 3000 mAh, 1C, PCM + 10k NTC, pack 7 × 51 × 65.5 mm max. Fits the 51.5 × 67 × 9 pocket. **9 W firmware cap.**
- **Production: custom cell ≥ 3.2 Ah, ≤ 8.5 mm (accepted)**, 2C. RFQ in `research/battery-rfq.md`.
- **Termination change:** Molex Pico-Lock 504051-0301 + terminal 504052-0098 (AWG24–28).
  - Per Molex PS-504051-001, a 3-circuit housing at AWG24 is rated **3.0 A/pin**. That is **under-rated for 6.5 A continuous**.
  - Options (paired-pin 5-pos, 2.00 mm Pico-Lock 205341/205342, or solder power) are flagged for a J7 decision.

## J7 battery connector, PM decision (2026-10-21, 22:52 IST): Molex Pico-Lock 2.00 mm, 5-pos
- **Housing:** 205341-0205 (5-ckt receptacle). **Terminal:** 205342-5028 (AWG 20–22). **Carrier header:** 205338-0005 (right-angle SMT, mated height 2.60 mm). **No vertical header** in the 205338 series (Molex series chart).
- **Pinout (schematic master, Rev C):** 1 VBAT, 2 VBAT, 3 GND, 4 GND, 5 NTC. AWG20.
- **Rating:** 5.0 A per pin at AWG20 in a 5-ckt housing (Molex 987650-9061, ≤ 30 °C rise). 2 pins per rail gives **about 10 A, which is ≥ 6.5 A ✅**.
- **Size:** housing about 14.55 × 9.1 × 2.54 mm (Arrow), which fits the 50 mm edge and is far below the 9 mm pocket.
- ⚠ **Fit issue:** a pack of up to 65.5 mm in the 67 mm pocket leaves ≤ 1.5 mm for an AWG20 bend. Options: a pack ≤ 61–62 mm, a straight exit through a wall slot, or a pre-formed flat fold. See battery-rfq.md §4c.
- **Prototype Akyga LP655063 must be re-terminated.**
  - Its stock leads are AWG24 UL1571, 40 mm, to a JST ZHR-3 (aky2210.pdf). The ZH contact is rated well below the 2.0 A system need (JST ZH is a 1 A-class contact; VERIFY on JST's datasheet).
  - Per Molex, AWG24 in a 2.00 mm Pico-Lock is only 3.5 A per pin (5-ckt).
  - **Recommendation:** replace the leads with 4 × AWG20 (2 + 2) plus the NTC wire, crimped into 205341-0205 / 205342-5028, soldered to the PCM pads by someone qualified for Li-po rework.
  - **Alternative:** keep the AWG24 leads paired 2 + 2 (3.5 A per pin, about 7 A per rail) **and keep the 9 W firmware cap**. Note that the cell itself is only rated 1C (3 A), so **cap the system at ≤ 3 A from the battery regardless of wiring**.
  - The LP655063 is 65.5 mm long, so it has the same pocket-length issue for wire exit.

## Battery Rev C decisions (2026-10-21, 22:54 IST)
- **Production pack:** ≤ 8.5 × 50.5 × **62.0 mm incl. PCM and tape**, leaving ≥ 5 mm of bend room in the 67 mm pocket. **≥ 3.0 Ah rated (target ≥ 3.1 Ah) at 0.2C**, 2C. Supersedes ≥ 3.2 Ah / 65.5 mm.
- **J7 pinout (schematic is master):** 1 VBAT, 2 VBAT, 3 GND, 4 GND, 5 NTC. Supersedes the earlier 1V/2V/3NTC/4G/5G order.

### Akyga LP655063 (prototype): datasheet facts (aky2210.pdf, Release 1, 2024-08-29)
| Item | Datasheet says |
|---|---|
| NTC resistance | **"PCM+NTC 10kR"** (§3.1 item 16). That is the only NTC statement |
| NTC beta (B25/50 or B25/85) | **Not stated.** Neither 3435 nor 3950 appears, and no temperature pair is given |
| NTC tolerance | **Not stated** |
| NTC wire colour | **Yellow** (drawing §6.1: "wire yellow", with red (+) and black (−)) |
| Bare cell | **L 63 × W 50 × T 6.5 mm, all "Max"**, at 300 gf, 25 °C, not including tabs. **No ± tolerances given** |
| Assembled with PCM | **L 65.5 × W 51 × T 7 mm, all "Max"**, not including lead wires. **No ± tolerances** |
| Leads | **40 mm** (drawing, no tolerance). AWG24 UL1571 (AWG22–26 option). JST ZHR-3, 1.5 mm, 3 pins |

**Actions:**
- Ask Akyga/Ropla for the NTC part number and its B value, or measure R at 0/25/45 °C on a sample.
- Re-terminate the AWG24 leads (see above).

### BQ25895 TS divider (TI BQ25895 datasheet Rev C, §8.2.7.5.1, Eq. 2, Fig. 8-6)
- **TI's design point for a 103AT (10k, B25/85 = 3435) NTC, 0–45 °C window:** RTH_COLD = 27.28 kΩ, RTH_HOT = 4.91 kΩ, giving **RT1 = 5.21 kΩ (REGN→TS) and RT2 = 29.87 kΩ (TS→GND)**.
- **Thresholds used** (datasheet typical): VT1 = V(LTF) = 73.25% REGN, VT5 = V(TCO) = 44.75% REGN.
- I re-ran Eq. 2 with these values and got 5.206 kΩ / 29.86 kΩ, matching TI's figures.
- **If the cell's NTC were B = 3950 instead (EST, simple beta model, same divider):** the window shifts to about **4.0 °C to 41.9 °C** (vs about 1.1 °C to 44.6 °C with B = 3435 in the same model). Charging would stop early in an Indian summer.
- **So:** confirm B before freezing RT1/RT2.
  - Production RFQ specifies 10k ±1%, B25/85 = 3435 ±1% (103AT-equivalent).
  - For the Akyga prototype, measure the NTC first. If it is B3950, recompute RT1/RT2 with Eq. 2 using RTH(0 °C) ≈ 33.6 kΩ and RTH(45 °C) ≈ 4.35 kΩ (beta-model EST), or use the actual R-T table.
- **The pinout change does not affect this:** the NTC returns to pack − (GND, pins 3–4), and TS reads pin 5.
