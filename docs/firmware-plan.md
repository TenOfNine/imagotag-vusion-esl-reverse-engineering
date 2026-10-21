# Custom firmware for the EFR32 — plan

Status: **concept, nothing built yet** (2026-09-23). Decisions still open are
marked **DECISION**.

> **Update 2026-10-21 (session 5 review):**
> - Display driver: the panel COG is (`[ASSUMPTION]`, strongly supported)
>   the Pervasive Displays "BWRY Medium" type; all panel-specific init
>   values are in our own boot capture. Init/refresh sequence and sources:
>   `panel-protocol.md`. The `ucbwry`/UC8179 assumption in section 2 is
>   superseded — the `ucbwry` init must **not** be used on this panel.
> - Pin map: a third-party map exists (issue #2 of this repo); M-012 now
>   verifies it (`measurement-requests.md`).
> - Flash size may be **256 kB**, not 512 kB (F-17) → linker script and
>   OEPL build must follow `commander device info`.
> - A third party announced an OEPL port for this board (board type, PD
>   BWRY Medium driver, 256 kB build); not in OEPL as of release v43
>   (2026-10-11).
> - Section 1 (lock state vs. §5.2) still applies; new arguments in
>   `open-questions.md` F-15.
> - Later 2026-10-21: the step-4 sequence comes from Pervasive Displays'
>   own driver (`panel-protocol.md` §7): OTP read of all 112 bytes with
>   chip-ID and bank check, init from the OTP, `10` + 96,000 bytes, `04`,
>   `12 00`, then the turn-off DC/DC sequence with its 6 s wait before
>   the panel supply is cut. Reimplemented, not copied (licence).

Maintainer decision (2026-09-23): the goal is a firmware that runs **on the
original EFR32FG22** of the tag. No ESP32, no hardware swap — the board stays
standard (this is path B from `open-questions.md` F-09).

---

## 1. The blocker first: lock state vs. safety rule 5.2

Everything depends on the result of the SWD lock check (F-05, M-011).

| Lock state | What flashing means | Consequence |
|---|---|---|
| **Not locked** | Original firmware can be **read and saved** first, then overwritten | Best case: full backup, init sequence recoverable from the binary, no rule conflict |
| **Locked**, unauthenticated unlock allowed | `commander device unlock` **erases** the original firmware | Conflicts with `CLAUDE.md` §5.2 ("sniff before unlock"): the display init/refresh was **never** captured and cannot be (the tag only refreshes on radio command, M-010 negative) |
| **Locked**, unlock disabled | Chip cannot be reflashed via SWD at all | Path B is dead for this board; back to path A or give up |

**DECISION (maintainer):** if the chip is locked — do we accept losing the
original firmware **on tag 02 only** (tag 01 and the others stay untouched)?
That is a deliberate exception to §5.2 and has to be written into
`CLAUDE.md` before any unlock. Claude Code will not suggest the unlock
without that decision.

What we lose on unlock: the only complete source of the correct init
sequence, waveform selection and refresh timing for this exact panel.
What we keep: the boot captures (pinout, panel OTP read, BUSY/RST timing),
which are enough to verify our own SPI access to the panel.

---

## 2. Base: OpenEPaperLink `Tag_FW_EFR32xG22`

`[RESEARCH]` https://github.com/OpenEPaperLink/Tag_FW_EFR32xG22 (read from a
shallow clone, 2026-09-23):

- Complete tag firmware for EFR32xG22 (BG22/FG22/MG22): OEPL radio
  protocol, image decompression, drawing, NVM, LEDs, NFC, debug output,
  OTA bootloader.
- Built with Gecko SDK 4.4.1 + `slc` + ARM GCC ≥ 12, or in their Docker
  image.
- Board support is a **table of hardware types** (`oepl_efr32_hwtypes.c`):
  per board a pin map for display SPI (MOSI, MISO, SCK, nCS, DC, BUSY,
  nRST, enable), external SPI flash, LEDs, NFC, buttons, debug UART.
  Development slots `0xF0…0xFA` exist for new boards.
- Display drivers include **UC8179, UC8159, "UC BWRY"** (four-colour, one
  frame at 2 bpp packed into 4-bit nibbles, codes 00 black / 01 white /
  10 yellow / 11 red), JD, interleaved BWRY, SSD variants.
- Licence: **CC BY-NC-SA 4.0** for the OEPL parts, Zlib for Silicon Labs SDK
  files. A port is therefore non-commercial and share-alike.

`[RESEARCH]` The UC8179/UC8159 drivers there define exactly the commands
seen in our boot capture: `0x70` = REVISION, `0x90` = PARTIAL_WINDOW,
`0x92` = PARTIAL_OUT, `0xA2` = READ_OTP.
`[ASSUMPTION]` Our panel's controller belongs to the **UltraChip (UC81xx)
command family**, in a BWRY variant. → **Test:** replay the boot reads
from our own firmware and get the same bytes back; later, the `ucbwry`
init on the panel.

Why port instead of writing from scratch: radio, power management,
bootloader and drawing already exist and are field-tested on other
EFR32xG22 tags. Our work is the **board definition** and the **display
driver parameters**.

---

## 3. What we still need to know

| # | Information | Why | How |
|---|---|---|---|
| 1 | SWD lock state | decides everything (section 1) | M-011 → `commander device info` / `security status` |
| 2 | **EFR32 pin for each display line** (FPC 9–14) | board definition | M-012 (continuity FPC pin → QFN pin) |
| 3 | EFR32 pin driving the panel supply switch `XDt` | `enable` pin in the board definition | M-012 / M-005 |
| 4 | EFR32 pins of the two LEDs | status output during bring-up | M-012 |
| 5 | **Is there external SPI flash?** OEPL stores images there | if not: images must go to internal flash (512 kB) — a code change | M-012: identify the SO-8 `8K417` (NFC IC or flash?) |
| 6 | Controller init sequence and waveform | drawing an image | best: from the original firmware (if readable); otherwise try the OEPL `ucbwry` / `uc8179` sequences |
| 7 | Debug output | seeing what the firmware does | SWO/RTT via J-Link — no UART needed |

---

## 4. Bring-up in small, verifiable steps

Each step has a check that does not depend on the next one.

| Step | Firmware | Check | Risk to the panel |
|---|---|---|---|
| 0 | none — read lock state, back up flash if possible | `commander` output | none |
| 1 | minimal: blink an LED, RTT "hello" | LED blinks, RTT text | none (panel untouched) |
| 2 | switch panel supply on, reset pulse, wait for BUSY | SLogic: same RST/BUSY timing as in `…_boot-overview-panel_2MHz.sr` | none (no HV commands) |
| 3 | **replay the boot reads** (`70`, `90`, `A2`, `92`) | we read `0D 04 01` and the 70-byte OTP block incl. `SPQ0KX` and `01 E0 03 20` | none (reads only) |
| 4 | full init + one refresh with a test pattern (`ucbwry` sequence as starting point) | image on the panel; SLogic confirms bytes | **medium** — power/booster settings; only on tag 02 |
| 5 | full OEPL port (board type, radio) | tag shows up at an OEPL access point | none beyond step 4 |

Step 3 is the key safety net: it proves pin mapping, SPI mode, the
bidirectional data line and timing **without sending a single power or
waveform command** to the panel.

---

## 5. Toolchain

- ARM GCC: available as `gcc-arm-none-eabi` (13.2) in this environment.
- Gecko SDK 4.4.1: public on GitHub (`SiliconLabs/gecko_sdk`).
- `slc` and Simplicity Commander: download from silabs.com — **not
  reachable** from the Claude Code environment.
- Update 2026-10-21: OEPL now ships `reflash.py` (pyOCD; status, unlock,
  flash with J-Link or CMSIS-DAP) — an alternative to Commander on the
  maintainer's machine. Flashing our own `.hex` works with
  `python reflash.py -f <file>.hex` (after an unlock only). OEPL's Docker image needs
  them too.
  → The maintainer builds/flashes locally (Simplicity Studio or Docker), or
  step 1–3 are done as a small bare-metal project that only needs GCC +
  the SDK's device headers (buildable here, flashable with J-Link /
  Commander on the maintainer's machine).

---

## 6. What does not go into this repo

- The original firmware image (copyright). Only findings derived from it.
- Copies of the OEPL sources — a port lives as patches / a fork with its
  licence, referenced from `firmware/`.
- Copies of Pervasive Displays driver code (CC BY-SA 4.0, "for exclusive
  use with Pervasive Displays screens") — reimplement from the procedure.
- The UserData page dump of a tag (vendor data of unknown content).

---

## 7. Flash image concept (2026-10-21)

Maintainer decision (2026-10-21): we go ahead on the assumption that the
panel is the Pervasive Displays BWRY Medium type (`panel-protocol.md`);
the colour mapping is tested in step 4. This section is a **concept** —
nothing is built yet. All pins come from the third-party map (issue #2)
and stay **unverified** until M-012; every image says so in its source
and in its first RTT line (`CLAUDE.md` §2).

### 7.1 Two kinds of image

| | Bring-up image (steps 1–4) | OEPL image (step 5) |
|---|---|---|
| Layout | one bare-metal application at `0x00000000`, no bootloader | bootloader `0x00000` + application `0x06000` + NVM3 at the end of flash |
| Size | small; `[ASSUMPTION]` well under 32 kB | application ≤ 208 kB on a 256 kB part (see 7.3) |
| Build | `gcc-arm-none-eabi` + CMSIS device headers / emlib from `SiliconLabs/gecko_sdk` on GitHub — buildable in the Claude Code container | GSDK 4.4.1 + `slc` (maintainer or Docker), as OEPL |
| Flashing | J-Link + Simplicity Commander, or `reflash.py -f <file>.hex`, **after** the unlock | the same once; afterwards OTA |
| Output | SEGGER RTT text log (J-Link RTT Viewer), no UART needed | OEPL radio protocol |

### 7.2 Bring-up image, step by step

> **Update 2026-10-21:** step 1 is written: `firmware/bringup/`
> (own startup, linker script and RTT; GSDK 4.4.1 device headers only).
> Tested in an emulator (`firmware/bringup/test/emulate.py`), not on
> hardware. Run on the tag: M-013.

One source tree, one build per step (a compile-time `STEP` switch), so
each image only contains what its step needs:

| Step | What the image does | What it must not do | Check |
|---|---|---|---|
| 1 | RTT "hello", prints DEVINFO: part number, **flash size** (F-17), unique ID | touch any panel or flash pin (all stay at reset default = disabled) | RTT log |
| 2 | panel supply on (PC06 low), vendor reset timing on RST (PC04), wait for BUSY high on PA07 with the ~1 ms pulse handled and a timeout | send any SPI byte | SLogic capture: same RST/BUSY shape as `…_boot-overview-panel_2MHz.sr` |
| 3 | OTP read exactly as the vendor driver: chip ID must be `0x0D04`, bank marker `A5`, all 112 bytes; prints them | send anything other than `70`, `90`, `A2 00 15 00 00 E0`, `92` | bytes 0–68 equal our capture |
| 4 | init from the OTP, `10` + test frame, `04`, `12 00`, turn-off DC/DC + 6 s, supply off | run without step 3 having passed | photo of the panel |

**Optional step 1b (added 2026-10-21):** SPI-flash JEDEC ID read
(`0x9F`, and `0xAB` release-power-down ID) — read-only, after M-012 has
verified the flash pins. Answers F-16 without relying on the marking.

**Step 3 note:** read all 112 OTP bytes. A part-number string at bytes
96–109 (third party: `S12741QS0B31CY`) would give our own evidence for
the panel type (`panel-protocol.md` §8).

Design points:

- **SPI by bit-banging first** (PC00 SDA, PC01 SCK, PC02 CS, PC03 D/C).
  It avoids the open USART-routing question (display on port C → only
  USART0?, `oepl-pin-comparison.md` §5) and is fast enough: 96,000 bytes × 8 bit at ~1 µs per bit ≈ 1 s.
  A USART version can follow once it works.
- **RAM is 32 kB, the frame is 96,000 bytes.** The image is therefore
  generated **line by line** (800 lines × 120 bytes) while it is sent —
  as OEPL does. Step 4's test frame: four bands, one per 2-bit code
  `00`, `01`, `10`, `11`, plus a small asymmetric marker in one corner.
  One photo then shows the colour mapping **and** the orientation/mirroring.
- **Temperature for `E6`:** first test with the vendor default 25 °C;
  then the EFR32's internal sensor. `[ASSUMPTION]` emlib offers a reader
  for it on Series 2 — **test:** check in `gecko_sdk`.
- **Timeouts everywhere:** BUSY after reset (the original firmware gives
  up after ≈ 10 s, `…_boot-overview_2MHz.sr`), BUSY during refresh
  (≈ 22 s expected, abort at e.g. 60 s), and the supply goes off on any
  error.

### 7.3 OEPL image

`[RESEARCH]` OEPL release v43 (`Tag_FW_EFR32xG22` commit `8a8d7a9`),
from the address ranges in `full_binaries/v43/*_FULL_v43.s37`:

| Region | Address | Size in v43 |
|---|---|---|
| Bootloader (Gecko SPIF bootloader, 3 pages reserved) | `0x00000`–`0x05FFF` | 17.6 kB used of 24 kB |
| Application | from `0x06000` | **233.6 kB** (ends at `0x40650`) |
| NVM3 (internal flash) | 3 pages | 24 kB (`NVM3_DEFAULT_NVM_SIZE`) |
| OTA slot | external SPI flash | max. 236 kB upgrade file, LZMA compressed (v43 OTA file: 131 kB) |

Consequences:

- **If our part has 256 kB (F-17), the v43 application does not fit:**
  256 − 24 (bootloader) − 24 (NVM3) = **208 kB** for the application,
  v43 needs 233.6 kB. A board-specific build without the drivers and
  fonts of other tags is needed. `[ASSUMPTION]` that saves ≥ 26 kB —
  **test:** link map of such a build. Issue #2 reports exactly such a
  separate 256 kB build.
- `[RESEARCH]` The **bootloader carries the hardware type**: OEPL patches
  one ID byte into each bootloader variant (`bootloader/generate_variants.py`),
  and the application selects its pin table by that byte
  (`oepl_efr32xg22_get_config()`). For our board: the existing
  `Custom_SPIF_BTL` base has the flash pins reported in issue #2
  (PB00/PA04/PA00/PA05, enable PA06) plus a development ID byte
  (`0xF0…`), or a new ID.
- Application changes: one `tagconfig` entry (display, flash, LEDs once
  known, no NFC interface), a Pervasive BWRY Medium display driver
  (reimplemented, `panel-protocol.md` §7), display parameters 480 × 800
  four-colour, device `EFR32FG22C121F256GM40` (or F512, per F-17).
- Licence: OEPL is CC BY-NC-SA 4.0 → the port is non-commercial and
  share-alike.

### 7.4 What the maintainer will do with the images (after F-15)

1. `commander device info` (flash size) and dump the UserData page, e.g.
   `python reflash.py --dump-ud-bin ud.bin` — keep it **outside** the
   repo; the unlock keeps the UserData page (issue #2), our images do
   not write it.
2. Flash `bringup_step1.hex`, start J-Link RTT Viewer, send the log.
3. Steps 2–4 the same way, each with its check from 7.2.
4. Only then the OEPL image (bootloader + application in one `.s37`).
