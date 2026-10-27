#!/usr/bin/env python3
"""Cross-check the LTE control pin map used by software (pinmap.env) against both KiCad netlists.

Checks:
  1. carrier hardware/kicad/PocketMate.net: each LTE_* net reaches the expected CM5 J1 GPIO / J2 USB pin.
  2. LTE board hardware/kicad-lte/kicad-lte.net: J1 pad (via the reversed-FFC map in gen/link_map.json)
     carries the same net name as carrier J14 pin.
  3. No CM5 GPIO used by LTE is also used by another carrier net (GPIO4/14/15/17, I2S 18-21, ...).
Exit 0 = all PASS. Usage: check_netlist.py [--repo /path/to/pocketmate]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
NODE = re.compile(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)(?: \(pinfunction "([^"]*)"\))?')
NET = re.compile(r'\(net \(code "?\d+"?\) \(name "([^"]+)"\)(.*?)(?=\(net \(code|\Z)', re.S)


def load_pinmap() -> dict[str, str]:
    out = {}
    for ln in (HERE / "pinmap.env").read_text().splitlines():
        m = re.match(r"\s*(LTE_[A-Z_]+_GPIO)=(\d+)", ln)
        if m:
            out[m.group(1)[:-5]] = f"GPIO{m.group(2)}"
    return out


def parse(path: Path) -> dict[str, list[tuple[str, str, str]]]:
    nets: dict[str, list[tuple[str, str, str]]] = {}
    for m in NET.finditer(path.read_text()):
        nets[m.group(1).split("/")[-1]] = NODE.findall(m.group(2))
    return nets


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=str(HERE.parents[1]))
    a = ap.parse_args()
    repo = Path(a.repo)
    carrier = parse(repo / "hardware/kicad/PocketMate.net")
    lte = parse(repo / "hardware/kicad-lte/kicad-lte.net")
    link = json.loads((repo / "hardware/kicad-lte/gen/link_map.json").read_text())["J14_to_J1"]
    fails = 0

    def res(ok: bool, msg: str) -> None:
        nonlocal fails
        print(("PASS " if ok else "FAIL ") + msg)
        fails += not ok

    pinmap = load_pinmap()
    for net, gpio in pinmap.items():
        fns = [fn for ref, _p, fn in carrier.get(net, []) if ref == "J1"]
        res(fns == [gpio], f"carrier {net} -> CM5 {gpio} (netlist: {fns or 'none'})")
    for net, fn in (("LTE_USB_DP", "USB3-0-DP"), ("LTE_USB_DM", "USB3-0-DM")):
        fns = [f for ref, _p, f in carrier.get(net, []) if ref == "J2"]
        res(fns == [fn], f"carrier {net} -> CM5 J2 {fn} (netlist: {fns or 'none'})")
    # J14 pin -> J1 pad on the LTE board
    j14 = {p: n for n, nodes in carrier.items() for ref, p, _f in nodes if ref == "J14"}
    j1 = {p: n for n, nodes in lte.items() for ref, p, _f in nodes if ref == "J1"}
    for pin in sorted(j14, key=int):
        a_net, b_net = j14[pin], j1.get(link[pin], "?")
        res(a_net == b_net, f"J14.{pin} {a_net} == LTE J1.{link[pin]} {b_net}")
    # GPIO conflicts
    users: dict[str, set[str]] = {}
    for n, nodes in carrier.items():
        for ref, _p, fn in nodes:
            if ref == "J1" and re.fullmatch(r"GPIO\d+", fn) and not n.startswith("unconnected"):
                users.setdefault(fn, set()).add(n)
    for net, gpio in pinmap.items():
        others = users.get(gpio, set()) - {net}
        res(not others, f"{gpio} used only by {net}" + (f" (also {sorted(others)})" if others else ""))
    print(f"{'OK' if not fails else 'MISMATCH'}: {fails} failure(s)")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
