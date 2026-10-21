# PocketMate v2 — rough steady-state thermal estimate (EST, validate in a chamber)
Model: 125x75x20 body, A_back(Al, anodised e=0.85) 0.0094 m², sides(plastic e=0.9) 0.0080 m², front(glass e=0.9) 0.0094 m². Natural convection h_c = 1.42(ΔT/L)^0.25 (vertical, L=75 mm), radiation linearised from exact σ(Ts⁴−Ta⁴). Temperature uniformity factors: back 1.0, sides 0.8, front 0.6 of the back's ΔT. Spreading from 30x30 pad into 1.5 mm Al ≈ 0.45 K/W (hot spot above the mean back). Hand contact is ignored (worse when gripped). "On table" = back face blocked.

Overall conductance to ambient: **G ≈ 0.21–0.22 W/K held/vertical, ≈ 0.12 W/K lying on the back.** Thermal mass ≈ 110 J/K (Al 31 g, plastic, cell) → τ ≈ 8–9 min.

## Skin rise at 3–5 W (held/vertical, hottest point over pad)
| Device power | ΔT mean back | Hot spot ΔT | Skin @35 °C amb | Skin @45 °C amb |
|---|---|---|---|---|
| 3 W | 12.7 K | ~14 K | ~49 °C ✗ | ~59 °C ✗ |
| 4 W | 16.4 K | ~18 K | ~53 °C ✗ | ~63 °C ✗ |
| 5 W | 19.9 K | ~22 K | ~57 °C ✗ | ~67 °C ✗ |
3–5 W sustained is not compatible with either skin spec; only short bursts.

## Sustained power budget (total device: CM5 + display backlight + charger/regulators)
| Case | Limit | ΔT allowed | Held/vertical | Flat on back |
|---|---|---|---|---|
| 35 °C ambient | skin ≤ 43 °C sustained | 8 K | **≈ 1.6 W** | ≈ 0.9 W |
| 45 °C ambient | skin ≤ 48 °C (amb+3) sustained & peak | 3 K | **≈ 0.6 W** | ≈ 0.35 W |
Note: CM5 idle plus backlight is already on the order of 1.5–2.5 W (VERIFY on hardware). At 45 °C the governor must dim the display, cut CPU to minimum and shed work (cloud offload / pause). The 48 °C cap is held by throttling, not by the cooling design. At 35 °C only light use is sustainable.
Bursts: with τ ≈ 8 min and C ≈ 110 J/K, a 5 W burst on top of the budget adds ≈ 0.04 K/s → ~30 s burst ≈ +1.2 K. Leave headroom below the trigger before running LLM/OCR bursts.

## Throttle triggers (case NTC on Al plate inner face, (-55.3,-10), next to left grip)
The NTC sits ~45 mm from the pad and reads below the hot spot by roughly 0.5 K per watt (EST, calibrate). T_lim = 43 °C if ambient ≤ 40 °C, otherwise ambient + 3 °C, capped at 48 °C. Ambient comes from the case NTC after ≥ 10 min idle, or from the cell NTC when not charging.
| Stage | NTC_case threshold | Action |
|---|---|---|
| 0 Warn / no new bursts | T_lim − 2.5 K (35 °C amb: 40.5 °C; 45 °C amb: 45.5 °C) | block new LLM/OCR bursts, offer cloud offload |
| 1 Soft throttle | T_lim − 1.5 K (41.5 / 46.5 °C) | cpufreq step −300 MHz per 0.5 K, backlight −30 % |
| 2 Hard throttle | T_lim − 0.5 K (42.5 / 47.5 °C) | arm_freq minimum (~1.0–1.2 GHz), GPU min, backlight floor |
| 3 Protect | T_lim + 0 K (43.0 / 48.0 °C), or SoC ≥ 80 °C | suspend compute, sleep the display, notify the user |
Release with 1.5 K hysteresis. SoC firmware throttling (80/85 °C) stays the last resort; it is not expected at these power levels (pad R ≈ 0.4 K/W).
Charging: cell NTC (under the cell) to BQ25895 TS with the JEITA profile. No charge > 45 °C cell, reduced charge 40–45 °C. At 45 °C ambient expect no charging ("too hot to charge").
