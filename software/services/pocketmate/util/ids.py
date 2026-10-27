"""UUIDv7 (RFC 9562) generator: time-ordered ids for items and request_id (§5.1, §7)."""
from __future__ import annotations

import os
import threading
import time
import uuid

_lock = threading.Lock()
_last_ms = 0
_seq = 0


def uuid7(now_ms: int | None = None) -> uuid.UUID:
    global _last_ms, _seq
    with _lock:
        ms = int(time.time() * 1000) if now_ms is None else now_ms
        if ms <= _last_ms:
            ms = _last_ms
            _seq = (_seq + 1) & 0xFFF
            if _seq == 0:          # counter overflow within one ms: borrow the next ms
                ms += 1
        else:
            _seq = int.from_bytes(os.urandom(2), "big") & 0x7FF
        _last_ms = ms
        rand_b = int.from_bytes(os.urandom(8), "big") & ((1 << 62) - 1)
        value = (ms & ((1 << 48) - 1)) << 80
        value |= 0x7 << 76
        value |= _seq << 64
        value |= 0b10 << 62
        value |= rand_b
        return uuid.UUID(int=value)


def new_id() -> str:
    return str(uuid7())
