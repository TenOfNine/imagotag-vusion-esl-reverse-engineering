# HISTORY — long-term memory of the project

Chronological log of all insights, attempts and dead ends.

**Rules for this file** (see also `CLAUDE.md` §4):

- New entries are **appended at the bottom**, old ones are never rewritten.
- A correction is a **new entry with a reference** to the old one.
- **Failures belong in here.** A documented wrong turn prevents it from
  being repeated.
- Every factual claim carries an evidence marker:
  `[MEASUREMENT] [CAPTURE] [PHOTO] [RESEARCH] [ASSUMPTION] [REFUTED]`

> **Translation note:** Up to and including the entry "Session 2: Session 1
> follow-up questions answered", this file was originally written in German
> and was translated into English on 2026-09-23 with the maintainer's
> approval (see the last entry). The unaltered German original is in
> `docs/archive/HISTORY.de.md`. The German evidence markers were mapped
> 1:1: `[MESSUNG]` → `[MEASUREMENT]`, `[MITSCHNITT]` → `[CAPTURE]`,
> `[FOTO]` → `[PHOTO]`, `[RECHERCHE]` → `[RESEARCH]`,
> `[ANNAHME]` → `[ASSUMPTION]`, `[WIDERLEGT]` → `[REFUTED]`.
> Markers were translated as they stood, **not** corrected — corrections
> are in later entries.

---

## 2026-09-22 — Session 1: Identifying the hardware

Starting point: the maintainer has more than five decommissioned ESL tags
and wants to drive the panels with their own ESP32. First photos of the
panel and the top side of the board.

### Panel

- `[PHOTO]` The panel carries the designation **`EL074TS1`** → E Ink,
  7.4 inch.
- `[MEASUREMENT]` Maintainer: outer dimensions approx. **170 × 112 mm**.
  Matches the usual 7.x-inch raw panel outline.
- `[MEASUREMENT]` Maintainer: the panel is **three-colour**
  (black/white/red).
- `[RESEARCH]` **No public datasheet can be found** for `EL074TS1`.
  Searched directly for the part number as well as via E Ink and
  distributor catalogues. ESL panels are supplied to OEMs under NDA.
  → This is the central hurdle of the project.
- `[PHOTO]` Three test points **`TP1`, `TP2`, `TP3`** are printed on the
  FPC. Function unknown.

### Board

- `[PHOTO]` Silkscreen: **`imagotag  RFRTx026D`**, plus `2,4 GHz`,
  `315 17 94V-0`, `13`, layer labels `1 TOP` / `2 BOT`.
- `[MEASUREMENT]` QR code on the board decodes to
  `060RFRTX026D00A120O262007587`.
- `[MEASUREMENT]` QR code on the panel decodes to `H7FZDSPQ0KXYZ5V00DAUAT`.
  → Both are serial numbers, **no additional technical value**. Dead end.

### MCU

- `[PHOTO]` QFN marking: **`FG22 / C121GG / C026ZX / 2419`**
  → **Silicon Labs EFR32FG22**, date code week 19/2024.
- `[RESEARCH]` The `C121` variant exists in two packages:
  QFN40 with 26 GPIO and QFN32 with 18 GPIO. Both: proprietary 2.4 GHz,
  6 dBm, 512 kB flash, 32 kB RAM, ARM Cortex-M33, max. 38.4 MHz.
  Source: EFR32FG22 Family Data Sheet.
- `[ASSUMPTION]` The package is **QFN40** (`EFR32FG22C121F512GM40`),
  derived from approx. 10 visible pads per side in the photo.
  → **Test:** count pads per side under a magnifier. 10/side = QFN40,
  8/side = QFN32.
- `[PHOTO]` Two crystals: **38.4 MHz** (marking `38.4 T4F`, HFXO) and
  **32.768 kHz** (marking `T422C`, LFXO). The 38.4 MHz exactly matches the
  reference clock of the EFR32 series.

### Other components

- `[PHOTO]` SO-8 with marking **`8K417 / 0E47AH`**.
  `[ASSUMPTION]` NFC front end, since there is an NFC antenna coil on the
  back side.
  → **Test:** measure continuity from this IC to the coil.
- `[PHOTO]` Boost circuitry to the right of the ZIF connector: storage
  inductor, SOT-23 MOSFET (marking `KM`), several Schottky diodes (`4`,
  `BR`, `ZV`), bulky MLCCs.
  → Matches the standard pattern for an e-ink COG with integrated DC/DC.
- `[PHOTO]` Further SOT-23: `S21`, `XDt`, `T0.`, `1R.` — function unclear.

### FPC connector

- `[PHOTO]` **24 contacts, 0.5 mm pitch.** Determined by colour
  segmentation and FFT period analysis on two independent photos, results
  consistent. Matches the de-facto standard for e-paper.

### Research on the ecosystem

- `[RESEARCH]` The VUSION family (2.4 GHz) exists from 1.6" to 12.2" in
  black/white/red or yellow.
- `[RESEARCH]` Several documented Imagotag hacks exist, but all for
  **older, different hardware**: CC2510-based Vusion 2.2/2.6 BWR,
  AX8052-based UU340. None of them fits `RFRTx026D`.
  → This work is methodologically useful, not directly transferable.
- `[RESEARCH]` **OpenEPaperLink** has firmware for EFR32xG22-based tags
  (`Tag_FW_EFR32xG22`). Supported so far: **Solum M3** and **Pricer HD150**
  (the latter via modchip). No Vusion port exists.
  → Path B would therefore be a **porting** project, not a new development.
- `[RESEARCH]` Debug-locked EFR32xG22 can be unlocked as long as
  "unauthenticated debug unlock" has not been disabled. **The unlock erases
  the original firmware.** Recommended tool: Simplicity Commander with a
  J-Link-based debugger.
  → Hence the order: **sniff first, then unlock.**

---

## 2026-09-22 — Session 1: Change of strategy

**Original plan:** separate the panel from the original board and connect
it to a Waveshare driver board.

**Rejected**, because: the original board contains the complete, correctly
dimensioned boost circuitry for VGH/VGL/VSH/VSL/VCOM. That is exactly where
a third-party adapter destroys the panel — swapped VGH/VGL (±20 V) kill it
immediately. In addition, ESL FPCs typically have their copper contacts on
the opposite side compared to Waveshare displays, which requires an A-B
reversing cable.

**New plan:** keep the original board as a carrier board. Only 8 lines to
the ESP32 are needed: 3V3, GND, SCK, MOSI, CS, D/C, RST, BUSY.

Two options for disabling the EFR32, in this order:
1. **Tie RESETn permanently to GND** — GPIOs go Hi-Z, non-destructive,
   reversible. Try this first.
2. Remove the QFN with hot air — final, but acceptable with >5 tags.

---

## 2026-09-22 — Session 1: Maintainer's constraints

- `[MEASUREMENT]` The maintainer owns **more than 5 tags**.
- Maintainer: the original board may be sacrificed.
- Maintainer: goal still open between "drive exactly this panel" and
  "quickly get an e-ink dashboard".
- `[MEASUREMENT]` Available instruments: **Sipeed SLogic Combo 8** (with
  PulseView), **SEGGER J-Link**, FTDI USB serial adapter. Details in
  `TOOLS.md`.

### Clarification on the FTDI

The maintainer asked whether the FTDI adapter is sufficient for the JTAG
part.

- `[RESEARCH]` **No.** First, EFR32 Series 2 supports **only SWD, no
  JTAG**. Second, only FTDI chips with an MPSSE engine (FT2232H, FT232H,
  FT4232H) can do SWD via OpenOCD at all, and only with a resistor trick
  between TDI and TDO. Classic FT232R/FT231X can only do UART.
- `[RESEARCH]` Even with an FT2232H the problem remains: on Series 2 the
  unlock goes through the **Authentication Access Port of the Secure
  Engine**. Simplicity Commander supports only J-Link for that.
  → Moot, since a J-Link is available.

---

## 2026-09-23 — Session 1: Back side of the board

### Breakthrough on the counting direction

- `[PHOTO]` The **FPC itself is labelled**: at the contact end there is
  **`24`** on one side and **`1`** on the other.
  → The counting direction is thereby settled at the source, no hypothesis
  needed.
- `[ASSUMPTION]` **Still open:** which end of the connector on the board is
  pin 1. Front and back are mirror images; this cannot be determined from
  the photos so far.
  → **Test:** insert the FPC and look at which end the `1` is.

### Further observations on the back side

- `[PHOTO]` Large **NFC antenna coil** in the upper area, with a
  handwritten `0181` in the middle. Indirectly confirms the NFC chip.
- `[PHOTO]` Two **LEDs** (one clear, one yellow) at the bottom centre —
  probably the tag's locate/status LEDs.
- `[PHOTO]` `2 BOT` is a **layer label**, not a test point.
- `[PHOTO]` The four soldered vias at the bottom left are the **solder
  joints of the battery spring contacts** from the front side.
  Not test points. (Corrects an earlier guess by the maintainer.)
- `[ASSUMPTION]` **Four open, uncovered vias** in the right half of the
  image, to the left of the `2 BOT` label: one on the left, one on the
  right, two close together below, plus a larger hole above.
  Number and arrangement fit **SWD** (SWDIO, SWCLK, GND, VDD, possibly
  RESET).
  → **Test:** continuity against battery minus, battery plus and the
  port A pins of the FG22.

---

## Open thread at the end of session 1

**Nothing has been measured electrically yet.** All pinouts are hypotheses
based on the Waveshare standard.

Next step: measurement request **M-001** in `docs/measurement-requests.md`
(continuity check of the FPC connector), then the first capture according
to `docs/capture-protocol.md`.

---

## 2026-09-23 — Session 2: Handover to Claude Code

### What was tried
Project taken over from Claude chat into Claude Code (cloud session).
Read every file in the repo. Checked the decoder with the synthetic
capture:

```bash
python3 analysis/make_testcapture.py <scratch>/fake.csv
python3 analysis/decode_spi.py <scratch>/fake.csv --busy D4 --rst D5 --out-prefix <scratch>/fake
```

Environment: Python 3.11; `numpy` and `pandas` had to be installed first
(not listed as a dependency anywhere in the repo).

### Result
- The decoder runs without errors: 10 transactions, reset, BUSY phase
  0.50 s, fingerprint UC8179 66.7 %, two equally sized blocks of 2,400
  bytes each detected. Runtime approx. 12 s for 10.4 million samples.
  → Only proves that the decoder understands its own test fixture.
  It says **nothing** about the real panel.
- Notable in the test capture: `TRES` reports `03 20 01 E0` (= 800 × 480),
  but the blocks only have 2,400 bytes (= 19,200 pixels). The decoder does
  **not** cross-check TRES against the block length. With the real capture,
  exactly this check would be a strong plausibility test.
- Opcodes `0x15` and `0x60` are shown without a description in the UC8179
  log.
- Open scaling question: a pass B (40 MSa/s × 30–60 s) yields 1.2–2.4
  billion samples. The decoder loads the whole CSV via pandas — whether
  that fits in the RAM of the maintainer's computer is untested.

### What follows
No new hardware insight. Status unchanged: **nothing measured**,
M-001 to M-003 open.

### Next step
Questions to the maintainer (multimeter available? operating system for
PulseView? FPC extension available?), then M-001.

---

## 2026-09-23 — Session 2: Instruments clarified

### Maintainer statements
- Multimeter: **OWON HDS242** — handheld oscilloscope (2 channels,
  40 MHz) with built-in multimeter including continuity tester. Key data
  `[RESEARCH]`, sources in `TOOLS.md`.
- FTDI adapter: stated as "FTDI1232". `[ASSUMPTION]` FT232R(L), i.e. UART
  only.
  → **Test:** read the chip marking. Not critical for the project.
- **No FPC extension**, **no hot-air station**, only a regular soldering
  station.
- PulseView runs on **Windows**.

### What follows
- M-001 to M-003 can be carried out with the HDS242.
- Capture only by **soldering to the vias** (capture path B).
- Sample-rate ceiling **20 MSa/s at 8 channels**. With SPI > 4 MHz,
  reduce to 4 channels.
- With the oscilloscope, logic levels and SPI clock can be checked
  **before** connecting the SLogic → new section 2a in
  `docs/capture-protocol.md`. This protects the SLogic against levels
  > 3.6 V and reveals 1.8 V logic it would not see.
- Desoldering the EFR32 (path A, variant 2) is **currently not feasible**
  without hot air. Only RESETn to GND remains (F-10).

---

## 2026-09-23 — Session 2: Correction of evidence markers from session 1

Corrects entries from "Session 1: Identifying the hardware" and
"Session 1: Maintainer's constraints". The old entries remain unchanged.

- "Maintainer owns more than 5 tags" and "instruments available" were
  marked `[MEASUREMENT]` (German original: `[MESSUNG]`). These are
  **maintainer statements**, not measurements. `CLAUDE.md` §3 has no marker
  of its own for them; from here on they are recorded as "maintainer
  statement" without an evidence marker.
- QR codes of board and panel: marked `[MEASUREMENT]`. How they were
  decoded (maintainer's scanner or from the photo) cannot be traced from
  the repo. From the photo it would be `[PHOTO]`.
  → **Open question to the maintainer.**
- Outer dimensions "approx. 170 × 112 mm" and "three-colour": marked
  `[MEASUREMENT]`, but without the date and method required by
  `CLAUDE.md` §3.
  → **Open question:** measured with what (ruler, calliper)? Three-colour
  seen on a displayed image?

---

## 2026-09-23 — Session 2: Decoder extended

### What was changed
- Created `analysis/requirements.txt` (`numpy`, `pandas`).
- `decode_spi.py` now cross-checks a `0x61` command (TRES) against the
  block lengths. Two payload layouts: 4 bytes (UC8179) and 3 bytes
  (IL0373). `[RESEARCH]` Layouts from memory of the controller families,
  not checked against a datasheet in the repo.
- `decode_spi.py` now loads only the required channels as `uint8` instead
  of all columns as `int64`. Reduces RAM requirements roughly tenfold.

### Result
- Test capture: transaction log, `_blocks.csv` and `_init_sequence.py`
  **byte-identical** to the output before the change.
- The TRES check correctly reports `MISMATCH` for the test capture
  (800 × 480 announced = 48,000 bytes, blocks have 2,400 bytes).
  The contradiction lies in `make_testcapture.py`, not in the decoder.

### What it does not prove
That the decoder can process a real PulseView export. Only the first real
capture will show that. Even after the change, a pass B at 20 MSa/s × 60 s
needs roughly 7 GB of RAM for the raw data alone.

---

## 2026-09-23 — Session 2: Correction to "Decoder extended"

The TRES payload layouts (UC8179: 4 bytes, IL0373: 3 bytes) were marked
`[RESEARCH]` there, without a source link. Correct is `[ASSUMPTION]`.
→ **Test:** compare against the UC8179 and IL0373 datasheets, or with the
real capture: if the check yields `MATCH`, that supports the layout used.

---

## 2026-09-23 — Session 2: Session 1 follow-up questions answered

Supplements "Session 2: Correction of evidence markers from session 1".

### QR codes → `[PHOTO]`
- The maintainer does not remember, presumes decoding from the photos.
- `[PHOTO]` Re-checked with OpenCV (`cv2.QRCodeDetector`) directly on the
  photos in the repo, result reproducible:
  - `pcb-top-overview.webp`, `pcb-top-mcu.webp`, `panel-fpc-overview.webp`
    → `060RFRTX026D00A120O262007587`
  - `panel-label-el074ts1.webp` → `H7FZDSPQ0KXYZ5V00DAUAT`
- Both values match session 1. The `[MEASUREMENT]` marker from session 1
  is hereby replaced by `[PHOTO]` (in `docs/hardware.md`).

### Outer dimensions → `[MEASUREMENT]` confirmed
- Maintainer: measured with a **calliper**, in session 1. Exact date no
  longer known. Row added to `hardware/measurements.md`.

### Three-colour → `[ASSUMPTION]`
- Maintainer: colour **from memory only**. Confirmation only once the
  display shows something.
- `[ASSUMPTION]` Three-colour B/W/red. According to the research in
  session 1, VUSION also exists with yellow.
  → **Test:** two equally sized frame blocks in the capture = two planes.
  The third colour is only shown by a displayed image. New as F-13 in
  `docs/open-questions.md`.

### FTDI
- Maintainer: the adapter can do "only UART, as far as I know". Not
  verified, but irrelevant for the project (J-Link available). Not pursued
  further.

---

## 2026-09-23 — Session 2: Repo switched to English, new working rules

### Maintainer decisions
- **Chat in German, everything in the repo in English** (docs, history,
  code, commit messages).
- The whole existing repo is translated now, including the evidence
  markers (`[MESSUNG]` → `[MEASUREMENT]` etc., mapping in the note at the
  top of this file).
- `HISTORY.md` is translated as a one-time, explicitly approved exception
  to the append-only rule. The unaltered German original is archived in
  `docs/archive/HISTORY.de.md`.
- **Push directly to `main`**, no pull requests. Ask only before large
  changes.

### What was changed
- All Markdown files and `.gitignore` comments translated to English.
- `CLAUDE.md` §3: maintainer statements documented as "maintainer
  statement" without a marker (already practised since the marker
  correction above, now written down).
- `CLAUDE.md` §4: note on the translation exception and the archive.
- `CLAUDE.md` §6: language and git workflow rules.
- `CLAUDE.md` §7: `docs/archive/` and `analysis/requirements.txt` added.

### Small content additions made during the translation
- `docs/measurement-requests.md`: tool named as OWON HDS242 for M-001 and
  M-002; M-003 notes that no magnifier/microscope is available and that a
  phone camera macro shot may be enough.
- `docs/references.md`: OWON HDS242 retailer sources added (they were
  previously only in `TOOLS.md`).
- `docs/open-questions.md`: note that the IDs `F-01` … are kept from the
  German original ("Frage") so references stay valid.
- `README.md`: install command and Windows `py` hint in the analysis
  section; "next step" now names M-001 first.

Otherwise no technical content was added or removed. Where the translation
had to interpret, the German archive is authoritative.

---

## 2026-09-23 — Session 2: M-001 started — counting direction and GND

### What was measured (maintainer statements, first M-001 results)
- `[MEASUREMENT]` Counting direction on the board: **pin 1 points towards
  the centre of the board, pin 24 is at the board edge.** Read from the `1`
  printed on the FPC cable, 2026-09-23.
- `[MEASUREMENT]` The FPC contacts face **down** (towards the board) and are
  not visible once the cable is unplugged. 2026-09-23.
- `[MEASUREMENT]` **Pin 17 = GND**, 2026-09-23. Method not stated yet
  (presumably continuity to battery minus with the OWON HDS242). Tag number
  not stated yet.

### What follows
- Plausibility check from `docs/pinout.md` step 3 passes: GND is the 8th
  pin counted from the pin 24 end, as in the standard. The board is **not**
  mirrored relative to the FPC numbering.
- This is **one** matching pin. It does not confirm the rest of the
  standard pinout.
- Contacts facing down agrees with `[RESEARCH]` on ESL FPCs (contacts on
  the bottom side, see `docs/pinout.md`). Only relevant if an FPC extension
  is ever bought (A-B cable).

### Next step
M-001 was refined into four rounds (GND, VDD, diode signature, targeted
checks), see `docs/measurement-requests.md`. The measurement table in
`hardware/measurements.md` got columns for them. The diode round lets the
MCU-connected pins be found from the connector side, without probing the
QFN pads. Its expected values are an `[ASSUMPTION]` (ESD diode forward
drop), tested by the round itself.

---

## 2026-09-23 — Session 2: M-001 rounds 1–4 — FPC pin signatures

### What was measured
Maintainer, 2026-09-23, FPC **unplugged**, battery out, board side of the
ZIF connector. Instrument presumably OWON HDS242 (not stated), tag number
not stated. Full table in `hardware/measurements.md`.

- `[MEASUREMENT]` Round 1, continuity to battery minus: **pins 3, 8, 17**
  beep. All others do not.
- `[MEASUREMENT]` Round 2, continuity to battery plus: **no pin** beeps.
- `[MEASUREMENT]` Round 3, diode mode:
  - pins 3, 8, 17: ≈ 0.001 V both ways (short to GND)
  - **pins 9–16**: 0.56 V with red on GND, OL reversed
  - pin 21: 0.7 V with red on GND, OL reversed
  - pin 23: OL with red on GND, 0.4343 V reversed
  - pins 1, 2, 4–7, 18–20, 22, 24: OL both ways
- `[MEASUREMENT]` Round 4: leg 1 of the `KM` SOT-23 has continuity to
  **FPC pin 2**. (That leg 1 is the gate is `[ASSUMPTION]`, usual SOT-23
  MOSFET pinout.)

### Interpretation
- Everything is **consistent with the standard pinout** in
  `docs/pinout.md`; nothing contradicts it:
  - 17 = GND, 2 = GDR as expected.
  - 3 on GND fits RESE (shunt of well under 1 Ω looks like a short to the
    meter). Not yet distinguished from plain GND.
  - 8 on GND fits BS tied low. `[ASSUMPTION]` BS low = 4-wire SPI, i.e. a
    separate D/C line — which matches pin 11 having a signal signature.
  - `[ASSUMPTION]` 21/23 match the Waveshare HAT boost topology
    (PREVGH: FET body diode + Schottky ≈ 0.7 V; PREVGL: two Schottky in
    series ≈ 0.43 V, opposite direction).
- **Deviation from the decision rule:** 8 pins with a signal-like diode
  signature (9–16), not 6. 15/16 are VDDIO/VCI in the standard. The diode
  test cannot tell a supply net fed by the MCU from a GPIO line.
- **No pin connects to battery plus.** `[ASSUMPTION]` The panel supply is
  switched by the MCU (load switch or GPIO). New question F-14 — relevant
  for path A, because with the EFR32 in reset the panel would stay
  unpowered.

### What it does not prove
That 9–14 are exactly BUSY/RST/D/C/CS/SCK/SDI in that order. The diode test
shows "connected to a semiconductor pin", not which signal. The order is
only settled by the capture (SCK toggles, D/C pattern, BUSY is driven by
the panel).

### Next step
M-001 round 5 (separate 9–14 from 15/16, find the supply switch, confirm
RESE), added to `docs/measurement-requests.md`.

---

## 2026-09-23 — Session 2: M-001 round 5 — signal lines are on 9–14

### What was measured
Maintainer, 2026-09-23, **OWON HDS242**, FPC unplugged, battery out. Tag:
the one shown in `hardware/photos/` (no number assigned yet). This also
answers the open questions from the previous two entries (instrument,
FPC state).

- `[MEASUREMENT]` 5a: pin 15 ↔ pin 16: continuity, 0.18 Ω.
- `[MEASUREMENT]` 5b: resistance to GND: pins 9–14 **1.85–1.9 MΩ**,
  steady; pins 15/16 rise to **9.98 kΩ** within 2 s.
- `[MEASUREMENT]` 5c: pin 16 ↔ **leg 3 of the SOT-23 `XDt`**. The parts
  marked `T0.` and `1R.` in session 1 were not found by the maintainer.
- `[MEASUREMENT]` 5d: pin 3 ↔ **leg 2 of the `KM` SOT-23**.
- `[MEASUREMENT]` 5e: pin 3 → GND 0.19 Ω, pin 8 → GND 0.17 Ω.

### Interpretation
- **15/16 are one supply net** (bridged, capacitor-like rise, 10 kΩ to
  GND), clearly different from 9–14 (no capacitor, MΩ range, not bridged).
  → Exactly **6 signal lines, contiguous on 9–14.** M-001 decision rule
  row 1 applies: the standard pinout is confirmed for the position of the
  signal group, GND (17), GDR (2) and VDDIO/VCI (15/16). M-001 closed.
- `[ASSUMPTION]` `XDt` is a P-MOSFET load switch for the panel supply (leg 3
  = drain, usual SOT-23 pinout). Together with "no pin on battery plus"
  this supports F-14. Follow-up: M-005 (path A only).
- `[ASSUMPTION]` The 9.98 kΩ on the supply net is a bleeder/pull-down that
  discharges the panel supply when switched off.
- Pin 3 sits on the `KM` source (leg 2, usual pinout) — consistent with
  RESE. A shunt, if any, is below the resolution of the meter
  (0.19 vs. 0.17 Ω is within lead/contact tolerance).

### What it does not prove
- Which signal is on which of the pins 9–14. That comes from the capture.
- The function of the OL pins (1, 4–7, 18–20, 22, 24). Not needed for the
  capture.

### Next step
- **M-004:** find solder points (vias) for pins 9–14 and GND.
- Then `capture-protocol.md`, starting with the oscilloscope check in
  section 2a — now including the voltage on pin 15 (VDDIO), which is the
  logic level of all six signals.
- M-005 (`XDt` legs) only if path A becomes relevant.

---

## 2026-09-23 — Session 2: Tag numbering, M-004 reported found

- Maintainer statement: tags get physical labels. **Tag 01** = reference
  unit (untouched). **Tag 02** = the tag shown in `hardware/photos/`, used
  for M-001. All M-001 results from today refer to tag 02.
- Maintainer statement: solder points for pins 9–14 "probably all found"
  (M-004). Locations not yet documented.
- Next: oscilloscope check (`capture-protocol.md` §2a), then pass A.

---

## 2026-09-23 — Session 2: First capture (pass A) — panel never signals ready

### What was tried
- Tag 02, SLogic Combo 8, PulseView on Windows, **2 MSa/s**, 71.7 s.
- Channels (named in the session file): D0 = pin 9, D1 = pin 10,
  D2 = pin 11, D3 = pin 12, D4 = pin 13, D5 = pin 14. D6/D7 unnamed.
- Refresh trigger: presumably battery insertion (not stated).
- Raw file: `captures/2026-09-23_tag02_boot-overview_2MHz.sr` (143 KB,
  sha256 `6158904d…6de3a8`, archive timestamp 2026-09-23 18:33:56).
- Evaluated with the new `analysis/sr_overview.py`; output in
  `analysis/out/2026-09-23_tag02_boot-overview_2MHz_overview.txt`.
- Not stated by the maintainer: whether the scope check (§2a) was done,
  whether the panel was plugged in, whether the display changed.

### Result
- `[CAPTURE]` Pin 14 goes high at 1.62 s (presumably power-up) and stays
  high for the whole capture. It never toggles.
- `[CAPTURE]` **Pin 9 is low for the entire capture. No edge at all.**
- `[CAPTURE]` A cycle repeats **three times**, period ≈ 10.59 s:
  1. pin 12 rises (6.667 s),
  2. pin 10: high → low for **10.05 ms** → high (20.1 ms after pin 12),
  3. **≈ 10.08 s of silence**,
  4. a short transaction (~200 µs): pin 12 low; one short burst; pin 11
     rises; three bursts of 8 pulses on pin 13, each framed by pin 12;
     pin 11 falls,
  5. pin 12 and pin 10 go low (≈ 0.46 s), then the next cycle.
  After the third cycle (38.22 s) nothing happens until the end (71.7 s).
- `[CAPTURE]` Pin 13 shows the bursts of pulses at 0.5 µs spacing —
  exactly the sample resolution. The SPI clock is therefore **≥ ~1 MHz**;
  its exact value cannot be determined at 2 MSa/s (aliasing).
- `[CAPTURE]` No long data blocks. **No image data was transferred.**
- `[CAPTURE]` Lines reached valid high levels on the SLogic (VIH > 2 V),
  so the logic level is at least ~2 V. This does not replace the scope
  check for the upper limit.

### Interpretation
- `[ASSUMPTION]` The roles match the standard order: pin 10 = RST (clean
  10 ms reset pulse), pin 11 = D/C (low for the first byte, high for the
  following ones), pin 12 = CS (idle high, framing each byte), pin 13 = SCK
  (8 pulses per byte), pin 9 = BUSY. → **Test:** pass B at 20 MSa/s.
- `[ASSUMPTION]` The ≈ 10.08 s gap is a **BUSY timeout**: after the reset
  the firmware waits for the panel to signal "ready", gives up, sends a
  short command (probably power-off/deep-sleep), powers down and retries —
  three times. That BUSY stays low is consistent with a UC81xx-type
  controller (BUSY low = busy) that never becomes ready.
  → **Test:** M-006.
- Pin 14 (SDI in the standard) constantly high is unexplained. If it is
  MOSI, all transmitted bits were 1 — or the first byte was clocked faster
  than the sample rate can show. Pass B settles it.

### What it does not prove
- That the panel is broken. The most likely simple cause is that the panel
  was not plugged in (it was unplugged for M-001) or the pin 9 wire is not
  connected. Both are checked in M-006.
- The exact SPI clock.

### Next step
M-006 (panel plugged in? pin 9 solder point? display reaction?), then
repeat pass A. Pass B only once BUSY shows activity.

---

## 2026-09-23 — Session 2: Pass A explained — panel was not plugged in

- Maintainer statement: during the first pass A the **panel was not
  plugged in** (it had been unplugged for M-001).
- This explains the flat BUSY line and the three timeout cycles in
  `captures/2026-09-23_tag02_boot-overview_2MHz.sr`. The capture is kept:
  it documents how the original firmware behaves **without a panel**
  (reset, ≈ 10.08 s wait, short command, power-down, three retries, then
  give up) — useful later as a reference for timeouts.
- `[ASSUMPTION]` "BUSY low = busy / not ready" (UC81xx-style) remains an
  assumption until a capture with the panel shows BUSY toggling.
- Next: pass A repeated with the panel plugged in.

---

## 2026-09-23 — Session 2: Pass A with panel — BUSY works, no refresh, no data on pin 14

### What was tried
- Tag 02, panel plugged in, SLogic 2 MSa/s, 28.0 s. Battery inserted after
  the recording had started. Channel names as before (D0 = pin 9 …
  D5 = pin 14).
- Raw file: `captures/2026-09-23_tag02_boot-overview-panel_2MHz.sr`
  (sha256 `7a1370fc…7a87`, archive timestamp 2026-09-23 18:42:52).
  Overview: `analysis/out/2026-09-23_tag02_boot-overview-panel_2MHz_overview.txt`.
- Maintainer statement: **nothing was visible on the panel.**

### Result
- `[CAPTURE]` 0.81 s: pin 14 high (battery in). 5.8585 s: pin 12 high.
- `[CAPTURE]` Reset on pin 10: high 5.8786 s, low 5.8887 s (10.05 ms), high
  5.9088 s — same timing as in the first capture.
- `[CAPTURE]` **Pin 9 now reacts:** a 0.78 ms high pulse at each rising
  edge of pin 10, then low, then **high at 5.9584 s** (49.6 ms after the
  reset) and high throughout the following transfer.
- `[CAPTURE]` 10.7 ms later, 5.9691–5.9704 s, **82 CS frames** (pin 12
  low per byte):
  - frame 1: D/C low, clocks too fast for 2 MSa/s (1 visible pulse);
    then 3 frames D/C high with 8 clean pulses each (1 µs period);
  - frames 5–12: mixed D/C, again too fast to resolve (0–1 visible
    pulses);
  - frame 13: D/C low (command), then **70 frames with D/C high and 8
    clean pulses each** (1 µs period, ~14 µs per byte).
- `[CAPTURE]` 5.9705 s: pins 9–13 all drop low within ~10 µs — the panel
  is powered down (consistent with F-14). Nothing else until the end.
- `[CAPTURE]` **Pin 14 never toggles** — high from 0.81 s to 27.65 s,
  exactly like in the first capture (0 data edges).
- No large data block — **no image transfer, no refresh.**

### Interpretation
- `[CAPTURE]` Pin 9 behaves like a BUSY output of the panel: it only
  moves when the panel is plugged in, goes high ~50 ms after reset and is
  waited for by the MCU (10.7 ms later the transfer starts).
  `[ASSUMPTION]` BUSY high = ready (UC81xx convention; the first capture's
  10 s timeout with pin 9 low fits).
- `[ASSUMPTION]` Roles now fit the standard order well: 9 BUSY, 10 RST,
  11 D/C, 12 CS (per byte), 13 SCK.
- **Two SPI speeds** seem to be in use: commands and some short writes
  clock faster than 2 MSa/s can show, the 3- and 70-byte blocks at a
  clean ~1 MHz. `[ASSUMPTION]` The 70-byte block at the slower clock is a
  **read** from the panel (e.g. OTP/ID/temperature) — reads are often
  clocked slower.
- **Pin 14 shows no data at all.** Command bytes must toggle MOSI, so
  either the D5 wire is not on FPC pin 14 (it follows the battery
  exactly — looks like a supply net) or pin 14 is not MOSI.
  → **Test:** M-007.
- F-08: within 27 s after battery insertion the tag does **not** refresh
  the panel, it only initialises and powers it down.

### What it does not prove
- The byte values — the data line was not captured and the command bytes
  are too fast for 2 MSa/s.
- That no refresh ever happens after boot — the capture was only 28 s.

### Next step
1. M-007: check/fix the D5 (pin 14) solder point.
2. Pass B: **20 MSa/s, 30 s**, battery insertion — captures the ~80-byte
   init sequence with real byte values.
3. A longer pass A (2 MSa/s, ≥ 5 min) to see whether a refresh happens
   later (F-08). If not: plan B (NFC) or a refresh triggered otherwise.

---

## 2026-09-23 — Session 2: First 20 MSa/s capture — SCK and data lost after re-soldering

### What was tried
- Tag 02, panel plugged in, **20 MSa/s**, 22.4 s, battery inserted during
  the recording. Pin 14 wire re-soldered to a different point beforehand
  (M-007); the maintainer suspects it is still wrong.
- Raw file: `captures/2026-09-23_tag02_boot-init_20MHz.sr` (446 KB,
  sha256 `e7e151cb…5b65`, archive timestamp 2026-09-23 19:00:12).
  Overview: `analysis/out/2026-09-23_tag02_boot-init_20MHz_overview.txt`.

### Result
- `[CAPTURE]` **D4 (pin 13) and D5 (pin 14): no edge at all**, low for the
  whole capture. D5 no longer follows the battery.
- `[CAPTURE]` D0–D3 show the same sequence as in the 2 MSa/s capture with
  panel (reset 10 ms, BUSY high ~49.6 ms after reset, then the transfer,
  then power-down) — now with 50 ns resolution.
- `[CAPTURE]` The transfer consists of **82 CS frames in three
  transactions** (CS-low width per frame, D/C level):
  1. 6.5811 s: 1 frame D/C=0 (5.85 µs), then **3** frames D/C=1
     (13.2–13.65 µs each),
  2. 6.5813 s: 2 frames D/C=0 (5.85 / 5.10 µs), then **5** frames D/C=1
     (3.80–3.95 µs each),
  3. 6.5814 s: 1 frame D/C=0 (5.05 µs), then **70** frames D/C=1
     (12.85–13.65 µs each).
- `[CAPTURE]` D/C is constant within each CS frame.

### Interpretation
- Every byte has its own CS frame; commands are D/C=0, parameters/data
  D/C=1. The frame widths show **at least two different byte timings**:
  ~3.8 µs (writes, `[ASSUMPTION]` hardware SPI ≥ 2 MHz) and ~13 µs with
  ~1 µs bit period (seen in the 2 MSa/s capture). `[ASSUMPTION]` The ~13 µs
  frames (3 bytes after the first command, 70 bytes after the last) are
  **reads** from the panel over a bidirectional data line, clocked slowly
  (bit-banged). Only the byte values will settle this.
- `[ASSUMPTION]` Losing D4 is a wiring problem caused by the re-soldering
  (pin 13 and 14 are neighbours), not a change in the tag's behaviour —
  the timing of D0–D3 is unchanged. → **Test:** M-007 extended checks.

### What it does not prove
The byte values — still no data line and now no clock.

### Next step
M-007 extended: check all six wires end-to-end from the SLogic side, fix,
then repeat pass B.

---

## 2026-09-23 — Session 2: Photo of the capture wiring

- Maintainer sent a photo of tag 02's back side with the capture wires:
  `hardware/photos/pcb-bottom-capture-wiring.webp`.
- `[PHOTO]` **Seven wires**: blue, grey and white on three vias close to the
  FPC exit (top right), yellow (upper middle), black (middle left), purple
  and green (bottom, above the `BOT` label, next to a bundle of parallel
  traces). Which colour is which SLogic channel / FPC pin is **not stated**.
- `[PHOTO]` Green joint: no via is clearly visible under the solder blob;
  a small via just above it (≈ 1 via pitch) is still unsoldered. The
  purple joint sits on a via.
- `[PHOTO]` Most small dark dots across the board are tented vias (covered
  by solder mask). `[ASSUMPTION]` Many of them are stitching vias of the
  ground pour. A wire on such a via, or a joint that does not reach the
  copper, would show as a flat line — consistent with D4/D5 being flat in
  `2026-09-23_tag02_boot-init_20MHz.sr`.
  → **Test:** M-007 extended checks (end-to-end continuity per wire to its
  FPC pin; no continuity to battery minus).
- Nothing about pin assignment is derived from this photo (`CLAUDE.md` §2).

---

## Open thread at the end of session 2 (2026-09-23)

Session paused by the maintainer. This entry is the resume point.

### Where we stand
- **Pinout (M-001, done):** `[MEASUREMENT]` 6 signal lines on FPC pins
  **9–14**, GND 17 (also 3, 8), GDR 2, VDDIO/VCI 15+16 (switched supply via
  SOT-23 `XDt`, not on battery plus). Pin 1 towards the board centre.
- **Roles from the captures:** `[CAPTURE]` 9 = BUSY (goes high ~50 ms after
  reset, only with panel), 10 = RST (10 ms low pulse), 11 = D/C,
  12 = CS (one CS frame per byte). `[ASSUMPTION]` 13 = SCK, 14 = data
  (SDI, possibly bidirectional).
- **Boot behaviour:** `[CAPTURE]` after battery insertion the tag resets the
  panel, waits for BUSY, sends 82 byte frames in three transactions
  (1+3, 2+5, 1+70), then powers the panel down. **No refresh within 27 s**,
  nothing visible on the panel. Without panel: three ~10 s BUSY timeouts.
- **Captures in `captures/`:** `…_boot-overview_2MHz.sr` (no panel),
  `…_boot-overview-panel_2MHz.sr` (panel, SCK visible, no data),
  `…_boot-init_20MHz.sr` (panel, 20 MSa/s, SCK and data flat).
- **Blocking problem:** the wires for pin 13 (SCK) and pin 14 (data) —
  M-007. Photo of the current wiring:
  `hardware/photos/pcb-bottom-capture-wiring.webp` (7 wires; green joint
  may not sit on a via).

### Waiting for the maintainer
1. **Colour → channel → FPC pin** mapping of the 7 wires in the photo.
2. **M-007 extended:** per wire, continuity from the SLogic end to its FPC
   pin (must beep) and to battery minus (must not beep, except GND);
   neighbour shorts 12↔13, 13↔14, 14↔15.
3. Fix wiring, then a **short pass A (2 MSa/s, ~15 s)** as a wiring check:
   all six lines must show edges, the data line *during* the transfers.
4. Then **pass B: 20 MSa/s, 30 s**, battery inserted after start →
   byte values of the 82-byte init sequence.
5. Later: **long pass A (2 MSa/s, ≥ 5 min)** to see whether a refresh ever
   happens after boot (F-08). If not: plan B (NFC) or another trigger.
6. Still open, lower priority: scope check of pin 15 level (§2a),
   M-002/M-003 (SWD), M-005 (`XDt`), strain relief and a second GND lead.

### What Claude Code does next time
- Read this entry, `docs/open-questions.md`, `docs/measurement-requests.md`.
- For new `.sr` files: `python3 analysis/sr_overview.py <file>` first
  (needs `numpy`), store the file in `captures/` with the naming scheme,
  commit with `git add -f`.
- Once SCK + data are captured: extend the decoder to read `.sr` directly
  or export CSV, decode the 82 frames, identify the controller (F-03).
- Working rules agreed this session: chat in German, repo in English,
  push directly to `main`, ask before large changes; tag 01 = reference
  unit (untouched), tag 02 = work tag.

---

## 2026-09-23 — Session 3: Second 20 MSa/s capture — D4/D5 still flat, analyser suspected

### What was tried
- Maintainer re-checked all wires (no shorts, mapping correct; details
  not given) and re-soldered pin 14. Tag 02, panel plugged in,
  **20 MSa/s**, 50.0 s.
- Raw file: `captures/2026-09-23_tag02_boot-init-rewired_20MHz.sr`
  (sha256 `521ea680…9316`, archive timestamp 2026-09-23 23:30:02).
  Overview: `analysis/out/2026-09-23_tag02_boot-init-rewired_20MHz_overview.txt`.

### Result
- `[CAPTURE]` **D4 (pin 13) and D5 (pin 14) again have no edge at all.**
- `[CAPTURE]` D0–D3 show the identical boot sequence as in the previous
  captures (reset 10 ms, BUSY high ~49.6 ms later, 82 CS frames in three
  transactions, power-down), shifted in time only.

### Interpretation
- Pattern over all four captures: D4 carried a clock at **2 MSa/s**;
  D4 **and** D5 (and D6/D7) are flat in **both 20 MSa/s** captures,
  independent of re-soldering. D0–D3 always work.
- `[ASSUMPTION]` Not a wiring problem but the analyser: at 20 MSa/s with
  8 channels on Windows (at the USB bandwidth limit, see `TOOLS.md`) only
  D0–D3 are sampled. This would also explain the flat D5 in
  `…_boot-init_20MHz.sr`; the earlier D5 behaviour at 2 MSa/s (following
  the battery) was a separate, real wiring fault.
  → **Test:** M-008 (2 MSa/s check with current wiring; then SCK/data/CS/DC
  moved to D0–D3 and recorded at 20 MSa/s with 4 channels).

### What it does not prove
That the current pin 14 wiring is correct — that is only shown by data
edges in the M-008 captures.

---

## 2026-09-23 — Session 3: Product identified as VUSION 7.4 BWRY (EDG3-0740A)

### Maintainer statement
- The tag is a **VUSION 7.4 BWRY GU140**, exact model **EDG3-0740A**.
  Source of this information not stated (presumably the housing label) —
  a photo of the label would make it `[PHOTO]`.

### Research
- `[RESEARCH]` FCC ID `2ACQM-EDG3-0740-A` belongs to "SES-imagotag GmbH
  VUSION 7.4 EDG3-0740-A" (search results; fccid.io not reachable from the
  Claude Code environment).
- `[RESEARCH]` VUSION 7.4 **BWR**: 800 × 480 px, 126 dpi (datasheet, via
  search snippet). Geometry check: 161 × 97 mm active area, 7.40" diagonal
  — fits the measured 170 × 112 mm outline.
- `[RESEARCH]` Four-colour BWRY e-paper of this class typically uses
  2 bpp in a single data plane (e.g. JD7966x-driven Good Display panels).

### What follows
- **Corrects** the entry "Session 2: Session 1 follow-up questions
  answered": the colour question is now "four colours", not "red or
  yellow". `[ASSUMPTION]` B/W/R/Y until the capture or the display shows it.
- Expected image payload changes: **one block of ~96,000 bytes at 2 bpp**
  instead of two 48,000-byte planes. The controller is likely **not** a
  plain UC8179/SSD16xx three-colour type — the fingerprint table in the
  decoder does not contain a BWRY family yet.
- `decode_spi.py` got a `--bpp` option (resolution candidates at 2 bpp) and
  the TRES check now tests 1 and 2 bpp. Re-tested on the synthetic capture:
  outputs unchanged at the default `--bpp 1`.
- The 70-byte read at boot may be panel-specific data (OTP/waveform
  settings) — typical for multi-colour panels, still `[ASSUMPTION]`.

### Next step
Captures from M-008 (SCK + data on D0–D3 at 20 MSa/s).

---

<!--
TEMPLATE FOR NEW ENTRIES — copy and fill in:

## YYYY-MM-DD — Session N: <title>

### What was tried
<setup, tool, settings>

### Result
- `[MARKER]` <observation>

### What follows
<conclusion — and what it does NOT prove>

### Next step
<concrete>
-->
