#ifndef PM_FRAME_H
#define PM_FRAME_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include "pm_proto_gen.h"

#define PM_HDR_LEN 4u
#define PM_RAW_MAX (PM_HDR_LEN + PM_MAX_PAYLOAD + 2u)
#define PM_WIRE_MAX (PM_RAW_MAX + PM_RAW_MAX / 254u + 2u)

typedef struct { uint8_t type, seq, len; uint8_t payload[PM_MAX_PAYLOAD]; } pm_frame_t;

typedef enum { PM_FR_OK = 0, PM_FR_SHORT, PM_FR_LEN, PM_FR_CRC, PM_FR_VER, PM_FR_COBS } pm_frame_err_t;

/* Encodes COBS(frame) + 0x00 delimiter into out. Returns bytes written or 0. */
size_t pm_frame_encode(uint8_t type, uint8_t seq, const uint8_t *payload, uint8_t len, uint8_t *out, size_t cap);
pm_frame_err_t pm_frame_decode_raw(const uint8_t *raw, size_t n, pm_frame_t *f);

/* Streaming de-framer: feed bytes, get frames. Oversize/garbled frames are dropped and counted. */
typedef struct {
    uint8_t buf[PM_WIRE_MAX];
    size_t n;
    bool overflow;
    uint32_t bad, good;
} pm_deframer_t;
void pm_deframer_init(pm_deframer_t *d);
/* Returns true and fills f when a valid frame completes on this byte. */
bool pm_deframer_feed(pm_deframer_t *d, uint8_t byte, pm_frame_t *f);
#endif
