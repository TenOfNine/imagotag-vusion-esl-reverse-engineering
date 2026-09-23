# Pinout — 24-pin FPC

> **⚠ Nothing in this document has been measured.**
> The table below is the Waveshare / Good Display standard as a working
> hypothesis. ESL panels regularly deviate from it.
> As long as the "measured" column is empty, **no** driver and **no**
> wiring may be built on it.

---

## Hypothesis: standard 24-pin e-paper pinout

`[RESEARCH]` Consistent across the Waveshare E-Paper Driver HAT schematic,
the Electronic Assembly ePaper datasheet and the Midas MDE0154A152152RBW
spec.

| Pin | Signal | Meaning | Class |
|---:|---|---|---|
| 1 | HLT_CTL | halt control | other |
| 2 | **GDR** | N-ch MOSFET gate drive control | boost |
| 3 | **RESE** | current sense input (shunt) | boost |
| 4 | VGL | negative gate voltage, approx. −20 V | ⚡ HV |
| 5 | VGH | positive gate voltage, approx. +22 V | ⚡ HV |
| 6 | TSCL | I²C clock temperature sensor | other |
| 7 | TSDA | I²C data temperature sensor | other |
| 8 | BS | bus selector | other |
| 9 | **BUSY** | busy output | 🟢 digital |
| 10 | **RST** | reset, active low | 🟢 digital |
| 11 | **D/C** | data (high) / command (low) | 🟢 digital |
| 12 | **CS** | chip select, active low | 🟢 digital |
| 13 | **SCK** | SPI clock | 🟢 digital |
| 14 | **SDI** | SPI data (MOSI) | 🟢 digital |
| 15 | VDDIO | I/O logic supply | 🔵 power |
| 16 | VCI | display driver supply | 🔵 power |
| 17 | VSS | ground | 🔵 power |
| 18 | VDD | supply | 🔵 power |
| 19 | VPP | OTP programming voltage | other |
| 20 | VSH | positive source voltage | ⚡ HV |
| 21 | PREVGH | supply for VGH/VSH | ⚡ HV |
| 22 | VSL | negative source voltage | ⚡ HV |
| 23 | PREVGL | supply for VCOM/VGL/VSL | ⚡ HV |
| 24 | VCOM | common electrode | ⚡ HV |

**⚡ HV = high voltage.** The SLogic tolerates max. 3.6 V. A slipped probe
destroys it.

---

## Measurement status (2026-09-23, M-001 complete)

Raw values: `../hardware/measurements.md`. FPC unplugged, board side only,
OWON HDS242.

| Pin | Standard | Measured | Status |
|---:|---|---|---|
| 2 | GDR | continuity to leg 1 of the `KM` SOT-23 | `[MEASUREMENT]` connection; "gate" is `[ASSUMPTION]` (usual SOT-23 pinout) |
| 3 | RESE | continuity to GND (0.19 Ω) and to leg 2 of `KM` | `[MEASUREMENT]`. Consistent with RESE at the MOSFET source; no shunt resolvable with this meter (pin 8 reads 0.17 Ω) |
| 8 | BS | continuity to GND (0.17 Ω) | `[MEASUREMENT]` GND-connected. `[ASSUMPTION]` BS = low selects 4-wire SPI (with D/C line) |
| **9–14** | BUSY, RST, D/C, CS, SCK, SDI | diode 0.56 V / OL; 1.85–1.9 MΩ to GND, steady; not connected to each other | `[MEASUREMENT]` **the 6 signal lines are on 9–14.** Which signal is on which pin: `[ASSUMPTION]` standard order, settled by the capture |
| 15, 16 | VDDIO, VCI | bridged (0.18 Ω); 9.98 kΩ to GND after a capacitor-like rise; 16 → leg 3 of `XDt`; no continuity to battery plus | `[MEASUREMENT]` one supply net. `[ASSUMPTION]` switched by `XDt` (M-005) |
| 17 | VSS | continuity to GND | `[MEASUREMENT]` |
| 21 | PREVGH | diode 0.70 V (red on GND) | `[MEASUREMENT]` signature; see below |
| 23 | PREVGL | diode 0.43 V (red on pin) | `[MEASUREMENT]` signature; see below |
| 1, 4–7, 18–20, 22, 24 | NC/HLT, VGL, VGH, TSCL, TSDA, VDD, VPP, VSH, VSL, VCOM | OL both ways | `[MEASUREMENT]` no DC path — consistent with pins that only carry capacitors or are unconnected. Not individually verified |

`[ASSUMPTION]` The signatures on 21 and 23 match the boost topology of the
Waveshare driver HAT: pin 21 (PREVGH) reaches GND through the MOSFET body
diode plus one Schottky diode (≈ 0.5 + 0.2 V), pin 23 (PREVGL) through two
Schottky diodes in series (≈ 2 × 0.2 V), in the opposite direction.
→ **Test:** only an actual power-up measurement of the rails, which is not
planned; the capture is what matters.

**Update 2026-09-23 (captures):** `[CAPTURE]` roles of all six signal
pins are now established from captures on tag 02:

| Pin | Signal | Evidence |
|---:|---|---|
| 9 | BUSY (panel output; high ≈ 50 ms after reset = ready) | toggles only with panel plugged in |
| 10 | RST (active low, 10 ms pulse) | `…_boot-overview_2MHz.sr` |
| 11 | D/C (low = command) | constant within each byte frame |
| 12 | CS (active low, one frame per byte) | `…_boot-init_20MHz.sr` |
| 13 | SCK (idle low; ~6.4 MHz writes, ~1 MHz reads) | `…_boot-init-4ch_20MHz.sr` |
| 14 | **SDA — bidirectional data** (MCU writes and panel answers on the same line) | read bytes contain the panel serial, see `HISTORY.md` |

**Summary:** M-001 decision rule row 1 applies — the six signal lines are
contiguous on 9–14. The logic analyser may be connected to **pins 9–14 and
GND only** (see `capture-protocol.md`). The hypothesis warning at the top
stays for all pins whose *function* is still only assumed.

---

## What is already settled

`[PHOTO]` The **FPC itself is labelled**: at the contact end there is `24`
on one side and `1` on the other. The counting direction of the cable is
thereby unambiguous.

`[MEASUREMENT]` 2026-09-23: on the board, **pin 1 points towards the
centre of the board, pin 24 is at the board edge** (read from the `1`
printed on the inserted FPC). The FPC contacts face down, towards the
board. GND on pin 17 confirms the numbering is not mirrored.

---

## Verification — measurement request M-001

Everything unpowered, battery removed, multimeter on continuity.

### Step 1 — find anchor points

| Search | Identifying feature | Expected with standard |
|---|---|---|
| **GND** | continuity to the battery minus terminal | pin 17 (VSS) |
| **RESE** | approx. 0.5 – 3 Ω to GND (the small shunt) | pin 3 |
| **GDR** | continuity to the **gate** of the SOT-23 `KM` | pin 2 |
| **HV pins** | end at the bulky MLCCs | 4, 5, 20–24 |

### Step 2 — identify the digital lines

The decisive measurement: **which FPC pins have continuity directly to a
QFN pin of the FG22?**

There should be **exactly 6**: BUSY, RST, D/C, CS, SCK, SDI.

- If they are **contiguous on 9–14** → standard confirmed, the rest of the
  table is credible.
- If they are **elsewhere** → discard the hypothesis, reconstruct the
  pinout entirely from the measured values.

### Step 3 — plausibility check

If GND is the **8th pin from one end**, that end is pin 24 — then the
counting direction on the board is mirrored relative to the assumption.

---

## Measurement result

Is entered in `../hardware/measurements.md`. As soon as the digital lines
are confirmed there, **this file** is updated with `[MEASUREMENT]` markers
and the hypothesis warning above is removed.

---

## Note on the contact side

`[RESEARCH]` ESL displays typically have the FPC copper contacts on the
**bottom side**, Waveshare displays on the **top side**.

Relevant if a third-party adapter or an FPC extension cable is used after
all: then an **A-B cable** ("D-type") is needed as a reverser, not an A-A
cable. Before buying, check which side the contacts are on.
