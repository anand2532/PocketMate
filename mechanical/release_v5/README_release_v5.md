# PocketMate enclosure – release v5 (prototype freeze)

Written Tue 27 Oct 2026, about 22:00 IST. Source: `../pocketmate_assembly_v4_22e.step`. All earlier files in `mechanical/` are untouched.
Board inputs are read-only copies:
- `hardware/kicad/PocketMate.kicad_pcb`, md5 `126f5c6c…`, 155 footprints including Layout's reserved **J14**. Exported with kicad-cli to `ref/carrier_kicad_export_126f5c6c.step`.
- `hardware/kicad-lte/kicad-lte.kicad_pcb` stub.

Neither board was modified. Frame: origin at body centre, +X right, +Y top edge, Z measured from the outer back face. Units are mm.

**Tooling note.** The FreeCAD MCP and the FreeCAD binary were not available for this release (the namespace is gone and apt returns 500). Release v5 is built in **CadQuery 2.8 / OpenCascade**, so **there is no .FCStd file for v5**. The STEP files open in FreeCAD, Fusion and SolidWorks. To rebuild everything: `build_release_v5.py` → `check_release_v5.py` → `export_release_v5.py` → `drawings_release_v5.py` (plus `key_gaps_release_v5.py`).

## 1. Deliverables
| What | Path |
|---|---|
| Assembly STEP (80 named bodies, coloured) | `pocketmate_assembly_release_v5.step` |
| Per-part STEP (24 physical parts) | `step_parts/<Part>_release_v5.step` |
| Envelopes and keep-outs (reference only) | `step_parts/envelopes_and_keepouts_release_v5.step` |
| STL, printable/machined (12) | `stl/` – unibody, bezel, action cap, 4 RF windows, 2 grip inlays, camera window, Cu spreader, LTE PCB outline |
| Drawings (18 sheets) | `drawings/pocketmate_drawings_release_v5.pdf` plus one DXF per sheet (`unibody_*`, `bezel_plan`, `window_*`, `flat_*`, `lte_daughterboard_outline`) |
| Interference list (full) | `INTERFERENCE_CHECK_release_v5.md`, `work/check.json`, `work/key_gaps.json` |
| Carrier reference | `ref/carrier_kicad_export_126f5c6c.step`, `ref/carrier_footprints_126f5c6c.json` |

All STLs are watertight except `Al_Unibody`, which has one inherited non-manifold edge (see open item O1). Slicers repair it automatically, and the CNC shop works from the STEP anyway, which is a valid single solid.

## 2. What changed vs v4_22e
1. **LTE daughterboard and shelf.** The 0.8 mm 4-layer board sits at Z 11.4–12.2 over the cell. The outline is X −52..−8, Y −32..17, with:
   - a speaker notch, X −52..−34.4 for Y < −23.4;
   - a J7-housing corner notch, X > −9.4 for Y > 15.5;
   - two ears down to Y −35: E1 at X −27..−22.5 and E2 at X −13..−10.
2. **Supports.** There is no room for a separate shelf plate: the cell pocket top is at Z 11.3 and the board bottom at 11.4. **The board is its own shelf.** It is held by:
   - two Al ledges in the bottom wall under the ears (top Z 11.40);
   - two PC clamp posts on the bezel above the ears (Z 12.25–15.85; add 0.2 foam tape for preload);
   - two PC fingers from the side-key rib at the top edge (X −41..−38 and −32..−29, Z 12.25–13.25);
   - foam underneath on the cell.

   There are no screws: the over-cell area cannot take bosses.
3. **U1 (EC25/EC200U) is rotated 90°, centred at (−35.8, −5.5).** Its shield/height keep-out is X −51.3..−20.3, Y −22.5..11.5, Z 12.2–15.5, with the shield top at 15.5 as specified.
4. **Nano-SIM, U.FLs and connector.** A hinged nano-SIM holder sits at X −19.95..−8.41, Y −31.6..−17.6. The U.FLs are Main (−51.6..−49.4, 12.4..14.6), GNSS (−47..−44.8, 14.4..16.6) and Div (−27.3..−24.7, −31.6..−29). The daughterboard J1 is an FH12-22S rotated 90°, mouth +X at X −8.0, with contacts centred at Y −6.5. That lines up with **carrier J14 as Layout placed it** (courtyard X −0.95..7.04, Y −15.1..2.1). The link is a 22P 0.5 mm FFC.
5. **Thermal path.**
   - 0.5 mm gap pad on the shield (29.4×33);
   - 0.5 mm C1100 Cu spreader, Ni-plated with Kapton on the display side. The plate is at Z 15.9–16.4, then a 0.7 mm joggle and a tab at Z 15.2–15.7;
   - 0.3 mm pad on a new **Al thermal post** in the bottom wall (X −34.4..−28.4, top Z 14.9). The bezel bottom lip (Z 15.8) clamps it.
6. **Cell insulation.** A PET/PI liner sits on the cell top: 0.1 mm at Z 10.8 for the production cell, 9.3 for the Akyga cell (with a relief around the Akyga leads). Closed-cell foam fills the gap to the board: 0.5 mm for production, 2.0 mm for the prototype. The daughterboard never touches the cell.
7. **RF windows** (plastic, bonded):
   - LTE main, left end wall: 42×16 (Y −28..14, Z 2..18);
   - GNSS, top-left of the left wall: 10.5×13.5 (Y 17..27.5, Z 2..15.5), with a 3 mm Al web between them;
   - diversity, bottom wall bottom-left: 18×5.6 (X −27.6..−9.6, Z 12..17.6).

   Each window has an antenna envelope, a 4.8–5 mm keep-out and a modelled coax route.
8. **Wi-Fi pigtail re-routed.** The v4 envelope rose through the CM5 and carrier and dipped into the floor rib. It now runs below the CM5 at Z 1.9–3.1, then up to the antenna feed.
9. **Bezel.**
   - The v4_22e bezel was **two bodies** (the frame and the inner skirt shared only 3.9 mm²). They are now bridged into one printable part.
   - The corner fixing had no screw path: the unibody had a Ø2.2 blind hole from the top and the bezel a Ø3.2 blind hole from the bottom. It is now **front-entry M2 countersunk**: Ø2.4 clearance plus a 90° countersink Ø4.1 in the bezel, and Ø2.1×7 in the Al bosses for M2 helical inserts.

## 3. Key clearances (measured on the B-rep)
| Pair | Gap |
|---|---|
| Shield top 15.5 → display back 16.8 | **1.30** |
| Cu spreader top 16.4 → display back | 0.40 (Kapton 0.05 on spreader) |
| Spreader → bezel lips | 0.10 |
| Shield → bezel left lip | 0.30 |
| Daughterboard → cell pocket | 0.10 (foam/liner fill it) |
| Daughterboard → production cell | 0.60 |
| Daughterboard → production leads | 1.10 |
| Daughterboard → Akyga leads | 1.30 |
| Daughterboard → J7 housing | 0.56 |
| Daughterboard → speaker | 0.60 |
| Shield → speaker | 1.50 |
| SIM holder → shield | 0.35 |
| SIM holder → U1 pad toes | ≈0.2 (courtyard overlap 0.3, see O6) |
| Coax GNSS → side-key flex riser | 0.15 |
| Coax GNSS → main U.FL | 0.10 (dress both with Kapton) |
| GNSS keep-out → ALS (−58, 20) | 1.47 |
| GNSS window → ALS | 1.96 |
| Main keep-out → ALS | 2.60 |
| GNSS keep-out → side-key flex | 0.80 |
| Main keep-out → side-key flex | 2.0 |
| Main keep-out → NTC case | 0.30 (below it; tiny SMD part, acceptable) |
| Main FPC → cell (production and Akyga) | 6.45 |
| Main / GNSS antennas → battery leads | ≥32 |
| LTE main FPC → Wi-Fi antenna / window | 119.8 / 120.7 |
| Diversity window → USB-C | 18.6 |
| Wi-Fi pigtail → unibody / CM5 / carrier | 0.57 / 1.90 / 4.49 |

## 4. Interference result (check_release_v5.py, 80 parts × 144 carrier solids)
Zero enclosure clashes remain. All of the new-part clashes found on the way were fixed in the builder:
- SIM ↔ shield 10.7 mm³;
- spreader ↔ shield 0.36;
- Akyga leads ↔ liner;
- bezel lip ↔ diversity FPC;
- floor fillet ↔ main keep-out;
- Wi-Fi pigtail ↔ CM5, carrier and floor;
- diversity coax ↔ clamp post;
- GNSS coax ↔ GNSS U.FL and flex;
- post and ledges floating 0.2 off the wall.

Remaining items (Layout or board level, not enclosure):
| # | Pair | Overlap | Fix |
|---|---|---|---|
| C1 | carrier **J8** THT pins ↔ CM5 envelope | 0.71 mm protrusion below the carrier (Z 9.23 vs 9.94) | Trim J8 leads flush (≤0.3 mm) after soldering, or use an SMD header. |
| C2 | Vol_J4 (FH12 cable/actuator envelope, 2 mm in front of the J4 body) ↔ **Q2**, **C6** | 0.10 / 0.50 mm | Layout: move Q2/C6 ≥0.6 mm −Y, or confirm the J4 actuator and DSI cable clear 0.79/0.5 tall parts. The real J4 body is 1.85 / 1.31 from them. |
| C3 | Vol_J12 (DNP fan header) ↔ **R3** | 0.07 mm | Layout nudge R3 −Y 0.2, or accept (J12 is DNP). |
| C4 | U1 courtyard ↔ SIM holder | 0.3 mm courtyard only | Accept/waive. Copper is 0.2 clear. No room to move: board edge −8.0, J7 notch. |

Intended or classified pairs (listed in the check file): mated connectors (B2B, J7, flex-in-FH12, coax-in-U.FL), face contacts (CM5 on standoffs, pad on pedestal, ears on ledges), production vs prototype variants, and pocket envelopes. **The SIM lid swing intersects the display, so the bezel and display must come off to swap a SIM.** That is a service step, not a clash.

## 5. RF decisions
- **LTE main:** a 42×16 PC window in the left end wall for a 40×15×0.2 FPC. The reference is the **Abracon AANI-FB-0173** class: 698–960 / 1710–2690 MHz, u.FL (datasheet checked). The Taoglas FXUB63 (96×21) and Molex 146185 (84×15) from `research/cellular-4g.md` **do not fit** any wall of this body. The FPC bonds to the window inner face; the keep-out is 4.8 mm inward with no metal. The cell is 6.45 mm away, so plan a matching/tuning pass (π-match on the daughterboard).
- **GNSS:** a 10.5×13.5 window, top-left of the left wall. **No verified FPC GNSS antenna fits.** The smallest Taoglas FPC found is 38×37. Options are a ≤9.5×12.5×1 chip or patch on a small FPC carrier, or **dropping GNSS for the prototype**. The ALS ledge is 2 mm away; there is no conflict.
- **Diversity:** an 18×5.6 window in the bottom wall, bottom-left. The space is boxed in by the speaker, the thermal post, the cell, the USB-C and the bezel lip at Z 15.8, so the FPC can be at most **16×3.3**. Only a custom high-band strip would fit. **Recommendation: fit no diversity antenna on the prototype.** Keep the U.FL, the window and the 0R/π footprint, and disable RX diversity in modem firmware (check the exact Quectel AT command in the EC25 AT manual).
- The Wi-Fi window (right end) is unchanged, ≈120 mm from LTE main. All coax is Ø1.13 mm U.FL, dressed with Kapton.
- **Window material:** SLA clear or tough resin, or machined PC. **No metal-, carbon- or graphite-filled resins.** Do not paint or plate the windows. Anodize the unibody before bonding.

## 6. Nano-SIM decision
**A hinged-lid nano-SIM holder on the daughterboard**, reached by removing the bezel (4× M2) and lifting the display. Candidates, MPN to be confirmed: TE 2452796-1 class (≈1.4 mm tall, 14×11.5), or SIM8060 / JXTCONN equivalents. Keep an **MFF2 eSIM footprint** as an option.

A wall slot or tray was rejected:
- the bottom wall is full (speaker, thermal post, diversity window, USB-C);
- the left wall is all antenna windows;
- a metal holder at an antenna window detunes it;
- a push-push holder needs a 3.2 mm recess and an insertion sweep that hits the shield or carrier.

For a prototype, SIM swaps are rare, so service access is acceptable.

## 7. Fab notes
### 7.1 Unibody – CNC 6061-T6 (India)
- Stock is ≥128×78×21 mm (finished 125×75×19). It is 3-axis plus end-wall ops: the RF windows, the action hole and the side slots need side access or a 4th axis.
- **Tolerances:**
  - general ISO 2768-mK;
  - RF window slots +0.10/0, inside corners R≤0.5 (match the plug corners);
  - thermal post top Z 14.90 +0/−0.05, flat 0.05;
  - DB ledges Z 11.40 +0/−0.05;
  - CM5 standoff tops Z 5.00 ±0.05;
  - display/bezel seat (top face Z 19.0) flat 0.1;
  - corner bosses Ø2.1 ×7 deep for M2×0.4 helical inserts (STI tap);
  - CM5 standoffs Ø2.05–2.1 tapped M2.5×0.45, 4 deep.
- **Finish:** bead blast, then **Type II anodize** (clear or black, 10–15 µm). Mask the thermal contact faces (CM5 pedestal under the pad, LTE post top) and the threads. Fit the inserts after anodize. For a scratch-resistant edge, use Type III hard anodize, accepting +25–50 µm/face on the window slots.
- **Verified Indian vendors (web, 27 Oct 2026):**
  - **Partwork**, Pune (partwork.io): 6061-T6, ±0.025–0.127, Type II/III anodize (Type II ≈ +₹500–1,200), plus SLA/SLS/MJF;
  - **ProtoWise** (protowise.in): instant CNC quotes;
  - **Robocon CNC** (roboconcnc.com): 6061-T6, thread inserts, hard anodise, CMM;
  - **BotBit** (shop.botbit.in): CNC RFQ with anodizing;
  - **ProtoZone** (theprotozone.com): CNC plus SLA/SLS/MJF;
  - **Cadqua 3D**: SLA/SLS/CNC.

  Send `step_parts/Al_Unibody_release_v5.step` with `drawings/unibody_*.dxf` and the PDF.
### 7.2 Whole-body fit-check alternative (before cutting Al)
Print the unibody and bezel from `stl/` in SLA tough resin, or MJF PA12, to check fit for the board, cell, daughterboard, FFC, coax and display. Robu.in's SLA service lists 0.025–0.2 mm layers, ±0.2 and 3–5 days. Its MJF goes through a partner and takes 15–20 business days, with no online quote. Partwork and ProtoZone also offer SLA and MJF. On a printed unibody, tap the M2.5/M2 holes directly or use heat-set inserts. Expect ±0.2 mm, so the 0.1–0.3 mm gaps in §3 are only indicative on a print.
### 7.3 Plastic parts
- Bezel/display frame, action cap and grip inlays: SLA tough resin (black). Machined PC for later builds.
- RF windows: SLA clear or tough resin, **no metal-filled resins**. Print 0.05/side under the slot and bond with two-part epoxy.
- Camera window: laser-cut 1.5 mm optical PC/PMMA. SLA clear is not optical grade without polishing.
- Cu spreader: laser-cut 0.5 C1100 from `flat_HeatSpreader_Cu_0p5_release_v5.dxf`, then form the joggle and Ni plate. **Fyord**, Bangalore (laser cutting from DXF), is verified for sheet-metal cutting; copper capability is **not** verified, so ask first.
- LTE PCB: 4-layer 0.8 mm. **PCB Power**, Ahmedabad (4-layer 0.8 mm fabrication and assembly, verified) has a 50×50 minimum assembly size, so panelize the 44×52 board.
### 7.4 Mechanical hardware BOM (per unit)
| Qty | Item | Notes |
|---|---|---|
| 4 | M2.5×10 pan head A2 (ISO 7045) | Carrier + CM5 → Al standoffs. **Confirm length on the first fit:** stack ≈6.5 mm + ≥3 mm thread. |
| 4 | M2×6 countersunk ISO 7046-1 A2 | Bezel corners, front entry |
| 4 | M2×0.4 helical insert 1.5D (3 mm), STI | Al corner bosses (printed body: heat-set M2) |
| 1 | Gap pad 0.5 mm ≥3 W/mK, 29.4×33.0 | Shield → spreader |
| 1 | Gap pad 0.3 mm ≥3 W/mK, 6.0×1.9 | Spreader tab → Al post |
| 1 | Cu C1100 0.5 spreader, Ni, Kapton 0.05 on top | `flat_HeatSpreader…dxf` |
| 1 | CM5 pad | Unchanged from v4_22e |
| 1+1 | PET/PI 0.1 liner (production / Akyga) | `flat_Liner_*` |
| 1+1 | Closed-cell PE/PU foam 0.5 / 2.0 | `flat_Foam_*`; fit the one that matches the cell |
| 4 | 0.2 mm foam tape dots | Bezel clamp-post tips and finger pads |
| 1 | 22P 0.5 mm FFC, Type A (same-side contacts), ≈14 mm | J1 (LTE) ↔ J14 (carrier). Confirm FH12 insertion depth. |
| 2–3 | U.FL Ø1.13 coax | Main, GNSS (and Div). Mostly integral to the antenna FPC; choose the shortest cable option. |
| 1 | LTE main FPC 40×15 (AANI-FB-0173 class) | GNSS and Div per §5 |
| 1 | Hinged nano-SIM holder (MPN TBC) | Optional MFF2 eSIM |
| — | Two-part epoxy, Kapton tape | Window bonding, coax and flex dressing |
### 7.5 Assembly order
1. Unibody: deburr, anodize, unmask. Install the 4 helical inserts.
2. Bond the 4 RF windows (Wi-Fi plus the 3 LTE windows) with epoxy and cure. Stick the antenna FPCs to the window inner faces: Wi-Fi, LTE main, GNSS (if fitted).
3. CM5 thermal pad, then CM5 + carrier onto the standoffs (4× M2.5). Route the Wi-Fi pigtail under the CM5 to its antenna.
4. Side-key flex and keys, action cap, cell NTC pad, then the cell into its pocket. Leads to J7.
5. **PET liner on the cell top, then foam** (0.5 mm production / 2.0 mm Akyga).
6. Daughterboard: ears onto the ledges. Plug the FFC into the daughterboard J1, then carrier J14. Lock both actuators.
7. Mate the U.FLs (main → left wall, GNSS → top-left, Div if fitted). Dress the coax with Kapton, keeping the GNSS coax under the flex riser.
8. Insert the nano-SIM and close the lid.
9. Shield pad, then the Cu spreader (tab onto the 0.3 pad on the Al post).
10. Connect the display FPC to J4 and seat the display in the bezel. Lower the bezel, so the clamp posts and fingers land on the daughterboard, and fit 4× M2 countersunk screws.
11. Power-on test, then the RF check (RSSI/RSRP on main) and the thermal soak (AT+QTEMP).

**SIM service:** remove the 4× M2 screws, lift the bezel + display (DSI FFC slack is needed; O8), and open the SIM lid, which swings 12 mm.

## 8. Thermal
Shield → 0.5 pad → Cu spreader → 0.3 pad → Al post into the bottom wall gives an estimated ~11–14 K/W junction-to-case path. That is fine for an average of ~1 W. EC25 uplink bursts reach about 2.9 W, so sustained uplink must be duty-limited: throttle on AT+QTEMP.

## 9. Open items
**Release v5**
- **O1** – The action-button hole (inherited from v4_22b) is tangent to the top face at Y 20, leaving a zero-thickness lintel. That gives 1 non-manifold STL edge. Fix in the next rev: lower the hole top or open it as a U-slot under the bezel. Check the cap top at 18.8.
- **O2** – Layout's `hardware/kicad-lte` stub does **not** match this release:
  - The stub outline is X −52.05..−7.95, Y −30..14, with no speaker notch. It clashes with the speaker by 18 mm³.
  - The stub's U1 is unrotated at (−33.75, −12), so the module overlaps the speaker by 88 mm³.
  - The stub's J1 is at Y −10; J14 is centred at Y −6.5.

  Action: import `drawings/lte_daughterboard_outline_release_v5.dxf`, rotate U1 90° to (−35.8, −5.5), and put J1 at X −12, Y −6.5, rot 90.
- **O3** – Carrier J8 THT leads (C1); J4 vs Q2/C6 (C2); J12 vs R3 (C3).
- **O4** – No verified GNSS antenna fits. The diversity antenna is a custom-only part; the recommendation is to omit it on the prototype.
- **O5** – Main antenna tuning near the cell and the Al wall. Order AANI-FB-0173 samples and verify the cable length options.
- **O6** – The SIM holder MPN is TBC, and SIM ↔ U1 courtyard is 0.3 (waiver).
- **O7** – Confirm LTE netlist nets on J14 and the VSYS budget: 6 pins × 0.5 A on FH12 ≈ 3 A, which covers the ~2 A EC25 TX peaks. Keep local bulk capacitance on the LTE board per the Quectel hardware design guide.
- **O8** – DSI FFC slack is needed to lift the bezel + display for SIM service. This ties into the DSI Z-fold item.
- **O9** – Screw lengths are to be confirmed on the first build (M2.5 stack).

**Carried forward**
- DSI Z-fold length;
- action-cap clearance;
- side switches 0.43 from the wall;
- Molex 205338/205341 insertion depth;
- JS202011 datasheet ambiguities;
- SW5 cap;
- J12 height limit 4.26;
- stale 504050 entry in the placement plan.

**Not produced**
- FCStd (no FreeCAD available).
