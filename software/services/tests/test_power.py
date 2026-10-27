import pytest

from pocketmate.mcu.messages import LightCase
from pocketmate.mcu.messages import ThermalStage as S
from pocketmate.power.actuators import Backlight, CpuControl, Rfkill, Sysfs
from pocketmate.power.brightness import AutoBrightness, session_backlight
from pocketmate.power.case_detect import CaseDetector
from pocketmate.power.governor import (
    Governor,
    HeatBudget,
    ThermalInputs,
    budget_w,
    cooldown_gate_ok,
    threshold,
)
from pocketmate.power.powercap import LADDER, PowerCap, cap_w
from pocketmate.power.radio import REBLOCK_AFTER_S, RadioLeaseManager


def inp(t, ntc, soc=50.0, **kw):
    return ThermalInputs(t=t, ntc_c=ntc, soc_c=soc, p_dev_w=0.0, **kw)


def test_thresholds_frozen():
    assert threshold(S.WARN, 25) == 41.0 and threshold(S.PROTECT, 25) == 43.0
    assert threshold(S.PROTECT, 44) == 47.0 and threshold(S.PROTECT, 46) == 48.0


def test_escalate_immediately_release_with_hysteresis_and_dwell():
    g = Governor(k_hs=0)
    assert g.update(inp(0, 30)).stage == S.NORMAL
    assert g.update(inp(1, 42.6)).stage == S.HARD
    assert g.update(inp(5, 30)).stage == S.HARD          # dwell < 30 s
    assert g.update(inp(32, 41.5)).stage == S.HARD       # not ≤ thr(HARD)-1.5 = 41.0
    assert g.update(inp(33, 40.9)).stage == S.SOFT       # one stage at a time
    assert g.update(inp(34, 30)).stage == S.SOFT
    assert g.update(inp(64, 30)).stage == S.WARN


def test_soft_steps_and_hard_actions():
    g = Governor(k_hs=0)
    a = g.update(inp(0, 41.8))
    assert a.stage == S.SOFT and a.cpu_max_khz == 2_100_000 and a.llm_threads_max == 2 and a.backlight_scale == 0.7
    a = g.update(inp(1, 42.3))
    assert a.cpu_max_khz == 1_800_000
    a = g.update(inp(2, 42.5))
    assert a.stage == S.HARD and a.cpu_max_khz == 500_000 and a.backlight_cap_pct == 10 and not a.local_ai_enabled
    a = g.update(inp(3, 43.0))
    assert a.request_s4 and a.backlight_cap_pct == 0


def test_ntc_fault_and_soc_protect_and_saver():
    a = Governor(k_hs=0).update(inp(0, None, soc=60))
    assert a.stage == S.WARN and not a.allow_new_local_ai
    assert Governor(k_hs=0).update(inp(0, 30, soc=80)).stage == S.PROTECT
    assert Governor(k_hs=0).update(inp(0, 30, battery_saver=True)).stage == S.WARN


def test_skin_hot_includes_power_term():
    g = Governor(k_hs=0.3)
    a = g.update(ThermalInputs(0, 40.0, 50.0, 4.0))
    assert a.t_skin_hot == pytest.approx(41.2) and a.stage == S.WARN


def test_budget_and_heatbudget_admission():
    assert budget_w(LightCase.HELD, 35) == pytest.approx(1.85)
    assert budget_w(LightCase.HELD, 40) == pytest.approx((1.85 + 0.66) / 2)
    assert budget_w(LightCase.UNKNOWN, 35) == budget_w(LightCase.POCKET, 35)
    hb = HeatBudget()
    assert hb.admit(35.0, 5.0, 60, LightCase.HELD, 25)
    assert not hb.admit(40.5, 5.0, 60, LightCase.HELD, 25)
    hb.update(0, 5.0, LightCase.HELD, 25)
    assert hb.update(10, 5.0, LightCase.HELD, 25) > 30
    assert cooldown_gate_ok(39.4, 25) and not cooldown_gate_ok(39.6, 25)


def test_case_detector():
    c = CaseDetector()
    assert c.update(0, 200, True, 0, 12) == LightCase.HELD
    assert c.update(100, 200, False, None, 12) == LightCase.TABLE
    for t in range(100, 110):
        r = c.update(t, 1, False, None, 12)
    assert r == LightCase.POCKET
    assert c.update(111, 1, False, None, 23) == LightCase.TABLE       # nightstand
    assert c.update(112, 1, False, None, 23, heat_rise_ratio=1.5) == LightCase.POCKET
    assert c.update(113, 1, True, 112, 23) == LightCase.HELD           # active use never pocket


def test_brightness():
    b = AutoBrightness()
    assert b.update(0, 1000) == 90
    assert b.update(1, 1000, stage_cap=10) == 10
    assert session_backlight(40, 0, False) == 40 and session_backlight(40, 6, False) == 10
    assert session_backlight(40, 11, False) == 0 and session_backlight(40, 11, True) == 40


def test_powercap_ladder():
    pc = PowerCap()
    assert cap_w(3.8) == 9.0 and cap_w(3.0) == pytest.approx(8.55)
    assert pc.update(0, 3.8, 3.0) == 1
    assert pc.update(1, 3.8, 3.0) == 2
    pc.update(2, 3.8, 1.0)
    assert pc.update(7.1, 3.8, 1.0) == 1
    for _ in range(10):
        pc.on_overcurrent(0)
    assert pc.level == len(LADDER) - 1 and pc.on_overcurrent(1) == "S5"


def test_radio_lease_reblock():
    calls, now = [], [0.0]
    m = RadioLeaseManager(lambda r, b: calls.append((r, b)), lambda: now[0])
    a = m.acquire("wlan", "cloud")
    b = m.acquire("wlan", "update")
    assert calls == [("wlan", False)]
    m.release(a); m.release(b)
    now[0] = REBLOCK_AFTER_S - 1; m.tick()
    assert calls[-1] == ("wlan", False)
    now[0] = REBLOCK_AFTER_S + 0.1; m.tick()
    assert calls[-1] == ("wlan", True)
    with pytest.raises(ValueError):
        m.acquire("wlan", "telemetry")


def test_sysfs_actuators(tmp_path):
    fs = Sysfs(tmp_path)
    for n in range(4):
        d = tmp_path / f"sys/devices/system/cpu/cpu{n}/cpufreq"
        d.mkdir(parents=True)
        (d / "scaling_max_freq").write_text("2400000")
        (d.parent / "online").write_text("1")
    bl = tmp_path / "sys/class/backlight/panel"
    bl.mkdir(parents=True)
    (bl / "max_brightness").write_text("255")
    (bl / "brightness").write_text("0")
    rf = tmp_path / "sys/class/rfkill/rfkill0"
    rf.mkdir(parents=True)
    (rf / "type").write_text("wlan\n")
    (rf / "soft").write_text("0")
    CpuControl(fs).set_max_khz(1_000_000)
    assert (tmp_path / "sys/devices/system/cpu/cpu3/cpufreq/scaling_max_freq").read_text().strip() == "1000000"
    Backlight(fs).set_pct(50)
    assert int((bl / "brightness").read_text()) in (127, 128)
    r = Rfkill(fs)
    assert r.set_blocked("wlan", True) == 1 and r.blocked("wlan") is True
