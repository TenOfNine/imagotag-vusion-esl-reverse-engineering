/*
 * efr32fg22_bringup.ld - linker script for the bare-metal bring-up images.
 *
 * The image starts at 0x00000000 (no bootloader). FLASH is limited to the
 * smaller of the two candidate parts (256 kB, see open question F-17), so
 * the same image runs on a 256 kB and on a 512 kB device.
 */
MEMORY
{
  FLASH (rx)  : ORIGIN = 0x00000000, LENGTH = 256K
  RAM   (rwx) : ORIGIN = 0x20000000, LENGTH = 32K
}

ENTRY(Reset_Handler)

SECTIONS
{
  .text :
  {
    KEEP(*(.vectors))
    *(.text*)
    *(.rodata*)
    . = ALIGN(4);
  } > FLASH

  .ARM.exidx :
  {
    *(.ARM.exidx*)
  } > FLASH

  .data :
  {
    . = ALIGN(4);
    __data_start__ = .;
    *(.data*)
    . = ALIGN(4);
    __data_end__ = .;
  } > RAM AT > FLASH

  __data_load__ = LOADADDR(.data);

  .bss (NOLOAD) :
  {
    . = ALIGN(4);
    __bss_start__ = .;
    *(.bss*)
    *(COMMON)
    . = ALIGN(4);
    __bss_end__ = .;
  } > RAM

  __StackTop = ORIGIN(RAM) + LENGTH(RAM);

  ASSERT(__bss_end__ + 4096 <= __StackTop, "less than 4 kB left for the stack")
}
