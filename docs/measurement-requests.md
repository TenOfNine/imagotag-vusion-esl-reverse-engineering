# Measurement requests

Claude Code cannot measure. Missing physical information is written here as
a request that the maintainer works through.

**For Claude Code:** append new requests at the bottom, numbered
consecutively (`M-004`, `M-005`, …). Every request must answer: *What
exactly is to be measured? With what? And what follows from which result?*
A request whose result decides nothing is superfluous.

**For the maintainer:** results go to `../hardware/measurements.md`, then
set the request here to `✅ done`.

---

## Status

| ID | Topic | Status | Blocks |
|---|---|---|---|
| M-001 | Continuity-check the FPC pinout | 🔴 open | **everything** |
| M-002 | Four open vias = SWD? | 🔴 open | J-Link access |
| M-003 | QFN package: 32 or 40 pins? | 🔴 open | SWD pin numbers |

---

## M-001 — Continuity-check the FPC pinout

**Priority: highest.** Nothing moves forward without this result.

**Tool:** multimeter with continuity tester (OWON HDS242)
**State:** unpowered, battery removed

### Task

For each of the 24 FPC pins, determine where it leads. Fill in the table in
`../hardware/measurements.md`.

Order of procedure:

1. **Settle the counting direction.** Insert the FPC, check at which end of
   the connector the printed `1` is. Note the result.
2. **Find GND:** continuity to the battery minus terminal.
3. **Find RESE:** approx. 0.5 – 3 Ω to GND (the small shunt).
4. **Find GDR:** continuity to the gate of the SOT-23 marked `KM`.
5. **Find the digital lines:** which pins have continuity **directly to a
   QFN pin of the FG22**? Note the QFN pin number as well.
6. Mark the rest as "ends at MLCC" or "unclear".

### Decision rule

| Result | Consequence |
|---|---|
| Exactly 6 digital lines, contiguous on 9–14 | Waveshare standard confirmed → `pinout.md` becomes `[MEASUREMENT]` |
| 6 digital lines, but elsewhere | Discard the standard, reconstruct the pinout from the measured values |
| Not 6 | Reconsider the assumption about the controller type, report back to Claude Code |

### ⚠ Safety

Several pins carry ±20 V in operation. **Measure unpowered only.** Only
after this measurement may the logic analyser be connected.

---

## M-002 — Are the four open vias the SWD port?

**Tool:** multimeter (OWON HDS242)
**State:** unpowered

### Task

On the back side, to the right of the `2 BOT` label, there are four open
vias (one on the left, one on the right, two close together below) plus a
larger hole above.

For each via check:

| Test | Meaning |
|---|---|
| Continuity to battery minus | GND |
| Continuity to battery plus | VDD |
| Continuity to an FG22 pin | candidate for SWDIO / SWCLK / RESET |

On hits on FG22 pins: **note the QFN pin number** and check it against the
port A assignment in the EFR32FG22 datasheet (on xG22, port A carries the
SWD function).

### Decision rule

| Result | Consequence |
|---|---|
| GND + VDD + 2 port A pins found | SWD port confirmed → the J-Link can be connected there |
| Only GND/VDD, no port A pins | Other function (e.g. production test points) → tap SWD directly at the QFN pins |

### Note

For the J-Link, additionally connect **VTref** (to VDD) — without VTref the
J-Link refuses to work.

---

## M-003 — QFN package: 32 or 40 pins?

**Tool:** magnifier or microscope, good side light (not available — see
`TOOLS.md`; a phone camera macro shot may be enough)

### Task

Count the pads per side on the EFR32FG22.

| Result | Type | GPIO |
|---|---|---|
| 8 per side = 32 total | `EFR32FG22C121F512GM32-C` | 18 |
| 10 per side = 40 total | `EFR32FG22C121F512GM40-C` | 26 |

### Why it matters

The pinout tables of the two packages are **not identical**. Without this
information the SWD pins cannot be assigned reliably — and connecting the
J-Link wrongly can damage the chip.

---

<!--
TEMPLATE:

## M-00N — <title>

**Priority:** <high/medium/low>
**Tool:** <instrument>
**State:** <unpowered / in operation>

### Task
<what exactly to do, step by step>

### Decision rule
| Result | Consequence |
|---|---|
| <case A> | <what happens then> |
| <case B> | <what happens then> |

### ⚠ Safety
<if relevant>
-->
