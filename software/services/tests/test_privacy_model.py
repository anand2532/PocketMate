from pocketmate.mcu.messages import MicMode, MicRailReason, Status
from pocketmate.mcu.privacy_model import PrivacyInterlock


def mk():
    p = PrivacyInterlock()
    p.boot()
    p.power_good, p.muted_pin = True, False
    p.events.clear()
    return p


def test_boot_rail_off_and_muted_default():
    p = PrivacyInterlock()
    p.boot()
    assert not p.mic_pwr_en and p.effectively_muted


def test_nak_priority():
    p = PrivacyInterlock()
    p.boot()
    p.power_good = False
    p.muted_pin = True
    assert p.mic_enable(True, 1, MicMode.HOLD, 0) == Status.MUTE_INVALID
    p.power_good = True
    assert p.mic_enable(True, 1, MicMode.HOLD, 0) == Status.MUTED
    p.muted_pin = False
    assert p.mic_enable(True, 1, MicMode.HOLD, 999) == Status.RANGE
    assert p.mic_enable(True, 1, MicMode.HOLD, 0) == Status.NO_PTT


def test_hold_mode_release_turns_off():
    p = mk()
    p.on_action(True)
    assert p.mic_enable(True, 5, MicMode.HOLD, 0) == Status.OK and p.mic_pwr_en
    p.on_action(False)
    assert not p.mic_pwr_en and p.events[-1][1] == MicRailReason.RELEASE


def test_tap_window_single_use():
    p = mk()
    p.now_ms = 1000
    p.on_action(True); p.on_action(False)
    p.now_ms = 1900
    assert p.mic_enable(True, 1, MicMode.TAP, 0) == Status.OK
    p.mic_enable(False, 1, MicMode.TAP, 0)
    assert p.mic_enable(True, 2, MicMode.TAP, 0) == Status.NO_PTT   # press consumed


def test_tap_window_expires():
    p = mk()
    p.now_ms = 0
    p.on_action(True); p.on_action(False)
    p.now_ms = 1001
    assert p.mic_enable(True, 1, MicMode.TAP, 0) == Status.NO_PTT


def test_caps_and_timeout():
    p = mk()
    p.on_action(True)
    assert p.mic_enable(True, 1, MicMode.HOLD, 121) == Status.RANGE
    assert p.mic_enable(True, 1, MicMode.HOLD, 0) == Status.OK
    p.on_heartbeat()
    for t in range(0, 121_000, 1000):
        p.on_frame_rx(); p.on_heartbeat(); p.tick(t)
    assert not p.mic_pwr_en and p.events[-1][1] == MicRailReason.TIMEOUT


def test_mute_cuts_rail_and_power_good_loss():
    p = mk()
    p.on_action(True)
    p.mic_enable(True, 1, MicMode.HOLD, 0)
    p.on_mute_pin(True)
    assert not p.mic_pwr_en and p.events[-1][1] == MicRailReason.MUTE
    p.on_mute_pin(False)
    p.mic_enable(True, 2, MicMode.HOLD, 0)
    p.on_power_good(False)
    assert not p.mic_pwr_en


def test_link_loss():
    p = mk()
    p.on_action(True)
    p.mic_enable(True, 1, MicMode.HOLD, 0)
    p.tick(2001)
    assert not p.mic_pwr_en and p.events[-1][1] == MicRailReason.LINK_LOSS
