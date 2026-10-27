/* Minimal Cortex-M0+ startup. Only the core exceptions + the IRQs we use are named; the remaining
 * device vector slots are Default_Handler. IRQ numbers for EXTI/USART2/RTC/LPTIM are VERIFY against
 * RM0503 / CMSIS stm32u031xx.h before relying on interrupts (the current main loop polls). */
#include <stdint.h>
extern uint32_t _estack, _sdata, _edata, _etext, _sbss, _ebss;
int main(void);
void Reset_Handler(void);
void Default_Handler(void) { for (;;) {} }
void NMI_Handler(void) __attribute__((weak, alias("Default_Handler")));
void HardFault_Handler(void) __attribute__((weak, alias("Default_Handler")));
void SVC_Handler(void) __attribute__((weak, alias("Default_Handler")));
void PendSV_Handler(void) __attribute__((weak, alias("Default_Handler")));
void SysTick_Handler(void);

__attribute__((section(".isr_vector"), used))
static void (*const vectors[16 + 32])(void) = {
    (void (*)(void))(&_estack), Reset_Handler, NMI_Handler, HardFault_Handler,
    0, 0, 0, 0, 0, 0, 0, SVC_Handler, 0, 0, PendSV_Handler, SysTick_Handler,
    [16 ... 47] = Default_Handler,
};

void Reset_Handler(void) {
    uint32_t *s = &_etext, *d = &_sdata;
    while (d < &_edata) *d++ = *s++;
    for (d = &_sbss; d < &_ebss; ) *d++ = 0;
    main();
    for (;;) {}
}
