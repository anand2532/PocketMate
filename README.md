# PocketMate
A personal AI companion built on the Raspberry Pi CM5 (4GB; CM4 alternate). PocketMate helps you capture anything important, find it when you need it, and get the next step done: dependable, fast, privacy-conscious, and not a phone replacement.

MVP: push-to-talk voice assistant, local voice/typed notes, searchable memory with source-linked answers, camera OCR, reminders and action items, configurable local/cloud processing, and a physical mic mute. Hardware: 4.3" touchscreen, autofocus camera, dual MEMS mics, battery with USB-C charging, custom carrier PCB and a compact, serviceable enclosure (~125x75x20mm).

See [docs/PRD.md](docs/PRD.md) for the full product brief.

## Repository layout
- `hardware/kicad/` – schematics and carrier PCB (KiCad)
- `mechanical/freecad/` – enclosure CAD (FreeCAD)
- `software/` – Linux services, Qt/QML UI, firmware
- `docs/` – PRD and project documentation
- `research/` – notes, datasheets, experiments
