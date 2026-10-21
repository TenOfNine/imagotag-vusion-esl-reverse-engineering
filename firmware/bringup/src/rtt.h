/*
 * rtt.h - minimal SEGGER-RTT-compatible text output (one up channel).
 *
 * Written for this project; no SEGGER code is used. The J-Link software
 * finds the control block by its ID string "SEGGER RTT" in RAM (or by the
 * symbol _SEGGER_RTT in the ELF file) and reads the ring buffer.
 */
#ifndef RTT_H
#define RTT_H

#include <stdint.h>

void rtt_init(void);
void rtt_write(const char *data, uint32_t len);
void rtt_puts(const char *s);
void rtt_hex(uint32_t value, unsigned digits);      /* with 0x prefix */
void rtt_hex_raw(uint32_t value, unsigned digits);  /* digits only */
void rtt_dec(uint32_t value);

#endif
