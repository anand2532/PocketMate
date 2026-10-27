"""Minimal AT command client for the Quectel AT port (/dev/ttyUSB2 on EC25, VERIFY per module) with an
injectable byte transport so it is unit-testable. Never logs payloads beyond the command name."""
from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from .quectel import AtStep, ModuleProfile

log = logging.getLogger("pm.lte")


class Port(Protocol):
    def write(self, data: bytes) -> object: ...
    def read(self, n: int) -> bytes: ...          # returns b"" on timeout


@dataclass
class AtResult:
    ok: bool
    lines: list[str]

    @property
    def text(self) -> str:
        return "\n".join(self.lines)


class AtClient:
    def __init__(self, port: Port, now: Callable[[], float] = time.monotonic) -> None:
        self.port, self.now = port, now

    def cmd(self, command: str, timeout_s: float = 2.0) -> AtResult:
        self.port.write(command.encode() + b"\r")
        buf, lines, end = b"", [], self.now() + timeout_s
        while self.now() < end:
            chunk = self.port.read(256)
            if not chunk:
                continue
            buf += chunk
            while b"\n" in buf:
                raw, buf = buf.split(b"\n", 1)
                ln = raw.strip(b"\r ").decode(errors="replace")
                if not ln or ln == command:
                    continue
                if ln == "OK":
                    return AtResult(True, lines)
                if ln == "ERROR" or ln.startswith("+CME ERROR") or ln.startswith("+CMS ERROR"):
                    lines.append(ln)
                    return AtResult(False, lines)
                lines.append(ln)
        return AtResult(False, lines + ["TIMEOUT"])


def apply_profile(at: AtClient, prof: ModuleProfile) -> dict[str, str]:
    """Run the profile's init steps. Returns {cmd: "ok"|"skipped"|"failed:<reason>"}.
    Optional steps with a `probe` are only sent if the test command lists that setting."""
    out: dict[str, str] = {}
    caps: dict[str, str] = {}
    for step in prof.init:
        if step.probe:
            base = step.cmd.split("=", 1)[0]               # AT+QCFG / AT+QGPSCFG
            if base not in caps:
                caps[base] = at.cmd(base + "=?", 3.0).text
            if step.probe not in caps[base]:
                out[step.cmd] = "skipped"
                continue
        if _divctl_already_done(step, out):
            out[step.cmd] = "skipped"
            continue
        r = at.cmd(step.cmd, 5.0)
        if r.ok or (step.cmd == "AT+QGPS=1" and "504" in r.text):   # 504 = session already active
            out[step.cmd] = "ok"
        else:
            out[step.cmd] = "failed:" + (r.lines[-1] if r.lines else "?")
            (log.info if step.optional else log.error)("AT step %s failed (%s)", step.cmd.split("=")[0], step.source)
    return out


def _divctl_already_done(step: AtStep, out: dict[str, str]) -> bool:
    return "diversity" in step.cmd and any("divctl" in k and v == "ok" for k, v in out.items())
