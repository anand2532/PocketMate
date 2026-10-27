#!/bin/bash
# Dry-run checks of pm-lte-power sequences (no GPIO access). Run: bash lte/tests/test_pm_lte_power.sh
set -euo pipefail
cd "$(dirname "$0")/.."
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
export PM_LTE_DRYRUN=1 PM_LTE_STATE_DIR="$T"
pass=0; fail=0
check() {  # check <name> <expected-substring-or-regex> <output>
    if printf '%s\n' "$3" | grep -Eq -- "$2"; then pass=$((pass + 1)); else fail=$((fail + 1)); echo "FAIL $1: /$2/"; printf '%s\n' "$3" | sed 's/^/    /'; fi
}
order() { # order <name> <output> <line1> <line2>... lines must appear in this order
    local name="$1" out="$2"; shift 2
    local n=0 l
    for l in "$@"; do
        local k; k="$(printf '%s\n' "$out" | grep -nF -- "$l" | cut -d: -f1 | awk -v n="$n" '$1 > n' | head -1)"
        if [ -z "$k" ] || [ "$k" -le "$n" ]; then fail=$((fail + 1)); echo "FAIL $name: order at '$l'"; return; fi
        n="$k"
    done
    pass=$((pass + 1))
}

out="$(PM_LTE_FAKE_USB_ON=2c7c:0125 ./pm-lte-power on 2>&1)"
order on-unknown "$out" "pinctrl set 13 op dl" "pinctrl set 24 op dh" "sleep_ms 50" "pinctrl set 9 op dh" "sleep_ms 2200" "pinctrl set 9 op dl"
check on-detect "module=ec25" "$out"

out="$(./pm-lte-power on 2>&1 || true)"
check on-ec25-pulse "sleep_ms 600" "$out"          # cached ec25 -> 600 ms (>= 500 ms)
check on-timeout "no USB and no STATUS" "$out"

out="$(PM_LTE_FAKE_USB=2c7c:0125 ./pm-lte-power off 2>&1)"
order off-ec25 "$out" "AT+QPOWD=1" "poll usb_absent" "pinctrl set 24 op dl"

echo ec200u > "$T/lte-module"
out="$(PM_LTE_FAKE_USB=2c7c:0901 PM_LTE_FAKE_STATUS=0 ./pm-lte-power off 2>&1)"
order off-ec200u "$out" "AT+QPOWD=1" "poll status_off" "poll usb_absent" "pinctrl set 24 op dl"

out="$(./pm-lte-power reset 2>&1)"
order reset-ec200u "$out" "pinctrl set 13 op dh" "sleep_ms 200" "pinctrl set 13 op dl"
out="$(PM_LTE_FAKE_STATUS=0 ./pm-lte-power status 2>&1)"
check status-ec200u-on "on=yes" "$out"

echo ec25 > "$T/lte-module"
out="$(PM_LTE_FAKE_STATUS=0 ./pm-lte-power status 2>&1)"
check status-ec25-ignores-gpio16 "on=no" "$out"     # H-LTE-1: STATUS unusable with EC25
out="$(./pm-lte-power reset 2>&1)"
check reset-ec25 "sleep_ms 300" "$out"

out="$(./pm-lte-power off 2>&1)"
check off-when-off "pinctrl set 24 op dl" "$out"
if ./pm-lte-power bogus 2>/dev/null; then fail=$((fail + 1)); echo "FAIL usage"; else pass=$((pass + 1)); fi

echo "pm-lte-power dry-run: $pass passed, $fail failed"
[ "$fail" = 0 ]
