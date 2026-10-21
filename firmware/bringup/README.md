# Bring-up images for the RFRTx026D (EFR32FG22)

Bare-metal test images for the bring-up steps in
`docs/firmware-plan.md` §7.2. One step at a time; each step has a check
that must pass before the next one is built.

| Step | Status | What it does |
|---|---|---|
| 1 | **written, tested in an emulator only** | prints chip identification over RTT, touches no GPIO |
| 2 | not written | panel supply, reset, BUSY |
| 3 | not written | OTP read |
| 4 | not written | first image |

---

## Step 1 — chip identification

### What it does

- Prints over SEGGER RTT (channel 0): DEVINFO `INFO`, `PART` (decoded
  family/part), `MEMINFO`, `MSIZE` (**flash and SRAM size** → F-17),
  `PKGINFO` (package, pin count, temperature grade), `EUI64`,
  `SYSCFG->CHIPREV` and the reset cause `EMU->RSTCAUSE`.
- Repeats the report every 10 s and prints `alive <n> s` in between, so a
  late RTT connection still sees everything.

### What it does not do

- **No GPIO is touched.** Every pin stays in its reset state (disabled).
  The pin map from issue #2 is not used in this step.
- No clock, DC-DC, radio or flash setup; it runs from the reset clock
  (FSRCO, 20 MHz). It never writes to flash, the UserData page or the lock
  configuration.

### Preconditions (do not skip)

1. **Never on tag 01** (`CLAUDE.md` §5.1).
2. M-011 done and the lock state known:
   - **not locked:** back up the whole original flash **first** (kept
     outside the repo), e.g. `commander readmem --range 0x0:0x40000
     --outfile tag02_flash_backup.bin` for a 256 kB part (use `0x80000`
     for 512 kB; check the syntax with `commander readmem --help`);
   - **locked:** only after the F-15 decision is written into
     `CLAUDE.md` and the unlock was done.
3. **FPC unplugged** for this step. Reason: with all GPIOs disabled, the
   gate of the panel supply switch (`XDt`, PC06 per issue #2) and the
   panel lines float; whether the board pulls them to a safe level is not
   known. The tag already ran without a panel during
   `captures/2026-09-23_tag02_boot-overview_2MHz.sr`.

### Flash and read the output (Windows)

Wiring as for M-011 (SWCLK, SWDIO, GND, VTref to battery plus; no 5 V from
the J-Link), battery in.

1. Flash, for example with Simplicity Commander:
   ```
   commander flash bringup_step1.hex
   ```
   (add `--device EFR32FG22C121F256GM40` if asked; the image is the same
   for the 512 kB part).
2. Start **J-Link RTT Viewer**: connection USB, target device from the
   J-Link list (search `EFR32FG22`), interface SWD, speed 1000 kHz, RTT
   control block "Auto Detection" (or search range
   `0x20000000 0x8000`).
3. Copy the full text of one report and send it.

Expected shape (values below are the **emulator's test values**, not
real ones):

```
=== RFRTx026D bring-up step 1: chip identification ===
GPIO: none touched in this step (pin map from issue #2 is UNVERIFIED)
INFO       0x01000000
PART       0x00160849  -> EFR32FG22 C121 (DEVICENUM 2121)
MEMINFO    0x00000803  -> FLASHPAGESIZE field 3
MSIZE      0x00200100  -> flash 256 kB, SRAM 32 kB
PKGINFO    0x00284D00  -> QFN40, -40..85 C
EUI64      0x0123456789ABCDEF
CHIPREV    0x00001D01  -> major 1, minor 1
RSTCAUSE   0x00000001  -> POR
=== end of report ===
alive 1 s
```

The values read on the real tag are a maintainer `[MEASUREMENT]`
(instrument: the chip itself via J-Link RTT) and go into
`hardware/measurements.md`.

### Decoding notes

- `[RESEARCH]` Register layout and field masks: GSDK 4.4.1 headers
  (`efr32fg22_devinfo.h`, `efr32fg22_emu.h`, `efr32fg22_syscfg.h`).
- `[ASSUMPTION]` `DEVICENUM` encodes the part as letter + three digits
  (`'A' + n/1000`, `n % 1000`). Supported by issue #2: `PART`
  `0x00160849` → DEVICENUM 2121 → `C121` for a part marked `C121GG`.
  **Test:** our own report vs. the marking `C121GG`.
- `FLASHPAGESIZE` is printed raw. `[ASSUMPTION]` page size =
  2^(field + 10) bytes (field 3 → 8 kB, the xG22 page size OEPL assumes).

---

## Build (Linux / WSL)

```bash
sudo apt install gcc-arm-none-eabi make     # or the Arm GNU Toolchain
./fetch_sdk.sh                               # device + CMSIS headers (Zlib/Apache) into ./sdk
make                                         # build/bringup_step1.{elf,hex,bin,map}
```

`fetch_sdk.sh` sparse-clones `SiliconLabs/gecko_sdk` at tag `v4.4.1`
(commit `911f6cd`) — only `platform/Device/SiliconLabs/EFR32FG22` and
`platform/CMSIS/Core/Include`. No SDK file is committed. The startup code,
linker script and RTT output are written for this project
(`src/startup.c`, `efr32fg22_bringup.ld`, `src/rtt.c`) — no SEGGER or
Silicon Labs startup code is used.

Built images are not committed: `.gitignore` excludes `*.hex`/`*.elf` on
purpose, so that no original firmware lands in the repo by accident.

## Test in an emulator

```bash
pip install unicorn pyelftools
python3 test/emulate.py build/bringup_step1.elf --steps 2500000
```

`test/emulate.py` runs the real ARM code in Unicorn with faked DEVINFO,
EMU, SYSCFG and SysTick, and drains the RTT buffer like a J-Link host. It
shows that vector table, startup, RTT and formatting work; it says
**nothing** about the real chip.
