# Progress

A checklist of what has been done and what is still open. Created 2026-09-25
at the maintainer's request.

**How this file relates to the others:**
- `HISTORY.md` is the chronological long-term memory and is append-only.
  This file is a **living checklist**: items are ticked and moved when their
  state changes. Details, evidence and dates stay in `HISTORY.md`.
- Evidence markers follow `CLAUDE.md` §3. A ticked item means "done", not
  "confirmed". Check its marker.
- Owner: **M** = maintainer (hardware, measurements), **C** = Claude Code
  (analysis, docs, code).

Last updated: 2026-09-25 (session 4, housekeeping done).

---

## Where we stand in one paragraph

The FPC pinout is measured, and the roles of the six signal lines are
established from captures. The tag's boot sequence is decoded (panel
ID/OTP read, 800 × 480 assumed). The tag never refreshes without its base
station, so the display init cannot be sniffed. **Path B is chosen:** custom
firmware on the original EFR32. Two things block the firmware: the **SWD
lock state** (M-011 / F-15) and the **EFR32 pin map** (M-012). The photos
suggest that the display lines end on QFN pads 1–8 (`[ASSUMPTION]`), and
no OpenEPaperLink pin map matches our board.

---

## Done

### Setup and project rules
- [x] Repo onboarding, write access, direct push to `main` (C, 2026-09-23)
- [x] Working rules in `CLAUDE.md`: chat in German, repo in English; ask
      before large changes (M/C, 2026-09-23)
- [x] Whole repo translated to English, German `HISTORY` archived in
      `docs/archive/HISTORY.de.md` (C, 2026-09-23)
- [x] Instruments documented in `TOOLS.md` (SLogic Combo 8 on Windows,
      OWON HDS242, FTDI adapter "FTDI1232" (exact chip unclear, probably
      UART only), soldering station, no hot air, no FPC extension) (M/C)
- [x] Tag numbering agreed: **tag 01 = untouched reference unit**,
      tag 02 = work tag (M, 2026-09-23)

### Hardware identification
- [x] Board `RFRTx026D`, MCU EFR32FG22, panel `EL074TS1` `[PHOTO]`
- [x] Product: VUSION 7.4 BWRY GU140, EDG3-0740A (maintainer statement).
      Four colours B/W/R/Y remain `[ASSUMPTION]` (F-13)
- [x] EFR32 package is **QFN40** `[PHOTO]` (M-003)
- [x] NFC: write-locked NXP NTAG-type tag with a Decathlon URL
      `[CAPTURE]`/screenshot (M-010)

### FPC pinout (M-001) `[MEASUREMENT]`
- [x] Pin 1 towards board centre, pin 24 at the board edge, contacts face down
- [x] GND on pins 3, 8, 17; GDR pin 2 → `KM` SOT-23 leg 1; pin 3 (RESE) → `KM` leg 2
- [x] Pins 15/16 (VDDIO/VCI) bridged, 9.98 kΩ to GND, → leg 3 of SOT-23 `XDt`;
      no FPC pin connects to battery plus
- [x] Signal lines on pins 9–14; diode signatures on pins 21/23

### Captures and decoding `[CAPTURE]`
- [x] Capture wiring on tag 02 (M-004), colour mapping documented
- [x] Analyser limit found: at ≥ 20 MSa/s only D0–D3 are recorded (M-008)
- [x] Signal roles: 9 BUSY, 10 RST, 11 D/C, 12 CS, 13 SCK, 14 bidirectional SDA
- [x] Boot sequence decoded (82 frames): `70` → `0D 04 01`, `90`, `A2`,
      `92` → 70-byte OTP read incl. `SPQ0KX` and `01 E0 03 20` (→ 800 × 480,
      `[ASSUMPTION]`)
- [x] Opcodes match UltraChip UC81xx → controller family `[ASSUMPTION]`
- [x] No refresh after boot (134 s, `…_boot-long_2MHz.sr`), none on NFC read (M-010)
- [x] Tools: `analysis/decode_spi.py`, `sr_overview.py`, `sr_spi_frames.py`

### Firmware concept (path B)
- [x] Decision path B: custom firmware on the original EFR32 (M, 2026-09-23)
- [x] Plan with lock-state table and bring-up steps 0–5:
      `docs/firmware-plan.md` (C)
- [x] SWD pins researched: pin 22 = PA01 SWCLK, pin 23 = PA02 SWDIO
      `[RESEARCH]`, from search snippets only (C)
- [x] OpenEPaperLink `Tag_FW_EFR32xG22` evaluated as a base (C)

### PCB traces from photos
- [x] Top and bottom photos registered via three holes
      (`analysis/register_photos.py`), set 2 with residual ≈ 0.12 mm (C)
- [x] Partial netlist `docs/netlist-from-photos.md`: FPC 9–14 bundle →
      vias V1–V8 → EFR32 **left pad column** `[PHOTO]` (C, 2026-09-24)
- [x] Error "pins 11–20" found and corrected (C, 2026-09-24)
- [x] OEPL pin maps compared with our board: **no match**
      (`docs/oepl-pin-comparison.md`) (C, 2026-09-25)

---

## Open — maintainer (hardware)

Order = suggested priority.

- [ ] **M-011 — SWD access and lock check** (blocks everything in path B)
  - [ ] confirm the vias for pin 22 (SWCLK) / pin 23 (SWDIO), unpowered continuity
  - [ ] J-Link: **only** `commander device info` + `commander security status`.
        No unlock, no erase, no flash (`CLAUDE.md` §5.2)
  - [ ] if unlocked: read out and back up the flash (backup stays **outside** the repo)
- [ ] **M-012 — EFR32 pin map** (unpowered; FPC carries ±20 V in operation → FPC unplugged)
  - [ ] FPC 9–14 → QFN pads **1–8** (continuity from the capture wires)
  - [ ] `XDt` leg 1 (gate) → QFN pad
  - [ ] both LEDs → QFN pad / supply
  - [ ] SO-8 `8K417`: all 8 pins → QFN pad / GND / VDD / NFC coil (SPI flash?)
  - [ ] **Document check:** compare the QFN40 table in
        `docs/oepl-pin-comparison.md` with the EFR32FG22 datasheet
- [ ] **F-15 decision** (only if the chip is locked): may the firmware of
      **tag 02** be erased? It must be written into `CLAUDE.md` before any
      unlock
- [ ] M-009 — re-capture the boot at 40 MSa/s, 4 channels (medium priority)
- [ ] M-005 — `XDt` supply switch in detail (low; path A only)

## Open — Claude Code (analysis, docs, code)

- [ ] After M-011: evaluate the lock state, update `docs/firmware-plan.md`
- [ ] After M-012 + datasheet check: write the board definition
      (OEPL dev slot `0xF0…0xFA`), including USART routing (display
      probably on port C → USART0?) and BUSY polling
- [ ] Bring-up firmware steps 1–3 (LED/RTT, panel power + reset + BUSY,
      replay of the boot reads), verified against the boot capture
- [ ] Toolchain: set up GSDK 4.4.1 / `slc` (silabs.com is blocked from the
      container → maintainer download or an alternative); a bare-metal
      project with `gcc-arm-none-eabi` for steps 1–3 is possible
- [ ] Step 4 (init + test refresh) only after step 3 succeeds, tag 02 only
- [ ] If the firmware is readable: extract the init/refresh sequence from the binary (F-04)
- [ ] M-009 evaluation as soon as the capture arrives

## Open — housekeeping (C, small doc fixes)

- [x] Stale statements corrected (C, 2026-09-25): `open-questions.md`
      (F-01/F-07/F-08/F-09 ✅, updates to F-02/03/04/05/06/10/14/16,
      "Answered" index), `README.md`, `docs/hardware.md`, `docs/pinout.md`
      header, `firmware/README.md`, M-010 decision row
- [x] `CLAUDE.md`: rules for `progress.md` (§4) and new files in §7
      (maintainer approved, 2026-09-25)

---

## Decisions still with the maintainer

| # | Decision | Blocks |
|---|---|---|
| F-15 | Erase the original firmware on tag 02 if the chip is locked? | flashing |

## Safety reminders (from `CLAUDE.md` §5)

- Tag 01 is never touched.
- No unlock before F-15 is decided.
- Check FPC-related points **unpowered** first; the logic analyser tolerates max. 3.6 V.
