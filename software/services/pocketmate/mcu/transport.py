"""Byte transports for the MCU link: pyserial (hardware) and an in-memory loopback pair (tests/sim)."""
from __future__ import annotations

import asyncio
from typing import Protocol


class Transport(Protocol):
    async def write(self, data: bytes) -> None: ...
    async def read(self) -> bytes: ...
    async def close(self) -> None: ...


class LoopbackEnd:
    def __init__(self, rx: asyncio.Queue[bytes], tx: asyncio.Queue[bytes]) -> None:
        self._rx, self._tx = rx, tx
        self.drop_tx = 0          # test hook: drop the next N writes
        self.corrupt_tx = 0       # test hook: flip a byte in the next N writes
        self.closed = False

    async def write(self, data: bytes) -> None:
        if self.closed:
            raise ConnectionError("closed")
        if self.drop_tx:
            self.drop_tx -= 1
            return
        if self.corrupt_tx and len(data) > 3:
            self.corrupt_tx -= 1
            b = bytearray(data)
            b[len(b) // 2] ^= 0x5A
            if 0 in b[1:-1]:
                b = bytearray(data)
                b[-2] ^= 0x01 if b[-2] != 0x01 else 0x02
            data = bytes(b)
        await self._tx.put(data)

    async def read(self) -> bytes:
        return await self._rx.get()

    async def close(self) -> None:
        self.closed = True


def loopback_pair() -> tuple[LoopbackEnd, LoopbackEnd]:
    a: asyncio.Queue[bytes] = asyncio.Queue()
    b: asyncio.Queue[bytes] = asyncio.Queue()
    return LoopbackEnd(a, b), LoopbackEnd(b, a)


class SerialTransport:
    """pyserial transport for /dev/ttyAMA0 (115200 8N1, no flow control). Blocking I/O runs in a thread."""

    def __init__(self, port: str = "/dev/ttyAMA0", baud: int = 115200) -> None:
        import serial  # optional import: only needed on hardware

        self._ser = serial.Serial(port, baud, bytesize=8, parity="N", stopbits=1, timeout=0.05,
                                  rtscts=False, xonxoff=False)

    async def write(self, data: bytes) -> None:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self._ser.write, data)

    async def read(self) -> bytes:
        loop = asyncio.get_running_loop()
        while True:
            chunk = await loop.run_in_executor(None, self._ser.read, 128)
            if chunk:
                return chunk

    async def close(self) -> None:
        self._ser.close()
