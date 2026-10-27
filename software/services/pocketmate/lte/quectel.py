"""Quectel EC25 / EC200U AT profiles used by pm-lte (ARCHITECTURE.md §19.4).

Every command carries its source. "unverified" means: taken from the cited manual but not yet run on
our module/firmware; pm-lte checks `AT+QCFG=?` / `AT+QGPSCFG=?` support at runtime and logs a
mismatch instead of failing.

Sources
  [QCFG-EC2x] Quectel EC2x&EG2x&EG9x&EM05 Series QCFG AT Commands Manual V1.1 (2023-06-27), §3.x
              "nwscanmode" (3 = LTE only) and §3.11 "divctl" (0 = PRX+DRX, 1 = PRX only, 2 = DRX only).
              https://sixfab.com/wp-content/uploads/2023/11/Quectel_EC2xEG2xEG9xEM05_Series_QCFG_AT_Commands_Manual_V1.1.pdf
  [EC25-HD]   Quectel EC25 Hardware Design V2.x (hardware/kicad-lte/ref/ec25_hd.txt): PWRKEY >= 500 ms on,
              >= 650 ms off, power-down up to 29.5 s, RESET_N 150-460 ms, USB active >= 13 s,
              STATUS open-drain LOW when on; ANT_DIV note: AT+QCFG="diversity",0 (older firmware).
  [EC200U-HD] Quectel EC200U Series Hardware Design V1.0 (ref/ec200u_hd.txt): PWRKEY >= 2 s on, >= 3 s
              off, power-down up to 30 s, RESET_N >= 100 ms, USB active >= 2.23 s after, STATUS push-pull
              HIGH when on.
  [EC200U-AT] Quectel EC200U&EG800G&EG91xU&EG915G Series AT Commands Manual V1.2 (2024-07-29), §4.5.1
              AT+QCFG="nwscanmode",<scan_mode>[,<effect>]: 0 auto GSM/LTE, 1 GSM only, 3 LTE only;
              effect 1 = immediately; saved automatically.
              https://kb.unipi.technology/_media/en:hw:004-edge:quectel_ec200u_eg800g_eg91xu_eg915g_series_at_commands_manual_v1.2.pdf
  [GNSS-EC2x] Quectel EC2x&EG9x&EG2x-G&EM05 Series GNSS Application Note V1.3: AT+QGPSCFG="autogps",1, AT+QGPS=1.
  [GNSS-EC200U] Quectel EC200U Series&EG912U-GL GNSS Application Note V1.1 (2022-08-23): AT+QGPSCFG="autogps",1
              (saved, effective after reboot), AT+QGPS=1, NMEA on the "usbnmea" port by default.
              https://7semi.com/content/datasheets/EC200U-GNSS.pdf
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AtStep:
    cmd: str
    source: str
    verified_on_hw: bool = False
    optional: bool = False          # failure is logged, not fatal (feature may be absent on a variant)
    probe: str | None = None        # substring that must appear in the test-command reply to send it


@dataclass(frozen=True)
class ModuleProfile:
    name: str
    usb_ids: tuple[tuple[int, int], ...]   # (VID, PID)
    net: str                                # "qmi" | "ecm"
    pwrkey_on_ms: int
    pwrkey_off_ms: int
    reset_ms: int
    vbat_settle_ms: int
    usb_ready_s: float                      # wait budget after PWRKEY before giving up
    poweroff_max_s: float
    status_on_level: int | None             # carrier LTE_STATUS level when module on; None = unusable
    init: tuple[AtStep, ...] = field(default=())


# Carrier LTE_STATUS = NOT(module STATUS) through Q3 (gate pulled up to VDD_EXT by R22).
#  EC200U: STATUS push-pull HIGH when on  -> Q3 on  -> LTE_STATUS LOW (0)  = on. Works.
#  EC25:   STATUS open-drain LOW when on   -> Q3 off -> LTE_STATUS HIGH; when off VDD_EXT=0 -> also HIGH.
#          => LTE_STATUS is HIGH in every state with an EC25: unusable (hardware issue, STATUS.md H-LTE-1).
EC25 = ModuleProfile(
    name="EC25",
    usb_ids=((0x2C7C, 0x0125),),            # QUECTEL_PRODUCT_EC25, linux drivers/usb/serial/option.c
    net="qmi",
    pwrkey_on_ms=600,                        # >= 500 ms [EC25-HD 3.7.1] + margin; < 650 ms off threshold
    pwrkey_off_ms=800,                       # >= 650 ms [EC25-HD 3.7.2.1]
    reset_ms=300,                            # 150..460 ms [EC25-HD 3.8]
    vbat_settle_ms=50,                       # >= 30 ms VBAT stable before PWRKEY [EC25-HD note]
    usb_ready_s=20.0,                        # USB active >= 13 s [EC25-HD Fig.12]
    poweroff_max_s=30.0,                     # <= 29.5 s [EC25-HD Fig.13]
    status_on_level=None,
    init=(
        AtStep("ATE0", "V.25ter"),
        AtStep('AT+QCFG="nwscanmode",3,1', "[QCFG-EC2x] nwscanmode 3 = LTE only, 1 = immediate"),
        AtStep('AT+QCFG="divctl","lte",1', "[QCFG-EC2x 3.11] 1 = PRX only (Rx-diversity off). NOTE: 0 ENABLES both chains",
               optional=True, probe='"divctl"'),
        AtStep('AT+QCFG="diversity",0', "[EC25-HD antenna note] fallback for firmware without divctl",
               optional=True, probe='"diversity"'),
        AtStep('AT+QGPSCFG="autogps",1', "[GNSS-EC2x]", optional=True),
        AtStep("AT+QGPS=1", "[GNSS-EC2x] (+CME ERROR 504 = already on)", optional=True),
    ),
)

EC200U = ModuleProfile(
    name="EC200U",
    usb_ids=((0x2C7C, 0x0901),),            # QUECTEL_PRODUCT_EC200U, linux option.c (PID may change with usbnet mode: VERIFY)
    net="ecm",
    pwrkey_on_ms=2200,                       # >= 2 s [EC200U-HD 3.7.1]
    pwrkey_off_ms=3200,                      # >= 3 s [EC200U-HD 3.7.2.1]
    reset_ms=200,                            # >= 100 ms [EC200U-HD 3.7.3]
    vbat_settle_ms=50,
    usb_ready_s=15.0,                        # USB >= 2.23 s, STATUS >= 5.05 s after PWRKEY [EC200U-HD Fig.12]
    poweroff_max_s=31.0,                     # <= 30 s [EC200U-HD Fig.13]
    status_on_level=0,
    init=(
        AtStep("ATE0", "V.25ter"),
        AtStep('AT+QCFG="nwscanmode",3,1', "[EC200U-AT 4.5.1] 3 = LTE only, 1 = immediate"),
        AtStep('AT+QCFG="usbnet",1', "[EC200U-AT] usbnet 1 = ECM (VERIFY value; takes effect after reboot)",
               optional=True, probe='"usbnet"'),
        AtStep('AT+QGPSCFG="autogps",1', "[GNSS-EC200U] (GNSS is optional per EC200U variant)", optional=True),
        AtStep("AT+QGPS=1", "[GNSS-EC200U]", optional=True),
    ),
)
# EC200U Rx diversity: EC200U-CN is Cat 1 with pad 35 = ANT_BT/WIFI_SCAN (no LTE diversity input,
# EC25_EC200U_pad_compat.md), so there is nothing to disable.

PROFILES = {p.name: p for p in (EC25, EC200U)}

# RAT switch (governor Rat.LTE_GSM) — same syntax on both modules (sources above). 0 = auto (GSM/LTE on
# EC200U; GSM/WCDMA/LTE on EC25).
RAT_CMD = {"lte": 'AT+QCFG="nwscanmode",3,1', "lte+gsm": 'AT+QCFG="nwscanmode",0,1'}
AIRPLANE_ON, AIRPLANE_OFF = "AT+CFUN=4", "AT+CFUN=1"   # 3GPP TS 27.007
POWER_DOWN = "AT+QPOWD=1"                              # normal power down (EC25/EC200U AT manuals)


def by_usb_id(vid: int, pid: int) -> ModuleProfile | None:
    for p in PROFILES.values():
        if (vid, pid) in p.usb_ids:
            return p
    return None
