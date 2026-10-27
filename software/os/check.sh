#!/bin/bash
# Host-side checks for os/ (no root, no device): shellcheck, partition layout on a sparse 32 GB eMMC image,
# RAUC tryboot backend state machine, slot generator, nftables syntax (if nft can run unprivileged).
# shellcheck disable=SC2015
set -uo pipefail
cd "$(dirname "$0")" || exit 1
pass=0; fail=0
ok() { pass=$((pass + 1)); echo "PASS $*"; }
ko() { fail=$((fail + 1)); echo "FAIL $*"; }
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT

mapfile -t scripts < <(printf '%s\n' rauc/rauc-tryboot-backend rauc/make-bundle.sh files/pm-slot-generator check.sh pi-gen/stage-pm/prerun.sh pi-gen/stage-pm/0*/00-run.sh)
if command -v shellcheck >/dev/null; then
    if shellcheck -x -e SC2154 "${scripts[@]}"; then ok "shellcheck ${#scripts[@]} scripts"; else ko shellcheck; fi
else echo "SKIP shellcheck (not installed)"; fi

# eMMC 32 GB on CM5: ~29.1 GiB usable (§2.1). 31268536320 B = 29.12 GiB [VERIFY exact user-area size on a unit]
truncate -s 31268536320 "$T/emmc.img"
if ! command -v sfdisk >/dev/null; then
    python3 - partitions/cm5-4g.sfdisk 31268536320 <<'PY' && ok "layout arithmetic (sfdisk not installed: python fallback)" || ko "layout arithmetic"
import re, sys
u = {"MiB": 2**20, "GiB": 2**30}
parts = [l for l in open(sys.argv[1]) if l.startswith("name=")]
fixed = sum(int(m.group(1)) * u[m.group(2)] for l in parts for m in [re.search(r"size=(\d+)(MiB|GiB)", l)] if m)
disk = int(sys.argv[2]); data = disk - 2048 * 512 - fixed - 33 * 512   # GPT backup header
print(f"INFO {len(parts)} partitions, fixed {fixed / 2**30:.2f} GiB, data {data / 2**30:.2f} GiB")
assert len(parts) == 9 and data > 11 * 2**30
PY
elif sfdisk -q "$T/emmc.img" < partitions/cm5-4g.sfdisk >/dev/null 2>"$T/sf.err"; then
    ok "sfdisk layout applies to a 29.12 GiB image"
    data_bytes=$(sfdisk -J "$T/emmc.img" | python3 -c 'import json,sys; p=json.load(sys.stdin)["partitiontable"]["partitions"]; print(p[-1]["size"]*512)')
    gib=$(python3 -c "print(round($data_bytes/2**30,2))")
    if python3 -c "import sys; sys.exit(0 if $data_bytes > 11*2**30 else 1)"; then ok "data partition ${gib} GiB (>= 11 GiB; §2.1 says ~11.6)"; else ko "data partition only ${gib} GiB"; fi
    n=$(sfdisk -J "$T/emmc.img" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["partitiontable"]["partitions"]))')
    [ "$n" = 9 ] && ok "9 partitions" || ko "partition count $n"
else ko "sfdisk: $(cat "$T/sf.err")"; fi

# RAUC custom backend
B=rauc/rauc-tryboot-backend
export PM_BOOTSEL_MNT="$T/bootsel" PM_RAUC_STATE="$T/st"
mkdir -p "$PM_BOOTSEL_MNT"; cp files/autoboot.txt "$PM_BOOTSEL_MNT/"
[ "$($B get-primary)" = A ] && ok "backend: primary A" || ko "backend get-primary"
$B set-primary B && [ "$($B get-primary)" = B ] && grep -q '^boot_partition=2' "$PM_BOOTSEL_MNT/autoboot.txt" \
    && sed -n '/\[tryboot\]/,$p' "$PM_BOOTSEL_MNT/autoboot.txt" | grep -q 'boot_partition=3' \
    && ok "backend: set-primary B stages tryboot only" || ko "backend set-primary"
$B set-state B good && sed -n '/\[all\]/,/\[tryboot\]/p' "$PM_BOOTSEL_MNT/autoboot.txt" | grep -q 'boot_partition=3' \
    && [ "$($B get-primary)" = B ] && ok "backend: good commits B" || ko "backend commit"
$B set-primary A && $B set-state A bad && [ "$($B get-primary)" = B ] && [ "$($B get-state A)" = bad ] \
    && ok "backend: bad try of A keeps B" || ko "backend bad"
PM_FAKE_BOOT_PART=3 $B get-current | grep -qx B && ok "backend: get-current" || ko "backend get-current"
$B set-state A weird 2>/dev/null && ko "backend accepted bad state" || ok "backend: rejects bad state"
unset PM_BOOTSEL_MNT PM_RAUC_STATE

# Slot generator
PM_CMDLINE="root=PARTLABEL=rootfs-B ro pm.slot=B" files/pm-slot-generator "$T/gen"
grep -q 'What=/dev/disk/by-partlabel/models-B' "$T/gen/opt-pm-models.mount" && [ -L "$T/gen/local-fs.target.wants/boot-firmware.mount" ] \
    && ok "pm-slot-generator slot B" || ko "pm-slot-generator"
if command -v systemd-analyze >/dev/null; then
    if systemd-analyze verify --man=no "$T"/gen/*.mount >/dev/null 2>"$T/sa.err" || ! grep -qv "Failed to\|not found\|by-partlabel" "$T/sa.err"; then
        ok "systemd-analyze generated mounts"; else ko "systemd-analyze: $(cat "$T/sa.err")"; fi
fi

# RAUC system.conf: INI parse + slot pairing
python3 - <<'PY' && ok "rauc system.conf parses, A/B slots paired" || ko "rauc system.conf"
import configparser, sys
c = configparser.ConfigParser(); c.read("rauc/system.conf")
assert c["system"]["bootloader"] == "custom" and c["handlers"]["bootloader-custom-backend"]
b = {c[s]["bootname"] for s in c.sections() if s.startswith("slot.rootfs.")}
assert b == {"A", "B"}, b
for cls in ("boot", "models"):
    assert c[f"slot.{cls}.0"]["parent"] == "rootfs.0" and c[f"slot.{cls}.1"]["parent"] == "rootfs.1"
assert "key" not in c["keyring"] and c["keyring"]["path"].endswith(".pem")
PY
if command -v rauc >/dev/null; then echo "INFO rauc present: $(rauc --version)"; else echo "SKIP rauc not installed on this host (bundle build not exercised)"; fi

if command -v nft >/dev/null && nft -c -f files/nftables.conf 2>"$T/nft.err"; then ok "nft -c nftables.conf"
else echo "SKIP nft -c ($(head -1 "$T/nft.err" 2>/dev/null || echo 'nft not installed'))"; fi

! find . -name '*.key' -o -name '*.p12' -o -name '*private*' | grep -q . && ok "no private key files under os/" || ko "key-like files present"

echo "os/check.sh: $pass passed, $fail failed"
[ "$fail" = 0 ]
