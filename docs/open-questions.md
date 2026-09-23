# Open questions

The work backlog. Answered questions move with their result to
`../HISTORY.md` and are set to `✅` here — **not deleted**, so that the path
remains traceable.

The IDs (`F-01` …) are kept from the German original ("Frage") so that
existing references stay valid.

---

## Blocking — nothing works without these answers

### 🔴 F-01 What is the actual FPC pinout?

Update 2026-09-23 (later): **answered for the signal pins** — roles of
9–14 established from captures (9 BUSY, 10 RST, 11 D/C, 12 CS, 13 SCK,
14 bidirectional SDA), see `pinout.md`.

Status 2026-09-23: **largely answered.** `[MEASUREMENT]` Signal lines on
9–14, supply on 15/16, GND on 17, GDR on 2. Still open: which signal is on
which pin within 9–14 → the capture settles it. See `pinout.md`,
"Measurement status".

### 🔴 F-02 What resolution does the panel have?

**Update 2026-09-23 (capture):** `[CAPTURE]` the 70 bytes the MCU reads
from the panel at boot contain `01 E0 03 20` = **480, 800**.
`[ASSUMPTION]` That is the panel's resolution stored in its OTP →
**800 × 480** very likely. Confirmed only by a frame block of matching size.

**Update 2026-09-23:** `[RESEARCH]` VUSION 7.4 BWR: 800 × 480 px, 126 dpi
(datasheet, see `hardware.md`). For the BWRY version still to be confirmed
from the capture — expect one block of 96,000 bytes at 2bpp.

`EL074TS1`, approx. 170 × 112 mm, probably three-colour (see F-13).
`[ASSUMPTION]` 800 × 480 is purely a size plausibility, not a value from a
source.

→ Calculate back from the payload block lengths in the capture:
`pixels per plane = block length in bytes × 8`. Two planes if three-colour.

### 🔴 F-03 Which COG controller is in the panel?

Determines whether GxEPD2 can be used directly or a custom driver is
needed.

→ Match the command bytes from the capture against the usual candidates:
UC8179, SSD16xx, IL0373.

---

## Important, but not blocking

### 🟡 F-04 Is the waveform LUT written by the MCU or stored in OTP?

- **Written by the MCU** → it is in the capture, we get it for free.
- **In the COG's OTP** → we don't need it at all, the controller knows it.

→ Falls out automatically when evaluating the capture: a conspicuously long
data block right after the init is a LUT candidate.

### 🟡 F-05 Is the EFR32 debug-locked?

If **no**: read out and save the original firmware. That would be much
more valuable for the EPD driver than any capture, because the init
sequence is then in plain form in the binary.

If **yes**: the unlock erases it irrevocably → sniff first.

→ `commander device info` and `commander security status`, **before**
anything is written.

### 🟡 F-06 Where is the SWD port?

→ Measurement request **M-002**

### 🟡 F-07 QFN32 or QFN40?

Decides which pinout table of the datasheet applies.

→ Measurement request **M-003**

### 🟡 F-08 Does the tag draw an image at all when the battery is inserted?

The whole sniffing strategy relies on it. If not: plan B via NFC.

→ Becomes apparent at the first recording attempt.

Update 2026-09-23 (later): `[CAPTURE]` `2026-09-23_tag02_boot-long_2MHz.sr`
— **no SPI activity for 134 s after the boot sequence.** The tag does not
refresh on battery insertion. → Measurement request **M-010** (NFC), then
SWD read-out (F-05) or own driver.

Update 2026-09-23: `[CAPTURE]` `2026-09-23_tag02_boot-overview-panel_2MHz.sr`
— within 27 s after battery insertion **no refresh**: the tag initialises
the panel (~80 bytes), then powers it down. Maintainer: nothing visible on
the panel. Still open: whether a refresh happens later (capture was only
28 s) → a longer pass A (≥ 5 min).

---

## Downstream — only relevant after the capture

### ⚪ F-09 Path A or path B?

| | Path A (ESP32 on carrier board) | Path B (OpenEPaperLink port) |
|---|---|---|
| Wireless | no, wired | yes, battery-powered |
| Effort | medium | high |
| Risk | low | unlock is irreversible |

The decision is made **after** the capture, once it is clear how complex
the EPD driver will be.

### ⚪ F-10 Can the EFR32 be disabled non-destructively?

Hypothesis: RESETn permanently to GND → GPIOs go Hi-Z, the SPI bus is
freed.

→ Try it on **one** tag before hot air is used anywhere.

Status 2026-09-23: **no hot-air station available.** As long as that
remains so, RESETn to GND is the only feasible variant.

### ⚪ F-11 What do the test points TP1/TP2/TP3 on the FPC do?

Unclear. Possibly production test of the panel. Low priority.

### ⚪ F-12 What refresh rate does the panel tolerate in continuous operation?

`[RESEARCH]` For three-colour panels E Ink recommends minimum intervals of
several minutes between updates; a full frame takes 15–30 s.

Uncritical for a dashboard, an exclusion criterion for anything dynamic.

### ⚪ F-13 Is the panel really three-colour — and which third colour?

**Update 2026-09-23:** maintainer statement: product is a **VUSION 7.4
BWRY GU140 (EDG3-0740A)** → most likely **four colours B/W/R/Y**
(`[ASSUMPTION]` until a capture shows one 2bpp frame block or the display
shows yellow). Original text below.

`[ASSUMPTION]` B/W/red comes from the maintainer's memory, not from an
observation of the device. VUSION also exists with yellow.

→ Capture: two equally sized frame blocks = two planes = three-colour.
→ The third colour is only shown by a displayed image (original tag or our
own driver).

### 🟡 F-14 Is the panel supply (VDDIO/VCI) switched by the MCU?

`[MEASUREMENT]` 2026-09-23: none of the 24 FPC pins has continuity to
battery plus, although pins 15/16 are VDDIO/VCI in the standard.
`[ASSUMPTION]` The panel supply is switched (load switch or GPIO-powered).

Relevant for path A: with the EFR32 held in reset, a switched supply would
stay **off** — the ESP32 would then have to switch it on or feed pins 15/16
itself.

Update 2026-09-23: `[MEASUREMENT]` 15/16 are one net, 9.98 kΩ to GND,
connected to leg 3 of the SOT-23 `XDt`. `[ASSUMPTION]` `XDt` is a P-MOSFET
load switch. → Measurement request **M-005** (only needed for path A).

---

## Answered

*(still empty — entries move here with result and date)*
