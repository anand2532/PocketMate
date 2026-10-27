#ifndef PM_COBS_H
#define PM_COBS_H
#include <stddef.h>
#include <stdint.h>
/* Returns encoded length (no trailing delimiter) or 0 if out_cap too small. */
size_t pm_cobs_encode(const uint8_t *in, size_t n, uint8_t *out, size_t out_cap);
/* Returns decoded length or (size_t)-1 on malformed input / overflow. */
size_t pm_cobs_decode(const uint8_t *in, size_t n, uint8_t *out, size_t out_cap);
#endif
