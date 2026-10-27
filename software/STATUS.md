# PocketMate software: STATUS

`/workspace/pocketmate` is **not a git repository**, so nothing has been committed or pushed. All the work is plain files under `software/`.

## Paused 2026-10-27 (22:25 IST, on Anand's order)

Every file is in a consistent state, and no edit was left half-done. The last full re-run before the pause:

| Area | Result |
|---|---|
| services pytest | 117 passed |
| ui pytest | 3 passed |
| ruff (services + ui) | clean |
| `lte/tests/test_pm_lte_power.sh` | 12 passed |

The other results below come from earlier in this session and were not re-run at the pause.

### Done and verified here (how)

- **services/** (Python, systemd units). Verified with:
  - pytest (117 tests), ruff, and `systemd-analyze verify` (pm-lte.service passes; the only complaint is the pre-existing pm-llm `llama-server` binary, which isn't on the build box).
  - LTE pieces:
    - governor (`pocketmate/lte/governor.py`)
    - AT client and profile apply (`lte/at.py`)
    - controller (`lte/controller.py`)
    - Quectel profiles (`lte/quectel.py`)
    - pm-power LTE integration
    - `pm_lte.py` service
  - The `LTE_CFG` MCU message.
  - `config.py` defaults for `lte`.
  - pm-power now also emits a `Battery` signal (soc, charging) for the UI.
- **firmware/** (STM32U031). Verified with:
  - Host tests: 19 tests, 587 checks, 0 failures.
  - arm-none-eabi build: no warnings, text 4408 B, bss 256 B.
  - What's implemented:
    - VREG clamp ≤ 4.24 V when the LTE board is present
    - `LTE_CFG` handler
    - minimal CM5 power FSM: power-on, shutdown-ready plus 10 s cut, and the hard-cut latch
    - rewritten `target/hal_stm32u0.c`
- **dts/**: overlays compiled with dtc and checked by `dts/validate.py` against the CM5 IO base DTB.
- **lte/**:
  - `check_netlist.py` passes.
  - `pm-lte-power` is shellcheck-clean and passes 12 dry-run tests.
  - Also written: `pm-lte-net`, udev rule, networkd file, systemd unit.
- **os/**: `os/check.sh` passed 12 and failed 0 (shellcheck on 8 scripts, partition arithmetic, tryboot backend state machine, slot generator, system.conf, and a no-key-files scan). `nft -c` and `rauc` checks were skipped because neither tool is installed. Contents:
  - pi-gen stage `stage-pm`
  - read-only rootfs files
  - GPT layout
  - RAUC `system.conf`, manifest, `make-bundle.sh`, tryboot backend
  - `keys/` placeholders only: **no keys were generated**
  - `README.md`
- **ui/** (PySide6 QML, 800×480). Verified offscreen:
  - zero QML warnings
  - 8 screenshots in `ui/screenshots/`
  - pixel checks
  - RPC round trip against fake pm-core/pm-power sockets
  - Screens: 01 home, 02 listening, 03 processing, 04 response, 06 memory, 10 tasks, 15 battery, plus the status bar and hint bar.

### Done, but can only be verified on hardware

- **LTE**:
  - real power sequencing and GPIO polarities
  - USB enumeration on CM5 USB3-0's USB2 pair
  - the AT port interface numbers (EC200U is VERIFY)
  - `AT+QNETDEVCTL` data bring-up
  - RI/AP_READY polarity
  - GNSS
  - the tc throttle
- **Firmware on the STM32U031**:
  - PA2/PA3 AF7, PB1 polarity, LSI/IWDG timing
  - USART2 link to the CM5
  - `hal_cm5_power_good` returns the commanded state, because there is no sense pin (a hardware gap)
- **OS**:
  - the pi-gen build itself (not run here)
  - CM5 tryboot one-shot behaviour, the `/proc/device-tree/chosen/bootloader/partition` path, and the RAUC install flow
  - LUKS /data, the read-only root, and the watchdog
- **UI**: EGLFS on the DSI panel, touch, 60 fps, and the < 3 s startup budget.
- **DT overlays**: loading on a real CM5, the I2S audio card, and `CONFIG_RFKILL_GPIO`.

### Partially done (exact stopping points)

- **`os/pi-gen/config` and `os/README.md`**:
  - Switched to `RELEASE=trixie`, because Debian packages `python3-pyside6.*` only from trixie on (ftp-master madison: stable 6.8.2.1-4; bookworm has none).
  - The pi-gen branch that builds trixie arm64 is marked VERIFY.
  - ARCHITECTURE.md §2 says "Bookworm or newer" but hasn't been updated to say trixie.
- **ui/**: 7 of the 70 frozen screens are done. Not started: the light theme, volume-key focus navigation, qmlcachegen, and the C++ host (§4 asks for C++; the PySide6 host is an [impl] deviation).
- **lte/**: `pm-lte-power` and `services/pocketmate/lte/quectel.py` still use **per-module** timings and the old H-LTE-1 logic. The new inputs below are not applied yet.
- **READMEs**: written for `os/`, `ui/` and `dts/`. Not yet written: `lte/README.md`, `firmware/README.md`, and the top-level `software/README.md`.

### Not started

- **`bringup/`**: `pm-bringup` with `--dry-run` and a pass/fail report. The design was sketched but no file was written; the empty directory was removed.
  - Device checks: CM5 model, overlays, MCU link ping (pm-power `ping`/`status`), aplay/arecord stereo, DSI connected, touch, camera AF still capture, battery gauge, LTE on + USB + AT, watchdog, `rauc status`, read-only root, pm-ui active.
  - Host checks: check_netlist, dts validate, LTE dry-run, os/check.sh.
- **ARCHITECTURE.md v0.4.0**:
  - Line 1 header and line 3 Status.
  - §19 LTE section: pins, netlist check, timings, STATUS, cited AT commands, governor, VBAT/VSYS note, VREG, diversity, GNSS, pm-lte.
  - Fix line 1766 (amp SD → GPIO27).
  - Note the 2.7/3.2 A vs 5.5 A conflict (line 1416).
  - Changelog of deviations.
- **Firmware**: the I2C charger driver (BQ25895 VREG write; until then the POR default of 4.208 V applies, which is LTE-safe), Stop2 low-power mode, and ship mode.
- **Production**: RAUC keyring (`os/keys/public/keyring.pem`), production LUKS key [A-4], APN default (none set).

### Latest LTE inputs NOT yet applied (2026-10-27 steering, ~22:24 IST)

1. **Use the schematic timing on both modules** (the prototype module is the EC200U-CN; `hardware/kicad-lte/README.md` lines 88–91):

   | Line | Timing |
   |---|---|
   | PWRKEY (GPIO9) on | 2.2 s |
   | PWRKEY off | 3.2 s, used only as a fallback (prefer `AT+QPOWD=1`) |
   | RESET (GPIO13) | 250 ms |

   - Q1 and Q2 are both open-drain DMG1012T with a 4.7 k / 47 k gate network. I checked kicad-lte.net, so GPIO high = asserted for both PWRKEY and RESET; the script already drives them that way.
   - **To do**: set one timing table in `pm-lte-power` (`do_on` / `do_off` / `do_reset`) and in `quectel.py` (`pwrkey_on_ms`, `pwrkey_off_ms`, `reset_ms`), drop the "refuse if module unknown" branch in `do_off`, and update `lte/tests/test_pm_lte_power.sh`.
2. **H-LTE-1 is resolved in hardware.** kicad-lte.net (modified 16:50 IST) adds Q7 as a build option:

   | Build | Fit | Leave DNP |
   |---|---|---|
   | EC200U | Q3 | Q7 (the BOM currently shows Q7 DNP) |
   | EC25 | Q7 | Q3 |

   - With the right parts fitted, LTE_STATUS low = on for both modules.
   - **To do**: set `status_on_level=0` for EC25 in `quectel.py`, rewrite the H-LTE-1 comments, and use STATUS for both modules in `pm-lte-power` `is_on` / `do_off`.
3. **EC25 diversity, looked up and confirmed**: the command is `AT+QCFG="divctl","lte",1`, which means PRX only and DRX off.
   - Source: Quectel EC2x&EG2x&EG9x&EM05 QCFG AT Commands Manual V1.1 (2023-06-27) §3.11.
   - In that manual, `0` *enables* both chains, so the steering's `,0` is wrong.
   - `AT+QCFG="diversity",0` is quoted in the EC25 HD (`ref/ec25_hd.txt` line 4339) as the fallback.
   - The diversity antenna (J3) has been removed from the board.
   - **To do**: apply it only when `ATI` reports EC25 (not just the USB ID). This needs an `ATI` model probe in `lte/at.py` / `pm_lte.py`.
4. **EC200U special firmware.** Per the EC200U HD (`ref/ec200u_hd.txt` around line 2625), firmware with the USIM2 function multiplexes AP_READY, WAKEUP_IN, SLEEP_IND and W_DISABLE# as USIM2 lines. The EC200U DSSS Application Note V1.0 adds that `AT+QDSIMCFG="dsss",1` disables those multiplexed functions; it is saved and takes effect after a reboot.
   - **To do**:
     - log `ATI` and `AT+QGMR` to the state dir
     - query `AT+QDSIMCFG="dsss"`
     - if dual-SIM is detected, stop driving GPIO25 and GPIO26 and flag it
     - no firmware-revision signature is known, so don't invent one
5. **EC200U LTE-only command**: `AT+QCFG="nwscanmode",3,1`, citing EC200U AT Commands Manual V1.2 §4.5.1 (already in `quectel.py`). It still needs to be run on a real module (status: unverified on hardware).

### How to resume

1. Apply LTE inputs 1–4 (`lte/pm-lte-power`, `services/pocketmate/lte/quectel.py`, `lte/at.py`, `services/pocketmate/services/pm_lte.py`, and the tests). Then re-run:
   - `bash lte/tests/test_pm_lte_power.sh`
   - `cd services && pytest -q`
2. Write `bringup/pm-bringup` with tests, `lte/README.md`, `firmware/README.md` and `software/README.md`.
3. Update ARCHITECTURE.md to v0.4.0 (see "Not started"), including trixie in §2.
4. Re-run everything:
   - pytest for services and ui, plus ruff
   - `firmware`: `cmake --build build-host && ctest`, then `cmake --build build-arm`
   - `python3 dts/validate.py --base /tmp/cm5io.dtb --readme /tmp/ovreadme.txt`
   - `python3 lte/check_netlist.py`
   - `systemd-analyze verify`
   - `bash os/check.sh`
   - `QT_QPA_PLATFORM=offscreen python -m pocketmate_ui.shots`
5. Finish this file and the final report. Still no git; nothing is pushed.

### Open issues and conflicts to raise

- The ARCHITECTURE overcurrent thresholds of 2.7/3.2 A (line 1416) conflict with the 5.5 A LTE throttle.
- The 5.5 A throttle is measured at the cell (VBAT, MAX17055) by design. VSYS isn't measured, so this is ambiguous.
- Line 1766 is stale: the amp SD pin is GPIO27, not GPIO16.
- Spec overlay errors (waveshare, imx708). googlevoicehat on GPIO16 conflicts, so the custom `pocketmate-audio` overlay is used.
- Research suggested USB3-1, but the netlist uses USB3-0; the netlist is followed.
- Deviations from spec:
  - a `bootsel` p1 partition (§2.1)
  - slot mounts via a generator
  - CI bundles signed with a throwaway dev key
  - pm-lte polls RPC instead of using D-Bus
  - PySide6 UI host instead of C++
  - trixie instead of bookworm

## Queued for resume (received 2026-10-27, while paused)
- Current limits finalised in `hardware/power-config.md`: prototype profile 2.7/3.2 A; production profile (measured at the cell) 5.5 A soft throttle, 6.0 A hard limit, -6.4 A gauge alert. Update ARCHITECTURE.md §10.5 (~L1410/1416) and the governor config.
- Fix ARCHITECTURE.md ~L1766: amp shutdown = GPIO27; GPIO16 = LTE_STATUS.
- LTE USB = USB2 pair of CM5 USB3-0 (already followed in code).
