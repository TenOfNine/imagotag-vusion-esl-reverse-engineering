# Hardware — inventory

Everything known about the test object. Evidence markers per `CLAUDE.md` §3.

---

## Overall system

Electronic Shelf Label of the **VUSION** family by VusionGroup
(formerly SES-imagotag, renamed in 2024; majority owner BOE Technology).

`[RESEARCH]` The VUSION family operates at **2.4 GHz** and covers display
sizes from 1.6" to 12.2" in black/white/red or yellow.
The infrastructure consists of server, access points and the tags
themselves.

---

## Board

| Feature | Value | Evidence |
|---|---|---|
| Silkscreen | `imagotag  RFRTx026D` | `[PHOTO]` |
| Radio band | `2,4 GHz` (printed) | `[PHOTO]` |
| Other silkscreen | `315 17 94V-0`, `13` | `[PHOTO]` |
| Layers | `1 TOP` / `2 BOT` (printed) | `[PHOTO]` |
| Serial number (QR) | `060RFRTX026D00A120O262007587` | `[PHOTO]` `pcb-top-overview.webp` |

The serial number visibly contains the type designation `RFRTX026D`, but
beyond that provides no technical information.

---

## MCU — Silicon Labs EFR32FG22

`[PHOTO]` QFN marking, four lines:

```
FG22
C121GG
C026ZX
2419
```

- `FG22` → product family EFR32**FG**22 "Flex Gecko", proprietary 2.4 GHz
- `C121` → feature variant
- `2419` → date code **week 19 / 2024**

`[RESEARCH]` Key data of the C121 variant according to the EFR32FG22
Family Data Sheet:

| Feature | Value |
|---|---|
| Core | ARM Cortex-M33 |
| Max. clock | 38.4 MHz |
| Flash | 512 kB |
| RAM | 32 kB |
| Max. TX power | 6 dBm |
| Protocol | proprietary |
| Temperature range | −40 to 85 °C |

Two package variants:

| Order code | Package | GPIO |
|---|---|---|
| `EFR32FG22C121F512GM40-C` | QFN40, 5 × 5 mm | 26 |
| `EFR32FG22C121F512GM32-C` | QFN32, 4 × 4 mm | 18 |

`[ASSUMPTION]` **QFN40** is fitted, estimated from approx. 10 visible pads
per side in the photo.
→ **Test:** count pads per side under a magnifier. 10 = QFN40, 8 = QFN32.
The result decides which pinout table of the datasheet applies.

### Clock sources

| Component | Marking | Function | Evidence |
|---|---|---|---|
| Large crystal | `38.4  T4F` | HFXO, 38.4 MHz | `[PHOTO]` |
| Small crystal | `T422C` | LFXO, 32.768 kHz | `[PHOTO]` |

The 38.4 MHz exactly matches the reference clock of the EFR32 series —
strong confirmation of the MCU identification.

### Debug interface

`[RESEARCH]` EFR32 Series 2 supports **SWD only**, no JTAG.
The SWD pins are on **port A**. The concrete pin numbers depend on the
package → take them from the datasheet only after QFN32/QFN40 is settled.

`[RESEARCH]` Factory-locked xG22 can be unlocked as long as
"unauthenticated debug unlock" has not been disabled. **The unlock erases
the original firmware.** Tool: Simplicity Commander + J-Link.

---

## Panel — E Ink EL074TS1

| Feature | Value | Evidence |
|---|---|---|
| Designation | `EL074TS1` | `[PHOTO]` |
| Size | 7.4 inch (from the type designation `074`) | `[RESEARCH]` |
| Outer dimensions | approx. 170 × 112 mm | `[MEASUREMENT]` calliper, session 1 |
| Product | **VUSION 7.4 BWRY GU140**, model **EDG3-0740A** | maintainer statement (2026-09-23); FCC ID `2ACQM-EDG3-0740-A` `[RESEARCH]` |
| Colours | **four-colour B/W/R/Y** (from "BWRY" in the product name) — display not yet seen | `[ASSUMPTION]` |
| Serial number (QR) | `H7FZDSPQ0KXYZ5V00DAUAT` | `[PHOTO]` `panel-label-el074ts1.webp` |
| Resolution | 800 × 480 at 126 dpi for the VUSION 7.4 **BWR**; for BWRY not confirmed | `[RESEARCH]` / `[ASSUMPTION]` |
| COG controller | **unknown** | — |
| Waveform / LUT | **unknown** | — |

**Update 2026-09-23:** maintainer statement — the tag is a **VUSION 7.4
BWRY GU140, model EDG3-0740A**. `[ASSUMPTION]` BWRY = black/white/red/
yellow, i.e. a **four-colour** panel. Such panels usually take **2 bits
per pixel in one data plane** instead of two 1-bit planes — at 800 × 480
that is one block of **96,000 bytes** (not 2 × 48,000).
`[RESEARCH]` The VUSION 7.4 BWR datasheet gives 800 × 480 px at 126 dpi
(https://www.glds.net/file/datasheet_ESL_VUSION_7_4_BWR_2_4GHz.pdf, via
search result; not opened). 800/126 × 480/126 in = 161 × 97 mm, diagonal
7.40" — consistent with the measured 170 × 112 mm outline.
`[RESEARCH]` Known BWRY panels of this size class use controllers such as
the JD7966x family (e.g. Good Display GDEM075F53, 800 × 480 BWRY,
https://www.good-display.com/product/546.html). Nothing says this panel
uses one of them.

(Older note, superseded:)
`[ASSUMPTION]` Three-colour B/W/red comes from the maintainer's memory.
The VUSION family also exists with **yellow** as the third colour.
→ **Test:** two equally sized data blocks in the capture (e.g. `0x10` +
`0x13`) indicate two planes, i.e. three-colour. Which third colour is only
shown by a displayed image.

`[RESEARCH]` **No public datasheet can be found.** Searched directly for
the type designation as well as via E Ink and distributor catalogues.
ESL panels are supplied to OEMs under NDA.

`[ASSUMPTION]` Resolution 800 × 480 — purely a size plausibility for 7.x",
**not a reliable value**.
→ **Test:** calculate back from the payload block lengths in the capture.
With two colour planes, `pixels = block length × 8` per plane.

### FPC

| Feature | Value | Evidence |
|---|---|---|
| Contacts | **24** | `[PHOTO]` |
| Pitch | 0.5 mm | `[PHOTO]` |
| Label at the contact end | `1` and `24` printed | `[PHOTO]` |
| Test points on the FPC | `TP1`, `TP2`, `TP3` | `[PHOTO]` |

Contact count and pitch were determined by colour segmentation and FFT
period analysis on two independent photos, results consistent.

Pinout → see `pinout.md`.

---

## Power stage (boost for the EPD voltages)

`[PHOTO]` To the right of the ZIF connector, standard pattern for an e-ink
COG with integrated DC/DC:

| Component | Marking | Presumed function |
|---|---|---|
| Storage inductor | — | boost inductor |
| SOT-23 | `KM` | switching MOSFET, gate-driven by `GDR` |
| SOD diodes | `4`, `BR`, `ZV` | Schottky rectifiers for VGH/VGL/VSH/VSL |
| MLCCs (large) | — | reservoir capacitors of the HV rails |

**This is the reason to keep the original board:** this circuitry is
correctly dimensioned and correctly wired. This is exactly where a
third-party adapter destroys the panel.

### Other unclear components

`[PHOTO]` SOT-23 packages with markings `S21`, `XDt`, `T0.`, `1R.` —
function unclear, probably LDO, load switch and/or level shifter.

---

## NFC

| Feature | Value | Evidence |
|---|---|---|
| IC | SO-8, marking `8K417 / 0E47AH` | `[PHOTO]` |
| Antenna | large coil on the back side | `[PHOTO]` |
| Label inside the coil | handwritten `0181` | `[PHOTO]` |

`[ASSUMPTION]` The SO-8 is the NFC front end.
→ **Test:** measure continuity IC ↔ antenna coil.

**Relevance:** plan B. If the tag does not draw a refresh when the battery
is inserted, the refresh might be triggered via NFC — and the capture
obtained after all.

---

## Back side

| Feature | Evidence |
|---|---|
| NFC antenna coil, upper area | `[PHOTO]` |
| Two LEDs (clear + yellow), bottom centre | `[PHOTO]` |
| `2 BOT` — layer label, **not** a test point | `[PHOTO]` |
| Four soldered vias bottom left = battery contact solder joints | `[PHOTO]` |
| **Four open vias** on the right, left of `2 BOT` | `[PHOTO]` |

`[ASSUMPTION]` The four open vias are the **SWD port**
(SWDIO, SWCLK, GND, VDD, possibly RESET). Arrangement: one on the left, one
on the right, two close together below, larger hole above.
→ **Test:** measurement request M-002.
