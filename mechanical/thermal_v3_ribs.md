# PocketMate v3: heat-sink rib study (EST, same lumped model as thermal_v3.md; validate in a chamber)
Zone: 40 x 40 mm centred on the SoC (22,-13), X 2..42, Y -33..7, ribs run along Y (vertical when held in landscape). The flat v3 file is unchanged.

| Variant | Geometry | Extra wetted area (CAD) | Effective credit | Spreading R |
|---|---|---|---|---|
| flat v3 | 1.5 mm floor + 0.5 mm pedestal under the pad | — | — | 0.30 K/W |
| (a) recessed | local floor thickened to 2.0 mm over 40x40 (inside), 15 grooves 1.0 w × 1.2 d, pitch 2.5, 0.8 mm web; envelope stays 20 mm | +1189 mm² | ~25 % (1 mm slots: little convection, radiation mostly self-viewing) | 0.28 |
| (b) proud | 10 fins 1.2 × 2.5 × 40 mm, pitch 4 (2.8 mm gaps), R0.5 tips; envelope 22.5 mm at the zone | +1886 mm² | ~50 % (narrow gaps limit natural convection) | 0.25 |

Assumptions: held = all faces free (h ≈ 8.7 W/m²K average); table = lying on the back (back blocked; proud fins keep a 2.5 mm air gap, credited at ~30 % of the back's free-air conductance); pocket = fabric-wrapped, G ≈ 0.08 W/K for all variants (fins pressed into fabric give ~no gain), pocket air at ambient. Idle floor 2.4–2.65 W (measured).

## Sustained device power and idle check (skin ≤ 43 °C @ 35 °C ambient, ≤ 48 °C @ 45 °C)
| Variant | Case | 35 °C: budget W | 35 °C: skin @ idle | Idle OK? | 45 °C: budget W | 45 °C: skin @ idle | Idle OK? |
|---|---|---|---|---|---|---|---|
| flat (v3) | held | 1.74 | 46.0–47.2 | NO | 0.62 | 56.5–57.7 | NO |
| flat (v3) | table | 1.02 | 53.9–55.9 | NO | 0.37 | 64.5–66.5 | NO |
| flat (v3) | pocket | 0.62 | 65.7–68.9 | NO | 0.23 | 75.7–78.9 | NO |
| (a) recessed grooves | held | 1.77 | 45.8–47.0 | NO | 0.63 | 56.3–57.5 | NO |
| (a) recessed grooves | table | 1.03 | 53.6–55.5 | NO | 0.38 | 64.1–66.1 | NO |
| (a) recessed grooves | pocket | 0.63 | 65.7–68.9 | NO | 0.23 | 75.7–78.9 | NO |
| (b) proud fins 2.5 mm | held | 1.83 | 45.5–46.6 | NO | 0.66 | 56.0–57.1 | NO |
| (b) proud fins 2.5 mm | table | 1.23 | 50.6–52.2 | NO | 0.45 | 61.1–62.8 | NO |
| (b) proud fins 2.5 mm | pocket | 0.63 | 65.6–68.8 | NO | 0.24 | 75.6–78.8 | NO |

| Case | Ambient | Required G (W/K) | Required area (m²) | × today's 0.027 m² |
|---|---|---|---|---|
| held | 35 °C | 0.37 | 0.042 | 1.6× |
| held | 45 °C | 1.20 | 0.138 | 5.2× |
| table | 35 °C | 0.37 | 0.075 | 2.8× |
| table | 45 °C | 1.20 | 0.244 | 9.1× |
| pocket | 35 °C | 0.37 | 0.123 | 4.6× |
| pocket | 45 °C | 1.20 | 0.402 | 15.0× |
**Result: no variant sustains idle in any case.** The best case, proud fins held at 35 °C, reaches 1.83 W, still 0.6–0.8 W short. Ribs buy +2 % (recessed) / +5 % (proud) held, and +20 % on a table for the proud fins only (air gap). The 40x40 zone is only ~6 % of the body area, and the limit is total surface-to-air conductance, not the SoC hot spot (Rs is already only ~0.3 K/W).

## Touch temperature and guard
- Ribs sit over the SoC, so they are the hottest skin: ≈ mean skin + 0.25–0.3 K/W × P, i.e. at idle ~0.7 K above the rest of the back. With the governor holding NTC-based limits, the ribs reach ≈ 43 °C / 48 °C at the trip points. Calibrate the case-NTC offset to the rib tips (NTC is ~75 mm away).
- Metal contact limits are the same for ribs and flat (43 °C > 8 h, 48 °C > 1 min). The thin fins have less contact area but conduct well, so the finger feels them as hot as the flat metal or hotter.
- **Plastic guard grille: not needed** if the governor caps skin at the limits (it must anyway). A guard over (b) would block most of the small convection gain, so it defeats the purpose. Only fit one if a burst policy lets the zone exceed 48 °C.

## Pocket snagging / handling
- (a) recessed: flush, no snag; the 1 mm slots collect lint and need a deburr and edge break. Acceptable.
- (b) proud: 2.5 mm fins snag fabric and lint, catch keys and coins, rock on a table, and need large radii. Not pocket-friendly. They also add 2.5 mm to the 20 mm thickness at the zone, which conflicts with the "compact" priority.

## Machining cost (EST, CNC 6061 unibody, ~1k qty)
- (a): 15 slots with a Ø1 mm end mill / slitting saw, ~3–5 min extra cycle → ≈ +US$1.5–3 per unit, small tool-wear risk.
- (b): needs stock 2.5 mm thicker over the whole back (all of it machined away except the fins). Extra roughing + finishing ~6–10 min → ≈ +US$3–6 per unit. Alternative: a separately extruded fin insert, bonded or screwed (≈ US$1–2 + assembly), adds a thermal interface.

## Surface area needed to sustain idle (2.65 W), at today's average h for each case

Held at 35 °C needs ≈ 0.042 m² (1.6× today's 0.027 m²), e.g. ~150 × 90 × 25 mm, or fins with real (≥ 6 mm) gaps. Held at 45 °C needs ≈ 0.14 m² (5×). Table/pocket cases need 3–15×. These cannot be met by any handheld passive design.

## Recommendation
Keep the **flat v3** (or (a) if a tactile/visual heat zone is wanted, cost ≈ +$2). Do not adopt (b). Close the gap on power instead: idle must fall to ≤ 1.7 W (35 °C, held), ≤ 1.0 W (table), ≤ 0.6 W (pocket) → screen-off/suspend states with the STM32U0 always-on, CM5 suspend when pocketed (proximity/ALS), dimmed backlight, Wi-Fi power save. Otherwise relax the spec (e.g. 48 °C short-contact rating with time limits).

Files: `pocketmate_al_unibody_v3a_ribs_recessed.step`, `pocketmate_al_unibody_v3b_ribs_proud.step`, `pocketmate_enclosure_v3_ribs.FCStd`, renders `pocketmate_enclosure_v3a_ribs_recessed_rear_iso.png`, `pocketmate_enclosure_v3b_ribs_proud_rear_iso.png`; builder `build_v3_ribs.py`.
Side fix applied to flat v3: right grip inlay shortened to Y -26..-4 (was -26..10) because the U.FL recess under it left no aluminium. v3 STEP/FCStd/renders were regenerated.

---
# v4 thickness sweep (Anand's scope extension)
Method: v3 stretched by dt at Z 3.05. All internals move up dt, the cell gets thicker, the SoC pedestal grows dt, and the 40x40 SoC zone gets 11 recessed fin slots 1.5 w × (1.2+dt) d (credited 20 %: narrow slots). Side area grows with thickness. Spreading R 0.27 / 0.26 / 0.25 K/W. Same h model, idle 2.4–2.65 W.

| Body | Held 35 °C (≤43) | Table 35 °C | Pocket 35 °C | Held 45 °C (≤48) | Table 45 °C | Pocket 45 °C | Idle sustained? |
|---|---|---|---|---|---|---|---|
| v3 20 mm flat | 1.75 W | 1.02 | 0.62 | 0.62 | 0.37 | 0.23 | NO (skin 46.0–47.1 °C held @35) |
| v4_22 | 1.85 W | 1.08 | 0.64 | 0.66 | 0.39 | 0.24 | NO (45.4–46.5 °C) |
| v4_24 | 1.93 W | 1.14 | 0.66 | 0.69 | 0.41 | 0.25 | NO (44.9–46.0 °C) |
| v4_26 | 2.02 W | 1.20 | 0.68 | 0.72 | 0.43 | 0.26 | NO (44.5–45.5 °C) |

**3 W held at 35 °C (≤ 43 °C) needs G ≈ 0.41 W/K. No thickness reaches it.** Each +2 mm adds only ~0.012 W/K (side area plus slots). Extrapolated, it would need ≈ 50–60 mm thick, so no realistic thickness works. 3 W needs ≈ 1.8× today's surface (~0.048 m², e.g. ~160 × 95 × 25 mm with fins at real ≥ 6 mm pitch) or forced air.

## Battery use of the extra thickness (EST 0.47 Wh/cc, 51 × 65.5 mm footprint; Tech Research to source)
| Body | Cell | Capacity (EST) | Cell mass |
|---|---|---|---|
| 20 | Akyga 7.0 × 51 × 65.5 | ~3.0 Ah / 11 Wh | ~51 g |
| 22 | 8.5 × 51 × 65.5 | ~3.6 Ah / 13.3 Wh | ~62 g |
| 24 | 10.5 × 51 × 65.5 | ~4.5 Ah / 16.5 Wh | ~77 g |
| 26 | 12.5 × 51 × 65.5 | ~5.3 Ah / 19.6 Wh | ~92 g |

## Weight estimate (Al 2.7 g/cc from CAD volumes; PC 1.2 g/cc; internals ex-cell ≈ 85 g: display+CTP ~45, CM5 ~11, carrier ~12, camera 4, speaker 3, flex/antenna/screws/pads ~10, all EST)
| Body | Al unibody | Plastic | Cell | Total |
|---|---|---|---|---|
| v3 20 | 24.8 cc → 67 g | ~9 g | 51 g | **~212 g** |
| v4_22 | 28.1 cc → 76 g | ~10 g | 62 g | **~233 g** |
| v4_24 | 31.8 cc → 86 g | ~10 g | 77 g | **~258 g** |
| v4_26 | 35.5 cc → 96 g | ~10 g | 92 g | **~283 g** |
All are inside the 200–300 g target.

## Choice
Thermally the sweep buys only +6 % (22) to +15 % (26), so thickness is not the fix. **Recommended: v4_22** (smallest step, +21 % battery, 233 g, inside the PRD 18–24 mm). Take v4_24 only if battery life outranks compactness. Board outline and keep-outs were issued for v4_22.
