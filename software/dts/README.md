# dts/: device tree for the PocketMate carrier (CM5)

| File | What |
|---|---|
| `pocketmate-carrier-overlay.dts` | UART0 to the MCU (GPIO14/15), MCU_IRQ_N GPIO4 as a gpio-keys wake source (KEY_WAKEUP), mic-mute sense GPIO17 as EV_SW/SW_MUTE_DEVICE, DRV2605L @0x5a (disabled, `haptics=okay` override), rfkill-gpio wwan on GPIO26 (disabled, `lte` override) |
| `pocketmate-audio-overlay.dts` | 2x I2S MEMS mic + MAX98357A. Clone of stock `googlevoicehat-soundcard` with amp SD_MODE moved from GPIO16 to GPIO27 (netlist) |
| `config.txt` | `/boot/firmware/config.txt` fragment installed by `os/stage-pm` |
| `validate.py` | compile with dtc, apply onto a stock CM5 base DTB with fdtoverlay, and check every `dtoverlay=`/`dtparam=` (name and params) in config.txt against the firmware `overlays/README` |
| `build/*.dtbo` | compiled overlays (copied to `/boot/firmware/overlays/`) |

Pin source of truth: `hardware/kicad/PocketMate.net`. CM5 GPIO use from that netlist: 2/3 I2C1, 4 MCU_IRQ_N, 9 LTE_PWRKEY,
12 LTE_RI, 13 LTE_RESET, 14/15 UART0, 16 LTE_STATUS, 17 MUTE_STATUS_IO, 18-21 I2S, 22 HAPTIC_EN, 23 CM5_ALIVE,
24 LTE_PWR_EN, 25 LTE_AP_READY, 26 LTE_W_DISABLE_N, 27 AMP_SD_MODE. Free: 5-8, 10, 11.

## Validate
```sh
# reference inputs (not committed): raspberrypi/firmware boot/ tree
curl -LO https://github.com/raspberrypi/firmware/raw/master/boot/bcm2712-rpi-cm5-cm5io.dtb
curl -L -o overlays-README https://github.com/raspberrypi/firmware/raw/master/boot/overlays/README
python3 validate.py --base bcm2712-rpi-cm5-cm5io.dtb --readme overlays-README   # exit 0 = all PASS
```
Needs `dtc` and `fdtoverlay` (device-tree-compiler >= 1.6).

## Corrections to ARCHITECTURE.md v0.3.13 (fixed in v0.4.0)
- `vc4-kms-dsi-waveshare-panel,4_3_inch,dsi1`: no such params. The 4.3" 800x480 panel uses `vc4-kms-dsi-waveshare-800x480` (DSI1 is the default; `-v2,4_3_inch_a` is a different 480x800 panel).
- `imx708,cam1`: no `cam1` param; CAM1 is the default (`cam0` selects the other port).
- `googlevoicehat-soundcard` drives GPIO16 as amp SD; GPIO16 is LTE_STATUS in the netlist, so it is replaced by `pocketmate-audio`.

## Hardware-only checks
- `dtoverlay -l`, `vcdbg log msg` / `dmesg` show both overlays applied with no errors.
- `evtest` on "pocketmate-keys": MCU IRQ gives KEY_WAKEUP; the mute slider toggles SW_MUTE_DEVICE; `echo enabled > .../power/wakeup` wakes from suspend.
- `/dev/ttyAMA0` talks to the MCU at the §11 baud (no getty on it).
- `aplay -l`/`arecord -l` show the voicehat card; amp mutes when GPIO27 low.
- With `,lte`: `rfkill list` shows `pocketmate-wwan` (wwan); `rfkill block wwan` drives GPIO26 low (`pinctrl get 26`).
- Panel and touch with `vc4-kms-dsi-waveshare-800x480`; camera with `rpicam-hello --list-cameras`.
