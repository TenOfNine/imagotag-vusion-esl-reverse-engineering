/*
 * rtt.c - minimal SEGGER-RTT-compatible text output (one up channel).
 *
 * Layout of the control block as expected by the J-Link software:
 * 16-byte ID, number of up/down buffers, then one descriptor per buffer
 * (name, buffer pointer, size, write offset, read offset, flags).
 * The target only writes WrOff of the up buffer, the host only RdOff.
 * When the buffer is full, the rest of a message is dropped (no blocking),
 * so the firmware never hangs when no debugger is attached.
 */
#include "rtt.h"

#include <stddef.h>

#define RTT_UP_SIZE   1024u
#define RTT_DOWN_SIZE 16u

typedef struct {
  const char *name;
  char *buffer;
  uint32_t size;
  volatile uint32_t wr_off;
  volatile uint32_t rd_off;
  uint32_t flags;
} rtt_ring_t;

typedef struct {
  char id[16];
  int32_t max_up;
  int32_t max_down;
  rtt_ring_t up[1];
  rtt_ring_t down[1];
} rtt_cb_t;

/* Name kept so that J-Link tools can also locate it via the ELF symbol. */
rtt_cb_t _SEGGER_RTT;

static char up_buffer[RTT_UP_SIZE];
static char down_buffer[RTT_DOWN_SIZE];

static inline void barrier(void)
{
  __asm volatile ("dmb" ::: "memory");
}

void rtt_init(void)
{
  static const char name[] = "Terminal";
  static const char id[] = "SEGGER RTT";
  rtt_cb_t *cb = &_SEGGER_RTT;

  cb->max_up = 1;
  cb->max_down = 1;
  cb->up[0] = (rtt_ring_t){ name, up_buffer, RTT_UP_SIZE, 0, 0, 0 };
  cb->down[0] = (rtt_ring_t){ name, down_buffer, RTT_DOWN_SIZE, 0, 0, 0 };
  barrier();

  /* Write the ID last, back to front, so the host never finds a
     half-initialised control block. */
  for (int i = (int)sizeof(id) - 1; i >= 0; i--) {
    cb->id[i] = id[i];
  }
  barrier();
}

void rtt_write(const char *data, uint32_t len)
{
  rtt_ring_t *ring = &_SEGGER_RTT.up[0];
  uint32_t wr = ring->wr_off;
  uint32_t rd = ring->rd_off;
  uint32_t free_bytes = (rd > wr) ? (rd - wr - 1u) : (ring->size - (wr - rd) - 1u);

  if (len > free_bytes) {
    len = free_bytes;
  }
  while (len--) {
    ring->buffer[wr++] = *data++;
    if (wr == ring->size) {
      wr = 0;
    }
  }
  barrier();
  ring->wr_off = wr;
}

void rtt_puts(const char *s)
{
  uint32_t len = 0;
  while (s[len] != '\0') {
    len++;
  }
  rtt_write(s, len);
}

void rtt_hex_raw(uint32_t value, unsigned digits)
{
  char out[8];
  unsigned n = 0;
  if (digits > 8u) {
    digits = 8u;
  }
  for (int shift = (int)(digits * 4u) - 4; shift >= 0; shift -= 4) {
    out[n++] = "0123456789ABCDEF"[(value >> shift) & 0xFu];
  }
  rtt_write(out, n);
}

void rtt_hex(uint32_t value, unsigned digits)
{
  rtt_write("0x", 2);
  rtt_hex_raw(value, digits);
}

void rtt_dec(uint32_t value)
{
  char out[10];
  unsigned n = sizeof(out);
  do {
    out[--n] = (char)('0' + value % 10u);
    value /= 10u;
  } while (value != 0u);
  rtt_write(&out[n], sizeof(out) - n);
}
