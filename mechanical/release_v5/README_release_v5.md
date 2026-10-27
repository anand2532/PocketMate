# PocketMate enclosure – release v5.1 (prototype freeze, updated in place)

Rev **5.1**, Tue 27 Oct 2026, 22:15 IST, with O10 FFC added at 22:33 IST. It is built on v5.0 (21:56 IST), whose files are preserved in `archive/release_v5.0_snapshot_20261027_1629.tar.gz`; the name carries the box clock in UTC, which is 21:59 IST. The source is `../pocketmate_assembly_v4_22e.step`. All earlier files in `mechanical/` are untouched.

Boards were read only, via /tmp copies, and never modified:
- `hardware/kicad/PocketMate.kicad_pcb`, md5 `126f5c6c…`, with J14 reserved. It was exported with kicad-cli to `ref/carrier_kicad_export_126f5c6c.step`.
- `hardware/kicad-lte/kicad-lte.kicad_pcb`, md5 `34c2eb67…`, Layout's 47×50 board, last modified 21:58 IST. Its footprints were dumped to `ref/lte_stub_footprints_34c2eb67.json`.

Frame: the origin is at the body centre, +X right, +Y to the top edge, and Z from the outer back. Units are mm.

**Tooling note.** The FreeCAD MCP and the FreeCAD binary are not available, so there is **no .FCStd file for v5/v5.1**. The geometry is built in CadQuery 2.8 / OpenCascade. To rebuild, run `build_release_v5.py` → `check_release_v5.py` → `export_release_v5.py` → `drawings_release_v5.py`, then `key_gaps_release_v5.py`, `make_interference_md.py` and `lte47_fit_check.py`. The FFC study is `ffc_bow.py` → `ffc_fit_check.py`; `ffc_geom.py` is imported by the builder.

## 0. Changelog
### v5.1 (27 Oct 2026, 22:15 IST): PM decisions
1. **O1 closed: action-button hole.**
   - In v4_22b–v5.0 the right-wall hole (Y 14.6–25.4, Z ≈8.0–19.0) was tangent to the top face Z 19 at Y 20. That left a zero-thickness lintel and a non-manifold edge.
   - The hole top is now flat at **Z 18.45**, giving a **0.55 mm Al lintel** to the top face.
   - The cap is unchanged. Its through-wall portion tops out at Z 18.25 and is 10.3 wide against the 10.8 hole, so the **cap-to-hole clearance is 0.20 mm (≥0.15 required)**, with interference volume 0.000.
   - The cap flange inside the wall keeps its v4 0.05 stop gap to the wall face.
2. **GNSS kept.**
   - The 10.5×13.5 top-left window stays, for a chip or patch antenna of **≤12.5 (Z) × 9.5 (Y) mm** on the EC25 ANT_GNSS port.
   - Envelopes:
     - `Vol_Ant_GNSS_Envelope`, the chip option: X −60.4..−58.8 (1.6 deep), Y 17.5–27, Z 2.5–15.
     - `Vol_Ant_GNSS_PatchOpt_Envelope`, the patch option: X −60.4..−55.6 (4.8 deep), Y 17.5–27, Z 2.5–12.0, kept under the side-key flex riser, which starts at Z 12.
   - The keep-out is now X −58.8..−55.0. The GNSS coax rise is shortened to Y ≤17.45 so it lands on the carrier's −Y edge.
   - See §5 for the parts.
3. **Diversity: none.**
   - Deleted: the bottom-left window (its STL, STEP, drawing sheet and DXF), the diversity FPC and its keep-out, the diversity coax and the diversity u.FL.
   - The bottom wall between the USB-C and the speaker is now **plain 6061**, and the unibody gains 201.6 mm³ where the window plug was.
   - The EC25 runs with RX diversity disabled in firmware.
4. **LTE board width, from the parent's question and Layout's 47 mm board.**
   - The daughterboard's right edge moves from X −8.0 to **X −5.0**, making it 47 wide. The speaker notch, J7 notch and ears are kept.
   - J1 moves +3 mm to mouth X −5.0, with contacts still centred at Y −6.5.
   - The FFC span is shortened, and the foams are extended to X −5.3.
   - The SIM is now the CUI/Same Sky **NSIM-2-C** (14×12.4×1.4, verified), moved to X −17.75..−5.35. That clears the U1 courtyard clash (C4 in v5.0 is closed).
   - See §2a.
5. **O10 closed (Layout decision, 22:15 IST): LTE FFC.** J14 stays where it is. The link is a custom 22P 0.5 mm Type A FFC, **14.5 ±0.3 mm overall (tip to tip)**, bowed upward. It is modelled as `LTE_Flex_22P`, an elastica centreline with 3.0×0.3 stiffened ends seated in J1/J14. `Vol_LTE_FFC_Bow_MaxTol_15p3` is the worst-case long-cable envelope. See §2b.
6. Layout's changes are recorded:
   - SIM 3 mm rework-rule waiver (2.40);
   - main u.FL moved to Y ≥14.65;
   - J3 (diversity) dropped.

   The u.FL move is **not yet modelled** and needs a coax re-route (O12).
7. The interference check (77 parts), key gaps, STEP/STL exports, the 17-sheet PDF plus DXFs, and this README were all regenerated from the same build.

### v5.0 (27 Oct 2026, 21:56 IST)
- The first release: LTE daughterboard shelf, thermal path, cell insulation, RF windows, SIM, bezel bridge, and front M2 screws.

## 1. Deliverables
| What | Path |
|---|---|
| Assembly STEP (77 named bodies, coloured) | `pocketmate_assembly_release_v5.step` |
| Per-part STEP (22 physical parts) | `step_parts/<Part>_release_v5.step` |
| Envelopes and keep-outs (reference only) | `step_parts/envelopes_and_keepouts_release_v5.step` |
| STL, printable/machined (11) | `stl/` – unibody, bezel, action cap, 3 RF windows (Wi-Fi, LTE main, GNSS), 2 grip inlays, camera window, Cu spreader, LTE PCB outline |
| Drawings (17 sheets) | `drawings/pocketmate_drawings_release_v5.pdf` plus one DXF per sheet (`unibody_*`, `bezel_plan`, `window_*`, `flat_*`, `lte_daughterboard_outline`) |
| Interference list (full) | `INTERFERENCE_CHECK_release_v5.md`, `work/check.json`, `work/key_gaps.json` / `key_gaps.txt` |
| STL mesh check | `work/stl_check.json` |
| 47 mm LTE board fit check | `lte47_fit_check.py`, `work/lte47_fit.json` |
| LTE FFC bow / length study (O10) | `ffc_bow.py`, `ffc_geom.py`, `ffc_fit_check.py`, `work/ffc_bow.json`, `work/ffc_fit.json` |
| Carrier reference | `ref/carrier_kicad_export_126f5c6c.step`, `ref/carrier_footprints_126f5c6c.json` |

**STL check (v5.1, trimesh 4).** All 11 STLs are **watertight, winding-consistent, `is_volume` true, a single body, with 0 edges whose face count ≠ 2**. admesh is not installed on the build box, so the trimesh edge-manifold count stands in for it.

| STL | Triangles | Volume mm³ |
|---|---|---|
| Al_Unibody | 41,836 | 27,231.8 |
| Bezel | 23,778 | 6,886.3 |
| ActionCap | 1,044 | 274.3 |
| RFWindow_PC (Wi-Fi) | 540 | 1,056.8 |
| LTE main window | 76 | 1,344.3 |
| GNSS window | 76 | 283.6 |
| GripInlay L / R | 524 / 524 | 486.6 / 155.8 |
| Camera window | 500 | 113.1 |
| Cu spreader | 44 | 554.5 |
| LTE PCB | 60 | 1,734.0 |

The STEP files for the unibody, bezel and cap each pass BRepCheck as a valid single solid.

## 2. What changed vs v4_22e (as of v5.1)
1. **LTE daughterboard and shelf.** The 0.8 mm 4-layer board sits at Z 11.4–12.2 over the cell. The outline is **X −52..−5 (47 mm), Y −32..17**, with:
   - a speaker notch, X −52..−34.4 for Y < −23.4;
   - a J7-housing corner notch, X > −9.4 for Y > 15.5;
   - two ears down to Y −35: E1 at X −27..−22.5 and E2 at X −13..−10.

   The DXF is `drawings/lte_daughterboard_outline_release_v5.dxf`.
2. **Supports.** **The board is its own shelf.** It is held by:
   - two Al ledges under the ears (top Z 11.40);
   - two PC clamp posts on the bezel above the ears (Z 12.25–15.85, with 0.2 foam tape);
   - two PC fingers on the top edge (X −41..−38 and −32..−29, Z 12.25–13.25);
   - foam on the cell.

   There are no screws over the cell.
3. **U1 (EC25/EC200U) is rotated 90°, centred at (−35.8, −5.5).** Its height keep-out is X −51.3..−20.3, Y −22.5..11.5, Z 12.2–15.5, with the shield top at 15.5.
4. **Connector, u.FL and SIM.**
   - **J1** is an FH12-22S rotated 90°, **mouth +X at the X −5.0 edge**, with contacts centred at Y −6.5, aligned with carrier **J14**.
   - **4.05 mm is the clearance from the DB edge / J1 courtyard (X −5.0) to the J14 courtyard (X −0.95). It is not the FFC span.** The FFC is 14.5 mm overall (§2b).
   - The u.FLs are Main (−51.6..−49.4, 12.4..14.6) and GNSS (−47..−44.8, 14.4..16.6). There is no diversity u.FL.
   - **SIM:** an NSIM-2-C at X −17.75..−5.35, Y −31.6..−17.6.
5. **Thermal path.** Shield → 0.5 gap pad → 0.5 Cu C1100 spreader (Ni plated, Kapton on the display side; plate at Z 15.9–16.4, joggle, tab at Z 15.2–15.7) → 0.3 pad → Al thermal post (X −34.4..−28.4, top Z 14.9).
6. **Cell insulation.** A 0.1 PET/PI liner sits on the cell: at Z 10.8 for production, 9.3 for the Akyga cell (with a lead relief). Closed-cell foam fills the gap to the board, 0.5 or 2.0 mm, now out to X −5.3. The daughterboard never touches the cell.
7. **RF windows**, plastic and bonded:
   - LTE main, left end wall: 42×16 (Y −28..14, Z 2..18);
   - GNSS, top-left: 10.5×13.5 (Y 17..27.5, Z 2..15.5), with a 3 mm Al web between them.

   **There is no diversity window as of v5.1.** Each window has an antenna envelope, a keep-out and a modelled Ø1.13 coax route.
8. **Wi-Fi pigtail re-routed** below the CM5 (Z 1.9–3.1).
9. **Bezel.** It is bridged into one solid; v4_22e was two bodies. Front-entry M2 countersunk screws (Ø2.4 + Ø4.1 csk) go into Ø2.1×7 holes for M2 helical inserts.
10. **Action-button hole** (v5.1): the top is flattened to Z 18.45, leaving a 0.55 lintel; the cap clears it by 0.20.

## 2a. Layout's 47 mm LTE board vs the shelf/window (answer for Layout/PM)
Layout's `hardware/kicad-lte` (md5 34c2eb67, 21:58 IST) is 47×50 at X −52..−5, Y −32..18, R2 corners, with U1 at rot 0 (−33.75, −12) and J5 (SIM) at the top-left. The v5.0 envelope was X −52..−8. `lte47_fit_check.py` measured:
- **Width: it fits.** The extra 3 mm strip (X −8..−5, Y −32..17) collides with nothing except the **J7 cell-connector housing in the top-right corner** (Molex 205341, X > −8.84, Y > 16.13): 3.4 mm³ for bare PCB, 4.3 mm³ for the X −9.4..−5 / Y 15.5..18 corner.
- Clearances from that strip:

| To | Gap (mm) |
|---|---|
| Carrier J14 courtyard | 4.05 |
| J14 body | 4.59 |
| Production / Akyga leads | 1.13 |
| Al unibody | 2.56 |
| Bezel | 2.57 |
| Production cell, below | 0.6 |
| Cell pocket, below | 0.1 (as v5.0) |

- **Decision: widen the shelf to X −5 (adopted in v5.1).** No board shift and no trim in X. The only condition is to **keep the J7 notch (X −9.4..−5, Y 15.5..17)**: the board is 0.56 from the J7 housing.
- **Y top: keep 17, not 18.** The Y 17–18 strip has no hard clash, but it leaves only **0.1 to the production-cell leads** (1.10 at Y 17) and 0.05 to the bezel. **The board is therefore 47×49.**
- **Not width-related, but must change in Layout's file:**
  - Layout's rectangle has no speaker notch. PCB ↔ speaker is **24 mm³**, and U1 at rot 0 ↔ speaker is **88.5 mm³**. Rotate U1 90° to centre (−35.8, −5.5) and cut the X < −34.4 / Y < −23.4 notch.
  - The ears are missing: E1 at X −27..−22.5 and E2 at X −13..−10 to Y −35. They sit on the Al ledges.
  - J5 at the top-left clashes:

| Against | Overlap mm³ |
|---|---|
| Bezel finger | 6.7 |
| GNSS coax | 2.2 |
| Main coax | 0.65 |

    Move it to X −17.75..−5.35, Y −31.6..−17.6 as modelled. That is 2.40 from the U1 pad toes, against Layout's 3 mm rework rule: a 0.6 waiver, compared with J5's existing 0.06.
  - Q6 and TP2 sit under the finger (Q6 1.45 mm³). Keep Y 16..17 under the fingers free of parts above 0.05 mm, i.e. bare copper only.
  - C22, C23 and C24 hit the J7 housing (0.3–1.1 mm³). They go away with the J7 notch.
  - U4 and the J1 area overlap the FFC path: Layout's J1 sits at X −13 and Y −10. Use J1 mouth X −5.0 with contacts at Y −6.5; Layout's own open item says "shift J1 +3 mm".
  - The u.FLs: Layout's J2/J3/J4 sit at X −26..−13, Y 10–14. The enclosure coax routes need **MAIN at X −51.6..−49.4, Y 12.4..14.6 and GNSS at X −47..−44.8, Y 14.4..16.6**. Drop J3 (diversity). The MAIN u.FL is 0.75 from the U1 pad toes, inside the 3 mm rework rule, so Layout must waive it or move it to Y ≥14.65 and re-route Coax_Main.

## 2b. LTE FFC length: authoritative breakdown (O10, v5.1)
Datum: J1 (FH12-22S-0.5SH, rot 90, mouth +X, courtyard edge X −5.0, contacts centred Y −6.5) on the daughterboard (Z 11.4–12.2), facing carrier J14 (courtyard X −0.95..7.04, mouth −X, same Y).

J14 geometry is taken from the KiCad 3D model in the read-only carrier export:
- FFC slot Z 11.725–12.05;
- FFC stop at X 2.55;
- housing front face X 0.60;
- actuator lip X −0.40.

J1 is the same part mirrored (x′ = −5.95 − x) and raised by 0.75.

| Segment | Length mm |
|---|---|
| J1 insertion: FFC tip at stop X −8.50 → housing face X −6.55 (**insertion depth 1.95**) | 1.95 |
| J1 under the actuator: face −6.55 → actuator lip −5.55 (FFC still flat, clamped) | 1.00 |
| Free span lip to lip: X −5.55 → −0.40 = 5.15 in X, with **Z drop 0.75** (FFC centre Z 12.64 at J1 = DB top 12.2 + 0.44 → Z 11.89 at J14 = carrier top 11.45 + 0.44). Straight chord √(5.15² + 0.75²) | 5.20 |
| J14 under the actuator: lip −0.40 → face 0.60 | 1.00 |
| J14 insertion: face 0.60 → stop 2.55 (**insertion depth 1.95**) | 1.95 |
| **Taut geometric length, tip to tip** | **11.10** |
| **Bend allowance (upward bow)** | **+3.40** |
| **Order length (overall, tip to tip)** | **14.5 ±0.3** |

The DB edge to J14 courtyard distance of 4.05 mm is only a clearance. The housing faces are 7.15 apart, and the actuator lips 5.15.

**Bow** (clamped–clamped planar elastica, `ffc_bow.py`; 0.1 mm film, 0.3 mm stiffened ends 3.0 long):

| Overall L | Crest Z (outer) | Bow above J1 / J14 slot centre | Display gap (16.8) | Min bend radius (R/t) |
|---|---|---|---|---|
| 14.0 | 15.03 | 2.34 / 3.09 | 1.78 | 1.00 (10.0) |
| 14.2 | 15.13 | 2.44 / 3.19 | 1.67 | 1.00 (10.0) |
| **14.5** | **15.29** | **2.60 / 3.35** | **1.51** | **1.00 (10.0)** |
| 14.8 | 15.45 | 2.76 / 3.51 | 1.36 | 1.00 (10.0) |
| 15.0 | 15.55 | 2.86 / 3.61 | 1.25 | 1.01 (10.1) |
| 15.3 | 15.70 | 3.01 / 3.76 | 1.10 | 1.02 (10.1) |

- The bow stays between the actuator lips in X (−5.55..−0.40) and never drops below the slot height.
- The bend radius is set by the 5.15 mm lip-to-lip span, not by the length. It is ≈1.0 mm (≈10×t) for any L from 14 to 15.3. Only shorter cables bend more gently (12.5 → R 1.10), but they leave less slack.
- **14.5 is recommended** because:
  - its slack (3.4) is more than one insertion depth (1.95), so the second end can be inserted after the first is locked;
  - it keeps ≥1.36 to the display over ±0.3.
- 15.0 also fits (display gap 1.25 nominal, 1.10 at +0.3).

**Free space along the route** (slab X −5.55..−0.40, Z 11.7–17):
- In Z, from the cell/foam (top 11.4 at X ≤ −5.3; liner 10.9 and cell 10.8 to X −2.75) up to the display back at Z 16.8 is open. There is no bezel, shield or spreader overhead: the bezel is 20.2 away, the shield 11.8, the spreader 12.6.
- In Y, the FFC is Y −12.25..−0.75. The nearest neighbours in the slab are the SIM corner (Y −17.6, at X < −5.35), the NTC rise (Y −32), and the J7 housing (Y +16.13).
- Laterally the FFC is guided by the FH12 actuator arms, 0.06 per side.

**Current derating** (pinout from the read-only netlists `hardware/kicad/PocketMate.net` and `hardware/kicad-lte/kicad-lte.net`):

| | J14 pins | J1 pads |
|---|---|---|
| LTE_VBAT (6 pins) | 1–6 | 17–22 |
| GND (6 pins) | 7, 8, 9, 12, 14, 22 | 16, 15, 14, 11, 9, 1 |
| LTE_USB_VBUS (sense only) | 13 | 10 |

- **Hirose FH12 rating:** 0.5 A DC per contact, or **70 % (0.35 A) when current flows through all contacts** (Hirose FH12 catalogue, checked).
- **EC25 peak:** VBAT_RF up to 1.8 A in a burst and VBAT_BB up to 0.8 A. The supply must provide **≥2.0 A** (Quectel EC25 Hardware Design, checked).
- **Supply margin:**
  - At the 70 % derating: 6 × 0.35 = **2.1 A vs 2.0 A peak, +5 % (0.1 A)**.
  - At the plain 0.5 A rating: 3.0 A, +50 %.
  - The GND return has the same count and margin.
- The peak is a short burst. Taking the GSM 1/8 slot as an example, 2.0 A peak is ≈0.71 A RMS, or ≈0.12 A per pin, so the contacts run thermally well inside their rating.
- **The short cable helps.** Assuming a typical 0.3×0.035 mm conductor (not verified for the chosen vendor), each conductor is ≈24 mΩ at 14.5 mm, versus ≈66 mΩ at 40 mm. Six in parallel gives ≈4 mΩ each way.
- **Worst-case drop at 2 A** ≈ 0.08 V. That combines 2×(4 mΩ cable) with 4 contact rows at the Hirose maximum of 50 mΩ per contact over 6 in parallel.
- **J14 does not need to move.**
- **Watch:** F1 is 4 A, so it does not protect the FFC/contacts between 2.1 and 4 A. Confirm the custom FFC conductor rating with the vendor (≥0.35 A per conductor).

## 3. Key clearances (B-rep, v5.1)
| Pair | Gap |
|---|---|
| Shield top 15.5 → display back 16.8 | **1.30** |
| Cu spreader → display back | 0.40 (Kapton 0.05 on the spreader) |
| Spreader → bezel lips | 0.10 |
| Shield → bezel left lip | 0.30 |
| Daughterboard → cell pocket / production cell | 0.10 / 0.60 |
| Daughterboard → production / Akyga leads | 1.10 / 1.30 |
| Daughterboard → J7 housing | 0.56 |
| Daughterboard → speaker | 0.60 |
| Daughterboard → bezel | 0.05 (clamp-post nominal; foam tape preload) |
| Daughterboard → J14 body / courtyard | 4.59 / 4.05 |
| J1 courtyard → J14 courtyard (clearance, **not** the FFC span) | 4.05 |
| FFC bow (14.5) → display back / bezel / shield / Cu spreader | **1.51** / 20.2 / 11.8 / 12.6 |
| FFC bow (15.3 worst) → display back | 1.10 |
| FFC → production cell / Akyga cell / foam / liner / battery pocket | 1.69 / 3.19 / 1.09 / 1.59 / 1.19 |
| FFC film → FH12 actuator side arms (lateral guide) | 0.06 |
| SIM → U1 courtyard / pad toes | 1.90 / 2.40 |
| SIM → shield keep-out / J1 / bezel clamp post | 2.55 / 2.53 / 1.00 |
| Shield → speaker | 1.50 |
| Action cap → hole (incl. new lintel) | **0.20** |
| Action cap flange → wall inner face | 0.05 (v4 stop) |
| Coax GNSS → side-key flex riser / main u.FL | 0.15 / 0.10 (Kapton) |
| GNSS patch-option envelope → coax GNSS / side-key flex / Al | 0.05 / 1.40 / 0.04 |
| GNSS keep-out → ALS (−58, 20) / side-key flex | 1.47 / 0.80 |
| GNSS window → ALS | 1.96 |
| Main keep-out → ALS / flex / NTC | 2.60 / 2.0 / 0.30 |
| Main FPC → cell | 6.45 |
| Main / GNSS antenna → battery leads | 35.5 / 31.4 |
| LTE main FPC → Wi-Fi antenna / window | 119.8 / 120.7 |
| Wi-Fi pigtail → unibody / CM5 / carrier | 0.57 / 1.90 / 4.49 |

## 4. Interference result (v5.1: 77 parts × 144 carrier solids)
There are **zero enclosure clashes**. Fixed along the way in v5.0:
- SIM ↔ shield;
- spreader ↔ shield;
- Akyga leads ↔ liner;
- floor fillet ↔ main keep-out;
- Wi-Fi pigtail ↔ CM5, carrier and floor;
- GNSS coax ↔ u.FL and flex;
- post and ledges floating.

Fixed in v5.1:
- the action-hole lintel;
- SIM ↔ U1 courtyard (formerly C4), by moving the SIM.

The GNSS chip and patch envelopes overlap each other; they are alternatives and are classed `other-variant`.

Remaining items are at board level, not in the enclosure:
| # | Pair | Overlap | Fix |
|---|---|---|---|
| C1 | Carrier **J8** THT pins ↔ CM5 envelope | 0.71 protrusion (Z 9.23 vs 9.94), 0.53 mm³ | Trim J8 leads to ≤0.3 after soldering, or use an SMD header |
| C2 | Vol_J4 (FH12 cable/actuator envelope) ↔ **Q2**, **C6** | 0.26 / 0.23 mm³ (0.1 / 0.5 in Y) | Layout: Q2/C6 ≥0.6 −Y, or confirm the DSI FFC clears them; the real J4 body is 1.85 / 1.31 away |
| C3 | Vol_J12 (DNP fan header) ↔ **R3** | 0.02 mm³ (0.07) | Nudge R3 −Y 0.2, or accept (DNP) |
| L1–L6 | Layout 47×50 file as drawn | See §2a | Notch, U1 rotation, ears, J5/J1/u.FL moves, J7 notch |

SIM service needs the bezel and display removed; the lid swing intersects the display.

## 5. RF decisions (v5.1)
- **LTE main:** a 42×16 window in the left end wall for a 40×15×0.2 FPC (**Abracon AANI-FB-0173** class, datasheet checked). The keep-out is 4.8 deep. The cell is 6.45 away, so plan a π-match tuning pass.
- **GNSS (kept):** a 10.5 (Y) × 13.5 (Z) window at the top-left of the left wall, for an antenna of **≤12.5 (Z) × 9.5 (Y)** on EC25 ANT_GNSS (pad 47), with the u.FL at (−47..−44.8, 14.4..16.6).
  - **Primary: Johanson 1575AT43A0040001E** (legacy 1575AT43A0040), an LTCC chip antenna for GPS/Galileo/BeiDou/GLONASS, 1561–1602 MHz, **7.0×2.0×0.8 mm**, linear polarisation, 0.5 dBi peak and 50 % average efficiency on the eval board, active status (Johanson datasheet and product page checked). Mount it on a 9.5×12.5×0.8 FR4/FPC carrier: GND plane, 50 Ω GCPW, a π-match as Johanson recommends, and a u.FL pigtail. It fills `Vol_Ant_GNSS_Envelope`, 1.6 deep.
  - **Alternative: Abracon APAKN0904-S1575-T**, a passive ceramic patch, **9.0×9.0×4 mm** (height from Abracon's parametric page). It is RHCP, 1575.42 MHz, 0.5 dBi peak on a 70×70 ground, and active status (Abracon datasheet checked). On a 9.5×9.5×0.8 carrier it is 4.8 deep, which exactly fills `Vol_Ant_GNSS_PatchOpt_Envelope` (4.8 deep, Z ≤12), so a carrier thicker than 0.8 does not fit.
  - **Caveat, honest:** both parts are ground-plane dependent. A carrier of ≤12.5×9.5 is far smaller than their reference grounds (Johanson eval board 40×20; Abracon 70×70), and the antenna faces −X, edge-on, rather than up. Expect several dB below datasheet and plan a tuning pass, or tie the carrier ground to the Al frame.
  - The EC25 GNSS port is passive by default. Layout's DNP bias tee (U4/L1) is only for an active antenna; leave it unpopulated for these passive parts.
  - Rejected: the smallest Taoglas GNSS FPC found in the v5.0 research is 38×37.
- **Diversity: none (PM, v5.1).** The window, FPC, coax and u.FL are removed and the bottom wall is plain Al. Disable RX diversity in firmware; check the exact command in the Quectel EC25 AT manual. Layout should drop J3 and its match, or fit them DNP.
- The Wi-Fi window (right end) is unchanged and about 120 mm from LTE main.
- **Window material:** SLA clear or tough resin, or machined PC. **No metal-, carbon- or graphite-filled resins**, and no paint or plating. Anodize first, then bond.

## 6. Nano-SIM decision
**A hinged-lid nano-SIM on the daughterboard: CUI/Same Sky NSIM-2-C.** It is 6 contacts, hinged, with card detect (normally open), SMT, **1.4 mm above the board, 14×12.4** (Same Sky product page checked). It is the part Layout already chose, and it sits at X −17.75..−5.35, Y −31.6..−17.6.

To reach it, remove the 4× M2 bezel screws and lift the bezel and display; the lid swings about 12 mm. Keep the MFF2 eSIM (U6) DNP as an option.

A wall slot or tray was rejected:
- the left wall is antenna windows;
- the bottom wall holds the speaker, the post and the USB-C;
- a metal holder at a window detunes the antenna;
- a push-push holder needs a recess and a sweep that hit the shield or carrier.

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
| 1 | **Custom** 22P 0.5 mm FFC, Type A (same-side contacts, reversed numbering, J14 pin k = J1 pad 23−k). **14.5 ±0.3 mm overall**, 11.5 wide, 0.3 ±0.05 thick at the contact ends (Hirose FH12 mating spec), stiffener **3.0 mm** each end, max | J1 (LTE) ↔ J14 (carrier). Breakdown in §2b. Stock 30–50 mm cables are for the bench only and do not fit inside the enclosure. |
| 2 | U.FL Ø1.13 coax | Main and GNSS (no diversity in v5.1). Integral to the antenna FPC or carrier. |
| 1 | LTE main FPC 40×15 (AANI-FB-0173 class) | |
| 1 | GNSS: Johanson 1575AT43A0040001E chip on a 9.5×12.5 carrier, **or** Abracon APAKN0904-S1575-T 9×9 patch | See §5 |
| 1 | Nano-SIM, hinged: CUI/Same Sky NSIM-2-C | Optional MFF2 eSIM (DNP) |
| — | Two-part epoxy, Kapton tape | Window bonding, coax and flex dressing |
### 7.5 Assembly order
1. Unibody: deburr, anodize, unmask. Install the 4 helical inserts.
2. Bond the 3 RF windows (Wi-Fi, LTE main, GNSS) with epoxy and cure. Stick the antenna FPCs to the window inner faces: Wi-Fi and LTE main. Bond the GNSS carrier inside the top-left window. The bottom wall has no window.
3. CM5 thermal pad, then CM5 + carrier onto the standoffs (4× M2.5). Route the Wi-Fi pigtail under the CM5 to its antenna.
4. Side-key flex and keys, action cap, cell NTC pad, then the cell into its pocket. Leads to J7.
5. **PET liner on the cell top, then foam** (0.5 mm production / 2.0 mm Akyga).
6. Daughterboard: plug the FFC into J1 and lock it, then set the ears onto the ledges. Slide the free end 1.95 mm into carrier J14; the 3.4 mm bow slack allows this. Lock J14 and check that the bow stands up (crest ≈ Z 15.3) and is not folded down onto the cell.
7. Mate the U.FLs (main → left wall, GNSS → top-left). Dress the coax with Kapton, keeping the GNSS coax under the flex riser.
8. Insert the nano-SIM and close the lid.
9. Shield pad, then the Cu spreader (tab onto the 0.3 pad on the Al post).
10. Connect the display FPC to J4 and seat the display in the bezel. Lower the bezel, so the clamp posts and fingers land on the daughterboard, and fit 4× M2 countersunk screws.
11. Power-on test, then the RF check (RSSI/RSRP on main) and the thermal soak (AT+QTEMP).

**SIM service:** remove the 4× M2 screws, lift the bezel + display (DSI FFC slack is needed; O8), and open the SIM lid, which swings 12 mm.

## 8. Thermal
Shield → 0.5 pad → Cu spreader → 0.3 pad → Al post into the bottom wall gives an estimated ~11–14 K/W junction-to-case path. That is fine for an average of ~1 W. EC25 uplink bursts reach about 2.9 W, so sustained uplink must be duty-limited: throttle on AT+QTEMP.

## 9. Open items
**Release v5.1**
- **O1 – CLOSED in v5.1.** The action-hole lintel is now 0.55 and the cap clears it by 0.20. All 11 STLs are watertight and manifold.
- **O2 – Layout's `hardware/kicad-lte` (47×50, md5 34c2eb67)** matches the v5.1 **width** (X −52..−5), but needs these changes (§2a):
  - add the speaker notch and ears;
  - add the J7 notch;
  - set the top to Y 17;
  - rotate U1 90° to (−35.8, −5.5);
  - move J5 to X −17.75..−5.35, Y −31.6..−17.6;
  - move J1 to mouth X −5.0, Y −6.5;
  - move the u.FL Main/GNSS to the top-left positions;
  - drop J3 (diversity);
  - keep Y 16–17 under the fingers bare.

  Import `drawings/lte_daughterboard_outline_release_v5.dxf`.
- **O3** – Carrier J8 THT leads (C1); J4 vs Q2/C6 (C2); J12 vs R3 (C3).
- **O4** – GNSS: get samples of 1575AT43A0040001E and APAKN0904-S1575-T. The patch height of 4 mm is confirmed; the carrier must be ≤0.8 thick. Tune on the small carrier; expect reduced gain. Leave the bias tee DNP for passive antennas.
- **O5** – Main antenna tuning near the cell and the Al wall. Order AANI-FB-0173 samples.
- **O6 – resolved by Layout (22:15 IST).** The SIM (NSIM-2-C, 2.40 from the U1 pad toes) takes a 3 mm-rule **waiver**. The main u.FL **moves to Y ≥14.65**. **J3 (diversity) is dropped.**
- **O7** – LTE_VBAT: 6 J14 pins, derated to 2.1 A, with a 4 A fuse. EC25 TX peaks reach about 2 A, so keep the bulk caps (C4/C5) on the LTE board and check the VSYS droop.
- **O8** – DSI FFC slack is needed to lift the bezel + display for SIM service.
- **O9** – Screw lengths are to be confirmed on the first build.
- **O10 – CLOSED (22:15 IST).** J14 is unmoved. The FFC is a custom 22P 0.5 mm Type A, **14.5 ±0.3 mm** overall, with 3.0 mm stiffeners (§2b).
  - Bend radius is ≈1.0 mm (10×t) at every length from 14.0 to 15.3.
  - Display clearance is 1.36–1.67 over the tolerance band.
  - `research/proto-bom-india.md` line 73 still says "free span 4.05 mm". That is the courtyard clearance, so the line should read 14.5 mm overall. The file was not edited here.
- **O11** – Turn off RX diversity in the EC25 firmware, using the exact command from the AT manual.
- **O12 (new)** – Moving the main u.FL to Y ≥14.65 (Layout) puts it under the modelled `Coax_GNSS` run (Y 14.7–15.85, Z 13.3–14.45). Box overlap is about 2.5 mm³ for a u.FL at X −51.6..−49.4, Y 14.65..16.85. `Coax_Main` also has to be re-routed. This is **not modelled in v5.1**: v5.1 still has the main u.FL at Y 12.4–14.6. Next rev: give Layout's final u.FL coordinates, then re-route both coax runs (e.g. GNSS coax over the main u.FL at Z ≥14.4, under the side-key flex riser).
- **O13** – LTE_VBAT current through the FFC is at the edge of its rating (§2b). The burst RMS is fine, but do not add more LTE load to these 6 pins.

**Carried forward**
- DSI Z-fold length;
- side switches 0.43 from the wall;
- Molex 205338/205341 insertion depth;
- JS202011 datasheet ambiguities;
- SW5 cap;
- J12 height limit 4.26;
- stale 504050 entry in the placement plan.

**Not produced**
- FCStd (no FreeCAD available).
