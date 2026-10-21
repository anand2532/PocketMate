# PocketMate v3 — rough steady-state thermal estimate, Al unibody (EST, validate in a chamber)
Same method as v2: 125x75x20 body. Back 0.0094 m² + sides 0.0080 m² are now **metal** (anodised e≈0.85, uniformity 1.0 / 0.95); front glass+bezel 0.0094 m² (e 0.9, uniformity 0.6). h_c = 1.42(ΔT/L)^0.25, radiation from σ(Ts⁴−Ta⁴). Spreading pad → unibody ≈ 0.3 K/W (was 0.45). Hand contact ignored. Flat = lying on its back (back blocked, ~0.6 W/K·m² conduction to table credited).

Conductance: **held ≈ 0.22–0.23 W/K, flat on back ≈ 0.13 W/K** (v2: 0.21–0.22 / 0.12). Total area is unchanged, so going to full metal adds only ~5–10 %. The real gains are uniformity (no cool plastic sides) and a lower hot spot. Thermal mass ≈ 140 J/K (Al ≈ 67 g) → τ ≈ 10 min.

## Skin rise (held, hottest point)
| Device power | Mean ΔT | Hot spot ΔT | @35 °C amb | @45 °C amb |
|---|---|---|---|---|
| 3 W | 12.2 K | 13.1 K | ~48 °C ✗ | ~58 °C ✗ |
| 4 W | 15.6 K | 16.8 K | ~52 °C ✗ | ~62 °C ✗ |
| 5 W | 19.0 K | 20.5 K | ~56 °C ✗ | ~65 °C ✗ |

## Sustained device power budget (all heat: CM5 + backlight + power stage)
| Case | Limit | Held | Flat on back |
|---|---|---|---|
| 35 °C ambient | ≤ 43 °C (8 K) | **≈ 1.75 W** | **≈ 1.0 W** |
| 45 °C ambient | ≤ 48 °C (3 K) | **≈ 0.6 W** | **≈ 0.35 W** |
Caveat: metal is touched everywhere now. Metal-skin limits are the same numbers (43/48 °C), but metal feels hotter and has no plastic relief except the grip inlays.

## Throttle triggers (case NTC on the Al floor at (-55.3,-10), next to the left grip)
The unibody is more isothermal: the NTC reads ~0.3 K/W below the hot spot (EST, calibrate). T_lim = 43 °C (ambient ≤ 40 °C), else ambient + 3 °C, capped at 48 °C.
| Stage | NTC threshold | @35 °C amb | @45 °C amb | Action |
|---|---|---|---|---|
| Warn | T_lim − 2.0 K | 41.0 | 46.0 | no new LLM/OCR bursts, offer offload |
| Soft | T_lim − 1.2 K | 41.8 | 46.8 | cpufreq −300 MHz per 0.5 K, backlight −30 % |
| Hard | T_lim − 0.5 K | 42.5 | 47.5 | CPU/GPU minimum, backlight floor |
| Protect | T_lim | 43.0 | 48.0 (or SoC ≥ 80 °C) | suspend compute, display off |
Hysteresis 1.5 K. Bursts: 5 W for 30 s ≈ +1.0 K. Charging: cell NTC → BQ25895 TS/JEITA, no charge above 45 °C cell.

## UPDATE: measured idle floor 2.4–2.65 W (CM5 idle + display); same model
| Design | Use | Ambient | Budget (limit) | Skin at 2.4 W | Skin at 2.65 W | Sustains idle? |
|---|---|---|---|---|---|---|
| v2 (Al plate, plastic sides) | held | 35 °C | 1.6 W (43 °C) | 46.5 °C | 47.6 °C | **NO** |
| v2 | held | 45 °C | 0.6 W (48 °C) | 56.0 °C | 57.1 °C | **NO** |
| v2 | flat on back | 35 °C | 0.9 W | 54.2 °C | 56.0 °C | **NO** |
| v2 | flat on back | 45 °C | 0.35 W | 63.4 °C | 65.1 °C | **NO** |
| v3 (Al unibody) | held | 35 °C | 1.75 W (43 °C) | 45.7 °C | 46.7 °C | **NO** |
| v3 | held | 45 °C | 0.6 W (48 °C) | 55.2 °C | 56.2 °C | **NO** |
| v3 | flat on back | 35 °C | 1.0 W | 52.4 °C | 54.0 °C | **NO** |
| v3 | flat on back | 45 °C | 0.37 W | 61.6 °C | 63.1 °C | **NO** |
**Conclusion: neither design can hold even measured idle within the skin spec in any case.** At 25 °C ambient held, v3 idle is ≈ 36–37 °C skin (OK). The spec is only reachable with one or more of:
- Idle cut to ≤ 1.6 W (35 °C) / ≤ 0.6 W (45 °C): display/backlight off or dimmed, CM5 in deep idle or suspend with the STM32U0 as the always-on part, Wi-Fi power save, aggressive DVFS.
- A larger or finned surface (a bigger body: roughly 2× the area for 35 °C held).
- Accepting a short-contact rating (48 °C up to ~10 min, MCPC) with a "screen-off pocket mode" duty cycle.
Governor implication: at 35 °C ambient the stage-3 "protect" trigger (NTC 43.0 °C) will be reached at idle within ~20–30 min (τ ≈ 10 min). The device must then suspend (screen off, CM5 suspend). The triggers above stay valid; they will simply fire at idle.
