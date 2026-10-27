"""Held / table / pocket detection (§10.4.3) from VEML7700 lux (via MCU), display and input state."""
from __future__ import annotations

from dataclasses import dataclass

from ..mcu.messages import LightCase

DARK_ENTER_LX = 3.0
DARK_EXIT_LX = 10.0
DEBOUNCE_S = 5.0
INPUT_RECENT_S = 30.0
NIGHT_START_H = 21
NIGHT_END_H = 7
HEAT_RISE_RATIO = 1.30


@dataclass
class CaseDetector:
    dark: bool = False
    _pending: bool | None = None
    _pending_since: float = 0.0

    def _update_dark(self, t: float, lux: float) -> None:
        want = self.dark
        if not self.dark and lux < DARK_ENTER_LX:
            want = True
        elif self.dark and lux > DARK_EXIT_LX:
            want = False
        if want == self.dark:
            self._pending = None
            return
        if self._pending != want:
            self._pending, self._pending_since = want, t
        elif t - self._pending_since >= DEBOUNCE_S:
            self.dark, self._pending = want, None

    def update(self, t: float, lux: float | None, display_on: bool, last_input_t: float | None,
               local_hour: int, heat_rise_ratio: float | None = None) -> LightCase:
        recent_input = last_input_t is not None and t - last_input_t < INPUT_RECENT_S
        if lux is not None:
            self._update_dark(t, lux)
        if display_on and recent_input:
            return LightCase.HELD                       # dark-room guard: active use is never pocket
        if lux is None:
            return LightCase.POCKET if not display_on else LightCase.TABLE
        if self.dark and (not display_on or not recent_input):
            night = local_hour >= NIGHT_START_H or local_hour < NIGHT_END_H
            if night and not display_on and not (heat_rise_ratio is not None and heat_rise_ratio > HEAT_RISE_RATIO):
                return LightCase.TABLE                  # nightstand
            return LightCase.POCKET
        return LightCase.TABLE
