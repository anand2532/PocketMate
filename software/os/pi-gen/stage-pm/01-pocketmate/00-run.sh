#!/bin/bash -e
# Install PocketMate services, units, DT overlays and config into the image.
: "${PM_SRC:?set PM_SRC to <repo>/software}"
R="${ROOTFS_DIR}"
install -d "$R/opt/pm" "$R/opt/pm/models" "$R/usr/lib/pocketmate" "$R/etc/pocketmate" "$R/data"
# Python services into a venv that can see the Debian PySide6 (system site packages).
on_chroot <<CHROOT
python3 -m venv --system-site-packages /opt/pm/venv
CHROOT
cp -r "$PM_SRC/services" "$R/tmp/pm-services"
cp -r "$PM_SRC/ui" "$R/tmp/pm-ui"
on_chroot <<CHROOT
/opt/pm/venv/bin/pip install --no-cache-dir /tmp/pm-services /tmp/pm-ui
for b in /opt/pm/venv/bin/pm-*; do ln -sf "\$b" /usr/bin/; done
rm -rf /tmp/pm-services /tmp/pm-ui
CHROOT
install -m 644 "$PM_SRC"/services/systemd/*.service "$PM_SRC"/services/systemd/*.timer "$PM_SRC"/services/systemd/*.target "$R/etc/systemd/system/"
install -m 644 "$PM_SRC/lte/systemd/pm-lte.service" "$R/etc/systemd/system/"
install -m 644 "$PM_SRC/services/os-integration/pocketmate.sysusers.conf" "$R/usr/lib/sysusers.d/pocketmate.conf"
install -m 644 "$PM_SRC/services/os-integration/pocketmate.tmpfiles.conf" "$R/usr/lib/tmpfiles.d/pocketmate.conf"
install -m 644 "$PM_SRC/services/os-integration/99-pocketmate.rules" "$PM_SRC/lte/udev/80-pm-lte.rules" "$R/etc/udev/rules.d/"
install -m 644 "$PM_SRC/services/dbus/org.pocketmate.conf" "$R/etc/dbus-1/system.d/"
install -m 755 "$PM_SRC/lte/pm-lte-power" "$PM_SRC/lte/pm-lte-net" "$R/usr/lib/pocketmate/"
install -m 644 "$PM_SRC/lte/pinmap.env" "$R/etc/pocketmate/lte-pinmap.env"
install -d "$R/etc/systemd/network" && install -m 644 "$PM_SRC/lte/network/40-pm-wwan.network" "$R/etc/systemd/network/"
# Device tree overlays + config.txt (dts/validate.py compiles the .dtbo files first)
python3 "$PM_SRC/dts/validate.py"   # compile only (no --base/--readme)
install -m 644 "$PM_SRC"/dts/build/*.dtbo "$R/boot/firmware/overlays/"
install -m 644 "$PM_SRC/dts/config.txt" "$R/boot/firmware/config.txt"
on_chroot <<CHROOT
systemd-sysusers
systemctl enable pocketmate.target nftables.service chrony.service
systemctl set-default multi-user.target
CHROOT
