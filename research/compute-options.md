# PocketMate: Compute Options v1 (2026-10-21)
Rules: every figure is cited. **EST** marks estimates. FX for comparison only (EST): ₹88 ≈ $1. Context: the thermal budget (`mechanical/thermal_v2.md`) is **≈ 1.6 W sustained at 35 °C held** and ≈ 0.6 W at 45 °C, covering the whole device.

## Part 1: Raspberry Pi CM5 volume path
| Channel | Published price | 1k price | Contact route (official pages) |
|---|---|---|---|
| **Silverline Electronics**, Bengaluru, "only Approved Raspberry Pi channel partner in India" | CM5104032 ₹15,000 · CM5102032 ₹9,690 · CM5102000 ₹7,145 · CM5108032 ₹19,900 ([collection](https://www.silverlineelectronics.in/collections/raspberry-pi-compute-module-5)) | **Not published.** Request a quote | Customer service **7090939819** (from the [home page](https://www.silverlineelectronics.in/)). GSTIN 29AAZPC3444K1Z5. Address: Unity Building, Bangalore |
| **Raspberry Pi direct** | US list from $67.50 for CM5 range ([cooler page "Available from $67.50"](https://www.raspberrypi.com/products/cooler/)). CM5 4GB/32GB tested at $70 ([Geerling](https://github.com/geerlingguy/sbc-reviews/issues/58)) | **Not published.** EST: near the $70 list for a 4GB/32GB version without wireless, VERIFY | [raspberrypi.com/contact](https://www.raspberrypi.com/contact/): Subject "Sales enquiries" (after the reseller route) or "Industrial applications". Design Partners via "Raspberry Pi for Industry" on the same page |
| **element14 India** | Sells CM5 ([RPi for Industry](https://in.element14.com/raspberry-pi-industry)). Price not captured | Quote | **in-sales@element14.com**, **1800 108 3888** (toll free), 9:00–18:00 Mon–Fri. Fax +91 80 4000 3880. Web form: [Request a Quote](https://in.element14.com/request-a-quote) (upload BOM with target price) |
| Aryabot / Glassfield Infotech (claims official sourcing; approved status not verified) | – | Bulk form | [aryabot.in/raspberry-pi-bulk-orders](https://aryabot.in/raspberry-pi-bulk-orders/) |

Note: the ₹15,000 India price (≈ $170 EST) is about 2.4× the $70 US test price. That gap is the main case for a direct or OEM quote.

## Part 2: Alternative compute modules
| Module | Price | Size / connector vs our CM5 carrier | CPU / GPU / NPU | Display / camera | BSP / mainline | Local-stack performance (sourced) | India |
|---|---|---|---|---|---|---|---|
| **Raspberry Pi CM5 4GB** (baseline) | $70 (4GB/32GB, tested). ₹15,000 India | 55 × 40 mm, 2 × 100-pin | 4× A76 2.4 GHz, VideoCore VII, **no NPU** | 2× 4-lane MIPI DSI/CSI. libcamera with IMX708 AF native | Raspberry Pi OS, first-party | whisper tiny.en 1.15 s / base.en 2.13 s. qwen2.5:1.5b 10 tok/s (Ollama). Piper 0.53 s | Silverline |
| **Radxa CM5** (RK3588S2) | **$75** (4GB/32GB) ([Liliputing](https://liliputing.com/radxa-cm4-with-an-rk3576-processor-could-be-a-cheaper-alternative-to-the-radxa-cm5-with-rk3588/)). **₹7,732.20 + GST** (Hubtronics, 0 in stock) ([Hubtronics](https://hubtronics.in/rm120%E2%80%91d4e32r26)) | 55 × 40 (Radxa site says 56 × 41) mm, **3 × 100-pin** 0.4 mm. Works in RPi **CM4** IO boards ([Radxa](https://www.radxa.com/products/cm/cm5/)). **Not drop-in for a Pi CM5 carrier**: the pinout is CM4-based, so needs a carrier spin/re-validation | 4× A76 + 4× A55, Mali-G610 MP4 (Vulkan 1.2, GLES 3.2), **6 TOPS NPU** | 1× 4-lane + 1× 2-lane MIPI DSI TX. 1× 4-lane + 1× 2-lane CSI RX. Rockchip ISP (vendor rkaiq). Operating 0–50 °C | Vendor Debian/Android (5.10/6.1). Mainline: Panthor GPU + Mesa (Vulkan 1.4 conformant). Rocket NPU in mainline 6.18+, but limited to quantised convs ([FOSDEM 2026](https://archive.fosdem.org/2026/events/attachments/KLFW73-no-line-like-mainline-rockchip/slides/267550/no-line-l_vrjwxmj.pdf), [techveda](https://www.techveda.live/2026/08/19/mainline-npu-driver-rk3588/)). ISP/libcamera upstream "in development" ([Collabora 7.2](https://www.collabora.com/news-and-blog/news-and-events/kernel-7.2-rk3588-media,-smarter-gpu-memory,-and-rust-foundations.html)) | **RKLLM Qwen2.5-1.5B W8A8: 16.32 tok/s** on RK3588 ([rknn-llm](https://github.com/airockchip/rknn-llm/tree/main/benchmark.md)). CPU about 7 tok/s ([rkllm-server](https://github.com/matttoledo/rkllm-server/blob/main/README.md)). whisper.cpp base RTF 0.16 at 8 threads ([TuringPi](https://turingpi.com/whisper-cpp-piper-tts-arm64-turing-pi-rk3588/)) | Hubtronics (stock 0) |
| **Radxa CM4** (RK3576) | **$70** (4GB/32GB) (Liliputing) | Same Radxa CM family form (55 × 40, 3 × 100-pin) (Liliputing table) | 4× A72 2.2 + 4× A53, Mali-G52 MC3, **6 TOPS NPU**, Wi-Fi 6/BT 5.4 | 1× 4-lane DSI. CSI per table. 16 MP ISP (RK3576, per Luckfox spec) | Vendor BSP. Mainline basic SoC support landed. **NPU not merged** (v10 patches, Aug 2026) ([dri-devel](https://lists.freedesktop.org/archives/dri-devel/2026-August/592332.html)) | RK3576 RKLLM: TinyLlama 1.1B w4a16 **21.32 tok/s**, InternLM2 1.8B w4a16 13.65 tok/s. **No Qwen2.5-1.5B row** (rknn-llm). ROCK 4D CPU deepseek-r1:1.5b **7.69 tok/s** ([sbc.compare](https://sbc.compare/48-radxa-rock-4d-8gb)) | Not found |
| **Radxa CM3** (RK3566) | From **$20** (1GB/8GB). 4GB price not found | 55 × 40, 3 × 100-pin, CM4-IO compatible ([Radxa docs](https://docs.radxa.com/en/som/cm/cm3/getting-started/introduction)) | 4× A55 1.8 GHz, Mali-G52 2EE, **1 TOPS NPU** | Dual MIPI-DSI, CSI. PDM 8-ch with VAD | Vendor BSP. Rocket NPU not supported for RK3566 (FOSDEM) | No sourced Whisper/LLM figures. 4× A55 is **likely too slow** for 1.5B at 8 tok/s (EST, unverified) | Not found |
| Luckfox Core3576 | $119.99–185.99 ([Luckfox](https://www.luckfox.com/EN-Core3576)) | 69.6 × 45 mm, **260-pin SO-DIMM**, ❌ not compatible | RK3576, 6 TOPS | 4-lane DSI, 2× CSI D-PHY + D/C-PHY, 16 MP ISP | Vendor | as RK3576 | – |
| Firefly Core-3576JD4 | $189 (4GB/64GB) ([Firefly](https://www.t-firefly.com/products/core-3576jd4-low-power-large-model-aiot-core-board)) | 69.6 × 45 × 4.15 mm SO-DIMM ❌ | RK3576 | – | Android 14 / Linux / Buildroot | – | – |
| Forlinx FET3576-C | Price not found | 50 × 68 mm, **4 × 100-pin** 0.4 mm B2B, 1.5 mm stack ❌. **12 V input** ([Forlinx](https://www.forlinx.net/product/rk3576-c-system-on-module-156.html)) | RK3576 | – | Linux 6.1, 10–15 yr lifecycle | – | – |
| Seeed reComputer RK3576 | $222.24 ([OpenELAB](https://openelab.com/products/seeed-studio-recomputer-rk3576-module-4gb-ram-32gb-emmc)) | 55 × 40 mm | RK3576, LPDDR5 | – | – | – | – |

**Under $60 with 4 GB and an NPU:** none confirmed. Radxa CM4 at $70 and Radxa CM5 at $75 are the cheapest 4GB NPU modules found. The Radxa CM5 India price of ₹7,732 + GST ≈ $88 incl. GST is already about half the Pi CM5 India price.

**Software change effort vs CM5 (qualitative):**
- **High** for Rockchip.
  - No Raspberry Pi OS and no `rpicam`/libcamera AF pipeline: camera via the vendor rkaiq ISP. IMX708 autofocus tuning is not available; use vendor-supported sensors.
  - Different DSI panel device-tree. NPU models need RKNN/RKLLM conversion (vendor kernel `rknpu`). Qt/Wayland on Mali is OK (Panthor/Panfrost).
  - Carrier respin: CM4-style pinout plus a third connector.
- **Medium-high** for the RK3576 parts: same as above, with less mainline maturity.

## Part 3: Power vs the about 2 W sustained budget
**Measured idle power (sourced; conditions as stated in each source):**
| Module / board | Idle | Load | Conditions | Source |
|---|---|---|---|---|
| Pi **CM5** 4GB | **2.4 W** (2.3 W Lite) at the wall | 8.5 W stress-ng, 9.4 W HPL | Pi OS Bookworm, kernel 6.6.51, on IO board. Display not stated | [Geerling sbc-reviews #58](https://github.com/geerlingguy/sbc-reviews/issues/58) |
| Pi CM5 | **2.65 W** | 6.66 W stress at 5 min (passive) | Passive cooler, stock 2.4 GHz | [shumeipai](https://shumeipai.nxez.com/2024/12/11/raspberry-pi-compute-module-5-review.html) |
| Pi 5 2GB D0 / 4GB C1 (proxy) | 2.4 W / 3.3 W | 8.9 / 9.8 W | Same test parameters across models | [Geerling](https://www.jeffgeerling.com/blog/2024/new-2gb-pi-5-has-33-smaller-die-30-idle-power-savings/) |
| Pi 5 | – | – | Idles at **1500 MHz** on default settings, Wi-Fi/BT on (LinuxLinks note) | [LinuxLinks](https://www.linuxlinks.com/radxa-rock-4d-single-board-computer-running-linux-power-consumption/) |
| **Radxa CM5** (RK3588S2) 8GB | **1.2 W** at the wall | 8.4 W stress-ng, 10 W HPL | Debian 11, kernel 5.10, Radxa CM5 IO board | [Geerling #40](https://github.com/geerlingguy/sbc-reviews/issues/40) |
| RK3588 SoM (Forlinx) | 2.37 W standby. **0.59 W suspend** | 6.98 W | Linux | [Forlinx](https://www.forlinx.com/article-new-c22/1335.html) |
| **RK3576** SoM (Forlinx) | **1.46 W** no-load boot | 3.44 W at 100% CPU | Linux | same |
| RK3576 Radxa ROCK 4D | **1.5 W** | 4.8 W load, 6.2 W Ollama | board | [sbc.compare](https://sbc.compare/48-radxa-rock-4d-8gb) |
| RK3576 ROCK 4D | 2.7 W | – | Radxa OS with KDE, **Wi-Fi/BT on**, idles at 408 MHz-class | LinuxLinks |
| Display (Lida 4.3" DSI) | LCD max **120 mA at 3.3 V ≈ 0.4 W** | – | module only | [Lida](https://www.made-in-china.com/showroom/lida-screen/product-detailmFwTsDCAkSVk/China-4-3inch-Mipi-Dsi-LCD-Module-800X480-with-Capacitive-Touch-for-Raspberry-Pi.html) |

**Ranking (lowest idle first):** Radxa CM5 1.2 W < RK3576 SoM 1.46–1.5 W < Pi CM5 Lite 2.3 W ≈ Pi CM5 4GB 2.4 W (to 2.65 W) < RK3588 SoM 2.37 W.

**Against the 1.6–2 W sustained budget (total device):**
- **Pi CM5:** idle at **2.3–2.65 W** plus the display at about 0.4 W is **already over 1.6 W and over 2 W**. It only fits with aggressive underclocking (not measured here) or display-off sleep. Burst AI is CPU-only at about 8–9 W, so bursts must be short (the thermal_v2 burst rule is about 30 s for about +1.2 K).
- **Radxa CM5 / RK3576:** idle at **1.2–1.5 W** plus 0.4 W display ≈ 1.6–1.9 W. That **fits about 2 W** and is marginal at the 1.6 W/35 °C limit. NPU LLM decode moves load off the CPU (rkllm-server notes the NPU "leaves the CPU free"). Measured NPU-inference power was not found, so VERIFY.
- **No option fits the 0.6 W budget at 45 °C while awake.** Only suspend fits (RK3588 SoM suspend 0.59 W).

**Power-saving levers:**
1. **CPU caps:** cpufreq governor `powersave`/`schedutil`, a lower `arm_freq_min`/`arm_freq`, and offlining 2 cores during idle (`echo 0 > /sys/devices/system/cpu/cpuN/online`). The Pi 5 idles at 1500 MHz by default, while the RK boards idle at about 400 MHz (LinuxLinks), which explains part of the idle gap.
2. **Backlight:** PWM dimming and auto-off. The LCD is about 0.4 W at max (Lida). Use the thermal_v2 stage 1/2 backlight cuts.
3. **Wi-Fi power save:** `iw dev wlan0 set power_save on`. Turn the radio off when offline. LinuxLinks shows idle rising with Wi-Fi/BT enabled (ROCK 4D 2.7 W with Wi-Fi vs 1.5 W in another test; the test setups differ).
4. **Companion MCU wake:** keep the CM5 off or suspended. The STM32U031 (Stop 2 at 630 nA) handles buttons, push-to-talk and RTC alarms, and powers up the CM5 on demand. Note that the Pi CM5 suspend-to-RAM behaviour was not sourced. Plan for a full power-down plus fast boot, or test suspend.
5. **NPU offload** (Rockchip only): run the LLM on RKLLM at 16 tok/s and Whisper on CPU/NPU. This frees CPU cores so they can stay clocked down.
6. **Cloud offload** with user consent when the device is hot, as in thermal_v2 stage 0.

## Recommendation
| SKU | Pick | Why | Risks |
|---|---|---|---|
| **₹29,999, 4 GB** | **Stay on Pi CM5 4GB (CM5104032)** for v1. Evaluate **Radxa CM5 4GB** in parallel on a second carrier spin | Lowest software risk (IMX708 AF, Pi OS, our existing design). Radxa CM5 roughly halves module cost in India (₹7,732 + GST vs ₹15,000), halves idle power (1.2 vs 2.4 W) and gives 16 tok/s LLM on the NPU | Pi CM5 idle already exceeds the 1.6 W thermal budget. Radxa needs a carrier respin, a new camera pipeline and RKLLM porting. India stock was 0 |
| **₹19,999, 2 GB** | **Radxa CM4 (RK3576) or Radxa CM5 2GB**, if the software port is funded. Otherwise **Pi CM5102032 (₹9,690)** | RK3576 has 1.46–1.5 W idle and 6 TOPS NPU (TinyLlama 1.1B at 21 tok/s on 4-bit). 2GB variant pricing was not found, so quote needed | RK3576 NPU is not mainline. Vendor-kernel dependence. Pi 2GB limits to a 0.5B LLM |
| Not recommended | Radxa CM3 (RK3566): 1 TOPS, A55-only, no LLM benchmarks. Luckfox/Firefly/Forlinx RK3576: wrong connector or 12 V input, and $119+ | | |
