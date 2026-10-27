# mechanical

**Current enclosure release: [`release_v5/`](release_v5/)**. This release adds the LTE daughterboard shelf, RF windows, SIM access and fab notes. See [`release_v5/README_release_v5.md`](release_v5/README_release_v5.md) for details and open items O1–O9, and [`release_v5/INTERFERENCE_CHECK_release_v5.md`](release_v5/INTERFERENCE_CHECK_release_v5.md) for the interference check.

- `release_v5/`: build scripts, the assembly STEP, per-part STEPs (`step_parts/`), STL meshes (`stl/`), and a PDF and DXF drawing set (`drawings/`).
- `freecad/`: the earlier v2 and v4_22c FreeCAD models. **Superseded by release_v5** and kept for reference.
- `thermal_*.md`: thermal notes (v2, v3, v3_ribs, v5_22).

Note: the release_v5 README and `key_gaps_release_v5.py` refer to `work/` (intermediate .brep and JSON files) and `ref/` (carrier KiCad STEP export). Neither folder is committed. Regenerate `work/` with the build scripts. Regenerate `ref/` by exporting `hardware/kicad/PocketMate.kicad_pcb` with `kicad-cli pcb export step`.
