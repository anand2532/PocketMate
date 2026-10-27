"""Radio leases (§10.6): Wi-Fi/BT (and LTE on the 4G SKU) stay rfkill-blocked; a lease unblocks
for a purpose and the radio is re-blocked 30 s after the last lease ends (or a lease times out).
Purposes mirror §10.6: cloud request (consented), update check, settings screen, ntp, bt_audio."""
from __future__ import annotations

import itertools
from collections.abc import Callable
from dataclasses import dataclass, field

REBLOCK_AFTER_S = 30.0
PURPOSES = {"cloud", "update", "settings", "ntp", "bt_audio"}


@dataclass
class Lease:
    id: int
    radio: str
    purpose: str
    expires_at: float


@dataclass
class RadioLeaseManager:
    set_blocked: Callable[[str, bool], object]      # e.g. Rfkill.set_blocked
    now: Callable[[], float]
    leases: dict[int, Lease] = field(default_factory=dict)
    _idle_since: dict[str, float] = field(default_factory=dict)
    _up: set[str] = field(default_factory=set)
    _ids: itertools.count = field(default_factory=lambda: itertools.count(1))

    def acquire(self, radio: str, purpose: str, timeout_s: float = 60.0) -> Lease:
        if purpose not in PURPOSES:
            raise ValueError(f"unknown radio purpose {purpose!r}")
        lease = Lease(next(self._ids), radio, purpose, self.now() + timeout_s)
        self.leases[lease.id] = lease
        self._idle_since.pop(radio, None)
        if radio not in self._up:
            self.set_blocked(radio, False)
            self._up.add(radio)
        return lease

    def release(self, lease: Lease) -> None:
        self.leases.pop(lease.id, None)
        if not any(x.radio == lease.radio for x in self.leases.values()):
            self._idle_since[lease.radio] = self.now()

    def tick(self) -> None:
        t = self.now()
        for _lid, ls in list(self.leases.items()):
            if t >= ls.expires_at:
                self.release(ls)
        for radio, since in list(self._idle_since.items()):
            if t - since >= REBLOCK_AFTER_S and radio in self._up:
                self.set_blocked(radio, True)
                self._up.discard(radio)
                del self._idle_since[radio]

    def block_all(self) -> None:
        for r in list(self._up) + ["wlan", "bluetooth", "wwan"]:
            self.set_blocked(r, True)
        self._up.clear()
        self.leases.clear()
        self._idle_since.clear()
