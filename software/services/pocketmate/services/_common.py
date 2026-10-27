from __future__ import annotations

import argparse
import asyncio
import contextlib
import logging
import os
import signal
import socket
from collections.abc import Awaitable, Callable

from ..config import RUN_DIR


def parser(name: str, doc: str) -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=name, description=doc)
    p.add_argument("--run-dir", default=str(RUN_DIR))
    p.add_argument("--log-level", default=os.environ.get("PM_LOG_LEVEL", "INFO"))
    return p


def setup_logging(level: str) -> None:
    # journald adds timestamps; never log payloads, transcripts or keys (privacy).
    logging.basicConfig(level=level.upper(), format="%(name)s %(levelname)s %(message)s")


def sd_notify(msg: str) -> None:
    addr = os.environ.get("NOTIFY_SOCKET")
    if not addr:
        return
    if addr.startswith("@"):
        addr = "\0" + addr[1:]
    with contextlib.suppress(OSError), socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as s:
        s.connect(addr)
        s.sendall(msg.encode())


async def watchdog_loop() -> None:
    usec = int(os.environ.get("WATCHDOG_USEC", "0"))
    if not usec:
        return
    while True:
        sd_notify("WATCHDOG=1")
        await asyncio.sleep(usec / 2e6)


def run(main: Callable[[asyncio.Event], Awaitable[None]]) -> None:
    async def _wrap() -> None:
        stop = asyncio.Event()
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, stop.set)
        wd = asyncio.create_task(watchdog_loop())
        try:
            await main(stop)
        finally:
            wd.cancel()
            sd_notify("STOPPING=1")
    asyncio.run(_wrap())
