import random

import pytest

from pocketmate.mcu import cobs
from pocketmate.mcu.crc import crc16_ccitt
from pocketmate.mcu.frame import Deframer, Frame, FrameError, decode_raw
from pocketmate.mcu.messages import BY_NAME, msg


def test_crc_check_value():
    assert crc16_ccitt(b"123456789") == 0x29B1
    assert crc16_ccitt(b"") == 0xFFFF


@pytest.mark.parametrize("data", [b"", b"\x00", b"\x00\x00", b"\x11\x22\x00\x33", bytes(range(1, 255)),
                                  bytes(range(256)), b"\x01" * 600])
def test_cobs_roundtrip(data):
    enc = cobs.encode(data)
    assert b"\x00" not in enc
    assert cobs.decode(enc) == data


def test_cobs_fuzz():
    rnd = random.Random(1)
    for _ in range(500):
        d = bytes(rnd.randrange(256) for _ in range(rnd.randrange(0, 80)))
        assert cobs.decode(cobs.encode(d)) == d


def test_frame_roundtrip_all_messages():
    for name, d in BY_NAME.items():
        fields = {f: 0 for f in d.fields}
        f = Frame.from_message(msg(name, **fields), 7)
        enc = f.encode()
        assert enc.endswith(b"\x00") and enc.count(b"\x00") == 1
        out = Deframer().feed(b"\x00" + enc)
        assert len(out) == 1 and out[0].message().name == name and out[0].seq == 7


def test_frame_rejects_bad_crc():
    raw = bytearray(Frame.from_message(msg("HEARTBEAT", uptime_s=5, cm5_state=1), 1).raw())
    raw[-1] ^= 0xFF
    with pytest.raises(FrameError):
        decode_raw(bytes(raw))


def test_deframer_split_and_garbage():
    a = Frame.from_message(msg("HEARTBEAT", uptime_s=1, cm5_state=0), 1).encode()
    b = Frame.from_message(msg("SET_WAKE", epoch_s=123), 2).encode()
    stream = b"\x55\x66\x00" + a + b
    d = Deframer()
    got = []
    for i in range(0, len(stream), 3):
        got += d.feed(stream[i:i + 3])
    assert [f.seq for f in got] == [1, 2]
