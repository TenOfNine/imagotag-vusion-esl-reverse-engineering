# Measurement log

Filled in by the **maintainer**. Claude Code enters nothing here — unless
the maintainer dictates values.

Every filled-in row is a `[MEASUREMENT]` in the sense of `CLAUDE.md` §3 and
may be treated as fact from then on.

---

## M-001 — FPC pinout

**Date:** 2026-09-23 (rounds 1–5 done)
**Tool:** OWON HDS242
**Tag no.:** **tag 02** (the tag shown in `hardware/photos/`)
**State:** unpowered, battery removed, FPC **unplugged** (board-side nets only).

### Counting direction

| Question | Answer |
|---|---|
| Pin 1 is … | ✅ towards the **centre of the board**; pin 24 is at the **board edge** (read from the `1` printed on the FPC, 2026-09-23) |
| FPC contacts face … | ✅ **down** (towards the board); not visible once unplugged (2026-09-23) |

### Pin table

Procedure: see `../docs/measurement-requests.md`, M-001, rounds 1–4.

| Column | Round | Meter mode | How |
|---|---|---|---|
| GND beep | 1 | continuity | one probe on battery minus, other on the pin |
| R to GND | 1 | resistance | same; write the value after ~2 s, or "rising" if it keeps climbing |
| VDD beep | 2 | continuity | one probe on battery plus, other on the pin |
| Diode A | 3 | diode | **red** on battery minus, **black** on the pin → volts or `OL` |
| Diode B | 3 | diode | **black** on battery minus, **red** on the pin → volts or `OL` |
| Target | 4 | — | anything else found (`Gate KM`, `MLCC`, `FG22 pin nn`, `?`) |

| Pin | GND beep | R to GND | VDD beep | Diode A (V) | Diode B (V) | Target | Standard would be |
|---:|---|---|---|---|---|---|---|
|  1 | no | ⬜ | no | OL | OL | ⬜ | HLT_CTL |
|  2 | no | ⬜ | no | OL | OL | KM SOT-23 leg 1 (presumed gate) | GDR |
|  3 | ✅ beep | 0.19 Ω | no | 0.0012 | 0.0013 | GND net; leg 2 of `KM` SOT-23 | RESE |
|  4 | no | ⬜ | no | OL | OL | ⬜ | VGL ⚡ |
|  5 | no | ⬜ | no | OL | OL | ⬜ | VGH ⚡ |
|  6 | no | ⬜ | no | OL | OL | ⬜ | TSCL |
|  7 | no | ⬜ | no | OL | OL | ⬜ | TSDA |
|  8 | ✅ beep | 0.17 Ω | no | 0.0012 | 0.0013 | GND net | BS |
|  9 | no | 1.85 MΩ | no | 0.56 | OL | ⬜ | BUSY 🟢 |
| 10 | no | 1.9 MΩ | no | 0.56 | OL | ⬜ | RST 🟢 |
| 11 | no | 1.9 MΩ | no | 0.56 | OL | ⬜ | D/C 🟢 |
| 12 | no | 1.85 MΩ | no | 0.56 | OL | ⬜ | CS 🟢 |
| 13 | no | 1.85 MΩ | no | 0.56 | OL | ⬜ | SCK 🟢 |
| 14 | no | 1.85 MΩ | no | 0.56 | OL | ⬜ | SDI 🟢 |
| 15 | no | 9.98 kΩ (rises, settles within 2 s) | no | 0.56 | OL | pin 16 (0.18 Ω) | VDDIO |
| 16 | no | 9.98 kΩ (rises, settles within 2 s) | no | 0.56 | OL | pin 15 (0.18 Ω); leg 3 of SOT-23 `XDt` | VCI |
| 17 | ✅ beep | ⬜ | no | 0.0012 | 0.0013 | GND net | VSS (GND) |
| 18 | no | ⬜ | no | OL | OL | ⬜ | VDD |
| 19 | no | ⬜ | no | OL | OL | ⬜ | VPP |
| 20 | no | ⬜ | no | OL | OL | ⬜ | VSH ⚡ |
| 21 | no | ⬜ | no | 0.7 | OL | ⬜ | PREVGH ⚡ |
| 22 | no | ⬜ | no | OL | OL | ⬜ | VSL ⚡ |
| 23 | no | ⬜ | no | OL | 0.4343 | ⬜ | PREVGL ⚡ |
| 24 | no | ⬜ | no | OL | OL | ⬜ | VCOM ⚡ |

Rounds 1–5 measured 2026-09-23, FPC unplugged. "R to GND" measured only
for pins 3, 8 and 9–16 (round 5).

### Round 5 details

| # | Test | Result |
|---|---|---|
| 5a | pin 15 ↔ pin 16 | continuity, **0.18 Ω** |
| 5b | pins 9–16 to GND, resistance | 9–14: **1.85–1.9 MΩ**, steady; 15/16: rise to **9.98 kΩ** within 2 s |
| 5c | pin 15/16 ↔ SOT-23 legs | pin 16 ↔ **leg 3 of `XDt`**. Parts marked `T0.` and `1R.` not found on the board |
| 5d | pin 3 ↔ `KM` legs | pin 3 ↔ **leg 2 of `KM`** |
| 5e | pin 3 / pin 8 to GND, resistance | **0.19 Ω / 0.17 Ω** |

### Evaluation

| Question | Answer |
|---|---|
| Number of pins with a GPIO-like diode signature | 8 (9–16); of these, 15/16 are one supply net (round 5) |
| Number of signal lines | **6** |
| Are they contiguous? | ✅ yes |
| On which pins? | **9–14** |
| **Standard confirmed?** | ✅ **for the position of the signal group (9–14), GND (17), GDR (2), VDDIO/VCI (15/16).** The order of the signals *within* 9–14 is not measurable this way — only the capture settles it. |

---

## M-002 — Four open vias on the back side

**Date:** ⬜ not yet measured

Location: right half of the image, left of the `2 BOT` label.

| Via | Position | Continuity to | FG22 pin | Probably |
|---|---|---|---|---|
| A | left | ⬜ | ⬜ | ⬜ |
| B | right | ⬜ | ⬜ | ⬜ |
| C | bottom left | ⬜ | ⬜ | ⬜ |
| D | bottom right | ⬜ | ⬜ | ⬜ |
| E | large hole at the top | ⬜ | ⬜ | ⬜ |

**Result:** ⬜ SWD port confirmed / ⬜ other function / ⬜ unclear

---

## M-003 — QFN package

**Date:** 2026-09-23 — counted by Claude Code from the maintainer's macro
photo `photos/pcb-top-mcu-macro.webp` (so this is `[PHOTO]`, not a
measurement)

| Question | Answer |
|---|---|
| Pads per side | **10** (top, left, bottom clearly; right side in shadow, ~10 visible) |
| Total | **40** |
| **Type** | ✅ QFN40 (`…GM40-C`) |

---

## M-011 — SWD access points (QFN pins 22/23)

**Reported:** 2026-11-07 (dictated by the maintainer in chat; date of the
measurement itself not stated)
**Tool:** OWON HDS242, continuity
**Tag no.:** ⬜ (presumably tag 02 — to be confirmed)
**State:** ⬜ (unpowered expected)
**Photo:** `photos/pcb-bottom-swd-pads-22-23.webp`

| Point (bottom side, below the LEDs) | Continuity to | Result |
|---|---|---|
| Pad "22" | QFN pin 22 (SWCLK, PA01) | ✅ beeps (traces followed, then continuity) |
| Pad "23" | QFN pin 23 (SWDIO, PA02) | ✅ beeps (traces followed, then continuity) |
| Pad "22" / "23" | battery minus | ⬜ |
| Pad "22" / "23" | battery plus | ⬜ |

### Lock status (J-Link read-out)

**Date:** 2026-11-07, first attempt
**Tool:** J-Link (J-Link DLL 8.94) + Simplicity Commander 1v25p2b2004
**Tag no.:** ⬜ (presumably tag 02)
**Wiring:** SWCLK → pad "22", SWDIO → pad "23", GND, VTref (as in M-011)

`commander security status --device EFR32FG22`:

| Field | Value |
|---|---|
| SE Firmware version | 1.2.14 |
| Serial number | `00000000000000000c2a6ffffee7942c` |
| Debug lock | **Enabled** |
| Device erase | **Enabled** |
| Secure debug unlock | Enabled |
| Secure boot | **Disabled** |
| Boot status | 0x20 - OK |
| Command key installed | True |
| Sign key installed | True |

`commander device info --device EFR32FG22`: "Device part number
'EFR32FG22' is not in the J-Link device database; falling back to generic
'Cortex-M4'" → "ERROR: Debug access is locked. Could not connect to
device" (expected while locked; flash size not readable).

---

## Other measurements

> Free field for anything that was not part of a request.

| Date | What was measured | Result |
|---|---|---|
| Session 1 (≤ 2026-09-22) | Panel outer dimensions, **calliper** (maintainer statement 2026-09-23) | approx. 170 × 112 mm |
| ⬜ | ⬜ | ⬜ |
