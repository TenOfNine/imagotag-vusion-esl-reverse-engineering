# Custom firmware for the EFR32 — plan

Status: **concept, nothing built yet** (2026-09-23). Decisions still open are
marked **DECISION**.

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
  reachable** from the Claude Code environment. OEPL's Docker image needs
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
