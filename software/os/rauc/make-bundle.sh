#!/bin/bash
# Build a RAUC system bundle from boot.vfat + rootfs.ext4 (§2.2 "routine release signing").
#   make-bundle.sh <version> <sku> <imagedir> <out.raucb>
# RAUC always signs bundles. CI/dev signs with a THROWAWAY dev key (generated per run in a tmpdir, never
# stored; the dev CA is not in production keyrings). Anand re-signs for release with the hardware token:
#   rauc resign --cert=pkcs11:... --key=pkcs11:... --keyring=keyring.pem in.raucb out-release.raucb
# This script never touches release keys.
set -euo pipefail
[ $# -eq 4 ] || { echo "usage: $0 <version> <sku> <imagedir> <out.raucb>" >&2; exit 64; }
VER="$1" SKU="$2" IMG="$3" OUT="$4"
HERE="$(cd "$(dirname "$0")" && pwd)"
W="$(mktemp -d)"; trap 'rm -rf "$W"' EXIT
mkdir "$W/bundle"
cp "$IMG/boot.vfat" "$IMG/rootfs.ext4" "$W/bundle/"
sed -e "s/@VERSION@/$VER/" -e "s/@SKU@/$SKU/" "$HERE/manifest.raucm.in" > "$W/bundle/manifest.raucm"
if [ -n "${PM_RAUC_CERT:-}" ] && [ -n "${PM_RAUC_KEY:-}" ]; then
    CERT="$PM_RAUC_CERT"; KEY="$PM_RAUC_KEY"        # e.g. pkcs11: URIs on Anand's machine
else
    openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:prime256v1 -nodes -days 1 \
        -subj "/O=PocketMate DEV/CN=throwaway $(date +%s)" -keyout "$W/dev.key" -out "$W/dev.crt" 2>/dev/null
    CERT="$W/dev.crt"; KEY="$W/dev.key"
    echo "make-bundle: signed with a throwaway DEV key; re-sign with the release token before publishing" >&2
fi
rauc bundle --cert="$CERT" --key="$KEY" "$W/bundle" "$OUT"
sha256sum "$OUT"
