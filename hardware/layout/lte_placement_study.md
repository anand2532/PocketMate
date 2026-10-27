# PocketMate: LTE Cat-4 (Quectel EC25-E/EUX) placement feasibility study
Date: 2026-10-21 IST. Read-only study. PocketMate.kicad_pcb was **not** edited.
Inputs: PocketMate.kicad_pcb (footprint positions parsed read-only), keepouts_v4_22/22b/22d.md, placement_plan_v1.md, and the Quectel EC25 Series Hardware Design V2.5 with its reference design.
Coordinates: enclosure frame, mm, origin at the body centre, +Y toward the top edge.

## 1. Module facts (Quectel EC25 HD V2.5)
- Size (29.0 ±0.15) x (32.0 ±0.15) x (2.4 ±0.2) mm. 144 pads (80 LCC + 64 LGA). 4.9 g. Operating range -35 to +75 °C.
- With a 2-piece shield (frame + lid, ~0.3 mm over the module, 0.5 mm side margin), the keep-out is about **31 x 34 mm and 2.9-3.1 mm above the PCB**. Allow 3.3 mm with tolerance.
- VBAT_BB (pins 59/60) and VBAT_RF (pins 57/58) run at 3.3-4.3 V (3.8 V typical) and **must never drop below 3.3 V**. The supply must deliver ≥2 A.
  - Use a star feed with about 100 µF low-ESR bulk per domain, plus 100 nF, 33 pF and 10 pF at the pins, and a TVS (WS4.5D3HV class, VRWM 4.5 V).
  - Trace widths: VBAT_BB ≥1 mm, VBAT_RF ≥2 mm, wider if long.
- Antenna ports: ANT_MAIN, ANT_DIV and ANT_GNSS, all 50 Ω. Route them as L1 CPWG over L2 GND on our stackup (~0.18 mm per plan §1, recalculate for CPWG), with U.FL/MHF4 at each port and a π-match on each.
- Host link: USB 2.0 HS (CM5 USB2 port). Also PWRKEY, RESET_N, W_DISABLE#, STATUS, RI, AP_READY, with 1.8 V VDD_EXT level shifting. USIM is local to the module.
- Variant: EC25-E covers EU bands (B1/3/7/8/20/38/40/41). EC25-EUX adds more. Both lack US low bands, so confirm the target market with Tech Research.

## 2. What is free on the carrier now
Carrier is X -1..54, Y -34..34.5 (55 x 68.5), with a camera notch at X ≥33, Y ≥10.5.
- **B side:** the CM5 rule area covers X -1..54, Y -30..10, with J1/J2 only. Outside it there is the strip Y 10..34.5 (≤24.5 tall, minus the notch, so ≤34 x 24 usable), which holds U13, U14, Q6, D4 and D5 near J11. There is also a sliver at Y -34..-30.
- **F side:** fully used.
  - Charger/USB-C/PD at X -1..25, Y -34..-14 (U4, Q1, U2, U3, J6, D2).
  - Boost U8/L2 and the MCU U9 at X 10..32, Y -14..2.
  - BQ25895 U5, gauge U6, Q4/Q5, U7 and L1 at X 5..22, Y 4..14.
  - J3/J11/J7 at the top.
  - J4 at (36,4.9), U1/U11/J5/J8/J9/TP1-2 at X 35..47.
  - Wi-Fi/CM5 antenna no-copper zone at X 47.5..54, Y -11.5..-0.5.
  - 150+ passives.
- Largest contiguous free F-side rectangle: well under 20 x 20. **The 31 x 34 module keep-out does not fit anywhere today.**
- Rest of the enclosure: cell 51 x 64 in X ≈ -54..-2.5, then the carrier, then the RF free volume at X 54.4..60 (Wi-Fi FPC antenna at X ~59.7, window in the right end wall at Y -26..12). There is no unused volume to grow the carrier into except over the cell.

## 3. Options

### A. Display side (F) of the carrier, over the CM5
- **Location:** for example X 12..43, Y -30..4, the only 31 x 34 region that avoids J3/J4 and the Wi-Fi zone.
- **Height:** carrier top Z 11.54 + 3.3 = Z 14.84, against the 4.9 limit (Z 16.44). OK, 1.6 margin. Outside the 4.0 ledge band only.
- **What moves:** the boost (U8, L2), MCU U9, Q1/Q2/Q3, U1, U11, J8, J9, TP1/TP2, J12 and roughly 60 passives would have to leave. There is no place on the board to put them, so this only works with option B or a second board. It also adds 3 module antenna feeds and a SIM across the CM5 high-speed field, with the DSI/CSI/USB stripline on L3 directly under the module's ground pads.
- **Antennas:** 3 coax pigtails to windows. The only window is the right end, which Wi-Fi already uses, so you need ≥2 new plastic windows.
- **SIM:** has to be an internal holder, only reachable with the display removed. Or route a tray to the bottom wall (Y -36), which collides with J6 and J12.
- **Thermal:** worst case. The module sits directly over the CM5 SoC (22,-13) and the boost. Up to 2-3 W of LTE TX heat would be added to the CM5 hot spot under the display, with no path to the Al heat-sink back.
- **VBAT:** VSYS is right there (short). That is the only advantage.
- **Verdict: not feasible** without removing the power and MCU section.

### B. Grow the carrier
- To the right there is only ~6 mm (X 54..60), and that is the Wi-Fi RF volume, so it is a no-go.
- Up and down are limited by the walls. The only option is a leftward tongue over the cell (X -1 → -35). That is really option D, but rigid, and rigid has drawbacks:
  - The cell can no longer be front-loaded or replaced.
  - The battery-lead route (X -27..-9, Y 21..32, Z 11.2..12.8) is blocked.
  - The carrier panel grows to ~90 x 68.5, which costs more on 6 layers.
- **Verdict:** possible, but inferior to D.

### C. Back side (B) outside the CM5
- The only region is Y 10..34.5 (24.5 tall). The module's short side is 29 (31 with the shield), so **it does not fit in any orientation**.
- Height (7.6) would be fine.
- The Y -34..-30 strip is 4 mm. No.
- **Verdict: not feasible.**

### D. Separate LTE daughterboard over the cell (**recommended**)
- **Location:** a 4-layer, 0.8 mm board at about **X -52..-8, Y -32..18 (44 x 50)**, sitting on standoffs/a bezel shelf over the cell, with its components facing the display.
  - The module sits at the left end, around X -50..-19, Y -30..4, which puts the RF ports near the left end wall.
  - The nano-SIM, U.FLs, bulk caps, TVS and the FPC connector use the rest.
  - Stay out of Y >18 (battery leads, side-key rib Y 32.4..33.3, flex) and X <-53 (flex drop at X -54.1, ALS at (-58,20)).
- **Height:**
  - Cell pocket top Z 11.3, display back Z 16.8, so there is 5.5 mm.
  - Stack: 0.1 air + 0.8 PCB (Z 11.4..12.2), module + shield 3.3 (Z 15.5), leaving **1.3 mm** to the display back. OK, but at the 4.9-class limit, so avoid the bezel lip (Z 15.8) zones and confirm Z 15.5 clears any bezel ribs over the cell.
  - With the 7.0 mm Akyga prototype cell and its face-folded leads (Z 9.3..10.9) there is more room.
  - Requires a ≥0.5 mm swell allowance to stay intact, so do not let the module bear on the cell. Mount the board on the bezel or frame, not on the cell.
- **What moves or changes:**
  - Nothing on the carrier except **one new FPC/B2B connector** on the carrier's left edge. Candidate: X 0..8, Y -14..-4 (F side, near J10/the boost). This needs a small placement nudge: J10 at (2,-20) and the plan's SWD TC2030 at X 4..12, Y -8..-2.
  - Flex: ~20-24 pins, 0.5 mm pitch, about 25 mm long.
    - Power: 4-6 VSYS pins and 4-6 GND pins, ≥2 A total.
    - USB DP/DM (90 Ω), PWRKEY, RESET_N, W_DISABLE#, STATUS, RI, AP_READY.
  - Alternative: carry VBAT on 2 separate wires plus a power connector.
  - Enclosure: a shelf or standoffs over the cell, a thermal pad path, new antenna windows and a SIM slot.
  - The cell must still drop in before the daughterboard.
- **Antennas:** 3 needed (main, div, GNSS).
  - **Main:** compact LTE FPC (for example a ~40 x 10 mm 698-2690 MHz class) behind a **new plastic window in the left end wall** (X ≈ -62, Y -26..10). That is ≥115 mm from the Wi-Fi antenna at X 59.7 at the opposite end, which gives good isolation (target ≥25 dB). Band-20/8 efficiency will be low in that size. Check with Tech Research.
  - **Diversity:** FPC in the bottom-wall plastic insert near the left corner (X -55..-25, Y ≈ -36), or in the grip-inlay plastic. Keep it ≥λ/4 at 800 MHz (~90 mm ideally, ≥40 mm minimum) from main, and keep it orthogonal.
  - **GNSS:** patch or FPC facing the sky. Put it under the display bezel plastic at the top-left or in the top-wall plastic near X -40, Y 34. It must stay clear of the side-key flex and the mic 1 port.
  - The Al unibody blocks RF, so every antenna needs a plastic window. The windows should be at the left end. Nothing should share the right-end Wi-Fi window.
  - Diversity can be dropped for a first spin (it degrades Cat-4 throughput, and some operators require it for certification).
- **SIM:** push-push nano-SIM (for example a Molex 78723-class part, ≤1.5 mm tall) at the daughterboard's left or bottom edge, with a tray slot in the left end wall or bottom wall at X -50..-38.
  - An internal holder (service access only, display off) is simpler and avoids another wall opening.
  - Alternative: an eSIM MFF2 (6 x 5 mm, soldered) avoids the slot entirely.
- **Thermal:**
  - LTE TX averages 1.5-2.5 W at high uplink power, and the module limit is 75 °C.
  - The board must **not** dump heat into the cell. Put a 0.1 mm PI plus graphite sheet between the board and the cell top, with an air gap.
  - Cut a thermal-pad window in the shield lid, or use a lid-to-bezel/display-frame gap pad (1 mm, ≥3 W/mK) into the Al frame.
  - Expect throttling under sustained uplink. Add the module's internal temperature via AT+QTEMP to the MCU/CM5 thermal policy.
  - The cell side is away from the CM5/fan hot zone, which is good.
- **VBAT source:**
  - **Recommended: VSYS from the BQ25895 (U5).**
    - VSYS stays ≥ VSYSMIN (3.5 V default), even with a low cell or while charging.
    - The MAX17055 sense resistor R18 sees the current, so the fuel gauge stays correct.
    - The BQ25895 BATFET handles 5 A.
    - Feed it through a load switch (≥3 A, for example a TPS22965 class) on the daughterboard, then the star feed to VBAT_RF and VBAT_BB.
    - Local bulk: 2 x 100 µF low-ESR (tantalum polymer, ≤2.0 mm) plus 2 x 22 µF MLCC, then 100 n/33 p/10 p at the pins, and the TVS.
    - Pours: ≥2 mm VBAT_RF, ≥1 mm VBAT_BB, and ≥4 x 0.3 mm vias per layer change.
    - Flex resistance budget: <50 mΩ round trip, so 2 A drops <0.1 V.
  - Direct-from-cell is **not recommended**:
    - It bypasses R18, so the gauge would miss the LTE load.
    - The cell sags below 3.3 V under a 2 A burst near empty.
    - The module would have no undervoltage protection.
    - The VSYSMIN 3.5 V floor would have to be replaced by a separate cutoff.
  - Check that VSYS can supply CM5 boost + LTE together: ~5 A cell-side worst case, with the BQ25895 limit at 5 A. Raise this with Schematic. The power budget may need an LTE power-cap/tx-backoff policy.

## 4. Recommendation
**Option D: a separate LTE daughterboard over the cell**, linked to the carrier by a ~22-pin flex (VSYS, GND, USB2, control).
- Antennas behind new left-end plastic windows (main in the left end wall, diversity in the bottom wall, GNSS at the top-left bezel).
- An internal nano-SIM (or eSIM).
- VBAT from VSYS through a load switch and local 2 x 100 µF bulk.
- The only carrier impact is one flex connector at the left edge (about X 0..8, Y -14..-4), plus a USB2 port and ~6 GPIOs from the CM5/MCU in the netlist. The current placement and routing pass is otherwise untouched.
- Options A and C don't fit; B is D made rigid, with worse serviceability.

## 5. Open items / owners
- Enclosure: daughterboard shelf and standoffs over the cell at Z 11.4. Confirm Z 15.5 + 1 mm clear of the display/bezel over X -52..-8, Y -32..18. Add left-end and bottom plastic windows and an optional SIM slot. Thermal-pad path to the Al.
- Schematic: EC25 sheet, flex connector, CM5 USB2 port allocation, VSYS current budget (BQ25895 5 A), load switch, level shifting.
- Tech Research: final variant (E vs EUX vs regional), antenna part numbers (LTE FPC ≤40 x 10 and GNSS), certification (an integrated module plus a custom antenna needs RED/FCC SAR).
- Layout (me): reserve the carrier flex connector spot once the netlist has it.
