# Measurement log

Filled in by the **maintainer**. Claude Code enters nothing here — unless
the maintainer dictates values.

Every filled-in row is a `[MEASUREMENT]` in the sense of `CLAUDE.md` §3 and
may be treated as fact from then on.

---

## M-001 — FPC pinout

**Date:** 2026-09-23 (started)
**Tool:** ⬜ (presumably OWON HDS242 — not yet stated)
**Tag no.:** ⬜ — must **not** be tag 01 (reference unit)
**State:** unpowered, battery removed. From round 1 on: FPC **unplugged** (board-side nets only). Pin 17 result: FPC state not stated.

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
|  1 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | HLT_CTL |
|  2 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | GDR |
|  3 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | RESE |
|  4 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | VGL ⚡ |
|  5 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | VGH ⚡ |
|  6 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | TSCL |
|  7 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | TSDA |
|  8 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | BS |
|  9 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | BUSY 🟢 |
| 10 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | RST 🟢 |
| 11 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | D/C 🟢 |
| 12 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | CS 🟢 |
| 13 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | SCK 🟢 |
| 14 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | SDI 🟢 |
| 15 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | VDDIO |
| 16 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | VCI |
| 17 | ✅ GND (method not stated, 2026-09-23) | ⬜ | ⬜ | ⬜ | ⬜ | GND | VSS (GND) |
| 18 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | VDD |
| 19 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | VPP |
| 20 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | VSH ⚡ |
| 21 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | PREVGH ⚡ |
| 22 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | VSL ⚡ |
| 23 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | PREVGL ⚡ |
| 24 | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | ⬜ | VCOM ⚡ |

### Evaluation

| Question | Answer |
|---|---|
| Number of pins with a GPIO-like diode signature | ⬜ (expected: 6) |
| Are they contiguous? | ⬜ yes / ⬜ no |
| On which pins? | ⬜ |
| **Standard confirmed?** | ⬜ yes / ⬜ no |

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

**Date:** ⬜ not yet measured

| Question | Answer |
|---|---|
| Pads per side | ⬜ |
| Total | ⬜ |
| **Type** | ⬜ QFN32 (`…GM32-C`) / ⬜ QFN40 (`…GM40-C`) |

---

## Other measurements

> Free field for anything that was not part of a request.

| Date | What was measured | Result |
|---|---|---|
| Session 1 (≤ 2026-09-22) | Panel outer dimensions, **calliper** (maintainer statement 2026-09-23) | approx. 170 × 112 mm |
| ⬜ | ⬜ | ⬜ |
