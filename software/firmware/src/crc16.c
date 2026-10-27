#include "pm_crc16.h"
/* Bitwise (no table) to save flash on the 26 KB slot. */
uint16_t pm_crc16(const uint8_t *d, size_t n, uint16_t crc) {
    uint32_t c = crc;
    while (n--) {
        c ^= (uint32_t)(*d++) << 8;
        for (int i = 0; i < 8; i++) c = (c & 0x8000u) ? ((c << 1) ^ 0x1021u) : (c << 1);
        c &= 0xFFFFu;
    }
    return (uint16_t)c;
}
