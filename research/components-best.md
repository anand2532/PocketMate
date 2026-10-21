# PocketMate: Best-in-Class Pass v1 (2026-10-21)
Constraints: 125 × 75 × ≤20 mm, about a $249 retail price. Baseline picks are in `components.md` and the baseline cost in `bom.md`. Flags: 🟥 breaks a constraint, 🟨 marginal, 🟩 fits. Any figure without a source is marked **EST** or "not found".

| Area | v1 pick | Best option | Tradeoff | Flags |
|---|---|---|---|---|
| Display | Waveshare 4.3inch DSI LCD, 800×480 IPS, 106.1 × 67.8 glass (PM decision), $34.97 at 100+ | **Waveshare 4.3-DSI-TOUCH-A** (SKU 34353): 480×800 IPS, **optical bonding**, 6H glass, aluminium back, Pi 5 support ([docs](https://docs.waveshare.com/4.3-DSI-TOUCH-A)) | Bonding gives better sunlight contrast and fewer reflections. Same resolution, rotated to portrait. Outline, brightness and price not found, so VERIFY that it fits the 75 mm width. **No 4.3" DSI OLED and no 1000-nit 4.3" DSI panel was found** for Pi. Waveshare's AMOLED panels are 5–5.5" HDMI ([selection guide](https://www.waveshare.com/rpi_lcd_selection_guide)) | 🟨 size/price unknown |
| Mics | 2× SPH0645 / ICS-43434 I2S | **XMOS XVF3800-QF60B-C** + 4 PDM mics: AEC, multi-beam beamformer, noise suppression, AGC, direction-of-arrival. 7 × 7 mm QFN60. **345 mW** typical core (I2S). DigiKey $29.74 qty 1, $19.50 at 416, 2,267 in stock ([DigiKey](https://www.digikey.sg/en/products/detail/xmos/XVF3800-QF60B-C/21280440), [datasheet](https://www.xmos.com/download/XVF3800-Device-Datasheet(3_0_0).pdf)). Dev option: ReSpeaker XVF3800 board, 35 × 86 mm, $60.99 ([Seeed](https://www.seeedstudio.com/ReSpeaker-XVF3800-USB-Mic-Array-p-6488.html)) | Much better speech-to-text in noise and lets audio play while listening (barge-in). Needs 4 mics, not 3 (it is designed for 4). It also needs QSPI flash and about 0.35 W, and adds about $20 at volume. The dev board's 86 mm length does not fit across the case, so use the chip only | 🟨 cost/power |
| Battery | LP684875: 3000 mAh, 11.1 Wh, 6.8 × 48 × 75 mm | **855465 cell, 4000 mAh**, 8.5 × 54 × 65 mm (listed in [supplier table](https://www.rechargeable-batterypack.com/sale-49665885-high-discharge-rate-battery-3-7v-3000mah-30c-max60c-rechargeable-lipo-battery-705060-pilas-rechargea.html), no datasheet or price). 65 + 40 (CM5) = 105 mm length ✅. 8.5 mm thick beside the CM5 stack ✅ | About 33% more energy. Discharge rate, PCM and price are unknown, so a quote is needed. **Full-day battery life is not proven.** CM5 average power was not measured in sources. Expect a "full day" only with aggressive suspend and the MCU holding wake. EST: 15 Wh ÷ about 3 W active ≈ 5 h of active use | 🟨 |
| Compute | CM5104032 4GB, $129 | **CM5108032 8GB/32GB/Wi-Fi**: €182.91 ex VAT ([raspberrypi.dk](https://raspberrypi.dk/en/product/cm5108032-sc1601/), out of stock). Conrad €265 incl. VAT ([Conrad](https://www.conrad.com/en/p/raspberry-pi-compute-modul-5-cm5108032-8-gb-ram-32-gb-emmc-4-x-2-4-ghz-3356679.html)) | Lets a 3B LLM run alongside speech-to-text and the UI (qwen2.5:3b Q4_K_M needs about 3.0 GB RAM, which is too tight on 4 GB). About +$90 EST (FX) | 🟥 cost |
| NPU | none | **Hailo-8L (13 TOPS)**. Raspberry Pi AI HAT+ is $70 list and 2.55 mm thick, HAT form factor ([brief](https://pip-assets.raspberrypi.com/categories/1081-raspberry-pi-ai-hat/documents/RP-008133-DS-1-raspberry-pi-ai-hat-plus-product-brief.pdf?disposition=inline)). The M.2 2280 module HM218B1C2LAE is 22 × 80 × 2.626 mm, **TDP 6.6 W**, 1.4–1.9 W typical ([datasheet](https://www.farnell.com/datasheets/4746521.pdf)). The AI Kit's 2242 module is discontinued ([docs](https://www.raspberrypi.com/documentation/accessories/ai-kit.html)) | Speeds up vision (detection, pose) at about 1.5 W. **It does not help the LLM or Whisper**: the Hailo-8L is aimed at CNN vision. A 2280 module needs 80 mm of length plus routing. The HAT form factor does not fit. A chip-down design needs a Hailo partnership | 🟥 cost/thermal/size. **Not recommended** |
| STT | faster-whisper tiny.en/base.en int8: 1.15 s / 2.13 s | **base.en** stays the best real-time option. **small.en** runs at about 0.5–0.6× real time on Pi 5, so it is for batch only ([promptquorum](https://www.promptquorum.com/power-local-llm/local-whisper-stt-comparison-2026)). distil-small.en takes 4.90 s and often gives incomplete long transcripts ([ACM](https://doi.org/10.1145/3769102.3774244)) | Use small.en for background re-transcription of saved notes, not for live use | 🟩 |
| LLM | gemma3-1b, about 11.5 tok/s | **qwen2.5:3b Q4_K_M**: 5.2 tok/s, about 3.03 GB RAM (Pi 5 8GB, Ollama) ([source](https://rstudio-pubs-static.s3.amazonaws.com/1315005_1e9af5bd949b42d8ab2345e2786ec71e.html)). On 4 GB it technically loads but leaves under 1 GB for the OS, STT and UI. **Use 8 GB for 3B.** qwen2.5:1.5b runs at 10 tok/s in 1.85 GB and is the best choice on 4 GB | 3B is about 2× slower and slow for chat. Use it for summaries and action items in the background | 🟨 |
| Speaker | CMS-15118D-L100 (15 × 11 × 3 mm, 0.7 W) | **CMS-25148N**: 8 Ω, 1 W, 92 dB, €5.58, 17 in stock ([DigiKey highlight](https://www.digikey.pt/en/product-highlight/c/cui/micro-speakers)). Size not captured, VERIFY (the name suggests about 25 × 14 × 8 mm) | +1 dB and +0.3 W. A larger back volume is needed for bass. Thickness may matter | 🟨 |
| Haptics | none | **TI DRV2605L** (VSSOP-10 3 × 4.9 mm or DSBGA-9, 2–5.2 V, auto-resonance, Immersion effect library), LCSC $1.24 / $0.763 at 1k ([TI](https://www.ti.com/product/DRV2605L), [LCSC](https://www.lcsc.com/category/1016.html)). Paired with a **Vybronics VG0832012** LRA, 8 × 3.25 mm, 235 Hz, 1.00 Grms, 58 mA typical, 1,212 in stock ([Vybronics](https://www.vybronics.com/coin-vibration-motors/lra/v-g0832012)) | Gives tactile confirmation for push-to-talk and mic mute. Adds about $1 plus the LRA (price not found). Negligible space | 🟩 **Recommended** |
| NFC/UWB | none | Not researched. Skip for the MVP: the PRD does not require it, and cost and antenna area conflict with "only if cheap" | – | – |

## Best-build BOM (about 1k, building on bom.md's ≈ $233 excluding battery)
| Delta | ~1k USD |
|---|---|
| CM5 4GB → 8GB (€182.91 ex VAT ≈ $212 EST FX vs about $124) | +88 |
| XVF3800 + 2 extra mics (+$19.50, +2× $3.09) | +25.70 |
| DRV2605L + LRA | +0.76 + LRA (price not found) |
| Optically bonded display, 4000 mAh cell, CMS-25148N | price not found, quote needed |
| Hailo-8L (not recommended) | +$70 list (HAT), excluded |
| **Best-build total (excluding battery and unpriced deltas)** | **≈ $347** |

**Against the $249 target:** the best build breaks cost (BOM ≈ $347 against a retail price of ≤ $249). The v1 build (≈ $233) already breaks it.
- **Value-best set** (keep CM5 4GB; add haptics, the bonded display if its price is close, and the 4000 mAh cell; skip XVF3800 and Hailo): BOM ≈ $235–245 plus cell and display deltas. It is still above a $249 retail price.
- **Size, power and thermal:** Hailo (6.6 W TDP, 80 mm module) 🟥. XVF3800 (+0.35 W) 🟨. 8GB CM5 has no extra thermal cost. Everything else fits within 125 × 75 × 20 mm, subject to the VERIFY items above.

---
# Budget filter v2 (₹30k retail, BOM $120–150, from PM/Anand)
The v2 BOM is already ≈ $197 (see bom.md), so only upgrades at or near $0 delta stay in.

**Keep (fits budget):**
- **Haptics:** DRV2605L ($0.763 at 1k) + VG0832012 LRA (price not found, expected to be small). Gives tactile push-to-talk and mute feedback.
- **Software-only:** base.en for live STT and small.en for background re-transcription; qwen2.5:1.5b on 4 GB; Piper TTS. $0.
- **Factory display at 106 × 68 mm** (Ronbo/Lida, $17.50–23) is a cost-down, not an upgrade. Ask the factory for a bonded-glass quote. It stays in only if the delta is $3 or less (no price found).

**Out of budget (delta vs v2):**
| Upgrade | Delta | Basis |
|---|---|---|
| CM5 8GB (CM5108032) | +₹4,900 in India (₹19,900 vs ₹15,000 at [Silverline](https://www.silverlineelectronics.in/collections/raspberry-pi-compute-module-5)) ≈ **+$56** EST FX | Required for a 3B LLM |
| XVF3800 + 2 more mics | **+$25.70** ($19.50 + 2× $3.09) | DigiKey |
| Hailo-8L AI HAT+ | **+$70** list, plus 🟥 size/thermal | RPi brief |
| Camera Module 3 instead of OV5647 AF | **+$22** ($25 vs $3) | listings |
| Waveshare 4.3-DSI-TOUCH-A (bonded) | price not found, likely above the $17.50 factory panel | – |
| 4000 mAh 855465 cell | quote needed; adds 1.5 mm of thickness | – |
| CMS-25148N speaker | +€5.58 vs CHF 1.68 ≈ **+$4.4 (qty 1 basis)** | DigiKey |
| NFC/UWB | not scoped | – |

**Best build within budget:** v2 BOM ≈ $197 + haptics ≈ **$198** (excluding battery and LRA). This is still above the $150 ceiling until the CM5 price is negotiated.
