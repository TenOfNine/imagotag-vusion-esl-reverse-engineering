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
| M-001 | Continuity-check the FPC pinout | 🟠 in progress (direction + GND done) | **everything** |
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

**Status 2026-09-23:** counting direction settled (pin 1 towards the board
centre, pin 24 at the board edge), pin 17 = GND. Rounds below still open.

#### Preparation

1. Use any tag **except tag 01** (reference unit). Note its number.
2. Remove the battery, wait **at least 1 minute** so the HV capacitors can
   discharge — residual charge falsifies the readings.
3. **Unplug the FPC.** We want the board-side nets only; with the panel
   attached, its internal circuitry adds paths and confuses the readings.
4. Probe point per pin: the **solder tails of the ZIF connector** on the
   board (or the fan-out vias next to it). A sharpened probe tip or a
   sewing needle held against the probe helps at 0.5 mm pitch. Accidentally
   bridging two neighbouring pins is harmless unpowered — just repeat that
   pin.

#### Round 1 — everything against GND (continuity + resistance)

One probe fixed on **battery minus**. Go through pins 1–24:

- continuity mode: beep yes/no
- then resistance mode: value after approx. 2 s. If the value keeps
  climbing, write "rising" — that is a capacitor charging (typical for the
  HV pins).

Expected with the standard: pin 17 beeps (done), pin 3 (RESE) shows a few
ohms (shunt).

#### Round 2 — everything against VDD (continuity)

One probe fixed on **battery plus**, pins 1–24 in continuity mode.
Expected with the standard: pins 15, 16, 18 (VDDIO, VCI, VDD) may beep.

#### Round 3 — diode signature (the key round)

Meter in **diode mode**. Every GPIO of the EFR32 has ESD protection diodes
to GND and VDD. They show up from the outside, without having to reach the
tiny QFN pads:

- **Diode A:** **red** probe on battery minus, **black** probe on the pin.
- **Diode B:** swap: **black** on battery minus, **red** on the pin.

Write down the displayed voltage or `OL` for every pin.

`[ASSUMPTION]` Pins wired directly to an MCU GPIO show approx.
0.4 – 0.8 V in diode A. Open pins show `OL` both ways; pins on large
capacitors show a slowly changing value.
→ **Test:** this round itself — if exactly 6 pins show the same kind of
value, the assumption is supported.

#### Round 4 — targeted checks (only for the interesting pins)

- **GDR:** continuity from the SOT-23 marked `KM` to the FPC pins.
  `[ASSUMPTION]` The gate is usually pin 1 of the SOT-23 (single pin on one
  side is the drain) — check all three legs, note which one hits.
- **Optional — FG22 pin numbers:** for the pins with a GPIO signature,
  which QFN pad they connect to. Only needed later for path B; skip it if
  the pads are too small to probe reliably.

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
