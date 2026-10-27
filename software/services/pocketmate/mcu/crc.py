"""CRC-16/CCITT-FALSE: poly 0x1021, init 0xFFFF, no reflection, xorout 0. check("123456789") == 0x29B1."""
from __future__ import annotations

POLY = 0x1021
INIT = 0xFFFF


def _table() -> list[int]:
    t = []
    for i in range(256):
        c = i << 8
        for _ in range(8):
            c = ((c << 1) ^ POLY) if c & 0x8000 else (c << 1)
        t.append(c & 0xFFFF)
    return t


_T = _table()


def crc16_ccitt(data: bytes, crc: int = INIT) -> int:
    for b in data:
        crc = ((crc << 8) & 0xFFFF) ^ _T[((crc >> 8) ^ b) & 0xFF]
    return crc
