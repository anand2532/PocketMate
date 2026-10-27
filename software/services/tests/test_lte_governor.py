import pytest

from pocketmate.lte.at import AtClient, apply_profile
from pocketmate.lte.governor import LteGovConfig, LteGovernor, LteInputs, Rat, Tx, gauge_to_discharge_mA
from pocketmate.lte.quectel import EC25, EC200U, RAT_CMD, by_usb_id


def run(gov, seq, v=3900, light=False):
    out = None
    for t, ma in seq:
        out = gov.update(LteInputs(t, v, ma, light))
    return out


def test_default_allows_lte_only():
    d = LteGovernor().update(LteInputs(0, 3900, 1000))
    assert d.tx == Tx.ALLOW and d.rat == Rat.LTE_ONLY and not d.throttled


def test_throttle_needs_more_than_hold_time():
    g = LteGovernor()
    assert run(g, [(0, 6000), (0.5, 6000)]).tx == Tx.ALLOW          # 0.5 s < 1 s
    assert run(g, [(1.0, 6000)]).tx == Tx.THROTTLE                   # held 1 s
    assert "cell" in " ".join(g.update(LteInputs(1.1, 3900, 6000)).reasons)


def test_spike_below_hold_resets():
    g = LteGovernor()
    run(g, [(0, 6000), (0.8, 5000), (1.2, 6000)])
    assert g.update(LteInputs(2.1, 3900, 6000)).tx == Tx.ALLOW       # 0.9 s since the re-cross
    assert g.update(LteInputs(2.2, 3900, 6000)).tx == Tx.THROTTLE    # 1.0 s


def test_release_hysteresis_band():
    g = LteGovernor()
    run(g, [(0, 6000), (1, 6000)])
    assert run(g, [(2, 5000), (5, 5000)]).tx == Tx.THROTTLE           # 5.0 A is inside the 4.5..5.5 band
    assert run(g, [(6, 4400)]).tx == Tx.THROTTLE                      # needs release dwell
    assert run(g, [(7, 4400)]).tx == Tx.ALLOW


def test_mcu_overcurrent_event_throttles_immediately():
    g = LteGovernor()
    d = g.update(LteInputs(0, 3900, 3000, overcurrent_evt=True))
    assert d.tx == Tx.THROTTLE and "mcu_overcurrent" in d.reasons


def test_lte_floor_blocks_tx_with_hysteresis():
    g = LteGovernor()
    assert g.update(LteInputs(0, 3549, 500)).tx == Tx.BLOCK
    assert g.update(LteInputs(1, 3560, 500)).tx == Tx.BLOCK           # < 3.55 + 0.05
    assert g.update(LteInputs(2, 3600, 500)).tx == Tx.ALLOW


def test_exact_floor_allows():
    assert LteGovernor().update(LteInputs(0, 3550, 500)).tx == Tx.ALLOW


def test_shutdown_below_3v45_and_recovery():
    g = LteGovernor()
    assert g.update(LteInputs(0, 3440, 500)).tx == Tx.SHUTDOWN
    assert g.update(LteInputs(1, 3580, 500)).tx == Tx.SHUTDOWN
    assert g.update(LteInputs(2, 3600, 500)).tx == Tx.ALLOW


def test_2g_never_by_default():
    d = LteGovernor().update(LteInputs(0, 4100, 500, cm5_light=True))
    assert d.rat == Rat.LTE_ONLY


def test_2g_opt_in_needs_voltage_light_and_no_throttle():
    g = LteGovernor(LteGovConfig(allow_2g=True))
    assert g.update(LteInputs(0, 3800, 500, cm5_light=True)).rat == Rat.LTE_GSM
    assert g.update(LteInputs(1, 3800, 500, cm5_light=False)).rat == Rat.LTE_ONLY
    d = g.update(LteInputs(2, 3740, 500, cm5_light=True))
    assert d.rat == Rat.LTE_ONLY and d.tx == Tx.ALLOW and "2g_denied" in d.reasons   # 3.74 < 3.75: 2G TX blocked, LTE ok
    assert g.update(LteInputs(3, 3770, 500, cm5_light=True)).rat == Rat.LTE_ONLY      # hysteresis: need 3.80
    assert g.update(LteInputs(4, 3800, 500, cm5_light=True)).rat == Rat.LTE_GSM
    run(g, [(5, 6000), (6, 6000)], v=3900, light=True)
    assert g.update(LteInputs(6.5, 3900, 6000, cm5_light=True)).rat == Rat.LTE_ONLY


def test_prototype_preset_and_validation():
    g = LteGovernor(LteGovConfig.prototype_akyga())
    assert run(g, [(0, 2600), (1, 2600)]).tx == Tx.THROTTLE
    with pytest.raises(ValueError):
        LteGovernor(LteGovConfig(throttle_on_mA=4000, throttle_off_mA=4500))
    with pytest.raises(ValueError):
        LteGovernor(LteGovConfig(lte_floor_mV=3800))
    with pytest.raises(ValueError):
        LteGovernor(LteGovConfig(current_point="vbus"))


def test_priority_shutdown_over_throttle():
    g = LteGovernor()
    run(g, [(0, 7000), (1, 7000)])
    assert g.update(LteInputs(1.5, 3400, 7000)).tx == Tx.SHUTDOWN


def test_gauge_sign():
    assert gauge_to_discharge_mA(-5600) == 5600


# --- AT / profiles ---------------------------------------------------------------------------
class FakeModem:
    def __init__(self, replies):
        self.replies, self.sent, self.pending = replies, [], b""

    def write(self, data):
        c = data.decode().strip()
        self.sent.append(c)
        self.pending += (self.replies.get(c, "OK") + "\r\n").encode()

    def read(self, n):
        out, self.pending = self.pending[:n], self.pending[n:]
        return out


def clock():
    t = [0.0]

    def now():
        t[0] += 0.01
        return t[0]
    return now


def test_ec25_profile_sets_lte_only_divctl1_gnss():
    m = FakeModem({"AT+QCFG=?": '+QCFG: "nwscanmode",(0-3)\r\n+QCFG: "divctl",("lte","wcdma"),(0-2)\r\nOK',
                   "AT+QGPSCFG=?": "OK"})
    res = apply_profile(AtClient(m, clock()), EC25)
    assert res['AT+QCFG="nwscanmode",3,1'] == "ok"
    assert res['AT+QCFG="divctl","lte",1'] == "ok"
    assert res['AT+QCFG="diversity",0'] == "skipped"
    assert 'AT+QCFG="divctl","lte",0' not in m.sent                 # 0 would ENABLE diversity
    assert res["AT+QGPS=1"] == "ok" and res['AT+QGPSCFG="autogps",1'] == "ok"


def test_ec25_old_firmware_falls_back_to_diversity0():
    m = FakeModem({"AT+QCFG=?": '+QCFG: "nwscanmode",(0-3)\r\n+QCFG: "diversity",(0,1)\r\nOK'})
    res = apply_profile(AtClient(m, clock()), EC25)
    assert res['AT+QCFG="divctl","lte",1'] == "skipped" and res['AT+QCFG="diversity",0'] == "ok"


def test_gnss_already_on_is_ok_and_errors_reported():
    m = FakeModem({"AT+QGPS=1": "+CME ERROR: 504", 'AT+QCFG="nwscanmode",3,1': "ERROR",
                   "AT+QCFG=?": '"usbnet"\r\nOK'})
    res = apply_profile(AtClient(m, clock()), EC200U)
    assert res["AT+QGPS=1"] == "ok"
    assert res['AT+QCFG="nwscanmode",3,1'].startswith("failed")


def test_at_timeout():
    class Dead:
        def write(self, d): pass
        def read(self, n): return b""
    r = AtClient(Dead(), clock()).cmd("AT", 0.1)
    assert not r.ok and r.lines[-1] == "TIMEOUT"


def test_profiles_timing_per_hardware_design():
    assert EC25.pwrkey_on_ms >= 500 and EC25.pwrkey_on_ms < 650 and EC25.pwrkey_off_ms >= 650
    assert 150 <= EC25.reset_ms <= 460
    assert EC200U.pwrkey_on_ms >= 2000 and EC200U.pwrkey_off_ms >= 3000 and EC200U.reset_ms >= 100
    assert EC25.status_on_level is None and EC200U.status_on_level == 0
    assert by_usb_id(0x2C7C, 0x0125) is EC25 and by_usb_id(0x2C7C, 0x0901) is EC200U
    assert by_usb_id(0x1234, 1) is None
    assert RAT_CMD["lte"].endswith(",3,1")
