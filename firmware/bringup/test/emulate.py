#!/usr/bin/env python3
"""
emulate.py - run a bring-up image in a CPU emulator and print its RTT output.

Purpose: check the *binary* (vector table, startup, RTT control block,
formatting) before it goes onto real hardware. The emulator executes the
real ARM Thumb instructions with Unicorn; the EFR32 peripherals are faked:

- DEVINFO page with configurable test values (default: the values reported
  for another RFRTx026D in issue #2 — PART 0x00160849, MSIZE 0x00200100 —
  plus made-up PKGINFO/EUI64/CHIPREV values),
- EMU->RSTCAUSE = POR,
- SysTick COUNTFLAG always set (so 1 ms delays pass instantly).

This proves nothing about the real chip; it only shows that the image does
what the source says. Requirements: `pip install unicorn pyelftools`.

Usage:
    python3 test/emulate.py build/bringup_step1.elf [--steps 2000000]

The RTT buffer is drained every --slice instructions, as a J-Link host
would do.
"""

from __future__ import annotations

import argparse
import struct
import sys

from elftools.elf.elffile import ELFFile
from unicorn import (UC_ARCH_ARM, UC_HOOK_MEM_READ, UC_HOOK_MEM_UNMAPPED,
                     UC_MODE_MCLASS, UC_MODE_THUMB, Uc, UcError)
from unicorn.arm_const import UC_ARM_REG_PC, UC_ARM_REG_SP

FLASH, FLASH_SIZE = 0x00000000, 256 * 1024
RAM, RAM_SIZE = 0x20000000, 32 * 1024
DEVINFO = 0x0FE08000
# Without TrustZone defines the GSDK headers use the non-secure aliases
# (EMU_NS_BASE etc.); both alias ranges are mapped.
PERIPH_S, PERIPH_NS, PERIPH_SIZE = 0x40000000, 0x50000000, 0x00100000
SCS = 0xE000E000
SYST_CSR = 0xE000E010

EMU_RSTCAUSE = 0x50004000 + 0x94      # EMU_NS_BASE + RSTCAUSE
SYSCFG_CHIPREV = 0x5007C000 + 0x14    # SYSCFG_NS_BASE + CHIPREV

# DEVINFO register offsets (efr32fg22_devinfo.h, GSDK 4.4.1)
DI = {"INFO": 0x00, "PART": 0x04, "MEMINFO": 0x08, "MSIZE": 0x0C,
      "PKGINFO": 0x10, "EUI64L": 0x48, "EUI64H": 0x4C}


def load(uc: Uc, elf: ELFFile) -> None:
    for seg in elf.iter_segments():
        if seg["p_type"] != "PT_LOAD" or seg["p_filesz"] == 0:
            continue
        uc.mem_write(seg["p_paddr"], seg.data())


def symbol(elf: ELFFile, name: str) -> int:
    for sym in elf.get_section_by_name(".symtab").iter_symbols():
        if sym.name == name:
            return sym["st_value"]
    raise SystemExit(f"symbol {name} not found")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("elf")
    ap.add_argument("--steps", type=int, default=2_000_000,
                    help="instructions to execute")
    ap.add_argument("--slice", type=int, default=20_000,
                    help="instructions between two RTT reads by the 'host'")
    ap.add_argument("--part", type=lambda v: int(v, 0), default=0x00160849)
    ap.add_argument("--msize", type=lambda v: int(v, 0), default=0x00200100)
    args = ap.parse_args()

    with open(args.elf, "rb") as f:
        elf = ELFFile(f)
        uc = Uc(UC_ARCH_ARM, UC_MODE_THUMB | UC_MODE_MCLASS)
        uc.mem_map(FLASH, FLASH_SIZE)
        uc.mem_map(RAM, RAM_SIZE)
        uc.mem_map(DEVINFO, 0x1000)
        uc.mem_map(PERIPH_S, PERIPH_SIZE)
        uc.mem_map(PERIPH_NS, PERIPH_SIZE)
        uc.mem_map(SCS, 0x1000)
        load(uc, elf)
        rtt = symbol(elf, "_SEGGER_RTT")

    values = {"INFO": 0x01000000, "PART": args.part, "MEMINFO": 0x00000803,
              "MSIZE": args.msize, "PKGINFO": 0x00284D00,
              "EUI64L": 0x89ABCDEF, "EUI64H": 0x01234567}
    for name, off in DI.items():
        uc.mem_write(DEVINFO + off, struct.pack("<I", values[name]))
    uc.mem_write(EMU_RSTCAUSE, struct.pack("<I", 0x1))
    uc.mem_write(SYSCFG_CHIPREV, struct.pack("<I", 0x00001D01))

    def systick_read(uc_, access, address, size, value, user):
        if address == SYST_CSR:
            uc_.mem_write(SYST_CSR, struct.pack("<I", 0x00010005))
    uc.hook_add(UC_HOOK_MEM_READ, systick_read, begin=SYST_CSR, end=SYST_CSR + 3)

    def unmapped(uc_, access, address, size, value, user):
        pc_now = uc_.reg_read(UC_ARM_REG_PC)
        print(f"unmapped access at 0x{address:08X} (size {size}) from "
              f"PC=0x{pc_now:08X}")
        return False
    uc.hook_add(UC_HOOK_MEM_UNMAPPED, unmapped)

    sp, pc = struct.unpack("<II", uc.mem_read(FLASH, 8))
    print(f"vector table: SP=0x{sp:08X} PC=0x{pc:08X}")
    uc.reg_write(UC_ARM_REG_SP, sp)

    # Run in slices and drain the RTT up buffer after each slice, like the
    # J-Link host does (it writes RdOff). This also exercises the wrap-around.
    out = bytearray()
    slices = max(1, args.steps // args.slice)
    for i in range(slices):
        try:
            uc.emu_start(pc, 0xFFFFFFFF, count=args.slice)
        except UcError as err:
            print(f"FAIL: emulation stopped: {err}")
            return 1
        pc = uc.reg_read(UC_ARM_REG_PC) | 1
        cb = uc.mem_read(rtt, 48)
        ident = bytes(cb[:16]).split(b"\0")[0].decode(errors="replace")
        if ident != "SEGGER RTT":
            continue
        _, buf, size, wr, rd, _ = struct.unpack("<IIIIII", cb[24:48])
        if wr >= rd:
            out += uc.mem_read(buf + rd, wr - rd)
        else:
            out += uc.mem_read(buf + rd, size - rd) + uc.mem_read(buf, wr)
        uc.mem_write(rtt + 24 + 16, struct.pack("<I", wr))   # RdOff = WrOff

    print(f"stopped at PC=0x{uc.reg_read(UC_ARM_REG_PC):08X} after "
          f"{slices * args.slice} instructions")
    print(f"RTT control block at 0x{rtt:08X}, id {ident!r}, "
          f"{len(out)} bytes read")
    if ident != "SEGGER RTT":
        print("FAIL: RTT ID not found")
        return 1
    print("----- RTT channel 0 -----")
    sys.stdout.write(out.decode(errors="replace").replace("\r\n", "\n"))
    print("----- end -----")
    return 0


if __name__ == "__main__":
    sys.exit(main())
