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

## What is already settled

`[PHOTO]` The **FPC itself is labelled**: at the contact end there is `24`
on one side and `1` on the other. The counting direction of the cable is
thereby unambiguous.

`[ASSUMPTION]` **Still open:** at which end of the connector on the board
pin 1 is. Front and back are mirror images.
→ Insert the FPC and look at which end the `1` is.

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
