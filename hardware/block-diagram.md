# PocketMate CM5 carrier: block diagram, power tree and power states (v0.1, 2026-10-21)
Schematic: `hardware/kicad/PocketMate.kicad_pro` (regenerate with `python3 hardware/kicad/gen/gen.py`).

## Block diagram
```mermaid
flowchart LR
  USBC[USB-C J6<br/>USBLC6 x2 + SMF15A TVS] -- CC1/CC2 --> PD[STUSB4500<br/>PD sink 9V]
  USBC -- D+/D- --> CM5
  PD -- VBUS_EN_SNK --> Q1[PMOS sink switch]
  USBC -- VBUS_C --> Q1 -- VBUS_CHG --> CHG[BQ25895<br/>charger + power path]
  CHG -- VSYS --> BOOST[TPS61088<br/>5.1V boost] --> LSW[PMOS load switch Q2/Q3] -- +5V_CM5 --> CM5[CM5 4GB<br/>2x Amphenol 10164227]
  BAT[1S LiPo J7] -- VBAT --> CHG
  BAT -- VBAT --> LDO[TPS7A02 3V3 AON<br/>25nA Iq] --> MCU[STM32U031K8<br/>always-on supervisor]
  BAT -. BAT_N / 10mOhm .-> GAUGE[MAX17055]
  MCU == PMIC I2C ==> CHG & GAUGE & PD
  MCU -- UART0 + MCU_IRQ_N --> CM5
  MCU -- PWR_Button / PMIC_Enable (2N7002) --> CM5
  MCU -- BOOST_EN / CM5_5V_EN --> BOOST & LSW
  BTN[Power / Action / Vol+ / Vol-] --> MCU
  BTN -- Power via Schottky D4 --> CHG
  CM5 -- MIPI1 2-lane + ID_SC/SD --> DSI[Waveshare 4.3in DSI J3]
  CM5 -- MIPI0 2-lane + SCL0/SDA0 --> CSI[Camera Module 3 IMX708 J4]
  CM5 -- I2S BCLK/LRCLK --> MICS[2x SPH0645LM4H L/R]
  MICS -- MIC_SD --> MUTE[DPDT mic-mute SW1<br/>pole1 power, pole2 data<br/>+ red LED]
  MUTE -- I2S_DIN GPIO20 --> CM5
  MUTE -- MIC_MUTE_STATUS --> CM5 & MCU
  CM5 -- I2S_DOUT GPIO21 --> AMP[MAX98357A] --> SPK[8 ohm speaker J5]
  CM5 == I2C1 GPIO2/3 ==> ALS[VEML7700] & HAP[DRV2605L + LRA, DNP]
```

## Power tree
```mermaid
flowchart TD
  VBUSC["VBUS_C 5-9V (USB-C, PD 9V request)"] --> Q1["Q1 PMOS (STUSB4500 VBUS_EN_SNK)"] --> VBUSCHG[VBUS_CHG] --> BQ[BQ25895 buck charger]
  VBUSC --> STUSB[STUSB4500 VDD]
  BQ -- "SYS (BATFET power path)" --> VSYS["VSYS 3.5-4.4V"]
  BQ -- BAT --> VBAT["VBAT 1S 3.0-4.2V"]
  VBAT --> TPS7A02["TPS7A02 3.3V 200mA, Iq 25nA"] --> AON["+3V3_AON: STM32U0, PMIC I2C pull-ups, button pull-ups, USBLC6 ref"]
  VBAT --> MAX17055["MAX17055 BATT (sense: BAT_N - 10mOhm - GND)"]
  VSYS --> TPS61088["TPS61088 boost 5.14V, ~3-4A (EN=BOOST_EN)"] --> V5B[+5V_BOOST] --> LSW["Q2 PMOS load switch (CM5_5V_EN)"] --> V5["+5V_CM5: CM5 5V pins (6x), MAX98357A"]
  VSYS --> DRV["DRV2605L VDD (DNP)"]
  V5 --> CM5PMIC[CM5 internal PMIC] --> V33["CM5_3V3 (600mA max): DSI, CSI, mics via mute switch, VEML7700, I2C1 pull-ups, GPIO_VREF"]
  CM5PMIC --> V18[CM5_1V8: unused]
```

## Power-state table
| State | How entered | BATFET | VSYS | +3V3_AON / MCU | BOOST_EN / CM5_5V_EN | CM5 | Exit / wake |
|---|---|---|---|---|---|---|---|
| Ship mode (storage / force-off) | MCU sets BQ25895 BATFET_DIS over PMIC I2C after a 10 s Power hold, or as the last step of a shutdown | off | off (on battery) | **on**: the LDO sits on VBAT before the BATFET; MCU in Stop 2/Standby | low / low | off | USB-C insertion (BQ exits ship mode on VBUS) or Power press (QON pulled low through D4, no MCU involved) |
| Off (MCU standby) | CM5 shutdown completes, then MCU drops BOOST_EN and CM5_5V_EN | on | on | on, Stop 2 with EXTI wake on all 4 buttons | low / low | off | Power press (wake via EXTI), charger/gauge/PD alert |
| Charging while off | VBUS present while Off | on | on (from VBUS) | on | low / low | off | as above; charge LED D3 on |
| Booting | MCU sets BOOST_EN, waits for PG, then CM5_5V_EN; releases PMIC_Enable | on | on | on | high / high | boots | |
| Running | CM5_ALIVE heartbeat high | on | on | on (UART link to CM5) | high / high | on | |
| Soft shutdown | short Power press: MCU sends event over UART + MCU_IRQ_N, or pulses CM5 PWR_Button via Q4 | on | on | on | high until CM5_ALIVE low + timeout | shutting down | |
| Hard force-off | Power held 10 s (MCU only, no CM5 dependence) | off (BATFET_DIS) and/or on | off / on | on | forced low | power removed | as in Ship mode |

Mic mute: SW1 (DPDT slide). Pole 1 moves CM5_3V3 from MIC_VDD to MUTE_LED_PWR, which lights the red LED D1 and drives MIC_MUTE_STATUS high. Pole 2 grounds I2S_DIN, so the mics are cut in hardware twice and no software sits in the path.
