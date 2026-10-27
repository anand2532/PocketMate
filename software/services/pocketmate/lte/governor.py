"""LTE power governor (ARCHITECTURE.md §19.5; hardware/power-config.md "Fix implemented" item 2).

Pure logic, fed at ~1 Hz by pm-power from MCU EVT_BATTERY (MAX17055 AvgVCell / AvgCurrent) and
EVT_OVERCURRENT. Decides whether LTE may transmit, must be throttled, must be blocked (airplane,
AT+CFUN=4) or shut down (AT+QPOWD then LTE_PWR_EN low), and whether 2G is permitted.

Measurement point (AMBIGUITY, documented in §19.5): the 5.5 A threshold is applied to the CELL
current measured by the MAX17055 across R18 (5 mOhm) at VBAT. That current INCLUDES the LTE board
(LTE_VBAT is taken from cell+ before the BATFET, and its return goes through R18). It is NOT the
BQ25895 VSYS/BATFET-path current, which excludes the LTE board. The steering request said
"system average current" without naming the node; power-config.md names "MAX17055 AvgCurrent", so the
cell/VBAT side is used. Set `current_point="vsys"` only if hardware decides otherwise (then the
throttle threshold must be re-derived because LTE current is no longer included).
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field


class Tx(str, enum.Enum):
    ALLOW = "allow"
    THROTTLE = "throttle"      # data-rate cap on the wwan interface + CPU cap (pm-power)
    BLOCK = "block"            # RF off: AT+CFUN=4 (airplane). Module stays powered (GNSS VERIFY)
    SHUTDOWN = "shutdown"      # AT+QPOWD, wait for STATUS/USB gone, LTE_PWR_EN low


class Rat(str, enum.Enum):
    LTE_ONLY = "lte"           # default: nwscanmode 3 on EC25 and EC200U
    LTE_GSM = "lte+gsm"        # only if allow_2g and V >= 2G floor and CM5 in "light" state


@dataclass(frozen=True)
class LteGovConfig:
    throttle_on_mA: int = 5500       # AvgCurrent above this for > hold_s -> THROTTLE
    throttle_off_mA: int = 4500      # release below this (power-config.md)
    hold_s: float = 1.0              # "for > 1 s"
    release_hold_s: float = 1.0      # [impl] same dwell on release to avoid chatter
    lte_floor_mV: int = 3550         # LTE TX allowed only at/above (LTE-only RAT)
    g2_floor_mV: int = 3750          # 2G TX allowed only at/above
    shutdown_mV: int = 3450          # below: AT+QPOWD then LTE_PWR_EN off
    hyst_mV: int = 50                # [impl] re-allow at floor + hyst
    allow_2g: bool = False           # LTE-only by default; 2G is opt-in
    current_point: str = "cell"      # "cell" (MAX17055 at VBAT, includes LTE) | "vsys" (see module doc)

    @classmethod
    def prototype_akyga(cls) -> LteGovConfig:
        """Akyga LP655063 (1C = 3 A) prototype cell: cap 2.5 A (power-config.md item 3)."""
        return cls(throttle_on_mA=2500, throttle_off_mA=2000)

    def validate(self) -> None:
        if not (self.throttle_off_mA < self.throttle_on_mA):
            raise ValueError("throttle_off_mA must be below throttle_on_mA")
        if not (self.shutdown_mV < self.lte_floor_mV <= self.g2_floor_mV):
            raise ValueError("need shutdown_mV < lte_floor_mV <= g2_floor_mV")
        if self.current_point not in ("cell", "vsys"):
            raise ValueError("current_point must be 'cell' or 'vsys'")


@dataclass(frozen=True)
class LteInputs:
    t: float                       # monotonic seconds
    cell_mV: int                   # MAX17055 AvgVCell
    discharge_mA: int              # positive = discharging (pm-power converts the gauge sign)
    cm5_light: bool = False        # CM5 in its "light" load state (no local AI running)
    overcurrent_evt: bool = False  # MCU EVT_OVERCURRENT seen since the last update


@dataclass(frozen=True)
class LteDecision:
    tx: Tx
    rat: Rat
    throttled: bool
    reasons: tuple[str, ...]


@dataclass
class LteGovernor:
    cfg: LteGovConfig = field(default_factory=LteGovConfig)
    _throttled: bool = False
    _over_since: float | None = None
    _under_since: float | None = None
    _blocked: bool = False
    _shutdown: bool = False
    _g2_ok: bool = False

    def __post_init__(self) -> None:
        self.cfg.validate()

    def update(self, x: LteInputs) -> LteDecision:
        c = self.cfg
        reasons: list[str] = []
        # --- current throttle (with dwell on both edges) ---
        if x.overcurrent_evt:
            self._throttled, self._under_since = True, None
            reasons.append("mcu_overcurrent")
        if x.discharge_mA > c.throttle_on_mA:
            self._under_since = None
            if self._over_since is None:
                self._over_since = x.t
            if x.t - self._over_since >= c.hold_s:
                self._throttled = True
        else:
            self._over_since = None
        if self._throttled and x.discharge_mA < c.throttle_off_mA and not x.overcurrent_evt:
            if self._under_since is None:
                self._under_since = x.t
            if x.t - self._under_since >= c.release_hold_s:
                self._throttled, self._under_since = False, None
        elif x.discharge_mA >= c.throttle_off_mA:
            self._under_since = None
        if self._throttled:
            reasons.append(f"avg_current>{c.throttle_on_mA}mA@{c.current_point}")
        # --- voltage floors (latched, released at floor + hysteresis) ---
        if x.cell_mV < c.shutdown_mV:
            self._shutdown = True
        elif self._shutdown and x.cell_mV >= c.lte_floor_mV + c.hyst_mV:
            self._shutdown = False
        if x.cell_mV < c.lte_floor_mV:
            self._blocked = True
        elif self._blocked and x.cell_mV >= c.lte_floor_mV + c.hyst_mV:
            self._blocked = False
        if x.cell_mV < c.g2_floor_mV:
            self._g2_ok = False
        elif x.cell_mV >= c.g2_floor_mV + c.hyst_mV:
            self._g2_ok = True
        # --- decision ---
        if self._shutdown:
            tx = Tx.SHUTDOWN
            reasons.append(f"vcell<{c.shutdown_mV}mV")
        elif self._blocked:
            tx = Tx.BLOCK
            reasons.append(f"vcell<{c.lte_floor_mV}mV_lte_floor")
        elif self._throttled:
            tx = Tx.THROTTLE
        else:
            tx = Tx.ALLOW
        g2 = (c.allow_2g and self._g2_ok and x.cm5_light and not self._throttled and tx == Tx.ALLOW)
        if c.allow_2g and not g2:
            reasons.append("2g_denied")
        return LteDecision(tx, Rat.LTE_GSM if g2 else Rat.LTE_ONLY, self._throttled, tuple(reasons))


def gauge_to_discharge_mA(gauge_mA: int) -> int:
    """MAX17055 Current/AvgCurrent: positive = charging, negative = discharging (MAX17055 datasheet,
    'Current Register'). VERIFY the MCU passes the sign through unchanged in EVT_BATTERY.mA."""
    return -gauge_mA
