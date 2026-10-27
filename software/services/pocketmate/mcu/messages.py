"""Message catalogue for the CM5<->MCU link (§11). All multi-byte fields are little-endian.

Wire frame (before COBS):  ver u8 | type u8 | seq u8 | len u8 | payload[len<=64] | crc16 u16 (LE)
The CRC covers ver..payload. On the wire: 0x00 preamble, >=2 ms gap, COBS(frame), 0x00.

Items marked [v0.4.0] are clarifications this implementation adds to §11 (§11 lists
names/fields but no ACK type id, field widths or enum codes). They are recorded in the
ARCHITECTURE.md v0.4.0 changelog.
"""
from __future__ import annotations

import enum
import struct
from dataclasses import dataclass, field

PROTO_VER = 1
MAX_PAYLOAD = 64
BAUD = 115200
ACK_TIMEOUT_S = 0.050
MAX_RETRIES = 3
HEARTBEAT_PERIOD_S = 5.0
HEARTBEAT_MISS_RESET_S = 30.0
PREAMBLE_GAP_S = 0.002


class Dir(enum.Enum):
    CM5_TO_MCU = "cm5->mcu"
    MCU_TO_CM5 = "mcu->cm5"
    BOTH = "both"


class Status(enum.IntEnum):
    """ACK status byte. 0 = ACK, anything else is a NAK reason (§11 'muted|no_ptt|timeout|cm5_down|range')."""
    OK = 0
    MUTED = 1
    NO_PTT = 2
    TIMEOUT = 3
    CM5_DOWN = 4
    RANGE = 5
    BAD_LEN = 6          # [v0.4.0]
    UNKNOWN_TYPE = 7     # [v0.4.0]
    BUSY = 8             # [v0.4.0]
    MUTE_INVALID = 9     # [v0.4.0] PA10 status not valid (mute rail/pull-up fault) -> treated as muted
    NOT_POWER_GOOD = 10  # [v0.4.0]
    BAD_VERSION = 11     # [v0.4.0]


class PowerState(enum.IntEnum):
    S0 = 0
    S1 = 1
    S2 = 2
    S3 = 3
    S4 = 4
    S5 = 5
    SHIP = 6


class MicMode(enum.IntEnum):
    HOLD = 0
    TAP = 1
    DICTATION = 2   # tap mode with the 600 s cap (P5)


class ButtonId(enum.IntEnum):
    PWR = 0
    ACTION = 1
    VOL_UP = 2
    VOL_DOWN = 3


class ButtonAction(enum.IntEnum):
    DOWN = 0
    UP = 1
    SHORT = 2
    LONG = 3
    DOUBLE = 4
    REPEAT = 5


class MicRailReason(enum.IntEnum):
    REQUEST = 0
    RELEASE = 1
    TIMEOUT = 2
    MUTE = 3
    LINK_LOSS = 4
    WDT = 5
    POWER_DOWN = 6
    OFF_CMD = 7      # [v0.4.0] MIC_ENABLE{on=0}
    RESET = 8        # [v0.4.0] MCU reset / boot


class BootReason(enum.IntEnum):
    POR = 0
    PWR_BUTTON = 1
    RTC_ALARM = 2
    USB_IN = 3
    WDT = 4
    BROWNOUT = 5
    ACTION_BUTTON = 6
    SOFTWARE = 7


class ThermalStage(enum.IntEnum):
    NORMAL = 0
    WARN = 1
    SOFT = 2
    HARD = 3
    PROTECT = 4


class LightCase(enum.IntEnum):
    UNKNOWN = 0
    HELD = 1
    TABLE = 2
    POCKET = 3


@dataclass(frozen=True)
class MsgDef:
    name: str
    type_id: int
    direction: Dir
    fmt: str                 # struct format without '<'
    fields: tuple[str, ...]
    var_tail: str | None = None   # name of a trailing bytes field (variable length)
    doc: str = ""

    @property
    def fixed_len(self) -> int:
        return struct.calcsize("<" + self.fmt)


C = Dir.CM5_TO_MCU
M = Dir.MCU_TO_CM5
B = Dir.BOTH

MESSAGES: tuple[MsgDef, ...] = (
    MsgDef("HELLO", 0x01, C, "BI", ("proto_ver", "cm5_fw_ver"), doc="cm5_fw_ver = major<<16|minor<<8|patch"),
    MsgDef("HELLO_ACK", 0x02, M, "BIBBH", ("proto_ver", "mcu_fw_ver", "boot_reason", "flags", "e_used_J"),
           doc="flags: b0 ptt_latched, b1 muted, b2 mute_valid, b3 recovery_requested, b4 protect_active; e_used_J per §10.3b"),
    MsgDef("ACK", 0x03, B, "BB", ("acked_seq", "status"), var_tail="data",
           doc="[v0.4.0] Reply to every command (and every MCU event). status=Status. Optional data (e.g. GET_TIME epoch)."),
    MsgDef("SET_STATE", 0x10, C, "B", ("state",)),
    MsgDef("HEARTBEAT", 0x11, C, "IB", ("uptime_s", "cm5_state")),
    MsgDef("SET_WAKE", 0x12, C, "I", ("epoch_s",), doc="0 clears the alarm"),
    MsgDef("TIME", 0x13, C, "", (), var_tail="epoch",
           doc="SET/GET_TIME: len 4 = set (u32 epoch_s), len 0 = get (epoch returned in ACK.data)"),
    MsgDef("MIC_ENABLE", 0x14, C, "BHBH", ("on", "session_id", "mode", "max_s")),
    MsgDef("LED", 0x15, C, "BB", ("pattern", "brightness")),
    MsgDef("HAPTIC", 0x16, C, "B", ("pattern",)),
    MsgDef("SHUTDOWN_READY", 0x17, C, "", ()),
    MsgDef("BOOT_MODE", 0x18, C, "B", ("mode",), doc="0 normal, 1 recovery"),
    MsgDef("WDT_CFG", 0x19, C, "H", ("timeout_s",)),
    MsgDef("FW_UPDATE", 0x1A, C, "B", ("sub",), var_tail="data",
           doc="sub 0 begin{size u32, slot u8}, 1 chunk{offset u32, data<=56}, 2 sig_lo[32], 3 sig_hi[32], 4 commit"),
    MsgDef("HAPTIC_CFG", 0x1B, C, "BB", ("present", "library")),
    MsgDef("SET_POWER_CAP", 0x1C, C, "HB", ("cap_mW", "fast_window_s")),
    MsgDef("EVT_BUTTON", 0x20, M, "BBIB", ("id", "action", "t_ms", "woke")),
    MsgDef("EVT_BATTERY", 0x21, M, "BHhhB", ("soc", "mV", "mA", "temp_dC", "chg")),
    MsgDef("EVT_POWER_SRC", 0x22, M, "BBB", ("usb", "chg_status", "chg_fault")),
    MsgDef("EVT_MIC_MUTE", 0x23, M, "BBI", ("muted", "valid", "t_ms")),
    MsgDef("EVT_RTC_ALARM", 0x24, M, "I", ("epoch_s",)),
    MsgDef("EVT_SHUTDOWN_REQ", 0x25, M, "BB", ("reason", "deadline_s")),
    MsgDef("EVT_THERMAL", 0x26, M, "hhhBBH",
           ("case_ntc_dC", "cell_dC", "ambient_dC_est", "stage", "adc_fault", "lux")),
    MsgDef("EVT_CHARGE_INHIBIT", 0x27, M, "BBh", ("inhibited", "reason", "cell_dC"),
           doc="reason: 0 none, 1 cold, 2 hot, 3 ntc_fault, 4 sensor_disagree, 5 protect"),
    MsgDef("EVT_OVERCURRENT", 0x28, M, "HHB", ("cell_mA", "duration_ms", "action"),
           doc="action: 0 drop one stage, 1 request S5"),
    MsgDef("SET_THERMAL_CAL", 0x29, C, "HHbHH",
           ("k_hs_mK_per_W", "tau_hs_s", "ntc_offset_dC", "lux_gain_q8", "p_avg_mW")),
    MsgDef("EVT_LIGHT", 0x2A, M, "BHB", ("case", "lux", "valid")),
    MsgDef("EVT_MIC_RAIL", 0x2B, M, "BBH", ("on", "reason", "session_id")),
    MsgDef("SET_CHARGE_CFG", 0x2C, C, "IHIIhhhhhB",
           ("ntc_r25", "beta", "rt1", "rt2", "cold_off_dC", "cold_on_dC", "hot_on_dC", "hot_off_dC",
            "derate_dC", "beta_measured")),
    MsgDef("LTE_CFG", 0x2D, C, "BH", ("present", "vreg_max_mV"),
           doc="[impl v0.4.0] LTE board fitted -> MCU clamps BQ25895 VREG to vreg_max_mV (<= 4240). MCU assumes "
               "present=1 until told otherwise (fail-safe)"),
    MsgDef("EVT_FAULT", 0x2F, M, "H", ("code",)),
)

BY_NAME: dict[str, MsgDef] = {m.name: m for m in MESSAGES}
BY_ID: dict[int, MsgDef] = {m.type_id: m for m in MESSAGES}
assert len(BY_ID) == len(MESSAGES), "duplicate type id"
for _m in MESSAGES:
    assert _m.fixed_len <= MAX_PAYLOAD, _m.name


@dataclass
class Message:
    name: str
    fields: dict[str, int] = field(default_factory=dict)
    tail: bytes = b""

    @property
    def defn(self) -> MsgDef:
        return BY_NAME[self.name]

    def pack_payload(self) -> bytes:
        d = self.defn
        vals = [self.fields[f] for f in d.fields]
        p = struct.pack("<" + d.fmt, *vals) + (self.tail if d.var_tail else b"")
        if len(p) > MAX_PAYLOAD:
            raise ValueError(f"{self.name}: payload {len(p)} > {MAX_PAYLOAD}")
        return p

    @classmethod
    def unpack(cls, type_id: int, payload: bytes) -> Message:
        d = BY_ID.get(type_id)
        if d is None:
            raise KeyError(f"unknown type 0x{type_id:02x}")
        n = d.fixed_len
        if len(payload) < n or (len(payload) != n and d.var_tail is None):
            raise ValueError(f"{d.name}: bad length {len(payload)} (want {n})")
        vals = struct.unpack("<" + d.fmt, payload[:n]) if n else ()
        return cls(d.name, dict(zip(d.fields, vals, strict=True)), payload[n:])


def msg(name: str, tail: bytes = b"", **fields: int) -> Message:
    d = BY_NAME[name]
    missing = set(d.fields) - set(fields)
    if missing:
        raise TypeError(f"{name}: missing {sorted(missing)}")
    return Message(name, dict(fields), tail)
