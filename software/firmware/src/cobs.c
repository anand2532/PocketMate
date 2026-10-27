#include "pm_cobs.h"

size_t pm_cobs_encode(const uint8_t *in, size_t n, uint8_t *out, size_t out_cap) {
    size_t o = 1, code_i = 0;
    uint8_t code = 1;
    if (out_cap < n + n / 254 + 1) return 0;
    for (size_t i = 0; i < n; i++) {
        if (in[i] == 0) {
            out[code_i] = code; code_i = o++; code = 1;
        } else {
            out[o++] = in[i];
            if (++code == 0xFF) { out[code_i] = code; code_i = o++; code = 1; }
        }
    }
    out[code_i] = code;
    return o;
}

size_t pm_cobs_decode(const uint8_t *in, size_t n, uint8_t *out, size_t out_cap) {
    size_t i = 0, o = 0;
    while (i < n) {
        uint8_t code = in[i++];
        if (code == 0) return (size_t)-1;
        for (uint8_t k = 1; k < code; k++) {
            if (i >= n || o >= out_cap || in[i] == 0) return (size_t)-1;
            out[o++] = in[i++];
        }
        if (code != 0xFF && i < n) {
            if (o >= out_cap) return (size_t)-1;
            out[o++] = 0;
        }
    }
    return o;
}
