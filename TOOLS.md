# TOOLS — available instruments

What is physically on the bench. Claude Code may **only** write measurement
requests that can be carried out with this equipment — or state explicitly
that an instrument is missing and which one would be needed.

Legend: **✅ available** · **❓ unclear** · **❌ missing**

---

## ✅ Sipeed SLogic Combo 8 — logic analyser

The central tool of this project.

| Property | Value |
|---|---|
| Channels | 8 |
| Max. sample rate | 80 MHz |
| Transfer bandwidth | 320 Mb/s |
| Sampling mode | **Streaming** (no on-board memory) |
| Input range | 0 – 3.6 V |
| Logic thresholds | VIH > 2 V, VIL < 0.8 V |
| Software | PulseView (sigrok) |

**Practically usable rates** (limited by USB stability):

| OS | Configuration |
|---|---|
| Linux | 80 MHz @ 4 channels · **40 MHz @ 8 channels** |
| Windows | 80 MHz @ 2 channels · **20 MHz @ 8 channels** |

→ **Prefer Linux** if available.

**Status 2026-09-23:** the maintainer runs PulseView on **Windows**.
→ Practical limit for this project: **20 MSa/s at 8 channels.**
With an SPI clock of up to 4 MHz that is 5 samples per clock — right at the
limit. If the clock is higher, reduce to 4 channels (SCK, MOSI, CS, D/C)
or consider Linux (e.g. a live USB stick).

**Status 2026-09-23:** `[CAPTURE]` in two 20 MSa/s captures on Windows
D4–D7 read constantly 0 while D0–D3 worked; at 2 MSa/s D4 carried data.
`[RESEARCH]` Search results for the Sipeed documentation give the Windows
bandwidth as 160 Mb/s with "typical 40M@4CH", i.e. 20 MSa/s × 8 channels
is exactly at the limit (https://github.com/sipeed/sipeed_wiki, Sipeed
wiki "Using as a Logic Analyzer" — the wiki itself was not reachable from
the Claude Code environment). `[ASSUMPTION]` Above a certain rate only
D0–D3 are sampled → put the lines that matter on D0–D3. Test: M-008.
**Result 2026-09-23:** `[CAPTURE]` with the four decode lines moved to
D0–D3 and D4–D7 disabled, 20 MSa/s works; the same wiring on D4/D5 works at
2 MSa/s. Rule for this project: **for ≥ 20 MSa/s use only D0–D3.**

### Consequences for use

- **Streaming** means: everything goes live over USB into RAM. Long
  recordings (30–60 s) are possible where a memory-based analyser would
  long be full. The price: RAM usage and usually **no hardware trigger**.
  → At 20 MSa/s × 8 channels × 30 s ≈ 600 MB. At 40 MSa/s ≈ 1.2 GB.
- **Known bug:** if D7 is unused during a recording, a **level inversion**
  can appear on that channel.
  → Always tie D7 to GND or use it.
- **GND routing:** keep the ground lead as close as possible to the
  measurement point. According to the manufacturer, even 1 cm closer can
  improve signal quality.
  → Use at least two GND leads.
- **No voltage protection.** 3.6 V is the end. The FPC carries ±20 V right
  next to it. See safety rule 3 in `CLAUDE.md`.

### Channel assignment (standard for this project)

| Channel | Signal |
|---|---|
| D0 | SCK |
| D1 | SDI / MOSI |
| D2 | CS |
| D3 | D/C |
| D4 | BUSY |
| D5 | RST |
| D6 | free |
| D7 | **to GND** (see bug above) |

---

## ✅ SEGGER J-Link — SWD debugger

For access to the EFR32FG22.

- **Important:** EFR32 Series 2 supports **only SWD, no JTAG**.
- Wiring: `SWCLK`, `SWDIO`, `GND` and **`VTref`**.
  → Without VTref the J-Link does nothing. The most common beginner's
  mistake. `RESET` is optional, but helps with connect-under-reset.
- Software: **Simplicity Commander** (Silicon Labs, free).
- Unlock command: `commander device unlock`
  **Erases the original firmware.** Only use after a successful capture —
  see `CLAUDE.md` §5.2.
- Query the state first: `commander device info`,
  `commander security status`
  → The chip may not be locked at all. Then the original firmware can be
  **read out and saved**, which would be more valuable for the EPD driver
  than any capture.

---

## ❓ FTDI USB serial adapter

Maintainer statement (2026-09-23): **"FTDI1232"**. I know of no FTDI chip
with exactly this designation. `[ASSUMPTION]` An **FT232R(L)** module is
meant — that would be UART only.
Maintainer (2026-09-23): "only has UART, as far as I know".
→ **Not relevant** for the project, since a J-Link is available. Will only
be clarified further if the adapter were needed for SWD after all.

- **FT232R / FT231X / FT230X** → UART only. Useless for SWD.
- **FT2232H / FT232H / FT4232H** → have MPSSE, can do SWD via OpenOCD
  (with the resistor trick TDI↔TDO, ~470 Ω–1 kΩ).

→ **Not critical** for this project, since a J-Link is available.
Only relevant if a UART debug output should be read in parallel.

---

## ✅ OWON HDS242 — handheld oscilloscope with multimeter

Maintainer statement (2026-09-23). Covers **multimeter and oscilloscope**.

`[RESEARCH]` Key data according to retailer listings
(https://vishaworld.com/products/owon-hds242-handheld-digital-oscilloscope-bandwidth-40-mhz-2-channel-sample-rate-250-msa-s-single-channel-125-msa-s-dual-channel,
https://toolboom.com/en/handheld-digital-oscilloscope-owon-hds242/):

| Property | Value |
|---|---|
| Channels | 2 |
| Bandwidth | 40 MHz |
| Sample rate | 250 MSa/s (1 channel), 125 MSa/s (2 channels) |
| Record length | 8 k points |
| Multimeter | 20,000 counts, voltage, current, resistance, capacitance, diode, **continuity** |
| Power | 18650 battery, USB-C |

### Consequences for use

- **Continuity tester available** → M-001 to M-003 can be carried out.
- **Oscilloscope available** → before connecting the SLogic, the
  **logic levels** and the **SPI clock** can be checked, and — for
  diagnosis — the boost voltages (VGH/VGL).
- **8 k points of memory** → **unsuitable** for capturing a whole refresh.
  That remains the SLogic's job.
- Maximum input voltage of the scope inputs with 1×/10× probe **not
  researched** → check the manual before measuring on the HV rails and use
  10×.

## ✅ Soldering station

Maintainer statement (2026-09-23): regular soldering station, **no hot
air**. Sufficient for enamelled copper wire on vias (capture path B).

---

## Test objects

| Item | Quantity | Status |
|---|---|---|
| ESL tags `RFRTx026D` | > 5 | available |
| of which **reference unit** | 1 | **tag 01**, **untouched**, see `CLAUDE.md` §5.1 |
| tag 02 | 1 | the tag in `hardware/photos/`; used for M-001 and the first capture |

Numbering agreed 2026-09-23: tags are labelled physically, tag 01 is the
reference unit.

---

## ❌ Useful, but not available

Claude Code may suggest these if they simplify a step decisively — but must
not build a work plan on them.

| Instrument | Purpose | Rough price |
|---|---|---|
| 24-pin FPC extension set (0.5 mm, adapter + cable) | Tapping the FPC **without soldering**. Note: A-A vs. A-B depending on the contact side. **Confirmed not available** (2026-09-23). | €10–20 |
| Hot-air station | Desoldering the EFR32 (path A, variant 2). **Confirmed not available** (2026-09-23) → variant 2 currently not feasible. | — |
| Microscope / illuminated magnifier | Counting QFN pads, reading markings | — |

---

## Tools Claude Code has itself

To make clear what is possible **without** hardware access:

- Evaluating captures (CSV/sigrok) with Python
- Writing decoder and driver code
- Researching datasheets and other people's reverse-engineering work
- Analysing photos: reading component markings, counting contacts,
  decoding QR codes, measuring geometry

**Not** possible: any electrical measurement, any access to hardware.
