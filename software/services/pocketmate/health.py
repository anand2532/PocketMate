"""pm-health (§3 OTA): boot health check within 120 s -> `rauc status mark-good`.
Checks: UI up, pm-core responding, DB open, MCU link OK. Each check is injectable for tests."""
from __future__ import annotations

import asyncio
import shutil
import sqlite3
import subprocess
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from pathlib import Path

HEALTH_DEADLINE_S = 120.0
Check = Callable[[], Awaitable[bool]]


@dataclass
class HealthReport:
    results: dict[str, bool] = field(default_factory=dict)
    elapsed_s: float = 0.0

    @property
    def ok(self) -> bool:
        return bool(self.results) and all(self.results.values())


def unit_active(unit: str) -> Check:
    async def _c() -> bool:
        if not shutil.which("systemctl"):
            return False
        p = await asyncio.create_subprocess_exec("systemctl", "is-active", "--quiet", unit)
        return await p.wait() == 0
    return _c


def db_opens(path: str | Path) -> Check:
    async def _c() -> bool:
        try:
            c = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
            c.execute("SELECT value FROM meta WHERE key='schema_version'").fetchone()
            c.close()
            return True
        except sqlite3.Error:
            return False
    return _c


def rpc_ping(sock: str | Path, method: str = "ping") -> Check:
    async def _c() -> bool:
        from .ipc.rpc import RpcClient
        cl = RpcClient(sock)
        try:
            await cl.connect()
            return bool(await cl.call(method, timeout=3))
        except (OSError, TimeoutError, Exception):  # noqa: BLE001
            return False
        finally:
            await cl.close()
    return _c


async def run_checks(checks: dict[str, Check], *, deadline_s: float = HEALTH_DEADLINE_S,
                     retry_s: float = 2.0) -> HealthReport:
    t0 = time.monotonic()
    rep = HealthReport({k: False for k in checks})
    while True:
        for name, c in checks.items():
            if not rep.results[name]:
                try:
                    rep.results[name] = await c()
                except Exception:  # noqa: BLE001
                    rep.results[name] = False
        rep.elapsed_s = time.monotonic() - t0
        if rep.ok or rep.elapsed_s + retry_s > deadline_s:
            return rep
        await asyncio.sleep(retry_s)


def mark(good: bool, *, dry_run: bool = False) -> list[str]:
    cmd = ["rauc", "status", "mark-good" if good else "mark-bad"]
    if not dry_run and shutil.which("rauc"):
        subprocess.run(cmd, check=False)
    return cmd
