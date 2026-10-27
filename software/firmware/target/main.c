/* Bare-metal event loop (§12). Stop2 entry between events is TODO(hardware): needs EXTI/LPTIM/RTC wake
 * configuration verified on the NUCLEO-U031R8. The loop below polls at 1 ms. */
#include "pm_app.h"
#include "pm_hal.h"

int main(void) {
    pm_app_init(BOOT_POR);          /* hal_init_safe_outputs() runs first inside: PA11 low */
    uint32_t last = 0;
    for (;;) {
        uint32_t now = hal_millis();
        for (int c; (c = hal_uart_getc()) >= 0;) pm_app_rx_byte((uint8_t)c);   /* polled; RX IRQ ring: TODO */
        if (now != last) { last = now; pm_app_tick(now); }
        /* TODO(hardware): WFI / Stop2 when idle (EXTI on PA0/PA1/PA10, USART2 wake) */
    }
}
