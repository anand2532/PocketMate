# PocketMate v4_22c keep-outs: Layout final positions (2026-10-21 IST)
This is a delta on keepouts_v4_22b.md; everything not listed here is unchanged. Builder: build_v4_22c.py. The v4_22b files are kept as they are.

| Item | v4_22c | Check |
|---|---|---|
| Carrier top edge | Y 34.5 | 0.5 to the unibody at the tightest point (corner) |
| J7 205338-0005 | (3.76,23.7), X -0.95..8.39, Y 15.59..31.82 | Mute slider: **0.08 (yes, marginal)**. J3 1.32, J11 3.51, pocket 1.57. Inside the carrier edge by 0.05 |
| J7 mated housing | X -8.88..0.22, Y 16.43..30.98, Z 11.60..14.14 | Pocket top 0.30, top wall 4.52, slider 0.96 |
| Battery leads | Pins at Y 27.7..19.7; same exit as v4_22b (X -20.2..-26.6, Y 28.5 production / 32.0 prototype) | **Yes.** Bezel rib 0.97 (production), wall 0.55 (prototype), J7 7.9. New lengths: production 22.1/24.5/26.9/29.4/31.8 mm, prototype 24.2/26.6/29.0/31.5/34.0 mm |
| J11 FH12-16S | (19,29.4), Y 26.36..34.34 | Wall 1.16. Tail bend into the mouth needs R 0.72 + t 0.12 = 0.84; room is 0.99. **Yes, 0.15 margin.** J3 2.31, camera 1.91 |
| J4 FH12-22 | (36,4.9), Y 0.95..8.85 | Camera keep-out 2.15. Camera FPC U-fold now has 1.55 ≥ 0.9 needed. **Yes.** J1 1.6 |
| J12 SM04B-SRSS-TB (DNP) | Placeholder X 24.65..34.55, Y -33.1..-26.5, Z ≤ 14.5 | Bezel lip 1.3 (limit 4.26). J6 6.68, J2 1.6. **Yes** |

## DSI display tail (drop zone Y 24.05..26.3)
- **Fold at the glass edge** (180°, Y 33.9..34.74):
  - It needs R ≥ 0.72 (0.12 PI, 6t), so the run sits at **Z ≈ 15.4–15.5** and not directly under the panel.
  - It is in the bezel notch (X 9.4..27.2, Y 32.2..35.3, Z 15..17.6) with 0.56 to spare in Y, and 0.59 to the side-key flex at the wall (Y 35.33).
- **Over J11:** tail bottom Z 15.4 vs J11 body top Z 13.54 (2.0 body) gives **1.86 clear**, or 1.36 if the actuator or tail adds 0.5. **Yes.** The display-side limit is 16.8. The keep-out box sits 0.06 from the J11 courtyard in Y, which is fine because they are at different Z.
- **Drop into J3:** an S-bend with 2.25 mm of Y and about 3.05 mm of Z. It needs R1 + R2 + t = 1.56 for a 0.12 mm tail. **Yes, for a tail ≤ 0.15 mm thick.** A 0.2 mm tail (R ≥ 1.2) needs 2.6 mm and **fails**. A 0.5 mm stiffened section cannot bend here at all, so the stiffener must stay inside J3 (Y < 24.05).
- **Free length** (glass edge to J3 mouth): fold 2.45 + run 7.6 + S-drop 3.95 ≈ **14.0 mm < 15. No.**
  - Fix (panel/FPC spec, no board change): order the tail with a **≥ 2.5 mm flat service Z-fold** on the run. That is 3 layers, 0.36 mm, at Z 15.0..15.5, still 1.46 above J11, for a total of **≥ 16.5 mm**.
  - Layout alternative: extend the drop zone to Y 27.3. That needs J11 moved +Y, which is impossible because of the wall bend, so the Z-fold is the route.
