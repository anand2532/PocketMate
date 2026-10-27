# PocketMate prototype test plan (battery entries)
## T-BAT-01: Akyga LP655063 NTC characterisation and BQ25895 TS divider
**Why:** aky2210.pdf states only "PCM+NTC 10kR". **No B value, temperature pair or tolerance** (see components.md). TI's RT1/RT2 = 5.21 k / 29.87 kΩ assume a 103AT (B25/85 = 3435) NTC (BQ25895 datasheet §8.2.7.5.1). With B3950 the charge window shifts to about 4–42 °C (estimate).

**Setup:**
- 3 cells, 5–10% SOC, NTC (yellow) to pack − measured with a 4-wire DMM (≤ 10 µA test current to avoid self-heating). PCM connected but no load.
- Reference thermocouple taped beside the NTC location on the cell. Soak in a chamber or bath (water-bath only for sealed bags) at **0 °C, 25 °C, 45 °C**. Hold 30 min after the reference stabilises within ±0.2 °C.

**Record:** R(0), R(25), R(45) per cell, plus the reference temperature.

**Derive:**
- R25 tolerance: |R(25) − 10 kΩ| / 10 kΩ.
- β(0/25) = ln(R0/R25) / (1/273.15 − 1/298.15).
- β(25/45) = ln(R25/R45) / (1/298.15 − 1/318.15).
- Compare with 3435 and 3950.

**Choose TS resistors:**
- Insert the measured R(0) as RTH_COLD and R(45) as RTH_HOT into **TI BQ25895 Eq. 2**, with VT1 = 73.25% and VT5 = 44.75% of REGN (datasheet typ).
- Pick the E96 values nearest the result.
- Verify on hardware by sweeping the chamber: charge must stop at TCO ≈ 45 °C and must not start below about 0 °C (read REG0C TS fault bits).

**Pass:**
- β within ±2% of 3435 → keep 5.21 k / 29.87 k (E96: 5.23 k / 30.1 k, VERIFY window).
- Otherwise use the recomputed values and log them in components.md.

## T-BAT-02: Akyga re-termination check
After replacing the leads per battery-rfq.md §4d (J7 pins 1–5 = VBAT, VBAT, BAT_N, BAT_N, NTC → 24.2 / 26.6 / 29.0 / 31.5 / 34.0 mm, pin mapping confirmed by Layout):
- Measure each lead length (±0.5 mm target).
- Check crimp pull force and continuity.
- Run 3 A for 30 min with a thermocouple at the J7 housing: the rise must stay ≤ 30 °C (the Molex derating basis).
