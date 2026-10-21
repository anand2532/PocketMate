# PocketMate v5_22 – micro-blower variant + v4_22 duty-cycle analysis
Generated 2026-10-21 (IST). Builder: build_v5_22.py (built from the PocketMate_v4_22 document). The v4 files were not changed.

## Blower candidates (real datasheets)
| Part | Size (mm) | V / W | Max flow | Max SP | Noise | Mass | Source |
|---|---|---|---|---|---|---|---|
| Sunon UB3H3-700B ("20x20 class") | 17x17x3 | 3 V / 0.11 W | 6.5 l/min | 40 Pa | 32 dBA @30 cm | ~1 g | Sunon Mighty Mini catalogue: https://www.sunon.com/en/MANAGE/Docs/WEBCONT/Files/826/Sunon%20Mighty%20Mini%20Fan_(223-W).pdf |
| Sunon UB5U3-700 | 30x30x3 | 5 V / 0.36 W | 18 l/min | 88 Pa | 25.6 dBA @1 m (~36 @30 cm) | 2.4 g | https://www.sunonusa.com/wp-content/uploads/2025/12/UB5U3-700D03018201F-00-13.pdf |
| Delta BFB03505HHA-CZMS | 30x30x4 | 5 V / 1.15 W | 60 l/min (2.12 CFM) | 110 Pa | 31 dBA avg @1 m (~41 @30 cm) | 11 g | https://media.digikey.com/pdf/Data%20Sheets/Delta%20PDFs/BFB03505HHA-CZMS_Ds.pdf |

## v5_22 placement (UB3H3, the only one that fits at 22 mm)
- Blower at X 4.5..21.5, Y 14..31, Z 2..5. This is the B-side bay between the CM5 top edge and the top wall. The plenum above it runs to Z 9.8 and stays clear of the DSI connector J3 (now X 11..21, Y 20..24, on the carrier at Z ≥ 9.94).
- Intake: 6 slots, each 1.6x5 mm, in the **top wall** at X 5..21, Z 3..8 (48 mm² open). They sit below and away from the mic-mute slider and mics. They are not under the palm.
- Path:
  1. Inlet duct machined into the thick floor block (X 4.5..37, Y 2.5..7.5, Z 2..4).
  2. **Comb fin stack** in the SoC pedestal at (22,-13): 15 channels 1.0 wide, 2.0 deep, at 2.0 mm pitch, X 7.5..37.5. The pad seat at Z 4.0 keeps about 50% contact.
  3. Exit channel at Y -31..-28.4.
  4. Corridor Y -33.2..-30.2 inside the block, then free air to X 54.
  5. It wraps around the boss at (57.5,-31.5), with a free section of about 34 mm².
- Exhaust: 3 slots, each 1.5x6 mm, in the **right-end wall** at Y -33..-26.5, Z 2.5..8.5 (27 mm²). They are below the RF window (Y ≥ -26) and outside the RF keep-out (Y -25..11).
- The v4_22 external recessed back slots are **filled** in v5. They would have broken through into the internal channels, letting dust in and making the back an air path under the fingers.
- Clash check: there are no clashes for the blower, plenum, ducts or corridor against the CM5, battery, camera, connectors or unibody. The only reported clash is `Vol_Fan_30x30_NOFIT`, which is intentional (see below). The Al unibody is now 28.2 cc (76 g). The added blower is about 1 g.
- Restriction: the comb is 30 mm² and the slots are 27–48 mm², at about 30–40 Pa. The UB3H3 runs at roughly 3 l/min in-system, about half its free-air flow. Air ΔT is about 13 K at 1 W picked up, so the exhaust is warm but under 50C at 35C ambient.

## Sustained budget, fan on at typical airflow (skin ≤43C @35C, ≤48C @45C; fan self-heat subtracted)
Model: the passive G (held 0.247 / table 0.140 W/K) plus G_fan = ε·ṁ·cp. The skin hot-spot spreading is Rs = 0.27 K/W; the fan cools the same spot. The idle floor is 2.4–2.65 W.
| Config | G_fan W/K | Held 35C | Flat 35C | Held 45C | Flat 45C | Fits 22 mm? |
|---|---|---|---|---|---|---|
| v4_22 passive | 0 | 1.85 W | 1.08 W | 0.66 W | 0.39 W | yes |
| **v5_22 UB3H3 17x17x3 @~3 l/min** | 0.056 | **2.13 W** | **1.38 W** | **0.70 W** | **0.45 W** | **yes** |
| UB5U3 30x30x3 @~12 l/min | ~0.19 | 2.77 W | 2.06 W | 0.78 W | 0.55 W | no |
| Delta BFB03505 30x30x4 @~25 l/min | ~0.29 | 2.61 W | 1.93 W | 0.23 W | ~0 W | no |
Notes:
- At 45C the air enters only 3 K below the skin limit, so any fan adds little. The Delta's 1.15 W draw cancels its gain at 45C.
- **No configuration sustains the 2.4 W idle at 45C, and the fitting blower does not sustain it even at 35C held.** The fan raises the 35C held budget by about 15%. It does not change the conclusion that the product has to run duty-cycled.

## Why 30x30 does not fit at 22 mm
- The free area beside the CM5 is about 25 mm in Y (CM5 top edge Y 10 to inner wall Y 35.5). The `Vol_Fan_30x30_NOFIT` volume overruns the top wall and camera by 196 mm³.
- Above the cell (Z 11.3..16.8) there is about 5.5 mm of height, enough for a 30x30x4. But it has no duct path to the SoC (1.5 mm gap) and it clashes with the side buttons and speaker.
- Options:
  - Grow the body to 24 mm and put the fan above the CM5 in a ducted lid region.
  - Shrink the cell in Y by about 10 mm, which costs about 0.6 Ah.

## Trade-offs
- Battery: none in v5_22. The cell pocket is unchanged (9.0 mm, about 3.6 Ah). The blower draws 0.11 W, about 3% of a 3 W session.
- Thickness: none (22 mm).
- Space lost: the top-edge B-side bay (about 17x21 mm), previously spare or test-pad space. The internal floor channels reduce floor mass by about 1 g.
- Noise: the UB3H3 makes about 32–35 dBA at 30 cm at full speed, with a high-pitched tonal component at 12.5 krpm. Run it PWM-scaled (about 25 dBA at 60%). A 30x30 Delta would be about 41 dBA at 30 cm.

## Dust ingress
- 1 mm comb channels will collect lint, especially if the device is carried in a pocket.
- Fit a 0.3 mm stainless or PET mesh (adhesive) on the inside of the intake slots and accept about 10–15% flow loss.
- Prefer 1.5 mm channels in production (this costs about 20% of fin area).
- Run the fan only while the CM5 is on. The MCU should do a short reverse-pressure "purge" spin, or none at all, when idle.
- The exhaust sits low on the right end, so it drains rather than collects. IP rating is lost: at best IP3X with mesh. Gaskets are not practical.

## v4_22 passive duty-cycle (from cold; C ≈ 205 J/K, off power 0.05 W)
Soft trip is the governor's first step. Limit is the skin limit reached. Duty is the allowed long-run average on-fraction.
| Case | τ | 35C budget | 3 W: soft / limit | 3 W duty | 5 W: soft / limit | 5 W duty | 45C budget | 3 W: soft / limit | 3 W duty | 5 W: soft / limit | 5 W duty |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Held | 830 s | 1.85 W | 564 / 744 s | 61% | 260 / 331 s | 36% | 0.66 W | 70 / 164 s | 21% | 19 / 70 s | 12% |
| Table | 1464 s | 1.08 W | 480 / 599 s | 35% | 242 / 302 s | 21% | 0.39 W | 69 / 157 s | 11% | 19 / 69 s | 7% |
| Pocket | 2500 s | 0.64 W | 447 / 547 s | 20% | 234 / 289 s | 12% | 0.23 W | 69 / 154 s | 6% | 19 / 69 s | 4% |
The single-node model underestimates the fast SoC-pad transient. Treat the 45C trip times (under 30 s) as indicative only.
