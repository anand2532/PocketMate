# PocketMate power: component values and NVM/register settings (v0.2, 2026-10-21)
All values below are in `kicad/gen/gen.py`; regenerate with `python3 kicad/gen/gen.py`.

## TPS61088 5 V boost (U8). Source: TI SLVSCM8A, §8.3, §9.2.2 (Eq. 1–20)
Design point: VIN 3.2–4.4 V (VSYS), VOUT 5.12 V, IOUT 3.5 A, efficiency (η) 0.88, PFM at light load (MODE left open).
| Part | Value | Calculation |
|---|---|---|
| R_FB top / bottom | 182 k / 56 k 1 % | VOUT = 1.204 × (1 + 182/56) = 5.12 V. 56 k is the datasheet's typical low-side value |
| R_FSW (FSW to SW) | 150 k 1 % | R = 4·(1/f − 89 ns·VOUT/VIN)/23 pF. At VIN 3.6 V, f = 1.0 MHz gives 151.9 k. Constant off-time, so f drifts about ±15 % across VIN |
| Inductor L2 | 1.0 µH Coilcraft XAL5030-102ME | IDC = 5.12·3.5/(3.2·0.88) = 6.36 A. Ripple (Ipp) = 1.20 A at 3.2 V / 1 MHz, so the peak current (ILpeak) is 6.96 A. **Check Isat ≥ 9.4 A and the DCR on the Coilcraft datasheet.** Height 3.1 mm, which fits the 4.9 mm limit but not the plan's ≤2 mm preference |
| R_ILIM | 127 k 1 % | PFM: ILIM = 1 190 000/R = 9.37 A typ, worst case 8.07 A (−1.3 A), which is above 6.96 A |
| C_SS | 47 nF | t_SS = 1.204·47 nF/5 µA = 11.3 ms |
| Compensation R5 / C5 / C8 | 10 k / 2.7 nF / 18 pF | RO = 1.46 Ω, D = 0.375, effective CO about 36 µF (3 × 22 µF 0805 derated at 5 V), RHP zero (fRHPZ) = 91 kHz, so the crossover (fC) is 15 kHz (< fRHPZ/5, < fSW/10). R5 = 2π·VOUT·0.08 Ω·fC·CO/((1−D)·1.204·190 µA/V) = 9.7 k. C5 = RO·CO/(2R5) = 2.6 nF. C8 = 5 mΩ·CO/R5 = 18 pF |
| VCC / BOOT | 2.2 µF / 100 nF | per datasheet |
| CIN / COUT | 22 µF + 100 nF / 3 × 22 µF | |

## Load switch Q2/Q3 (CM5 5 V)
Q2 is a DMP3013SFV (−30 V, 9.5 mΩ, PowerDI3333-8), giving about 33 mV drop at 3.5 A. Gate: 100 k to +5V_BOOST, pulled low by a 2N7002 (Q3) that CM5_5V_EN drives (MCU PB1), with a 100 k pull-down. A 10 nF capacitor from gate to source sets the turn-on slew. The TPS61088 is not true-disconnect when EN is low (VIN leaks through the body diode to VOUT), so this switch is needed to remove CM5 power in the Off state.

## BQ25895 (U5). Source: TI SLUSC88 and the TI schematic checklist v1.1
| Item | Value | Note |
|---|---|---|
| R_ILIM | 130 Ω 1 % | IINMAX = KILIM(max 390)/R = 3.0 A hard ceiling. Firmware sets IINLIM after PD (9 V/2 A means IINLIM 2.0 A) |
| TS divider | RT1 5.23 k 1 % (REGN to TS), RT2 30.1 k 1 % (TS to GND), 10 k B3435 NTC in the pack | see 'TS divider' section below |
| L1 | 1.0 µH Coilcraft XAL4020-102ME (4 × 4 × 2.1 mm): Isat 8.7 A (−30 %), Irms 6.7 A (+20 °C), DCR 14.6 mΩ max | **Verified.** SLUSC88 §9.2.2.1: "1-µH and minimum 20-µF output capacitor recommended" at 1.5 MHz; TI checklist allows 1–2.2 µH. Worst case: ILIM ceiling 3.0 A at 9 V → ~24 W → 6.6 A avg into VSYS/BAT at 3.6 V, ripple 9·0.47·0.53/(1 µH·1.5 MHz) = 1.5 A → peak 7.4 A < 8.7 A. Normal (9 V/2 A PD) peak ≈ 5.2 A |
| VBUS / PMID / SYS / BAT caps | 1 µF / 10 µF / 2 × 22 µF / 10 µF | checklist: PMID ≥ 8.2 µF |
| BTST / REGN | 47 nF / 4.7 µF | |
| /CE, OTG | GND | charging always enabled, OTG off |
| D+/D− | NC | PD is done by the STUSB4500. Note: the **BQ25896 is NOT pin-compatible** (it has PSEL in place of D+/D−) |
| STAT | 2.2 k from REGN to green LED D3 | |
| QON | RB521S30 Schottky from BTN_PWR_N | wakes from ship mode without the MCU |
| Registers set by MCU firmware | **ICHG 2.048 A (REG04 ICHG=0x20, ≈0.57 C for the 3.6 Ah cell)**; drop to 1.024 A (0x10) when the skin NTC > 40 °C or BQ TREG loop engages; ≤1 C (3.6 A) not used for thermals (charger loss ≈0.9 W at 2 A from 9 V, plus SYS load). JEITA: keep BQ defaults (JEITA_ISET 20 % in 0–10 °C). VREG 4.208 V, **ITERM 192 mA (C/19)**, IPRECHG 256 mA, IINLIM after PD contract, BATFET_DIS = 1 for ship mode, watchdog disabled or kicked by MCU | |

## STUSB4500 (U4). Source: ST DS12499 §2.2, UM2650
| Item | Value |
|---|---|
| VBUS_VS_DISCH series R | 1 k (max pin current 50 mA: 20 V gives 20 mA) |
| DISCH series R (system side, VBUS_CHG) | 220 Ω 0603 (9 V gives 41 mA, max 500 mA) |
| VSYS | GND (unused, per datasheet) |
| VREG_1V2 / VREG_2V7 | 1 µF each |
| ADDR0/ADDR1 | GND, so I2C address 0x28 |
| RESET | GND (MCU can re-negotiate over I2C soft reset) |

NVM image (write once with the ST GUI or MCU firmware, per UM2650):
| NVM field | Value |
|---|---|
| SNK_PDO_NUMB | 2 |
| PDO1 | 5 V, 1.5 A (fixed 5 V) |
| PDO2 | 9 V, 2.0 A |
| PDO3 | unused (or 9 V/3 A if a larger cell is used) |
| POWER_ONLY_ABOVE_5V | 0 (also charge from 5 V-only chargers) |
| REQ_SRC_CURRENT | 0 |
| USB_COMM_CAPABLE | 0 |
| SNK_UNCONS_POWER | 0 |
| VBUS_DISCH_TIME_TO_0V / TO_PDO | defaults |
| Over/undervoltage windows | default ±10 % (SHIFT_VBUS_HL/LL defaults) |

## MAX17055 (U6). Source: MAX17055 datasheet rev. 2
Sense resistor R = 10 mΩ 1 % **1206, 0.5 W** (5 A → 0.25 W), low side (BAT− to GND). Current LSB 156.25 µA, range ±5.12 A, capacity LSB 0.5 mAh. **Cell: 1S Li-ion ~3.6 Ah** (charge to 4.2 V).
EZ config, written by MCU firmware after POR (check Status.POR, wait for FSTAT.DNR = 0, then write and set Refresh):
| Register | Value | Meaning |
|---|---|---|
| DesignCap (18h) | **0x1C20** | 3600 mAh / 0.5 mAh = 7200 |
| IChgTerm (1Eh) | **0x04CD** | 192 mA / 156.25 µA = 1229 (= BQ ITERM 192 mA) |
| VEmpty (3Ah) | 0xA561 | VE 3.30 V, VR 3.88 V |
| ModelCfg (DBh) | 0x8000 | Refresh = 1, VChg = 0 (4.2 V), ModelID 0 (LiCoO2) |
| Config (1Dh) | 0x2214 | default 0x2210 plus Aen (ALRT pin enabled) |
| dQAcc (45h) / dPAcc (46h) | **0x00E1 / 0x0563** | EZ init flow (MAX17055 Software Implementation Guide UG6365 §EZ config): dQAcc = DesignCap/32 = 225; dPAcc = dQAcc·44138/DesignCap = 1379 (VChg = 0, i.e. 4.2 V; use 51200 instead of 44138 for >4.275 V cells). Write both, then ModelCfg with Refresh |
| AIN | tied to CSP (unused). THRM NC. The cell NTC goes to BQ TS |

## Peripheral 3V3 buck U12 (v0.3). TI TLV62585DRLR, SOT-563, LCSC C485117
- VIN = VSYS (3.0–4.4 V; 2.5–5.5 V part). 3 A switch, 1.5 MHz, internal comp, 100 % duty mode near empty (3V3_PERIPH ≈ VSYS − I·(56 mΩ + 40 mΩ) when VSYS < 3.4 V).
- FB 100 k / 22.1 k 1 % → VOUT = 0.6·(1 + 100/22.1) = 3.315 V.
- L3 = Murata DFE252012F-1R0M=P2 (LCSC C435392), 2.5 × 2.0 × **1.2 mm**, Isat 4.7 A, Itemp 3.3 A, 40 mΩ. Design load 1.5 A; ripple 3.3·(1−3.3/4.4)/(1 µH·1.5 MHz) = 0.55 A → peak 1.78 A ≪ 4.7 A (also above the part's ~4 A high-side current limit, so it stays unsaturated in short-circuit hiccup).
- CIN 10 µF 0603 + 100 nF; COUT 2 × 22 µF 0805.
- EN = CM5_3V3 via 10 k, 100 k to GND: the rail only comes up after the CM5 PMIC has its 3V3 up and drops with it → no back-powering of CM5 I/O (display/camera I2C and GPIOs) when the CM5 is off.
- **Rail split:** +3V3_PERIPH feeds display J3 pin 22 (and its DSI pin-17 pull-up), camera J4 pin 22, mics via mute switch SW5, VEML7700 and their decoupling. CM5_3V3 now only carries the CM5's own I/O reference: GPIO_VREF (J1-78), I2C/DSI-I2C/CAM-I2C pull-ups, MCU_IRQ pull-up, fan-tach pull-up, CM5 3V3 decoupling, and the U12 EN divider (~30 µA).
- Budget: display ~360 mA + Camera Module 3 ~250 mA + mics/ALS ~5 mA ≈ 0.62 A typ, 1.5 A design.

## Fan header J12 (DNP). JST SH SM04B-SRSS-TB, 1.0 mm
| Pin | Net | Notes |
|---|---|---|
| 1 | +5V_CM5 | switched with the CM5 5 V load switch, so the fan stops with the CM5 (CM5 datasheet §2.11) |
| 2 | GND | |
| 3 | FAN_PWM | CM5 J1 pin 19 Fan_PWM (open-drain output) → direct, as on CM5IO. No MOSFET: the blower must take a 4-wire PWM input (internal pull-up). For a 2/3-wire blower, fit a low-side NMOS in a later rev |
| 4 | FAN_TACH | CM5 J1 pin 16 Fan_Tacho (input, 1.8 k internal pull-up to CM5_3V3, RP1 GPIO29). Extra 10 k to CM5_3V3 placed DNP |
1 µF on +5V_CM5 at the header (DNP).

## BQ25895 TS divider (cell NTC on J7 pin 5). Source: TI SLUSC88 §8.2.7.5.1, Eq. 2
Target window 0–45 °C. Thresholds used: VT1 (cold) ≈ 73.75 % and VT5 (hot) ≈ 44.46 % of REGN. These are back-solved from the stated calculation (5.21 k / 29.87 k for B3435); **check them against the datasheet electrical-characteristics table**.
NTC model: R(T) = 10 k · exp(B·(1/T − 1/298.15 K)).

| Case | RT1 / RT2 | Cold trip | Hot trip |
|---|---|---|---|
| B3435, ideal (Eq. 2) | 5.21 k / 29.87 k | 0.0 °C | 45.0 °C |
| **B3435, fitted E96 values (5.23 k / 30.1 k)** | 5.23 k / 30.1 k | **0.5 °C** | **44.9 °C** |
| B3950 cell with the B3435 values | 5.23 k / 30.1 k | 3.5 °C | 42.2 °C (conservative: narrower window) |
| B3950, ideal | 4.44 k / 19.42 k | 0.0 °C | 45.0 °C |
| **B3950 alternate E96** | **4.42 k / 19.6 k** | **0.5 °C** | **45.2 °C** |
| B3435 cell with the B3950 values | 4.42 k / 19.6 k | −2.8 °C | 48.5 °C (**unsafe**: too wide) |

**Prototype cell (Akyga LP655063): the NTC beta is unconfirmed.** Measure R at 0 °C (ice bath) and at 25/45 °C. Then:
- If it is B3435 (103AT class), keep RT1 = 5.23 k and RT2 = 30.1 k.
- If it is B3950, fit **RT1 = 4.42 k and RT2 = 19.6 k** (1 % E96).

If the beta is unknown, the B3435 values are the safe default: with a B3950 cell they only narrow the window, to 3.5–42.2 °C.
