"""Reference model of the MCU microphone interlock (§12 'Microphone power control', P3/P5).

This is the executable spec that firmware/src/privacy.c mirrors; firmware host tests and
tests/test_privacy_model.py check the same scenarios.

Signals: PA11 MIC_PWR_EN (output, drives U14 TPS22917 ON), PA10 MUTE_STATUS (input, high = muted,
pulled up to CM5_3V3 by R9, so it is only *valid* while CM5 power-good), PA1 ACTION button.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .messages import MicMode, MicRailReason, Status

TAP_WINDOW_MS = 1000
CAP_HOLD_S = 120
CAP_DICTATION_S = 600
LINK_LOSS_MS = 2000
HEARTBEAT_LOSS_MS = 30000


@dataclass
class PrivacyInterlock:
    now_ms: int = 0
    mic_pwr_en: bool = False            # PA11 (configured LOW first thing at boot)
    action_held: bool = False
    last_action_press_ms: int | None = None
    power_good: bool = False
    muted_pin: bool = True              # PA10 raw level (high = muted)
    session_id: int = 0
    mode: MicMode = MicMode.HOLD
    deadline_ms: int = 0
    last_rx_ms: int = 0
    last_hb_ms: int = 0
    events: list[tuple[bool, MicRailReason, int]] = field(default_factory=list)

    # -- derived -------------------------------------------------------------
    @property
    def mute_valid(self) -> bool:
        return self.power_good           # R9 pull-up is on CM5_3V3

    @property
    def effectively_muted(self) -> bool:
        return self.muted_pin or not self.mute_valid

    # -- outputs -------------------------------------------------------------
    def _off(self, reason: MicRailReason) -> None:
        if self.mic_pwr_en:
            self.mic_pwr_en = False
            self.events.append((False, reason, self.session_id))

    # -- inputs --------------------------------------------------------------
    def boot(self) -> None:
        self.mic_pwr_en = False
        self.events.append((False, MicRailReason.RESET, 0))

    def on_frame_rx(self) -> None:
        self.last_rx_ms = self.now_ms

    def on_heartbeat(self) -> None:
        self.last_hb_ms = self.now_ms
        self.last_rx_ms = self.now_ms

    def on_action(self, down: bool) -> None:
        self.action_held = down
        if down:
            self.last_action_press_ms = self.now_ms
        elif self.mic_pwr_en and self.mode == MicMode.HOLD:
            self._off(MicRailReason.RELEASE)

    def on_mute_pin(self, level_high: bool) -> None:
        self.muted_pin = level_high
        if level_high:
            self._off(MicRailReason.MUTE)   # EXTI edge, before any other work

    def on_power_good(self, pg: bool) -> None:
        self.power_good = pg
        if not pg:
            self._off(MicRailReason.POWER_DOWN)

    def on_shutdown_ready(self) -> None:
        self._off(MicRailReason.POWER_DOWN)

    def on_cm5_run_reset(self) -> None:
        self._off(MicRailReason.POWER_DOWN)

    def on_wdt(self) -> None:
        self._off(MicRailReason.WDT)

    def mic_enable(self, on: bool, session_id: int, mode: int, max_s: int) -> Status:
        self.on_frame_rx()
        if not on:
            self._off(MicRailReason.OFF_CMD)
            return Status.OK
        if not self.mute_valid:
            return Status.MUTE_INVALID
        if self.muted_pin:
            return Status.MUTED
        if not self.power_good:
            return Status.NOT_POWER_GOOD
        try:
            m = MicMode(mode)
        except ValueError:
            return Status.RANGE
        cap = CAP_DICTATION_S if m == MicMode.DICTATION else CAP_HOLD_S
        if max_s == 0:
            max_s = cap
        if max_s > cap:
            return Status.RANGE
        if m == MicMode.HOLD:
            if not self.action_held:
                return Status.NO_PTT
        else:
            p = self.last_action_press_ms
            if p is None or self.now_ms - p > TAP_WINDOW_MS:
                return Status.NO_PTT
            self.last_action_press_ms = None     # one press -> at most one tap session
        self.session_id, self.mode = session_id, m
        self.deadline_ms = self.now_ms + max_s * 1000
        if not self.mic_pwr_en:
            self.mic_pwr_en = True
            self.events.append((True, MicRailReason.REQUEST, session_id))
        return Status.OK

    def tick(self, now_ms: int) -> None:
        self.now_ms = now_ms
        if not self.mic_pwr_en:
            return
        if self.effectively_muted:
            self._off(MicRailReason.MUTE)
        elif now_ms >= self.deadline_ms:
            self._off(MicRailReason.TIMEOUT)
        elif now_ms - self.last_rx_ms > LINK_LOSS_MS:
            self._off(MicRailReason.LINK_LOSS)
        elif now_ms - self.last_hb_ms > HEARTBEAT_LOSS_MS:
            self._off(MicRailReason.LINK_LOSS)
