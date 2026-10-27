"""Injectable clocks so the governor/scheduler logic is deterministic under test."""
from __future__ import annotations

import time
from dataclasses import dataclass


class Clock:
    def monotonic(self) -> float:
        return time.monotonic()

    def time(self) -> float:
        return time.time()


@dataclass
class FakeClock(Clock):
    mono: float = 1000.0
    wall: float = 1_793_000_000.0  # 2026-10-27-ish

    def monotonic(self) -> float:
        return self.mono

    def time(self) -> float:
        return self.wall

    def advance(self, seconds: float) -> None:
        self.mono += seconds
        self.wall += seconds
