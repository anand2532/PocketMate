# PocketMate CM5 configuration (carrier v0.2, 2026-10-21)

## 1. Power: tell the firmware the 5 V supply can deliver 5 A
The carrier feeds CM5 5V from the TPS61088 boost (5.12 V, sized for 3.5 A continuous). CC1/CC2 on the CM5 are **not** connected (PD is handled by the STUSB4500), so the CM5 cannot negotiate 5 A itself and would otherwise limit USB current and warn about the supply.

Bootloader EEPROM (`sudo rpi-eeprom-config --edit`):
```
[all]
PSU_MAX_CURRENT=5000
POWER_OFF_ON_HALT=1      # let CM5 PMIC go fully off on halt; MCU then drops CM5_5V_EN
WAKE_ON_GPIO=0
```
`/boot/firmware/config.txt`:
```
[all]
usb_max_current_enable=1
```
Note: the boost is sized for about 3.5 A. PSU_MAX_CURRENT=5000 only lifts the firmware's USB current limit. There's no USB-A port on this board, so actual draw is CM5 + DSI + CSI. Do not add high-power USB loads.

## 2. Interfaces (config.txt)
```
dtparam=i2c_arm=on            # I2C1 GPIO2/3: VEML7700 (0x10), DRV2605L (0x5A, DNP)
enable_uart=1                 # UART0 GPIO14/15 <-> STM32U0 USART2 (115200 8N1)
dtoverlay=vc4-kms-v3d
# Display: Waveshare 4.3in DSI on MIPI1/DSI1 connector J3 (per Waveshare wiki, Pi5/CM5 section)
dtoverlay=vc4-kms-dsi-7inch
#   fallback reported by Waveshare: dtoverlay=vc4-kms-dsi-waveshare-800x480
# Camera: Camera Module 3 (IMX708) on MIPI0 connector J4 (I2C on SCL0/SDA0)
camera_auto_detect=0
dtoverlay=imx708,cam0
# Audio: mics (I2S in, GPIO20) + MAX98357A (I2S out, GPIO21) share BCLK GPIO18 / LRCLK GPIO19.
# Stock overlays conflict; ship ONE combined overlay "pocketmate-audio" (simple-audio-card with
# MAX98357A codec + SPH0645 capture, shared bit/frame clock). TODO firmware.
# CM5_ALIVE heartbeat to MCU on GPIO23: drive high once booted; low at poweroff
gpio=23=op,dl
dtoverlay=gpio-poweroff,gpiopin=23,active_low=1
```
(The `gpio-poweroff` line needs a check: the goal is GPIO23 high while Linux runs and low after halt, so a userspace service can also set it. Check this on hardware.)

## 3. Cables implied by the 22-pin connectors (Pi 5 / CM5IO-style, 0.5 mm FH12-22S-0.5SH)
| Connector | Pinout | Device | Cable |
|---|---|---|---|
| J3 DSI (MIPI1, 4 lanes wired, panel uses 2) | identical to CM5IO J16 (verified against CM5IO rev2 KiCad netlist) | Waveshare 4.3in DSI LCD (15-pin 1.0 mm connector on panel, see wiki pin table) | Raspberry Pi 5 display cable 22p 0.5 mm to 15p 1.0 mm ("Pi5-Display-Cable", e.g. Waveshare Pi5-Display-Cable-200mm, or the official RPi 200 mm/500 mm display cable). Use Waveshare panel Rev2.2 or later; older revisions trip Pi5/CM5 power detection |
| J4 CSI (MIPI0, 4 lanes wired) | identical to CM5IO J5 | Raspberry Pi Camera Module 3 (IMX708) has a 15p 1.0 mm FPC on the module | Raspberry Pi 5 camera cable "standard-to-mini" 22p 0.5 mm to 15p 1.0 mm (official 200/300/500 mm). This is a straight cable, not an adapter board. Alternatively, a module with a native 22-pin connector |

## Fan (v0.3, header J12 DNP)
CM5 Fan_PWM (J1-19) / Fan_Tacho (J1-16) drive the 4-wire blower directly; the firmware's default fan curve applies (same as CM5IO). Tune with `dtparam=fan_temp0=...,fan_temp0_hyst=...,fan_temp0_speed=...` (TODO: confirm parameter names for CM5 on the current firmware).
