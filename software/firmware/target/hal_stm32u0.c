/* STM32U031K8 (QFN32, U9) implementation of pm_hal.h — PROTOTYPE / HARDWARE-ONLY.
 *
 * Register-level so it builds without vendoring STM32CubeU0. Addresses, offsets and bit positions are
 * taken from CMSIS stm32u031xx.h (github.com/STMicroelectronics/cmsis-device-u0) and the reset clock from
 * system_stm32u0xx.c (MSI 4 MHz). Pin assignments are from hardware/kicad/PocketMate.net (U9), read
 * 2026-10-27 16:22 IST. Items still marked VERIFY need RM0503 / DS14581 or a NUCLEO-U031R8.
 * Nothing here has run on silicon. */
#include "pm_hal.h"

#define REG(a) (*(volatile uint32_t *)(a))
/* CMSIS stm32u031xx.h */
#define GPIOA_BASE   0x50000000u
#define GPIOB_BASE   0x50000400u
#define RCC_BASE     0x40021000u
#define RCC_IOPENR   (RCC_BASE + 0x4Cu)     /* bit0 GPIOAEN, bit1 GPIOBEN */
#define RCC_APBENR1  (RCC_BASE + 0x58u)     /* bit17 USART2EN */
#define USART2_BASE  0x40004400u
#define USART_CR1    (USART2_BASE + 0x00u)  /* UE bit0, RE bit2, TE bit3 */
#define USART_BRR    (USART2_BASE + 0x0Cu)
#define USART_ISR    (USART2_BASE + 0x1Cu)  /* RXNE bit5, TXE bit7 */
#define USART_RDR    (USART2_BASE + 0x24u)
#define USART_TDR    (USART2_BASE + 0x28u)
#define IWDG_BASE    0x40003000u
#define IWDG_KR      (IWDG_BASE + 0x00u)
#define IWDG_PR      (IWDG_BASE + 0x04u)
#define IWDG_RLR     (IWDG_BASE + 0x08u)
#define GPIO_MODER(b)  ((b) + 0x00u)
#define GPIO_OTYPER(b) ((b) + 0x04u)
#define GPIO_PUPDR(b)  ((b) + 0x0Cu)
#define GPIO_IDR(b)    ((b) + 0x10u)
#define GPIO_ODR(b)    ((b) + 0x14u)
#define GPIO_BSRR(b)   ((b) + 0x18u)
#define GPIO_AFRL(b)   ((b) + 0x20u)
/* SysTick (architectural, Cortex-M0+) */
#define SYST_CSR 0xE000E010u
#define SYST_RVR 0xE000E014u
#define SYST_CVR 0xE000E018u
#define PM_SYSCLK_HZ 4000000u               /* MSI 4 MHz after reset (system_stm32u0xx.c). No PLL set up. */
#define PM_UART_BAUD 115200u
#define USART2_AF    7u                     /* GPIO_AF7_USART2 exists in the U0 HAL; PA2/PA3 = AF7: VERIFY DS AF table */

/* U9 pins (PocketMate.net) */
#define PA0_BTN_PWR      0u
#define PA1_BTN_ACTION   1u
#define PA2_MCU_TX       2u
#define PA3_MCU_RX       3u
#define PA4_BTN_VOLUP    4u
#define PA5_BTN_VOLDN    5u
#define PA6_CM5_PWRBTN   6u   /* high -> Q4 pulls CM5 PWR_Button (J1-92) low */
#define PA7_CM5_PMIC_OFF 7u   /* high -> Q5 pulls CM5 PMIC_Enable (J1-99) low = CM5 PMIC off */
#define PA10_MUTE        10u
#define PA11_MICEN       11u
#define PB1_CM5_5V_EN    1u   /* Q3 NMOS -> Q2 PMOS gate: high = CM5 5 V on (VERIFY polarity on board) */
#define PB3_MCU_IRQ_N    3u   /* open-drain to CM5 GPIO4 */

static volatile uint32_t ms;
static bool cm5_5v_on;
void SysTick_Handler(void) { ms++; }

static void gpio_mode(uint32_t base, uint32_t pin, uint32_t mode) {
    uint32_t v = REG(GPIO_MODER(base));
    v &= ~(3u << (pin * 2)); v |= (mode & 3u) << (pin * 2);
    REG(GPIO_MODER(base)) = v;
}
static void gpio_pull(uint32_t base, uint32_t pin, uint32_t pull) {
    uint32_t v = REG(GPIO_PUPDR(base));
    v &= ~(3u << (pin * 2)); v |= (pull & 3u) << (pin * 2);
    REG(GPIO_PUPDR(base)) = v;
}
static void gpio_set(uint32_t base, uint32_t pin, bool hi) { REG(GPIO_BSRR(base)) = hi ? (1u << pin) : (1u << (pin + 16)); }
static void gpio_af(uint32_t base, uint32_t pin, uint32_t af) {
    uint32_t v = REG(GPIO_AFRL(base));
    v &= ~(0xFu << (pin * 4)); v |= (af & 0xFu) << (pin * 4);
    REG(GPIO_AFRL(base)) = v;
}
static void delay_ms(uint32_t n) { uint32_t t0 = ms; while ((uint32_t)(ms - t0) < n) { REG(IWDG_KR) = 0xAAAAu; } }

void hal_init_safe_outputs(void) {
    REG(RCC_IOPENR) |= 3u;                                    /* GPIOA + GPIOB clocks */
    /* Drive every output to its safe level BEFORE switching the pin to output mode. */
    gpio_set(GPIOA_BASE, PA11_MICEN, false);       gpio_mode(GPIOA_BASE, PA11_MICEN, 1u);
    gpio_set(GPIOA_BASE, PA6_CM5_PWRBTN, false);   gpio_mode(GPIOA_BASE, PA6_CM5_PWRBTN, 1u);
    gpio_set(GPIOA_BASE, PA7_CM5_PMIC_OFF, false); gpio_mode(GPIOA_BASE, PA7_CM5_PMIC_OFF, 1u);
    gpio_set(GPIOB_BASE, PB1_CM5_5V_EN, false);    gpio_mode(GPIOB_BASE, PB1_CM5_5V_EN, 1u);  /* CM5 off until app decides */
    REG(GPIO_OTYPER(GPIOB_BASE)) |= 1u << PB3_MCU_IRQ_N;      /* open-drain */
    gpio_set(GPIOB_BASE, PB3_MCU_IRQ_N, true);                /* released (Hi-Z) */
    gpio_mode(GPIOB_BASE, PB3_MCU_IRQ_N, 1u);
    gpio_mode(GPIOA_BASE, PA10_MUTE, 0u); gpio_pull(GPIOA_BASE, PA10_MUTE, 0u);   /* driven by Q6 (§3) */
    const uint32_t btn[] = {PA0_BTN_PWR, PA1_BTN_ACTION, PA4_BTN_VOLUP, PA5_BTN_VOLDN};
    for (unsigned i = 0; i < 4; i++) { gpio_mode(GPIOA_BASE, btn[i], 0u); gpio_pull(GPIOA_BASE, btn[i], 1u); }
    /* USART2 PA2/PA3 115200 8N1. PA2 stays an input (Hi-Z) until the CM5 is powered (no back-powering). */
    REG(RCC_APBENR1) |= 1u << 17;
    gpio_af(GPIOA_BASE, PA2_MCU_TX, USART2_AF); gpio_af(GPIOA_BASE, PA3_MCU_RX, USART2_AF);
    gpio_mode(GPIOA_BASE, PA3_MCU_RX, 2u); gpio_pull(GPIOA_BASE, PA3_MCU_RX, 1u);
    gpio_mode(GPIOA_BASE, PA2_MCU_TX, 0u);
    REG(USART_BRR) = (PM_SYSCLK_HZ + PM_UART_BAUD / 2u) / PM_UART_BAUD;   /* 35 -> 114286 baud, -0.8 % */
    REG(USART_CR1) = (1u << 0) | (1u << 2) | (1u << 3);
    /* IWDG: LSI ~32 kHz, /256 -> 125 Hz, reload 500 -> ~4 s (LSI tolerance: VERIFY). Cannot be stopped. */
    REG(IWDG_KR) = 0xCCCCu; REG(IWDG_KR) = 0x5555u; REG(IWDG_PR) = 6u; REG(IWDG_RLR) = 500u; REG(IWDG_KR) = 0xAAAAu;
    REG(SYST_RVR) = PM_SYSCLK_HZ / 1000u - 1u; REG(SYST_CVR) = 0; REG(SYST_CSR) = 7u;
}

uint32_t hal_millis(void) { return ms; }
void hal_mic_pwr_en(bool on) { gpio_set(GPIOA_BASE, PA11_MICEN, on); }
bool hal_mute_pin_high(void) { return (REG(GPIO_IDR(GPIOA_BASE)) >> PA10_MUTE) & 1u; }
bool hal_button_raw_down(uint8_t id) {
    static const uint8_t pin[4] = {PA0_BTN_PWR, PA1_BTN_ACTION, PA4_BTN_VOLUP, PA5_BTN_VOLDN};
    return id < 4 && !((REG(GPIO_IDR(GPIOA_BASE)) >> pin[id]) & 1u);     /* active low */
}

/* No CM5 power-good sense pin exists in the netlist: report the commanded state of PB1 (HARDWARE GAP,
 * see STATUS.md). The app's CM5-up decision therefore relies on HELLO over UART. */
bool hal_cm5_power_good(void) { return cm5_5v_on; }
void hal_cm5_power(bool on) {
    cm5_5v_on = on;
    gpio_set(GPIOB_BASE, PB1_CM5_5V_EN, on);
    gpio_mode(GPIOA_BASE, PA2_MCU_TX, on ? 2u : 0u);           /* TX only while the CM5 rail is up */
}
/* Hard reset: hold CM5 PMIC_Enable low via Q5 for 100 ms [impl] then release (VERIFY minimum on CM5). */
void hal_cm5_run_pulse(void) { gpio_set(GPIOA_BASE, PA7_CM5_PMIC_OFF, true); delay_ms(100); gpio_set(GPIOA_BASE, PA7_CM5_PMIC_OFF, false); }
void hal_irq_n(bool assert_low) { gpio_set(GPIOB_BASE, PB3_MCU_IRQ_N, !(assert_low && cm5_5v_on)); }
void hal_uart_write(const uint8_t *b, size_t n) {
    if (!cm5_5v_on) return;
    for (size_t i = 0; i < n; i++) { while (!(REG(USART_ISR) & (1u << 7))) {} REG(USART_TDR) = b[i]; }
}
int hal_uart_getc(void) { return (REG(USART_ISR) & (1u << 5)) ? (int)(REG(USART_RDR) & 0xFFu) : -1; }
void hal_wdt_refresh(void) { REG(IWDG_KR) = 0xAAAAu; }

/* ---- TODO(hardware): I2C1 (PB6/PB7) to BQ25895 0x6A / MAX17055 0x36 / TCPP03 needs TIMINGR for the
 * chosen clock (generate with CubeMX, not guessed here). Until then the charger runs on its own
 * power-on defaults: CHG_CONFIG=1 and VREG=4.208 V, which is already <= 4.24 V (LTE-safe). ---- */
void hal_charger_enable(bool en) { (void)en; }        /* REG03 bit4 CHG_CONFIG */
void hal_charger_vreg_mV(uint16_t mV) { (void)mV; }   /* REG06[7:2] = (mV-3840)/16 */
