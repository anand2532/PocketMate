# ui/ — pm-ui (Qt 6 / QML, 800×480)

Prototype UI host in **PySide6** [impl v0.4.0]. §4 asks for a C++ host for memory/startup; the QML is
host-agnostic (one context property `pm`), so it can move to a C++ `QGuiApplication` later unchanged.

Implemented screens (design/png ids): **01 home, 02 PTT listening, 03 processing, 04 response (source chips),
06 memory search, 10 tasks list, 15 battery** (+ mobile-data state from the LTE governor), with the fixed
status bar (time · mic pill READY/REC/MUTED · 4G state · LOCAL/CLOUD · battery) and hint bar.
Not implemented: the other 61 frozen screens (onboarding, camera/OCR, privacy, data, settings, update, errors,
diagnostics, summary, keyboards), the light theme, volume-key focus navigation, and qmlcachegen.

Data: `backend.py` talks to pm-core (`core.sock`: handle, search, reminders) and pm-power (`power.sock`
signals: Battery, MicMute, MicRail, LteGovernor) over the project's Unix-socket RPC on a background thread.
With `--demo`, or when `/run/pm/core.sock` is missing, it shows built-in demo data.

```sh
pip install PySide6 -e ../services -e .            # dev
pm-ui --demo                                        # desktop window
QT_QPA_PLATFORM=offscreen python -m pocketmate_ui.shots out/   # 8 PNGs at 800x480
QT_QPA_PLATFORM=offscreen pytest -q tests            # 3 tests: zero QML warnings, pixels, RPC round trip
```
On the device `pm-ui.service` runs it with `QT_QPA_PLATFORM=eglfs` as user `pm`. EGLFS on the CM5 + DSI panel,
touch input, the 60 fps and < 3 s startup budgets are **hardware-only** checks.
