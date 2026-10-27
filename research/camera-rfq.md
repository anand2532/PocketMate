# PocketMate camera RFQ: OV5647 AF with custom 22-pin tail (v1, 2026-10-21, not sent)
**Basis:** display-spec.md §3–§5.
- Pinout and connector verified from the Raspberry Pi *CM5 IO Board rev 2 KiCad files* (RP-008099-DD-1), sheet CM5_HighSpeed 2/4 (Rev 1), J5/J16 FH12-22S-0.5SH.
- Impedance from the *CM5 Datasheet* Release 3, §2.5.2, p.10.

## Vendor
**Shenzhen City Haozhou Technology Co., Ltd** (HZ-OV5647AF S1.0)
- **ceo@cammoduletech.com**, +86 13682433881 (Mrs. Penny, phone/WhatsApp)
- B310, Nanshan Internet Innovation and Creative Service Base (Phase II), No. 126 Xia Road, Shekou, Nanshan, Shenzhen
- ✅ Fetched live from [cmoscameramodules.com/contactus.html](https://www.cmoscameramodules.com/contactus.html) on 2026-10-21
- Product: [ChinaX listing](https://www.chinax.com/cmoscameramodules/c2042731-raspberry-pi-camera-module)

## Requirements
| Item | Value |
|---|---|
| Module | OV5647 5 MP, autofocus (HZ-OV5647AF), 2-lane MIPI CSI-2 |
| Tail | **22-pin, 0.5 mm pitch**, for Hirose FH12-22S-0.5SH (bottom contact), **about 14 mm** (to be fixed by drawing), U-fold-capable. Stiffener on the contact end only; thin PI (≤ 0.15 mm target, same as display) |
| Pinout | RPi 22-pin (display-spec.md §4): 1 GND, 2 D0_N, 3 D0_P, 4 GND, 5 D1_N, 6 D1_P, 7 GND, 8 C_N, 9 C_P, 10 GND, 11–15 D2/D3 (unused, 2-lane), 13/16/19 GND, 17 CAM_GPIO0 (power enable), 18 CAM_GPIO1, 20 SCL, 21 SDA, 22 +3.3 V |
| Impedance | 100 Ω differential, P/N matched within 0.15 mm |
| AF | Please state the AF driver (VCM IC) and I2C address |

## Email (paste-ready)
**To:** ceo@cammoduletech.com
**Subject:** RFQ: HZ-OV5647AF with custom 22-pin 0.5 mm × ~14 mm FPC tail (PocketMate)

> Dear Penny,
>
> We are developing PocketMate, a handheld device on the Raspberry Pi Compute Module 5. We would like a quotation for your **HZ-OV5647AF** autofocus module with a **custom FPC tail** in place of the standard 15-pin connector:
>
> 1. **22-pin, 0.5 mm pitch** contact end for a Hirose FH12-22S-0.5SH (bottom-contact) connector, **tail length about 14 mm**. We will send a drawing to fix the length and contact side. Stiffener on the contact end only, thin polyimide (≤ 0.15 mm target) so the tail can U-fold.
> 2. **Raspberry Pi 22-pin camera pinout:** 1 GND, 2 D0_N, 3 D0_P, 4 GND, 5 D1_N, 6 D1_P, 7 GND, 8 CLK_N, 9 CLK_P, 10 GND, 11 D2_N, 12 D2_P, 13 GND, 14 D3_N, 15 D3_P, 16 GND, 17 CAM_GPIO0 (power enable), 18 CAM_GPIO1, 19 GND, 20 SCL, 21 SDA, 22 +3.3 V. 2-lane, so D2/D3 are not used.
> 3. MIPI pairs **100 Ω differential**, P/N length-matched within 0.15 mm.
>
> **Quantities:** 10 samples; 1,000 pcs; 10,000 pcs/year.
>
> **Please provide:**
> - FPC drawing and stack-up
> - Price breaks
> - NRE
> - Sample and mass-production lead times
> - Lens FOV options
> - AF driver IC details
>
> Best regards,
> Anand Mohan Pandey
> PocketMate
