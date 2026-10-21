/*
 * main.c - RFRTx026D bring-up, step 1: identify the chip.
 *
 * See ../README.md and docs/firmware-plan.md section 7.2.
 *
 * This step touches NO GPIO at all: every pin stays in its reset state
 * (disabled). The only peripherals used are SysTick (core), DEVINFO
 * (read-only), EMU->RSTCAUSE (read-only) and SYSCFG->CHIPREV (read-only,
 * its bus clock is switched on for that).
 *
 * Output goes to SEGGER RTT channel 0 (J-Link RTT Viewer).
 */
#include <stdint.h>

#include "em_device.h"
#include "rtt.h"

#define FSRCO_HZ 20000000u  /* SYSCLK after reset, GSDK 4.4.1 system_efr32fg22.c */

static void delay_ms(uint32_t ms)
{
  SysTick->LOAD = FSRCO_HZ / 1000u - 1u;
  SysTick->VAL = 0u;
  SysTick->CTRL = SysTick_CTRL_CLKSOURCE_Msk | SysTick_CTRL_ENABLE_Msk;
  while (ms--) {
    while ((SysTick->CTRL & SysTick_CTRL_COUNTFLAG_Msk) == 0u) {
    }
  }
  SysTick->CTRL = 0u;
}

static void field(const char *name, uint32_t raw)
{
  rtt_puts(name);
  rtt_hex(raw, 8);
}

static void print_part(uint32_t part)
{
  uint32_t devnum = (part & _DEVINFO_PART_DEVICENUM_MASK) >> _DEVINFO_PART_DEVICENUM_SHIFT;
  uint32_t famnum = (part & _DEVINFO_PART_FAMILYNUM_MASK) >> _DEVINFO_PART_FAMILYNUM_SHIFT;
  uint32_t family = (part & _DEVINFO_PART_FAMILY_MASK) >> _DEVINFO_PART_FAMILY_SHIFT;
  const char *fam = "??";

  switch (family) {
    case _DEVINFO_PART_FAMILY_FG: fam = "FG"; break;
    case _DEVINFO_PART_FAMILY_MG: fam = "MG"; break;
    case _DEVINFO_PART_FAMILY_BG: fam = "BG"; break;
    case _DEVINFO_PART_FAMILY_PG: fam = "PG"; break;
    default: break;
  }

  field("PART       ", part);
  rtt_puts("  -> EFR32");
  rtt_puts(fam);
  rtt_dec(famnum);
  rtt_puts(" ");
  /* Decoding of DEVICENUM as letter + 3 digits is an assumption,
     see README.md; the raw value is printed as well. */
  char letter = (char)('A' + devnum / 1000u);
  rtt_write(&letter, 1);
  rtt_dec(devnum % 1000u);
  rtt_puts(" (DEVICENUM ");
  rtt_dec(devnum);
  rtt_puts(")\r\n");
}

static void print_memory(uint32_t meminfo, uint32_t msize)
{
  uint32_t page = (meminfo & _DEVINFO_MEMINFO_FLASHPAGESIZE_MASK) >> _DEVINFO_MEMINFO_FLASHPAGESIZE_SHIFT;
  uint32_t flash_kb = (msize & _DEVINFO_MSIZE_FLASH_MASK) >> _DEVINFO_MSIZE_FLASH_SHIFT;
  uint32_t sram_kb = (msize & _DEVINFO_MSIZE_SRAM_MASK) >> _DEVINFO_MSIZE_SRAM_SHIFT;

  field("MEMINFO    ", meminfo);
  rtt_puts("  -> FLASHPAGESIZE field ");
  rtt_dec(page);
  rtt_puts("\r\n");
  field("MSIZE      ", msize);
  rtt_puts("  -> flash ");
  rtt_dec(flash_kb);
  rtt_puts(" kB, SRAM ");
  rtt_dec(sram_kb);
  rtt_puts(" kB\r\n");
}

static void print_package(uint32_t pkginfo)
{
  uint32_t pins = (pkginfo & _DEVINFO_PKGINFO_PINCOUNT_MASK) >> _DEVINFO_PKGINFO_PINCOUNT_SHIFT;
  uint32_t type = (pkginfo & _DEVINFO_PKGINFO_PKGTYPE_MASK) >> _DEVINFO_PKGINFO_PKGTYPE_SHIFT;
  uint32_t temp = (pkginfo & _DEVINFO_PKGINFO_TEMPGRADE_MASK) >> _DEVINFO_PKGINFO_TEMPGRADE_SHIFT;
  const char *type_s = "?";
  const char *temp_s = "?";

  switch (type) {
    case _DEVINFO_PKGINFO_PKGTYPE_QFN: type_s = "QFN"; break;
    case _DEVINFO_PKGINFO_PKGTYPE_QFP: type_s = "QFP"; break;
    case _DEVINFO_PKGINFO_PKGTYPE_BGA: type_s = "BGA"; break;
    case _DEVINFO_PKGINFO_PKGTYPE_WLCSP: type_s = "WLCSP"; break;
    default: break;
  }
  switch (temp) {
    case _DEVINFO_PKGINFO_TEMPGRADE_N40TO85: temp_s = "-40..85 C"; break;
    case _DEVINFO_PKGINFO_TEMPGRADE_N40TO105: temp_s = "-40..105 C"; break;
    case _DEVINFO_PKGINFO_TEMPGRADE_N40TO125: temp_s = "-40..125 C"; break;
    case _DEVINFO_PKGINFO_TEMPGRADE_N0TO70: temp_s = "0..70 C"; break;
    default: break;
  }

  field("PKGINFO    ", pkginfo);
  rtt_puts("  -> ");
  rtt_puts(type_s);
  rtt_dec(pins);
  rtt_puts(", ");
  rtt_puts(temp_s);
  rtt_puts("\r\n");
}

static void print_reset_cause(uint32_t cause)
{
  static const struct { uint32_t bit; const char *name; } names[] = {
    { EMU_RSTCAUSE_POR, "POR" },
    { EMU_RSTCAUSE_PIN, "PIN" },
    { EMU_RSTCAUSE_EM4, "EM4" },
    { EMU_RSTCAUSE_WDOG0, "WDOG0" },
    { EMU_RSTCAUSE_LOCKUP, "LOCKUP" },
    { EMU_RSTCAUSE_SYSREQ, "SYSREQ" },
    { EMU_RSTCAUSE_DVDDBOD, "DVDDBOD" },
    { EMU_RSTCAUSE_DVDDLEBOD, "DVDDLEBOD" },
    { EMU_RSTCAUSE_DECBOD, "DECBOD" },
    { EMU_RSTCAUSE_AVDDBOD, "AVDDBOD" },
    { EMU_RSTCAUSE_IOVDD0BOD, "IOVDD0BOD" },
    { EMU_RSTCAUSE_DCI, "DCI" },
    { EMU_RSTCAUSE_VREGIN, "VREGIN" },
  };

  field("RSTCAUSE   ", cause);
  rtt_puts("  ->");
  for (unsigned i = 0; i < sizeof(names) / sizeof(names[0]); i++) {
    if (cause & names[i].bit) {
      rtt_puts(" ");
      rtt_puts(names[i].name);
    }
  }
  rtt_puts("\r\n");
}

static void print_chiprev(void)
{
  CMU->CLKEN0_SET = CMU_CLKEN0_SYSCFG;
  uint32_t rev = SYSCFG->CHIPREV;

  field("CHIPREV    ", rev);
  rtt_puts("  -> major ");
  rtt_dec((rev & _SYSCFG_CHIPREV_MAJOR_MASK) >> _SYSCFG_CHIPREV_MAJOR_SHIFT);
  rtt_puts(", minor ");
  rtt_dec((rev & _SYSCFG_CHIPREV_MINOR_MASK) >> _SYSCFG_CHIPREV_MINOR_SHIFT);
  rtt_puts("\r\n");
}

static void print_report(uint32_t reset_cause)
{
  rtt_puts("\r\n=== RFRTx026D bring-up step 1: chip identification ===\r\n");
  rtt_puts("GPIO: none touched in this step (pin map from issue #2 is UNVERIFIED)\r\n");
  field("INFO       ", DEVINFO->INFO);
  rtt_puts("\r\n");
  print_part(DEVINFO->PART);
  print_memory(DEVINFO->MEMINFO, DEVINFO->MSIZE);
  print_package(DEVINFO->PKGINFO);
  field("EUI64      ", DEVINFO->EUI64H);
  rtt_hex_raw(DEVINFO->EUI64L, 8);
  rtt_puts("\r\n");
  print_chiprev();
  print_reset_cause(reset_cause);
  rtt_puts("=== end of report ===\r\n");
}

int main(void)
{
  /* Read once: the value is kept until the next reset. */
  uint32_t reset_cause = EMU->RSTCAUSE;

  rtt_init();
  print_report(reset_cause);

  /* Repeat the report every 10 s, so an RTT viewer that attaches late
     still sees it; print a heartbeat in between. */
  for (uint32_t seconds = 1u; ; seconds++) {
    delay_ms(1000u);
    if (seconds % 10u == 0u) {
      print_report(reset_cause);
    } else {
      rtt_puts("alive ");
      rtt_dec(seconds);
      rtt_puts(" s\r\n");
    }
  }
}
