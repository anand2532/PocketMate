/* Thin hardware abstraction (ARCHITECTURE.md §12 "thin hal_* layer of our own, so logic is host-testable").
 * target/hal_stm32u0.c implements it on the MCU; test/hal_mock.c implements it on the host. */
#ifndef PM_HAL_H
#define PM_HAL_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

void     hal_init_safe_outputs(void);      /* FIRST call after reset: PA11 MIC_PWR_EN low */
uint32_t hal_millis(void);
void     hal_mic_pwr_en(bool on);           /* PA11 -> U14 TPS22917 EN */
bool     hal_mute_pin_high(void);           /* PA10 MUTE_STATUS_IO, high = muted */
bool     hal_cm5_power_good(void);          /* no sense pin on the netlist: commanded PB1 state */
bool     hal_button_raw_down(uint8_t id);   /* PA0/PA1/PA4/PA5 active low -> true when pressed */
void     hal_cm5_power(bool on);            /* PB1 CM5_5V_EN (Q3/Q2) */
void     hal_cm5_run_pulse(void);           /* PA7 -> Q5 holds CM5 PMIC_Enable low 100 ms */
void     hal_irq_n(bool assert_low);        /* PB3 MCU_IRQ_N open-drain to CM5 GPIO4; Hi-Z when CM5 off */
void     hal_uart_write(const uint8_t *buf, size_t len);   /* dropped while the CM5 rail is off */
int      hal_uart_getc(void);               /* next RX byte or -1 */
void     hal_charger_enable(bool en);       /* BQ25895 CHG_CONFIG over I2C (0x6A) */
void     hal_charger_vreg_mV(uint16_t mV);  /* BQ25895 REG06[7:2] VREG; caller passes a clamped value */
void     hal_wdt_refresh(void);             /* IWDG */
#endif
