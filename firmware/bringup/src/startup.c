/*
 * startup.c - minimal Cortex-M33 startup for the bring-up images.
 *
 * Copies .data, clears .bss and calls main(). No clock, DC-DC or watchdog
 * setup: after reset the EFR32FG22 runs from FSRCO (20 MHz) and the
 * watchdog is disabled (`_CMU_SYSCLKCTRL_RESETVALUE`, `_WDOG_EN_RESETVALUE`
 * in the GSDK 4.4.1 device headers).
 */
#include <stdint.h>

#include "em_device.h"

extern uint32_t __data_load__;
extern uint32_t __data_start__;
extern uint32_t __data_end__;
extern uint32_t __bss_start__;
extern uint32_t __bss_end__;
extern uint32_t __StackTop;

int main(void);

void Reset_Handler(void);
void Default_Handler(void);

void Reset_Handler(void)
{
  uint32_t *src = &__data_load__;
  for (uint32_t *dst = &__data_start__; dst < &__data_end__; ) {
    *dst++ = *src++;
  }
  for (uint32_t *dst = &__bss_start__; dst < &__bss_end__; ) {
    *dst++ = 0u;
  }
  (void)main();
  for (;;) {
  }
}

/* No interrupt is enabled in the bring-up images; any exception ends here
   and can be inspected with the debugger. */
void Default_Handler(void)
{
  for (;;) {
  }
}

typedef void (*vector_t)(void);

__attribute__((section(".vectors"), used))
const vector_t vector_table[16 + EXT_IRQ_COUNT] = {
  [0] = (vector_t)&__StackTop,
  [1] = Reset_Handler,
  [2 ... 15] = Default_Handler,
  [16 ... 16 + EXT_IRQ_COUNT - 1] = Default_Handler,
};
