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
| M-001 | Continuity-check the FPC pinout | ✅ done 2026-09-23 | — |
| M-002 | Four open vias = SWD? | 🔴 open | J-Link access |
| M-003 | QFN package: 32 or 40 pins? | 🔴 open | SWD pin numbers |
| M-004 | Solder points for FPC pins 9–14 + GND | 🟠 maintainer reports points found, details pending | **the capture** |
| M-005 | Panel supply switch `XDt` | 🟡 open, low priority | path A only |
| M-006 | Why BUSY (pin 9) never changed in pass A | 🟠 cause found (panel unplugged), pass A being repeated | **pass B** |

---

## M-001 — Continuity-check the FPC pinout

**Priority: highest.** Nothing moves forward without this result.

**Tool:** multimeter with continuity tester (OWON HDS242)
**State:** unpowered, battery removed

### Task

For each of the 24 FPC pins, determine where it leads. Fill in the table in
`../hardware/measurements.md`.

**Status 2026-09-23: ✅ done.** Rounds 1–5 carried out, results in
`../hardware/measurements.md`. Outcome: signal lines on **9–14**, supply
(VDDIO/VCI) on 15/16, GND on 17 — decision rule row 1 applies.

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

#### Round 5 — separate signal lines from supply lines (added 2026-09-23)

Rounds 1–4 found **8** pins with the same diode signature (9–16), not 6.
Pins 15/16 are VDDIO/VCI in the standard, i.e. supply pins — but none of
them has continuity to battery plus. This round separates them. Still
unpowered, battery out, FPC unplugged.

| # | Test | Mode | Expected if standard | Why |
|---|---|---|---|---|
| 5a | pin 15 ↔ pin 16 | continuity | **beep** (same supply net) | signal lines are never shorted together |
| 5b | pins 9–16 each against battery minus | resistance, read after ~3 s | 15/16: value **keeps rising** (decoupling capacitor); 9–14: no rising | supply nets carry capacitors, signal lines do not |
| 5c | pin 15 (or 16) ↔ every leg of the SOT-23s marked `S21`, `XDt`, `T0.`, `1R.` | continuity | one leg beeps | finds the component that switches the panel supply |
| 5d | pin 3 ↔ each leg of the `KM` SOT-23 | continuity | one leg beeps (the source) | RESE senses the current at the MOSFET source; pin 3 alone beeping to GND does not distinguish RESE from plain GND |
| 5e | pin 3 and pin 8 against battery minus | resistance | pin 3: a few tenths of an ohm more than pin 8 (shunt) | may be below the meter's resolution — then just write "same" |

`[ASSUMPTION]` The panel supply (pins 15/16) is switched by the MCU (load
switch or GPIO-powered), which is common in battery ESLs.
→ **Test:** 5a–5c.

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

## M-004 — Solder points for FPC pins 9–14 and GND

**Priority: high** — this is the last step before the capture.
**Tool:** OWON HDS242, continuity mode
**State:** unpowered, battery removed, FPC may stay unplugged

### Task

Find one solder point per signal that is easier to hit than the 0.5 mm
connector tails — typically the vias in the fan-out to the right of the
connector (see `capture-protocol.md`, section 1B).

1. For each of FPC pins **9, 10, 11, 12, 13, 14**: find a via (or test pad,
   or resistor pad) with continuity to that pin. Note where it is — best
   mark it on a photo.
2. Find a **GND point** as close as possible to those vias (battery minus
   works, closer is better). Two GND points are better than one.
3. Optional: a photo of the area with the vias marked, into
   `../hardware/photos/`.

### Decision rule

| Result | Consequence |
|---|---|
| A via found for all six pins | solder there, proceed with `capture-protocol.md` |
| Some pins have no reachable via | solder those at the connector tails; take extra care not to bridge to pin 8 (GND) or pin 15 (supply) |

### ⚠ Safety

Pins 9–14 are bordered by pin 8 (GND) and pin 15 (panel supply) — no HV
pin is directly adjacent. HV pins are 4, 5 and 20–24. When soldering at the
connector, still check afterwards (unpowered) that no pin 9–14 has
continuity to a neighbour.

---

## M-005 — Panel supply switch `XDt`

**Priority: low** — only needed for path A (ESP32 on the carrier board).
**Tool:** OWON HDS242, continuity + resistance
**State:** unpowered, battery removed

### Background

`[MEASUREMENT]` Pin 16 (VCI, bridged to 15/VDDIO) connects to leg 3 of the
SOT-23 `XDt`, and no FPC pin connects to battery plus.
`[ASSUMPTION]` `XDt` is a P-channel MOSFET switching the panel supply
(usual SOT-23 pinout: 1 = gate, 2 = source, 3 = drain), with the gate
driven by an EFR32 GPIO.

### Task

| Test | Expected if the assumption holds |
|---|---|
| `XDt` leg 2 ↔ battery plus | continuity (source on the battery) |
| `XDt` leg 1 ↔ battery plus, resistance | a pull-up resistor (e.g. 10 k–1 MΩ), keeps the switch off by default |
| `XDt` leg 1 ↔ an EFR32 pin (optional) | continuity → which GPIO enables the panel supply |

### Decision rule

| Result | Consequence |
|---|---|
| Source on battery plus, gate pulled up | path A: the ESP32 pulls the gate low (or feeds pin 15/16 directly) to power the panel |
| Different picture | report back, reconsider the supply path |

---

## M-006 — Why BUSY (pin 9) never changed in pass A

**Priority: high** — pass B makes no sense until the panel answers.
**Tool:** eyes, OWON HDS242, SLogic
**State:** as stated per step

### Background

`[CAPTURE]` `2026-09-23_tag02_boot-overview_2MHz.sr`: the tag resets the
panel three times, waits ~10.08 s each time with **pin 9 constantly low**,
sends one short transaction, drops all lines and retries. No image data.
`[ASSUMPTION]` The tag waits for BUSY to go high and times out — the panel
never signals "ready". Details in `HISTORY.md`.

### Task

1. **Was the panel plugged in during the capture?** After M-001 the FPC
   was unplugged. Check that it is fully inserted and the ZIF latch is
   closed.
2. **Did the display change** during the capture (flicker, new image)?
3. **Solder point of pin 9** — unpowered, battery out: continuity from the
   D0 wire's solder point to FPC pin 9 at the connector. Also check it has
   **no** continuity to pin 8 (GND) or pin 10.
4. **D7 on GND?** (SLogic bug, see `TOOLS.md`.)
5. Repeat **pass A** (2 MHz, 60 s) with the panel verified as plugged in.

### Decision rule

| Result | Consequence |
|---|---|
| Panel was unplugged | plug in, repeat pass A — expect BUSY activity and a much longer transaction |
| Panel was plugged in, pin 9 solder point OK, BUSY still flat | report back; next suspects: panel supply (pin 15 level during the reset window, scope) or a damaged panel |
| Pin 9 solder point wrong/open | fix, repeat pass A |

### ⚠ Safety

Unpowered for step 3. The scope check of pin 15 happens only with the
probe ground on GND, never near pins 4, 5, 20–24 (±20 V).

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
