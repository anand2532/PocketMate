"""Frame = u32 LE length | u8 codec (1=msgpack, 2=json) | body. Max 1 MiB."""
from __future__ import annotations

import asyncio
import json
import struct
from typing import Any

try:
    import msgpack  # type: ignore[import-not-found]
except ImportError:  # pragma: no cover
    msgpack = None

MAX_FRAME = 1 << 20
CODEC_MSGPACK, CODEC_JSON = 1, 2


class FrameError(ValueError):
    pass


def encode(obj: Any, *, prefer_msgpack: bool = True) -> bytes:
    if prefer_msgpack and msgpack is not None:
        codec, body = CODEC_MSGPACK, msgpack.packb(obj, use_bin_type=True)
    else:
        codec, body = CODEC_JSON, json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode()
    if len(body) + 1 > MAX_FRAME:
        raise FrameError("frame too large")
    return struct.pack("<IB", len(body) + 1, codec) + body


def decode_body(codec: int, body: bytes) -> Any:
    if codec == CODEC_MSGPACK:
        if msgpack is None:
            raise FrameError("msgpack frame but msgpack not installed")
        return msgpack.unpackb(body, raw=False)
    if codec == CODEC_JSON:
        return json.loads(body)
    raise FrameError(f"unknown codec {codec}")


async def read_frame(r: asyncio.StreamReader) -> Any:
    hdr = await r.readexactly(4)
    (n,) = struct.unpack("<I", hdr)
    if n < 1 or n > MAX_FRAME:
        raise FrameError(f"bad length {n}")
    data = await r.readexactly(n)
    return decode_body(data[0], data[1:])


async def write_frame(w: asyncio.StreamWriter, obj: Any) -> None:
    w.write(encode(obj))
    await w.drain()
