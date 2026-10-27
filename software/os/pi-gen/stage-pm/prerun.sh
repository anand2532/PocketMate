#!/bin/bash -e
# pi-gen stage-pm: start from stage2 (Lite) rootfs.
if [ ! -d "${ROOTFS_DIR}" ]; then
    copy_previous
fi
