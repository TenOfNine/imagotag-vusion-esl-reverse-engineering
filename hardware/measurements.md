# Measurement log

Filled in by the **maintainer**. Claude Code enters nothing here — unless
the maintainer dictates values.

Every filled-in row is a `[MEASUREMENT]` in the sense of `CLAUDE.md` §3 and
may be treated as fact from then on.

---

## M-001 — FPC pinout

**Date:** 2026-09-23 (rounds 1–4 done)
**Tool:** ⬜ (presumably OWON HDS242 — not yet stated)
**Tag no.:** ⬜ — must **not** be tag 01 (reference unit)
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
|  3 | ✅ beep | ⬜ | no | 0.0012 | 0.0013 | GND net | RESE |
|  4 | no | ⬜ | no | OL | OL | ⬜ | VGL ⚡ |
|  5 | no | ⬜ | no | OL | OL | ⬜ | VGH ⚡ |
|  6 | no | ⬜ | no | OL | OL | ⬜ | TSCL |
|  7 | no | ⬜ | no | OL | OL | ⬜ | TSDA |
|  8 | ✅ beep | ⬜ | no | 0.0012 | 0.0013 | GND net | BS |
|  9 | no | ⬜ | no | 0.56 | OL | ⬜ | BUSY 🟢 |
| 10 | no | ⬜ | no | 0.56 | OL | ⬜ | RST 🟢 |
| 11 | no | ⬜ | no | 0.56 | OL | ⬜ | D/C 🟢 |
| 12 | no | ⬜ | no | 0.56 | OL | ⬜ | CS 🟢 |
| 13 | no | ⬜ | no | 0.56 | OL | ⬜ | SCK 🟢 |
| 14 | no | ⬜ | no | 0.56 | OL | ⬜ | SDI 🟢 |
| 15 | no | ⬜ | no | 0.56 | OL | ⬜ | VDDIO |
| 16 | no | ⬜ | no | 0.56 | OL | ⬜ | VCI |
| 17 | ✅ beep | ⬜ | no | 0.0012 | 0.0013 | GND net | VSS (GND) |
| 18 | no | ⬜ | no | OL | OL | ⬜ | VDD |
| 19 | no | ⬜ | no | OL | OL | ⬜ | VPP |
| 20 | no | ⬜ | no | OL | OL | ⬜ | VSH ⚡ |
| 21 | no | ⬜ | no | 0.7 | OL | ⬜ | PREVGH ⚡ |
| 22 | no | ⬜ | no | OL | OL | ⬜ | VSL ⚡ |
| 23 | no | ⬜ | no | OL | 0.4343 | ⬜ | PREVGL ⚡ |
| 24 | no | ⬜ | no | OL | OL | ⬜ | VCOM ⚡ |

Rounds 1–4 measured 2026-09-23, FPC unplugged. "R to GND" (resistance values) not yet measured.

### Evaluation

| Question | Answer |
|---|---|
| Number of pins with a GPIO-like diode signature | **8** (expected: 6) |
| Are they contiguous? | ✅ yes |
| On which pins? | **9–16** (0.56 V / OL) |
| **Standard confirmed?** | ⬜ partly — 9–14 vs. 15/16 still to be separated (round 5) |

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
