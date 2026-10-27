#!/usr/bin/env python3
"""Validate dts/: compile overlays with dtc, apply them to a stock CM5 base DTB with fdtoverlay, and
check every dtoverlay/dtparam in config.txt against the firmware overlays/README.

Usage: validate.py [--base bcm2712-rpi-cm5-cm5io.dtb] [--readme overlays/README]
Without --base/--readme the corresponding checks are skipped (reported as SKIP). Exit 1 on any FAIL.
Base DTB + README: https://github.com/raspberrypi/firmware/tree/master/boot
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def readme_params(readme: str) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for block in re.split(r"\n(?=Name:\s+)", readme):
        m = re.match(r"Name:\s+(.+?)\s*$", block, re.M)
        if not m:
            continue
        params: set[str] = set()
        pm = re.search(r"\nParams:(.*?)(?=\n\S|\Z)", block, re.S)
        if pm:
            for line in pm.group(1).splitlines():
                mm = re.match(r"\s{0,9}(\S+)\s{2,}", " " + line.strip() + "  ") if line.strip() else None
                if mm and not line.startswith(" " * 20):
                    params.add(mm.group(1))
        out[m.group(1)] = params
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base")
    ap.add_argument("--readme")
    a = ap.parse_args()
    fails = 0
    build = HERE / "build"
    build.mkdir(exist_ok=True)
    for dts in sorted(HERE.glob("*-overlay.dts")):
        out = build / (dts.name.replace("-overlay.dts", ".dtbo"))
        r = subprocess.run(["dtc", "-@", "-q", "-I", "dts", "-O", "dtb", "-o", str(out), str(dts)],
                           capture_output=True, text=True)
        ok = r.returncode == 0
        print(f"{'PASS' if ok else 'FAIL'} dtc {dts.name}{'' if ok else ': ' + r.stderr.strip()}")
        fails += not ok
        if ok and a.base:
            r = subprocess.run(["fdtoverlay", "-i", a.base, "-o", str(build / "applied.dtb"), str(out)],
                               capture_output=True, text=True)
            ok = r.returncode == 0
            print(f"{'PASS' if ok else 'FAIL'} fdtoverlay {out.name} onto {Path(a.base).name}"
                  f"{'' if ok else ': ' + r.stderr.strip()}")
            fails += not ok
        elif ok:
            print(f"SKIP fdtoverlay {out.name} (no --base)")
    if a.readme:
        known = readme_params(Path(a.readme).read_text())
        own = {p.name.replace("-overlay.dts", "") for p in HERE.glob("*-overlay.dts")}
        base = known.get("<The base DTB>", set())
        for ln in (HERE / "config.txt").read_text().splitlines():
            m = re.match(r"\s*dtparam=([^=\s#,]+)", ln)
            if m:
                ok = m.group(1) in base
                print(f"{'PASS' if ok else 'FAIL'} config.txt dtparam {m.group(1)}")
                fails += not ok
                continue
            m = re.match(r"\s*dtoverlay=([^,\s#]+)(?:,([^\s#]*))?", ln)
            if not m:
                continue
            name, params = m.group(1), [p.split("=")[0] for p in (m.group(2) or "").split(",") if p]
            if name in own:
                print(f"PASS config.txt overlay {name} (ours)")
                continue
            if name not in known:
                print(f"FAIL config.txt overlay {name}: not in overlays/README")
                fails += 1
                continue
            bad = [p for p in params if p not in known[name]]
            print(f"{'FAIL' if bad else 'PASS'} config.txt overlay {name}{' unknown params ' + str(bad) if bad else ''}")
            fails += bool(bad)
    else:
        print("SKIP config.txt overlay names (no --readme)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
