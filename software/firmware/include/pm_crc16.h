#ifndef PM_CRC16_H
#define PM_CRC16_H
#include <stddef.h>
#include <stdint.h>
/* CRC-16/CCITT-FALSE (poly 0x1021, init 0xFFFF); check("123456789") == 0x29B1 */
uint16_t pm_crc16(const uint8_t *d, size_t n, uint16_t crc);
#endif
