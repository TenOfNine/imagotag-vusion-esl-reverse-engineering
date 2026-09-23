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
| M-002 | Four open vias = SWD? | 🟡 unlikely — maintainer: they are through-holes of the battery contact pads; SWD must be found elsewhere (after M-003) | J-Link access |
| M-003 | QFN package: 32 or 40 pins? | ✅ QFN40 (counted on macro photo 2026-09-23) | — |
| M-004 | Solder points for FPC pins 9–14 + GND | ✅ done — see `pcb-bottom-capture-wiring-v2.webp`; mapping verified by captures | — |
| M-005 | Panel supply switch `XDt` | 🟡 open, low priority | path A only |
| M-006 | Why BUSY (pin 9) never changed in pass A | ✅ done — panel was unplugged; with panel BUSY toggles | — |
| M-007 | D5 wire (pin 14) shows no data — check solder point | ✅ done — wiring OK (confirmed by M-008 captures) | — |
| M-008 | D4–D7 flat only at 20 MSa/s? Analyser channel-mode test | ✅ done 2026-09-23 — yes; 4 channels on D0–D3 work | — |
| M-009 | Re-capture boot at 40 MSa/s, 4 channels (write clock ~6 MHz) | 🟡 open | confidence in write bytes |
| M-010 | Trigger a refresh (NFC) while capturing | ✅ done 2026-09-23 — negative: NFC read causes no SPI activity | — |
| M-011 | Find reachable points for SWCLK (pin 22) / SWDIO (pin 23) | 🔴 open | **SWD lock check (F-05)** |

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

## M-007 — D5 wire (FPC pin 14) carries no data

**Priority: high** — without the data line, pass B only shows timing.
**Tool:** OWON HDS242, continuity
**State:** unpowered, battery out

### Background

`[CAPTURE]` `2026-09-23_tag02_boot-overview-panel_2MHz.sr`: ~80 bytes are
clocked on pin 13 while CS (pin 12) and D/C (pin 11) behave as expected,
but **D5 (pin 14) never toggles** — it goes high at 0.81 s (battery in)
and low at 27.65 s (presumably battery out), in both captures.
`[ASSUMPTION]` The D5 wire does not sit on FPC pin 14 but on a supply net
(it follows the battery), or pin 14 is not the data line.

### Task

1. Continuity from the **D5 solder point** to **FPC pin 14** at the
   connector.
2. Continuity from the D5 solder point to **battery plus**.
3. If 1 fails or 2 beeps: find the correct via for pin 14 (M-004) and
   re-solder.

### Update 2026-09-23 — after re-soldering pin 14

`[CAPTURE]` `2026-09-23_tag02_boot-init_20MHz.sr`: D5 no longer follows
the battery (good), but now **both D4 (pin 13, SCK) and D5 (pin 14) are
flat low** for the whole capture, while D0–D3 behave exactly as before.
SCK was clearly visible in the previous capture, so the D4 connection was
most likely disturbed while re-soldering pin 14 (neighbouring via), or a
wire/clip came loose.

Extended task — unpowered, battery out, FPC plugged in or out:

| # | Check | Expected |
|---|---|---|
| 4 | For **each** of D0–D5: continuity from the **end of the wire at the SLogic** (not the solder point) to its FPC pin 9–14 at the connector | beep for each, 6 × |
| 5 | Neighbour shorts: 12↔13, 13↔14, 14↔15 at the solder points | no beep |
| 6 | D4 and D5 solder points to battery minus and battery plus | no beep |
| 7 | SLogic side: D4/D5 leads firmly on the right header pins | — |

Checking from the SLogic end of the wire covers the solder joint, the
wire and the via in one go.

### Decision rule

| Result | Consequence |
|---|---|
| 1 fails and/or 2 beeps | wire was on the wrong point → fix, then pass B |
| 1 beeps, 2 silent | wiring is right; pin 14 is not MOSI → report back, rethink the pin roles |

---

## M-008 — Are D4–D7 dropped by the analyser at 20 MSa/s?

**Priority: high** — cheapest possible test, no soldering.
**Tool:** SLogic Combo 8, PulseView (Windows)
**State:** tag 02 in operation, panel plugged in

### Background

`[CAPTURE]` D4 (pin 13) showed a clean clock at **2 MSa/s**
(`…_boot-overview-panel_2MHz.sr`), but D4 **and** D5 are completely flat in
both **20 MSa/s** captures (`…_boot-init_20MHz.sr`,
`…_boot-init-rewired_20MHz.sr`) — even after the maintainer re-checked
all wires (no shorts, mapping correct). D0–D3 work in every capture.
`[RESEARCH]` The SLogic Combo 8 is bandwidth-limited on Windows (sources in
`TOOLS.md`); 20 MSa/s × 8 channels sits right at that limit.
`[ASSUMPTION]` At 20 MSa/s the driver/device runs in a reduced channel
mode and only D0–D3 carry data; D4–D7 read 0.

### Task

1. **Wiring check at 2 MSa/s, current wiring**, ~15 s, battery inserted
   during the recording. Expect edges on D4 (SCK) **and D5 (data)** during
   the transfer at ~6 s.
2. **Move the leads at the SLogic header** (no soldering) so that the four
   lines needed for decoding sit on D0–D3:

   | Channel | FPC pin | Signal (`[ASSUMPTION]` standard order) |
   |---|---|---|
   | D0 | 13 | SCK |
   | D1 | 14 | data (SDI/SDA) |
   | D2 | 12 | CS |
   | D3 | 11 | D/C |
   | D4–D7 | — | **disable** in PulseView (D7 lead on GND if connected) |

   Name the channels in PulseView accordingly (`Pin13`, `Pin14`, …).
   BUSY and RST are already known from earlier captures and are not needed
   for decoding.
3. Record **20 MSa/s, 4 channels, ~15 s**, battery inserted during the
   recording.

### Decision rule

| Result | Consequence |
|---|---|
| Step 1 shows D4/D5 edges, step 3 shows SCK + data | analyser channel mode was the cause → decode the init sequence; note the limit in `TOOLS.md` |
| Step 1 already flat on D4/D5 | wiring after all → back to M-007 |
| Step 1 fine, step 3 flat on D0/D1 | problem moves with the wire → wiring/lead, not the analyser |

---

## M-009 — Re-capture the boot at 40 MSa/s, 4 channels

**Priority: medium** — verifies the write bytes; no rewiring.
**Tool:** SLogic, PulseView (Windows)

### Background

`[CAPTURE]` `2026-09-23_tag02_boot-init-4ch_20MHz.sr`: the MCU writes with
an SCK period of ~0.157 µs (≈ 6.4 MHz) — only ~3 samples per clock period
at 20 MSa/s. Reads run at ~1 MHz and are safe. Rising- and falling-edge
sampling agreed for all 82 bytes, but the margin is thin.
`[RESEARCH]` 4 channels × 40 MSa/s = 160 Mb/s, the Windows limit given for
the SLogic (see `TOOLS.md`).

### Task

Same wiring as the last capture (D0 = pin 13, D1 = pin 14, D2 = pin 12,
D3 = pin 11, D4–D7 disabled). **40 MSa/s**, ~15 s, battery inserted during
the recording.

### Decision rule

| Result | Consequence |
|---|---|
| Same 82 bytes | 20 MSa/s result confirmed |
| Different write bytes | 20 MSa/s was too slow for writes → use 40 MSa/s from now on |
| D0–D3 flat / capture aborts | 40 MSa/s too much for this PC → stay at 20 MSa/s |

---

## M-010 — Trigger a refresh while capturing

**Priority: high** — `[CAPTURE]` the tag does **not** refresh within 134 s
after battery insertion (`2026-09-23_tag02_boot-long_2MHz.sr`). Without a
refresh there is no image data and no display init sequence to sniff.
**Tool:** SLogic, an NFC-capable phone
**State:** tag 02 in operation, panel plugged in, 4-channel wiring

### Task

1. Start a **2 MSa/s, 4-channel** recording (same wiring), insert the
   battery, wait ~15 s until the boot sequence is over.
2. Hold the phone's NFC area against the tag's NFC coil (back side, upper
   area). Try a generic NFC reader app (e.g. "NFC Tools" — reading only,
   **no writing**). Keep it there for ~10 s, then remove, repeat 2–3 times.
3. Note the timestamps of each attempt and whether the display changed.
   Keep recording for ~60 s after the last attempt.
4. Send the `.sr` file and whatever the phone app shows (screenshot).

### Decision rule

| Result | Consequence |
|---|---|
| Long SPI activity (≥ ~96 kB) after an NFC tap | refresh captured → decode init + frame (pass at 20–40 MSa/s next) |
| Short SPI activity only | NFC wakes the tag but no refresh → analyse the bytes |
| Nothing | NFC is not a trigger → next options: SWD lock check (F-05, needs M-002/M-003) or driving the panel ourselves |

### ⚠ Safety

Reading with the phone is harmless. **Do not write** to the tag via NFC —
unknown effect on the original firmware.

---

## M-011 — Reachable points for SWCLK / SWDIO

**Priority: high** — prerequisite for the non-destructive lock check (F-05).
**Tool:** OWON HDS242 (continuity), sharp probe tip or needle
**State:** unpowered, battery out

### Background

`[PHOTO]` The EFR32 is a QFN40. `[RESEARCH]` On xG22 QFN40, **pin 22 =
PA01 = SWCLK** and **pin 23 = PA02 = SWDIO** (see `docs/hardware.md`).
`[ASSUMPTION]` Counting counter-clockwise from the pin-1 dot (top left in
`hardware/photos/pcb-top-mcu-macro.webp`): pins 1–10 left side top→bottom,
11–20 bottom left→right, **21–30 right side bottom→top** → pin 22 and 23
are the **2nd and 3rd pad from the bottom on the right side**.

### Task

1. Confirm pin 1: the dot on the chip is at the top-left corner in the
   macro photo — is that how you read it?
2. On the **right side** of the QFN, touch the 2nd pad from the bottom
   (pin 22) and follow continuity to **the nearest via, test pad or
   resistor pad** — on the top side or the back side. Note/mark it.
   Same for the 3rd pad from the bottom (pin 23).
3. For both: check they do **not** beep to battery minus or battery plus.
4. Optional: find **RESETn** the same way once its pin number is known
   (I will look it up).
5. A photo with the found points marked.

### Decision rule

| Result | Consequence |
|---|---|
| Both have a reachable via/pad | solder thin wires there → J-Link: SWCLK, SWDIO, GND, VTref (to battery plus) |
| Only the QFN pads themselves | solder 0.1 mm wire directly to the pad toes — doable but delicate; decide together |
| A pin beeps to GND/VDD | numbering assumption wrong → report back |

### ⚠ Safety

- Tag 02 only, never tag 01.
- In the later J-Link step: **only** `commander device info` and
  `commander security status`. **No** `device unlock`, **no** erase, **no**
  flash (CLAUDE.md §5.2). The tag stays powered by its battery; VTref
  only senses the voltage.

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
