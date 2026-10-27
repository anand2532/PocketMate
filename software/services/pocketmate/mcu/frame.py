"""Frame encode/decode and a streaming de-framer (§11)."""
from __future__ import annotations

import struct
from dataclasses import dataclass

from . import cobs
from .crc import crc16_ccitt
from .messages import MAX_PAYLOAD, PROTO_VER, Message

HEADER = struct.Struct("<BBBB")


class FrameError(ValueError):
    pass


@dataclass
class Frame:
    type_id: int
    seq: int
    payload: bytes
    ver: int = PROTO_VER

    def raw(self) -> bytes:
        if len(self.payload) > MAX_PAYLOAD:
            raise FrameError("payload too long")
        body = HEADER.pack(self.ver, self.type_id, self.seq & 0xFF, len(self.payload)) + self.payload
        return body + struct.pack("<H", crc16_ccitt(body))

    def encode(self) -> bytes:
        """COBS-encoded frame followed by the 0x00 delimiter (no preamble)."""
        return cobs.encode(self.raw()) + b"\x00"

    @classmethod
    def from_message(cls, m: Message, seq: int) -> Frame:
        return cls(m.defn.type_id, seq, m.pack_payload())

    def message(self) -> Message:
        return Message.unpack(self.type_id, self.payload)


def decode_raw(raw: bytes) -> Frame:
    if len(raw) < HEADER.size + 2:
        raise FrameError("short frame")
    ver, type_id, seq, ln = HEADER.unpack_from(raw)
    if ln > MAX_PAYLOAD or len(raw) != HEADER.size + ln + 2:
        raise FrameError("length mismatch")
    (crc,) = struct.unpack_from("<H", raw, HEADER.size + ln)
    if crc16_ccitt(raw[: HEADER.size + ln]) != crc:
        raise FrameError("crc")
    if ver != PROTO_VER:
        raise FrameError(f"version {ver}")
    return Frame(type_id, seq, bytes(raw[HEADER.size: HEADER.size + ln]), ver)


class Deframer:
    """Feed arbitrary byte chunks; yields Frames. Bad frames are counted and dropped."""

    MAX_ENCODED = MAX_PAYLOAD + 6 + 2 + 4

    def __init__(self) -> None:
        self._buf = bytearray()
        self.errors = 0
        self._overflow = False

    def feed(self, data: bytes) -> list[Frame]:
        out: list[Frame] = []
        for b in data:
            if b == 0:
                if self._buf and not self._overflow:
                    try:
                        out.append(decode_raw(cobs.decode(bytes(self._buf))))
                    except (FrameError, cobs.COBSDecodeError):
                        self.errors += 1
                elif self._overflow:
                    self.errors += 1
                self._buf.clear()
                self._overflow = False
            else:
                if len(self._buf) >= self.MAX_ENCODED:
                    self._overflow = True
                else:
                    self._buf.append(b)
        return out
