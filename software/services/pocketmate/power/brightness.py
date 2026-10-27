"""Auto-brightness (§10.4.3) and session backlight timeouts (§10.6)."""
from __future__ import annotations

import math
from dataclasses import dataclass

DEFAULT_PCT = 40
DIM_PCT = 10
DIM_AFTER_S = 5.0
OFF_AFTER_S = 10.0
TAU_UP_S = 2.0
TAU_DOWN_S = 5.0


@dataclass
class AutoBrightness:
    # a, b: curve coefficients. Placeholders until M5b calibration (lux_gain from SET_THERMAL_CAL).
    a: float = 25.0
    b: float = 15.0
    user_max: int = 100
    user_offset: float = 0.0
    lux_gain: float = 1.0
    value: float = DEFAULT_PCT
    _last_t: float | None = None

    def target(self, lux: float) -> float:
        lc = max(lux * self.lux_gain, 0.1)
        return min(max(self.a * math.log10(lc) + self.b + self.user_offset, 10.0), float(self.user_max))

    def update(self, t: float, lux: float, *, stage_cap: int = 100, stage_scale: float = 1.0) -> int:
        tgt = self.target(lux)
        if self._last_t is None:
            self.value = tgt
        else:
            dt = max(0.0, t - self._last_t)
            tau = TAU_UP_S if tgt > self.value else TAU_DOWN_S
            self.value += (tgt - self.value) * (1 - math.exp(-dt / tau))
        self._last_t = t
        out = self.value * stage_scale
        return int(round(min(out, stage_cap)))


def session_backlight(base_pct: int, idle_s: float, overlay_active: bool) -> int:
    """40 % default; 10 % after 5 s without touch; off after 10 s. Listening/processing overlays keep it on."""
    if overlay_active:
        return base_pct
    if idle_s >= OFF_AFTER_S:
        return 0
    if idle_s >= DIM_AFTER_S:
        return min(base_pct, DIM_PCT)
    return base_pct
