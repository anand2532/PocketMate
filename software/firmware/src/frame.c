#include "pm_frame.h"
#include <string.h>
#include "pm_cobs.h"
#include "pm_crc16.h"

size_t pm_frame_encode(uint8_t type, uint8_t seq, const uint8_t *payload, uint8_t len, uint8_t *out, size_t cap) {
    uint8_t raw[PM_RAW_MAX];
    if (len > PM_MAX_PAYLOAD) return 0;
    raw[0] = PM_PROTO_VER; raw[1] = type; raw[2] = seq; raw[3] = len;
    if (len) memcpy(&raw[4], payload, len);
    uint16_t c = pm_crc16(raw, 4u + len, 0xFFFFu);
    raw[4 + len] = (uint8_t)(c & 0xFF); raw[5 + len] = (uint8_t)(c >> 8);   /* little-endian, as Python "<H" */
    size_t n = pm_cobs_encode(raw, 6u + len, out, cap ? cap - 1 : 0);
    if (!n) return 0;
    out[n] = 0x00;
    return n + 1;
}

pm_frame_err_t pm_frame_decode_raw(const uint8_t *raw, size_t n, pm_frame_t *f) {
    if (n < PM_HDR_LEN + 2) return PM_FR_SHORT;
    uint8_t len = raw[3];
    if (len > PM_MAX_PAYLOAD || n != PM_HDR_LEN + len + 2u) return PM_FR_LEN;
    uint16_t c = (uint16_t)(raw[4 + len] | (raw[5 + len] << 8));
    if (pm_crc16(raw, 4u + len, 0xFFFFu) != c) return PM_FR_CRC;
    if (raw[0] != PM_PROTO_VER) return PM_FR_VER;
    f->type = raw[1]; f->seq = raw[2]; f->len = len;
    if (len) memcpy(f->payload, &raw[4], len);
    return PM_FR_OK;
}

void pm_deframer_init(pm_deframer_t *d) { memset(d, 0, sizeof *d); }

bool pm_deframer_feed(pm_deframer_t *d, uint8_t b, pm_frame_t *f) {
    if (b != 0x00) {
        if (d->n < sizeof d->buf) d->buf[d->n++] = b; else d->overflow = true;
        return false;
    }
    /* delimiter: an empty run is the CM5's 0x00 wake preamble (§11), not an error */
    if (d->n == 0) return false;
    bool ok = false;
    if (!d->overflow) {
        uint8_t raw[PM_RAW_MAX];
        size_t m = pm_cobs_decode(d->buf, d->n, raw, sizeof raw);
        ok = (m != (size_t)-1) && pm_frame_decode_raw(raw, m, f) == PM_FR_OK;
    }
    if (ok) d->good++; else d->bad++;
    d->n = 0; d->overflow = false;
    return ok;
}
