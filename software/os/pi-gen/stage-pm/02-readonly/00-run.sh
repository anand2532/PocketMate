#!/bin/bash -e
# Read-only rootfs (§2) + system policy.
: "${PM_SRC:?}"
R="${ROOTFS_DIR}"; F="$PM_SRC/os/files"
install -m 644 "$F/fstab" "$R/etc/fstab"
install -m 600 "$F/crypttab" "$R/etc/crypttab"
install -m 755 "$F/pm-slot-generator" "$R/usr/lib/systemd/system-generators/pm-slot-generator"
install -m 644 "$F/nftables.conf" "$R/etc/nftables.conf"
install -d "$R/etc/systemd/system.conf.d" "$R/etc/systemd/journald.conf.d"
install -m 644 "$F/watchdog.conf" "$R/etc/systemd/system.conf.d/pm-watchdog.conf"
install -m 644 "$F/journald.conf" "$R/etc/systemd/journald.conf.d/pm.conf"
sed 's/@SLOT@/A/g' "$F/cmdline.txt.in" > "$R/boot/firmware/cmdline.txt"
on_chroot <<CHROOT
# UART0 belongs to the MCU link: no serial console/getty on ttyAMA0 (§3)
systemctl mask serial-getty@ttyAMA0.service
# Nothing on a read-only root may need writes at runtime:
systemctl mask apt-daily.timer apt-daily-upgrade.timer man-db.timer dphys-swapfile.service 2>/dev/null || true
ln -sf /proc/self/mounts /etc/mtab
rm -f /etc/machine-id && touch /etc/machine-id   # systemd: transient machine-id on ro root (first-boot TODO: persist in /data)
CHROOT
