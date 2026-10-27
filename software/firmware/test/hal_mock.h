#ifndef HAL_MOCK_H
#define HAL_MOCK_H
#include "pm_hal.h"
typedef struct {
    uint32_t now; bool pa11, mute_high, pg, btn[4], cm5_power, irq_low, charger;
    unsigned pa11_on_count, safe_init_calls, run_pulses, charger_writes, wdt_refreshes, vreg_writes;
    uint16_t vreg_mV;
    uint8_t tx[4096]; size_t tx_len;
} hal_mock_t;
extern hal_mock_t M;
void hal_mock_reset(void);
#endif
