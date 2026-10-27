"""9 W system power cap at the cell (§10.5) with the MCU overcurrent fast path."""
from __future__ import annotations

from dataclasses import dataclass

CAP_W = 9.0
CELL_I_LIMIT_A = 3.0
LOW_V = 3.3
OC_STEP_A, OC_STEP_S = 2.7, 2.0
OC_S5_A, OC_S5_S = 3.2, 5.0

# Actuator ladder in §10.5 order: level 0 = unrestricted.
LADDER = (
    {"exclusive_heavy": False, "llm_threads": 4, "cpu_max_khz": 2_400_000, "backlight_scale": 1.0},
    {"exclusive_heavy": True, "llm_threads": 4, "cpu_max_khz": 2_400_000, "backlight_scale": 1.0},
    {"exclusive_heavy": True, "llm_threads": 2, "cpu_max_khz": 2_400_000, "backlight_scale": 1.0},
    {"exclusive_heavy": True, "llm_threads": 2, "cpu_max_khz": 1_800_000, "backlight_scale": 1.0},
    {"exclusive_heavy": True, "llm_threads": 2, "cpu_max_khz": 1_500_000, "backlight_scale": 1.0},
    {"exclusive_heavy": True, "llm_threads": 1, "cpu_max_khz": 1_000_000, "backlight_scale": 0.7},
)


def cap_w(v_cell: float) -> float:
    return CAP_W if v_cell >= LOW_V else min(CAP_W, 0.95 * CELL_I_LIMIT_A * v_cell)


@dataclass
class PowerCap:
    """Discrete step controller: >cap steps down immediately; <85 % cap for 5 s steps up."""
    level: int = 0
    _below_since: float | None = None

    def update(self, t: float, v_cell: float, i_cell_a: float, on_usb: bool = False) -> int:
        p = v_cell * max(0.0, i_cell_a)
        cap = cap_w(v_cell)
        if p > cap:
            self.level = min(self.level + 1, len(LADDER) - 1)
            self._below_since = None
        elif p < 0.85 * cap and self.level > 0:
            if self._below_since is None:
                self._below_since = t
            elif t - self._below_since >= 5.0:
                self.level -= 1
                self._below_since = t
        else:
            self._below_since = None
        return self.level

    def on_overcurrent(self, action: int) -> str:
        """EVT_OVERCURRENT: action 0 -> drop one stage now; 1 -> request S5."""
        if action == 1:
            return "S5"
        self.level = min(self.level + 1, len(LADDER) - 1)
        return "step"

    @property
    def settings(self) -> dict:
        return LADDER[self.level]
