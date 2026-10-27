"""Skin-temperature governor, §10.4 (frozen limits v0.3.4) + §10.3b session accounting.

Pure logic: feed `update()` at ~1 Hz with sensor readings; apply the returned `Actions` through
`actuators.py`. Thresholds compare T_skin,hot = T_NTC + k_hs * P_avg (A-64)."""
from __future__ import annotations

import enum
import math
from dataclasses import dataclass, field

from ..mcu.messages import LightCase, ThermalStage

# --- frozen constants -------------------------------------------------------------
OFFSETS = {ThermalStage.WARN: 2.0, ThermalStage.SOFT: 1.2, ThermalStage.HARD: 0.5, ThermalStage.PROTECT: 0.0}
HYSTERESIS_K = 1.5
MIN_DWELL_S = 30.0
SOC_PROTECT_C = 80.0
NTC_FAULT_SOC_OFFSET = 25.0
K_HS_DEFAULT = 0.30          # K/W
TAU_HS_DEFAULT = 60.0        # s
HEAT_CAPACITY_J_PER_K = 205.0
CPU_MAX_KHZ = 2_400_000
CPU_UI_KHZ = 1_500_000
CPU_SOFT_FLOOR_KHZ = 1_000_000
CPU_MIN_KHZ = 500_000        # arm_freq_min=500 [A-54: verify CM5 min OPP]
SOFT_STEP_KHZ = 300_000
SOFT_STEP_K = 0.5
BACKLIGHT_FLOOR_PCT = 10

# §10.3b frozen sustained budgets (W) and time constants (s)
BUDGET_W = {LightCase.HELD: (1.85, 0.66), LightCase.TABLE: (1.08, 0.39), LightCase.POCKET: (0.64, 0.23)}
TAU_S = {LightCase.HELD: 830.0, LightCase.TABLE: 1464.0, LightCase.POCKET: 2500.0}


def t_lim(ta: float) -> float:
    return 43.0 if ta <= 40.0 else min(ta + 3.0, 48.0)


def threshold(stage: ThermalStage, ta: float) -> float:
    return t_lim(ta) - OFFSETS[stage]


def budget_w(case: LightCase, ta: float) -> float:
    """Linear interpolation between the 35 °C and 45 °C frozen budgets (clamped).
    UNKNOWN case uses POCKET (the conservative default)."""
    c = case if case in BUDGET_W else LightCase.POCKET
    b35, b45 = BUDGET_W[c]
    f = min(1.0, max(0.0, (ta - 35.0) / 10.0))
    return b35 + (b45 - b35) * f


class Reason(str, enum.Enum):
    NORMAL = "normal"
    NTC_FAULT = "ntc_fault"
    SOC_PROTECT = "soc_protect"
    BATTERY_SAVER = "battery_saver"


@dataclass
class ThermalInputs:
    t: float                         # monotonic seconds
    ntc_c: float | None              # case NTC; None = ADC fault
    soc_c: float                     # thermal_zone0
    p_dev_w: float                   # device power (gauge/INA226)
    ta_c: float = 25.0               # ambient estimate
    case: LightCase = LightCase.HELD
    battery_saver: bool = False


@dataclass
class Actions:
    stage: ThermalStage
    t_skin_hot: float
    allow_new_local_ai: bool
    local_ai_enabled: bool
    offer_cloud: bool
    defer_background: bool
    cpu_max_khz: int
    gpu_min: bool
    backlight_cap_pct: int           # absolute cap (0-100) applied on top of user/auto value
    backlight_scale: float           # multiplicative (Soft -30 %)
    llm_threads_max: int
    request_s4: bool
    reasons: list[Reason] = field(default_factory=list)


@dataclass
class Governor:
    k_hs: float = K_HS_DEFAULT
    tau_hs: float = TAU_HS_DEFAULT
    stage: ThermalStage = ThermalStage.NORMAL
    stage_since: float | None = None
    p_avg: float = 0.0
    _last_t: float | None = None

    def _filter_power(self, t: float, p: float) -> None:
        if self._last_t is None:
            self.p_avg = p
        else:
            dt = max(0.0, t - self._last_t)
            a = 1.0 - math.exp(-dt / self.tau_hs) if self.tau_hs > 0 else 1.0
            self.p_avg += (p - self.p_avg) * a
        self._last_t = t

    def raw_stage(self, temp: float, ta: float) -> ThermalStage:
        for st in (ThermalStage.PROTECT, ThermalStage.HARD, ThermalStage.SOFT, ThermalStage.WARN):
            if temp >= threshold(st, ta):
                return st
        return ThermalStage.NORMAL

    def update(self, x: ThermalInputs) -> Actions:
        self._filter_power(x.t, x.p_dev_w)
        reasons: list[Reason] = []
        if x.ntc_c is None:
            temp = x.soc_c - NTC_FAULT_SOC_OFFSET
            reasons.append(Reason.NTC_FAULT)
        else:
            temp = x.ntc_c + self.k_hs * self.p_avg
        target = self.raw_stage(temp, x.ta_c)
        if x.soc_c >= SOC_PROTECT_C:
            target = ThermalStage.PROTECT
            reasons.append(Reason.SOC_PROTECT)
        if self.stage_since is None:
            self.stage_since = x.t
        if target > self.stage:
            self.stage, self.stage_since = target, x.t          # escalate immediately
        elif target < self.stage and self.stage != ThermalStage.NORMAL:
            # release one stage at a time: T <= threshold(current) - 1.5 K and >= 30 s dwell
            if (temp <= threshold(self.stage, x.ta_c) - HYSTERESIS_K and x.t - self.stage_since >= MIN_DWELL_S
                    and Reason.SOC_PROTECT not in reasons):
                self.stage = ThermalStage(self.stage - 1)
                self.stage_since = x.t
        eff = self.stage
        if Reason.NTC_FAULT in reasons and eff < ThermalStage.WARN:
            eff = ThermalStage.WARN
        if x.battery_saver and eff < ThermalStage.WARN:
            eff = ThermalStage.WARN
            reasons.append(Reason.BATTERY_SAVER)
        return self._actions(eff, temp, x.ta_c, reasons or [Reason.NORMAL], ntc_fault=Reason.NTC_FAULT in reasons)

    def _actions(self, st: ThermalStage, temp: float, ta: float, reasons: list[Reason], ntc_fault: bool) -> Actions:
        cpu, scale, cap, threads = CPU_MAX_KHZ, 1.0, 100, 4
        if st == ThermalStage.SOFT:
            steps = 1 + int(max(0.0, temp - threshold(ThermalStage.SOFT, ta)) // SOFT_STEP_K)
            cpu = max(CPU_SOFT_FLOOR_KHZ, CPU_MAX_KHZ - steps * SOFT_STEP_KHZ)
            scale, threads = 0.70, 2
        elif st >= ThermalStage.HARD:
            cpu, cap, threads = CPU_MIN_KHZ, BACKLIGHT_FLOOR_PCT, 1
        return Actions(
            stage=st, t_skin_hot=temp,
            allow_new_local_ai=st == ThermalStage.NORMAL and not ntc_fault,
            local_ai_enabled=st < ThermalStage.HARD and not ntc_fault,
            offer_cloud=st >= ThermalStage.WARN,
            defer_background=st >= ThermalStage.WARN,
            cpu_max_khz=cpu, gpu_min=st >= ThermalStage.HARD,
            backlight_cap_pct=0 if st == ThermalStage.PROTECT else cap,
            backlight_scale=scale, llm_threads_max=threads,
            request_s4=st == ThermalStage.PROTECT, reasons=reasons)


def cooldown_gate_ok(ntc_c: float, ta: float) -> bool:
    """§10.3b / §10.4.4: no non-user wake (and MCU blocks power-on after Protect) until NTC < Warn - 1.5 K."""
    return ntc_c < threshold(ThermalStage.WARN, ta) - HYSTERESIS_K


@dataclass
class HeatBudget:
    """§10.3b: E_used = heat above the detected case's budget, decaying with that case's τ."""
    e_used_j: float = 0.0
    _last_t: float | None = None

    def update(self, t: float, p_w: float, case: LightCase, ta: float) -> float:
        if self._last_t is not None:
            dt = max(0.0, t - self._last_t)
            tau = TAU_S.get(case, TAU_S[LightCase.POCKET])
            self.e_used_j = max(0.0, self.e_used_j * math.exp(-dt / tau) + (p_w - budget_w(case, ta)) * dt)
        self._last_t = t
        return self.e_used_j

    def predict_ntc(self, ntc_now: float, p_job_w: float, duration_s: float, case: LightCase, ta: float) -> float:
        """Single-node prediction: the job's above-budget heat raises the case by ΔE / C."""
        extra = max(0.0, (p_job_w - budget_w(case, ta)) * duration_s)
        return ntc_now + extra / HEAT_CAPACITY_J_PER_K

    def admit(self, ntc_now: float, p_job_w: float, duration_s: float, case: LightCase, ta: float) -> bool:
        """Full-speed local AI only if the predicted NTC at job end stays below Warn."""
        return self.predict_ntc(ntc_now, p_job_w, duration_s, case, ta) < threshold(ThermalStage.WARN, ta)
