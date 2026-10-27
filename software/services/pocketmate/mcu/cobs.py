"""Consistent Overhead Byte Stuffing (Cheshire & Baker). The 0x00 byte is the frame delimiter."""
from __future__ import annotations


class COBSDecodeError(ValueError):
    pass


def encode(data: bytes) -> bytes:
    out = bytearray()
    code_idx = 0
    out.append(0)
    code = 1
    for b in data:
        if b == 0:
            out[code_idx] = code
            code_idx = len(out)
            out.append(0)
            code = 1
        else:
            out.append(b)
            code += 1
            if code == 0xFF:
                out[code_idx] = code
                code_idx = len(out)
                out.append(0)
                code = 1
    out[code_idx] = code
    return bytes(out)


def decode(data: bytes) -> bytes:
    out = bytearray()
    i = 0
    n = len(data)
    while i < n:
        code = data[i]
        if code == 0:
            raise COBSDecodeError("zero byte inside COBS block")
        i += 1
        end = i + code - 1
        if end > n:
            raise COBSDecodeError("truncated COBS block")
        chunk = data[i:end]
        if 0 in chunk:
            raise COBSDecodeError("zero byte inside COBS block")
        out += chunk
        i = end
        if code != 0xFF and i < n:
            out.append(0)
    return bytes(out)
