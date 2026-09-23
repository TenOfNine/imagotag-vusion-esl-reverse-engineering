# Measurement log

Filled in by the **maintainer**. Claude Code enters nothing here — unless
the maintainer dictates values.

Every filled-in row is a `[MEASUREMENT]` in the sense of `CLAUDE.md` §3 and
may be treated as fact from then on.

---

## M-001 — FPC pinout

**Date:** ⬜ not yet measured
**Tool:** ⬜
**Tag no.:** ⬜

### Counting direction

> Insert the FPC, check at which end the printed `1` is.

| Question | Answer |
|---|---|
| Pin 1 is … | ⬜ near the panel end / ⬜ near the board edge |
| FPC contacts face … | ⬜ up / ⬜ down |

### Pin table

Column "Target": `GND`, `VDD`, `MLCC`, `Gate KM`, `Shunt`, `FG22 pin nn`, `open`, `?`

| Pin | Target (measured) | Resistance to GND | Identified as | Standard would be |
|---:|---|---|---|---|
|  1 | ⬜ | ⬜ | ⬜ | HLT_CTL |
|  2 | ⬜ | ⬜ | ⬜ | GDR |
|  3 | ⬜ | ⬜ | ⬜ | RESE |
|  4 | ⬜ | ⬜ | ⬜ | VGL ⚡ |
|  5 | ⬜ | ⬜ | ⬜ | VGH ⚡ |
|  6 | ⬜ | ⬜ | ⬜ | TSCL |
|  7 | ⬜ | ⬜ | ⬜ | TSDA |
|  8 | ⬜ | ⬜ | ⬜ | BS |
|  9 | ⬜ | ⬜ | ⬜ | BUSY 🟢 |
| 10 | ⬜ | ⬜ | ⬜ | RST 🟢 |
| 11 | ⬜ | ⬜ | ⬜ | D/C 🟢 |
| 12 | ⬜ | ⬜ | ⬜ | CS 🟢 |
| 13 | ⬜ | ⬜ | ⬜ | SCK 🟢 |
| 14 | ⬜ | ⬜ | ⬜ | SDI 🟢 |
| 15 | ⬜ | ⬜ | ⬜ | VDDIO |
| 16 | ⬜ | ⬜ | ⬜ | VCI |
| 17 | ⬜ | ⬜ | ⬜ | VSS (GND) |
| 18 | ⬜ | ⬜ | ⬜ | VDD |
| 19 | ⬜ | ⬜ | ⬜ | VPP |
| 20 | ⬜ | ⬜ | ⬜ | VSH ⚡ |
| 21 | ⬜ | ⬜ | ⬜ | PREVGH ⚡ |
| 22 | ⬜ | ⬜ | ⬜ | VSL ⚡ |
| 23 | ⬜ | ⬜ | ⬜ | PREVGL ⚡ |
| 24 | ⬜ | ⬜ | ⬜ | VCOM ⚡ |

### Evaluation

| Question | Answer |
|---|---|
| Number of digital lines found | ⬜ (expected: 6) |
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
