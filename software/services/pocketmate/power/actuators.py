"""sysfs actuators (CPU caps, core hotplug, backlight, rfkill). `root` lets tests use a fake sysfs.
On hardware pm-power needs write access via the udev rule in systemd/90-pocketmate.rules."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

log = logging.getLogger("pm.power")


@dataclass
class Sysfs:
    root: Path = Path("/")

    def p(self, rel: str) -> Path:
        return self.root / rel.lstrip("/")

    def write(self, rel: str, value: str | int) -> bool:
        try:
            self.p(rel).write_text(f"{value}\n")
            return True
        except OSError as e:
            log.warning("sysfs write %s=%s failed: %s", rel, value, e)
            return False

    def read(self, rel: str, default: str = "") -> str:
        try:
            return self.p(rel).read_text().strip()
        except OSError:
            return default


class CpuControl:
    def __init__(self, fs: Sysfs, ncpu: int = 4) -> None:
        self.fs, self.ncpu = fs, ncpu

    def set_max_khz(self, khz: int) -> None:
        for n in range(self.ncpu):
            if n == 0 or self.fs.read(f"sys/devices/system/cpu/cpu{n}/online", "1") == "1":
                self.fs.write(f"sys/devices/system/cpu/cpu{n}/cpufreq/scaling_max_freq", khz)

    def set_online(self, count: int) -> None:
        """Cores 2-3 offline when no engine is busy (§10.6). cpu0 can't be offlined."""
        for n in range(1, self.ncpu):
            self.fs.write(f"sys/devices/system/cpu/cpu{n}/online", 1 if n < count else 0)


class Backlight:
    def __init__(self, fs: Sysfs, name: str | None = None) -> None:
        self.fs = fs
        base = fs.p("sys/class/backlight")
        if name is None and base.is_dir():
            names = sorted(x.name for x in base.iterdir())
            name = names[0] if names else None
        self.name = name

    def set_pct(self, pct: int) -> None:
        if not self.name:
            return
        b = f"sys/class/backlight/{self.name}"
        mx = int(self.fs.read(f"{b}/max_brightness", "255") or 255)
        self.fs.write(f"{b}/bl_power", 0 if pct > 0 else 4)     # FB_BLANK_POWERDOWN when off
        self.fs.write(f"{b}/brightness", round(mx * max(0, min(100, pct)) / 100))


class Rfkill:
    """Soft-block by type via /sys/class/rfkill/*/{type,soft}. Types: wlan, bluetooth, wwan."""

    def __init__(self, fs: Sysfs) -> None:
        self.fs = fs

    def _devs(self, kind: str) -> list[str]:
        base = self.fs.p("sys/class/rfkill")
        if not base.is_dir():
            return []
        return [f"sys/class/rfkill/{d.name}" for d in sorted(base.iterdir())
                if self.fs.read(f"sys/class/rfkill/{d.name}/type") == kind]

    def set_blocked(self, kind: str, blocked: bool) -> int:
        n = 0
        for d in self._devs(kind):
            n += self.fs.write(f"{d}/soft", 1 if blocked else 0)
        return n

    def blocked(self, kind: str) -> bool | None:
        ds = self._devs(kind)
        if not ds:
            return None
        return all(self.fs.read(f"{d}/soft") == "1" for d in ds)
