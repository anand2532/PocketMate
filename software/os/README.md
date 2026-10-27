# os/ — PocketMate prototype image (ARCHITECTURE.md §2, §3)

Raspberry Pi OS Lite (**Trixie**, arm64 — Debian only packages PySide6 from trixie on) built with **pi-gen** plus one custom stage, `stage-pm`.

| Path | What |
|---|---|
| `pi-gen/config` | pi-gen config: stage0–2 + `stage-pm`, SSH off, en_IN, Asia/Kolkata |
| `pi-gen/stage-pm/00-packages` | Debian packages: PySide6/QML, libcamera, PipeWire, nftables, chrony, cryptsetup, rauc, libqmi-utils |
| `pi-gen/stage-pm/01-pocketmate` | installs services + UI into `/opt/pm/venv`, systemd units, sysusers, tmpfiles, udev, D-Bus policy, LTE scripts, compiled DT overlays and `config.txt` |
| `pi-gen/stage-pm/02-readonly` | read-only root: fstab (tmpfs /tmp, LUKS `/data` with bind mounts for `/var/lib/pm`, `/var/log`, NetworkManager), crypttab, slot mount generator, nftables egress policy, `RuntimeWatchdogSec=15`, journald 50 MB, `serial-getty@ttyAMA0` masked (UART0 = MCU link) |
| `pi-gen/stage-pm/03-rauc` | `/etc/rauc/system.conf`, tryboot backend, public keyring (fails closed if missing) |
| `partitions/cm5-4g.sfdisk` | GPT layout (§2.1) |
| `files/` | fstab, crypttab, nftables, watchdog, journald, autoboot.txt, cmdline template, `pm-slot-generator` |
| `rauc/` | `system.conf`, `manifest.raucm.in`, `make-bundle.sh`, `rauc-tryboot-backend` |
| `keys/` | **placeholders only** — no keys are generated or stored (see `keys/README.md`) |
| `check.sh` | host checks (below) |

## Build (needs a Debian/Ubuntu host with root or Docker; not run on the build box)

```sh
git clone https://github.com/RPi-Distro/pi-gen && cd pi-gen   # VERIFY: branch that builds trixie arm64
cp -r <repo>/software/os/pi-gen/stage-pm . && cp <repo>/software/os/pi-gen/config .
PM_SRC=<repo>/software PM_DEV_KEYRING=1 ./build-docker.sh      # dev image; drop PM_DEV_KEYRING for production
```
Then partition the eMMC with `partitions/cm5-4g.sfdisk` (rpiboot + `sfdisk`), write `boot.vfat`/`rootfs.ext4`
into the A slot, copy `files/autoboot.txt` to `bootsel`, and `luksFormat` the `data` partition.

## Layout change vs §2.1 (v0.4.0)
Partition 1 is now a 16 MiB FAT **`bootsel`** holding only `autoboot.txt`. The CM5 bootloader reads
`autoboot.txt` from the first FAT partition, and RAUC writes boot-A/boot-B as whole images, so the A/B switch
can't live inside a slot. Data shrinks by 16 MiB (≈ 12.1 GiB on a 29.12 GiB eMMC by arithmetic; §2.1 says
≈ 11.6 GiB — measure the real user-area size on a unit).

## A/B with tryboot (RAUC custom backend)
`set-primary X` writes X into `[tryboot]` only and marks it pending; pm-update reboots with `reboot "0 tryboot"`.
pm-health → `rauc status mark-good` → `set-state X good` commits X to `[all]`. A failed try needs no action:
tryboot is one-shot, so the next boot is the old slot. **VERIFY on hardware**: tryboot one-shot behaviour with
`tryboot_a_b=1`, and the `/proc/device-tree/chosen/bootloader/partition` path used by `get-current`.

## Signing
`rauc/make-bundle.sh` signs with a throwaway DEV cert made in a temp dir (RAUC can't make unsigned bundles), or
with `PM_RAUC_CERT`/`PM_RAUC_KEY` (PKCS#11 URIs on Anand's machine). Release = `rauc resign` with token T1 (§2.2.1).
It was not run on the build box (rauc isn't installed there, and the "no keys on the box" rule applies).

## Checks (`bash os/check.sh`)
shellcheck of every script; partition arithmetic (sfdisk on a sparse image if installed); the tryboot backend
state machine (stage, commit, bad try, bad args); the slot generator + `systemd-analyze verify`; system.conf
structure; a scan for key files. `nft -c` and `rauc` run only where installed.
