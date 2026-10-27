/* Host mock of pm_hal.h: records outputs, lets tests drive inputs. */
#include "hal_mock.h"
#include <string.h>
hal_mock_t M;
void hal_mock_reset(void) { memset(&M, 0, sizeof M); M.mute_high = true; }
void hal_init_safe_outputs(void) { M.pa11 = false; M.safe_init_calls++; }
uint32_t hal_millis(void) { return M.now; }
void hal_mic_pwr_en(bool on) { M.pa11 = on; if (on) M.pa11_on_count++; }
bool hal_mute_pin_high(void) { return M.mute_high; }
bool hal_cm5_power_good(void) { return M.pg; }
bool hal_button_raw_down(uint8_t id) { return id < 4 && M.btn[id]; }
void hal_cm5_power(bool on) { M.cm5_power = on; }
void hal_cm5_run_pulse(void) { M.run_pulses++; }
void hal_irq_n(bool a) { M.irq_low = a; }
void hal_uart_write(const uint8_t *b, size_t n) {
    if (M.tx_len + n <= sizeof M.tx) { memcpy(M.tx + M.tx_len, b, n); M.tx_len += n; }
}
void hal_charger_enable(bool en) { M.charger = en; M.charger_writes++; }
int hal_uart_getc(void) { return -1; }
void hal_charger_vreg_mV(uint16_t mV) { M.vreg_mV = mV; M.vreg_writes++; }
void hal_wdt_refresh(void) { M.wdt_refreshes++; }
