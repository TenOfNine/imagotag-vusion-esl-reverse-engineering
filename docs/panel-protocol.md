# Panel protocol — EL074TS1 controller, OTP and init sequence

Status 2026-10-21. Written after the project review in session 5;
updated the same day with Pervasive Displays' own driver library
(section 7). Where the two disagree, the vendor driver wins.
Evidence markers as in `CLAUDE.md` §3. **Nothing here has been sent to a
panel by us yet.** The first real test is bring-up step 3/4 in
`firmware-plan.md`.

---

## 1. Controller: Pervasive Displays "BWRY Medium" COG

- `[CAPTURE]` `2026-09-23_tag02_boot-init-4ch_20MHz.sr`: at boot the
  original firmware sends `70` (reads `0D 04 01`), `90`, `A2 00 15 00 00 E0`,
  `92` (reads 70 bytes).
- `[RESEARCH]` Pervasive Displays knowledge base, "BWRY Medium" (5.8" and
  7.4"), EPD update procedure:
  https://docs.pervasivedisplays.com/knowledge/Hardware/epd-usage/Screens/BWRY_Medium/update-procedure.html
  — **via search-result snippets only**; the site is not reachable from the
  Claude Code environment. According to the snippets: `0x70` chip ID,
  `0x90` (index only), `0xA2` with the OTP start address
  `[0x00, 0x15, 0x00, 0x00, 0xE0]`, `0x92` reads the OTP with **1 dummy
  byte** first; "if the address 0 data is 0xA5, the active space is Bank0,
  otherwise Bank1"; for 5.8"/7.4" the banks are `0x1500–0x156F` and
  `0x1570–0x15DF` (112 bytes each); max. SPI clock 2.5 MHz for reads; the
  OTP is read once, before the init.
- Our capture matches that byte for byte: same commands, same five
  address bytes, first byte read after `92` is `00` (dummy), the next one
  is `A5` (→ bank 0).
- `[RESEARCH]` Third-party report on another RFRTx026D (GitHub issue #2 of
  this repo, see section 6): `0x70` returns chip ID `0D 04`; panel label
  there `SE2741QS0B3` (Pervasive Displays part number).
- `[PHOTO]` Our panel label (`panel-label-el074ts1.webp`):
  `EL074TS1 / C5-ZD / EB2000-GDA (SPQ0KX)LF / H7FZDSPQ0KXYZ5V00DAUAT`.
  Different label from the third-party unit, same serial format
  (`SPQ0KX` vs. `SPQ1CY`).

`[ASSUMPTION]` Our panel has the same COG and OTP layout as the Pervasive
Displays E2741QS0B3. Strong support: section 2. **Test:** bring-up step 3
(our own OTP read gives the same bytes) and step 4 (a refresh).

## 2. Our OTP bytes contain every init parameter

`[CAPTURE]` The 69 OTP bytes (after the dummy byte) read by the original
firmware. Row labels are hex offsets; the table below uses decimal offsets.

```
00: A5 1D 87 04 01 53 50 51 30 4B 58 04 FF FF FF FF
10: 07 07 2B 01 E0 03 20 40 40 40 07 AB FF FF 00 00
20: 00 3C 00 00 00 00 08 37 03 03 00 01 1E 06 0A 0F
30: 19 0F 09 FF FF FF FF FF FF FF FF 01 04 01 01 3F
40: FF FF FF FF FF
```

`[RESEARCH]` bitbank2/bb_epaper, pull request #44 (commit `61de1cf`),
table `epd74yr_init_full` for the Pervasive Displays E2741QS0B3, commented
"Register values dumped from the panel's COG OTP memory":
https://github.com/bitbank2/bb_epaper/pull/44

`analysis/otp_init_map.py` compares both. Result: **every OTP-derived
parameter of that table is present in our OTP, 0 mismatches**, and the
parameters use **every non-`FF` byte from offset 16 to 63**. Only the
header (0–4), the serial (5–10), byte 11 and `FF` fill are left over.

| Command | Meaning (per bb_epaper comments) | Parameters | Our OTP offset |
|---|---|---|---|
| `E6` | temperature | 1 byte, **host-supplied** (`19` = 25 °C) | — |
| `E0` | | `02` | fixed |
| `A5` | (no parameter), then wait for BUSY | — | fixed |
| `01` | PWR | `07` | 16 |
| `00` | PSR (1st write) | `07 AB` | 26–27 |
| `61` | TRES | `01 E0 03 20` (480 × 800) | 19–22 |
| `00` | PSR (2nd write) | `07 2B` | 17–18 |
| `06` | BTST_P | `40 40 40` | 23–25 |
| `03` | PFS | `00 00 00` | 30–32 |
| `E7` | | `3C` | 33 |
| `65` | | `00 00 00 00` | 34–37 |
| `30` | PLL | `08` | 38 |
| `50` | CDI | `37` | 39 |
| `60` | TCON | `03 03` | 40–41 |
| `E3` | PWS | `00` | 42 |
| `FF` | | `A5` | fixed |
| `EF` | | `01 1E 06 0A 0F 19 0F 09` | 43–50 |
| `DC` / `DD` / `DE` / `E8` / `DA` | "Spectra 4 tuning" | `01` / `04` / `01` / `01` / `3F` | 59 / 60 / 61 / 62 / 63 |
| `FF` | | `E3` | fixed |
| `E9` | | `01` | fixed |
| `04` | power on, then wait for BUSY | — | fixed |

- The **values** are `[CAPTURE]` (our panel). The **command order and the
  fixed bytes** are `[RESEARCH]` (bb_epaper; the Pervasive app note says
  the same according to issue #2). ~~The **offsets** are `[ASSUMPTION]`:
  found by value matching, not read from the app note.~~
  **Update 2026-10-21:** the offsets are now `[RESEARCH]`: Pervasive
  Displays' own `COG_initial()` reads exactly these 18 offsets, in this
  order (section 7). Command order and fixed bytes are confirmed by the
  same code.
- Consequence: the panel-specific part of the init sequence (the part
  `CLAUDE.md` §5.2 wants captured before an unlock) **is in our own
  capture**. What is not captured is the order and the fixed bytes;
  these come from two public sources.
- `[ASSUMPTION]` The original firmware reads 69 of the 112 OTP bytes
  because offset 63 is the last one it needs.

## 3. Full update sequence (as published, not tested by us)

> **Superseded 2026-10-21 by section 7** (vendor driver). Two differences:
> the vendor sends `04` (power on) **after** the image data, and it ends
> with a dedicated "turn-off DC/DC" sequence instead of `07 A5`. The
> bb_epaper-based list below is kept for traceability.

`[RESEARCH]` bb_epaper (`bbepRefresh`, `bbepSleep` for 4-colour UC81xx
panels) and issue #2:

1. Panel supply on, reset pulse, wait for BUSY high.
2. OTP read (section 1) — once.
3. Init (section 2), ending with `04` (power on) + BUSY.
4. `10` + **96,000 bytes** image data (480 × 800 at 2 bpp).
5. `12 00` (display refresh) + BUSY. Duration ≈ 22 s (bb_epaper comment;
   issue #2: 21.9 s).
6. `02 00` (power off) + BUSY, then `07 A5` (deep sleep), supply off.

Pixel coding `[RESEARCH]` (bb_epaper `u8Colors_4clr_v2`, issue #2,
OEPL `jd` driver): 2 bits per pixel, `00` black, `01` white, `10` yellow,
`11` red, first pixel in the top bits. The controller scans 800 lines of
480 pixels (TRES `01 E0 03 20`).

## 4. Timing and electrical details

- `[CAPTURE]` After reset, BUSY gives a ~0.78 ms high pulse, goes low, and
  is high for real ~49.6 ms after the reset
  (`…_boot-overview-panel_2MHz.sr`). Issue #2 reports the same quirk and
  that reading the chip ID too early returns `00 00`.
  → Firmware must not take the first BUSY-high as "ready".
- `[CAPTURE]` Writes at ~6.4 MHz, reads at ~1 MHz; one CS frame per byte.
- `[RESEARCH]` Read clock max. 2.5 MHz (Pervasive app note, snippet).
- `[RESEARCH]` `E6` carries the temperature. The firmware needs a
  temperature value — `[ASSUMPTION]` the EFR32's internal temperature
  sensor is good enough. **Test:** compare with a thermometer during
  bring-up.

## 5. Open points

- ~~Offsets in section 2 → Pervasive app note (maintainer).~~ Answered
  by the vendor driver (section 7).
- Pixel coding (`00` black, `01` white, `10` yellow, `11` red): not in
  the vendor driver code read so far — still from bb_epaper / issue #2.
  **Test:** bring-up step 4 with a four-colour test pattern.
- Whether the image appears in the right orientation / mirrored →
  bring-up step 4.
- What the header bytes `1D 87 04 01` and byte 11 (`04`) mean — not needed
  for driving the panel.

## 6. Sources in short

| Source | What it gives | Reliability |
|---|---|---|
| Our boot capture | OTP values, read procedure, timing | `[CAPTURE]` |
| Pervasive Displays BWRY Medium app note | procedure, banks, read clock | `[RESEARCH]`, snippets only |
| bitbank2/bb_epaper PR #44 | complete init table, refresh, sleep | `[RESEARCH]`, code |
| Issue #2 of this repo (third party, AI-assisted, unit not ours) | chip ID, pin map, flash, unlock, working refresh | `[RESEARCH]`, unverified on our unit |
| Pervasive Displays `Pervasive_BWRY_Medium` + `PDLS_Common` (vendor code) | OTP read, OTP offsets, init, update, turn-off DC/DC, reset/BUSY/SPI timing, frame size | `[RESEARCH]`, primary source (section 7) |

## 7. Vendor driver: Pervasive Displays `Pervasive_BWRY_Medium`

Added 2026-10-21. The maintainer found the Pervasive Displays app note
pages (overview, SPI timing format, update procedure). The site is blocked
for Claude Code, but the `.cpp` references point to Pervasive Displays'
public driver on GitHub, which implements the app note step by step
(comments "Application note § 2 … § 5"):

- `Pervasive_BWRY_Medium` (PervasiveDisplays/Pervasive_BWRY_Medium, commit `d877f73`, 2026-10-19),
  supports "iTC colour black-white-red-yellow screens (film `Q`) with sizes
  of 5.8 and 7.4\"" — references `581-QS-0B` and `741-QS-0B`.
- `PDLS_Common` (PervasiveDisplays/PDLS_Common, commit `5f53ef2`,
  2026-10-19) for reset, BUSY and SPI helpers.
- Licence: basic edition CC BY-SA 4.0, "For exclusive use with Pervasive
  Displays screens". → We **reimplement from the documented procedure**
  and do not copy the source into this repo or into an OEPL
  (CC BY-NC-SA) port. `[ASSUMPTION]` this keeps the licences apart — not
  legal advice.

Everything below is `[RESEARCH]` from that code unless marked otherwise.

### 7.1 OTP read (`COG_getDataOTP`)

1. Chip-ID check: `70` (command), wait 8 ms, read **2 bytes** → must be
   `0x0D04`. `[CAPTURE]` ours: `0D 04` (+ a third byte `01` that the
   original firmware also reads).
2. `90` (command, no data), wait 8 ms.
3. `A2` + `00 15 00 00 E0` (OTP start address).
4. `92`, then read: 1 dummy byte, then byte 0. If byte 0 = `A5` → bank 0.
   Otherwise skip to offset `0x70` and read again; if that is `A5` →
   bank 1, else abort.
5. Read **112 bytes** in total (`COG_data[0…111]`).

All reads use 3-wire SPI on the bidirectional data line, bit-banged with
1 µs half periods (≈ 0.5 MHz), one CS frame per byte.
`[CAPTURE]` The original Vusion firmware does the same with ~1 MHz reads
and without the 8 ms waits.

### 7.2 Initialisation (`COG_initial`)

| Step | Command + data | Source of the data |
|---|---|---|
| 1 | `E6` + temperature | host value, signed °C, default 25 (`0x19`) |
| 2 | `E0 02` | fixed |
| 3 | `A5`, then wait for BUSY high | fixed |
| 4 | `01` PWR | OTP[16] |
| 5 | `00` PSR | OTP[26–27] |
| 6 | `61` TRES | OTP[19–22] |
| 7 | `00` PSR | OTP[17–18] |
| 8 | `06` BTST_P | OTP[23–25] |
| 9 | `03` PFS | OTP[30–32] |
| 10 | `E7` | OTP[33] |
| 11 | `65` | OTP[34–37] |
| 12 | `30` PLL | OTP[38] |
| 13 | `50` CDI | OTP[39] |
| 14 | `60` TCON | OTP[40–41] |
| 15 | `E3` PWS | OTP[42] |
| 16 | `FF A5` | fixed |
| 17 | `EF` | OTP[43–50] |
| 18 | `DC`, `DD`, `DE`, `E8`, `DA` | OTP[59], [60], [61], [62], [63] |
| 19 | `FF E3` | fixed |
| 20 | `E9 01` | fixed |

Identical to the table in section 2 (`analysis/otp_init_map.py`), except
that `04` is **not** part of the init.

### 7.3 Full update (`updateNormal`)

1. Panel power/GPIO on, reset: wait 20 ms, RST high 10 ms, **RST low
   20 ms**, RST high 10 ms, CS high, wait 10 ms, wait for BUSY **high**.
   `[CAPTURE]` the original firmware holds RST low for 10.05 ms.
2. If the OTP has not been read yet: OTP read (7.1), then reset again.
3. Init (7.2).
4. `10` + frame: **96,000 bytes** for 7.41" (demo `frameSize`; 46,080 for
   5.81").
5. `04` (power on), wait for BUSY high.
6. `12 00` (display refresh), wait for BUSY high (≈ 22 s, see F-12).
7. Turn-off DC/DC (`COG_stopDCDC`):
   `02 00`, wait for BUSY high → `00 07 2B 01` → `FF A5` → wait 400 ms →
   `EE A0 1E` → wait 4 ms → `EE 00 00` → wait 3 ms → `FF E3` →
   **wait 6000 ms**. No `07 A5` deep sleep.

`[ASSUMPTION]` The panel supply (`XDt`, PC06) may only be switched off
after step 7 including the 6 s wait. **Test:** none without a scope on the
HV rails; follow the vendor order.

### 7.4 Bus details

- BUSY: the driver waits for **high** = ready, polling every 32 ms, no
  timeout. (Firmware of ours needs a timeout.)
- Writes: hardware SPI up to **16 MHz**; CS stays low for a whole
  command + data block (D/C low for the command byte, high for the data).
  `[CAPTURE]` The original firmware uses ~6.4 MHz and one CS frame per
  byte — `[ASSUMPTION]` the COG accepts both.
- Reads: see 7.1.
- Single commands (`b_sendCommand8`, `b_sendCommandData8`) are preceded
  by a 1 ms pause ("extra delay required for some MCUs").

### 7.5 What this changes

- Section 2 offsets: confirmed (`[RESEARCH]`).
- Section 3: superseded (`04` after the data; turn-off DC/DC sequence).
- Bring-up step 3 should read all **112** bytes and check chip ID `0D04`
  and the bank marker, as the vendor does.
- Our firmware has to send the turn-off sequence and respect the 6 s wait
  before cutting the panel supply.

## 8. A second panel's full OTP, and the panel orientation

Added 2026-10-21. `[RESEARCH]` Third-party comment in issue #2
(https://github.com/TenOfNine/imagotag-vusion-esl-reverse-engineering/issues/2#issuecomment-6320136057), another RFRTx026D, panel label `SE2741QS0B3`. Not our unit.

### 8.1 Full bank 0 (112 bytes, dummy byte dropped)

```
  0: a5 1d 87 07 01 53 50 51 31 43 59 04 ff ff ff ff
 16: 07 07 2b 01 e0 03 20 40 40 40 07 ab ff ff 00 00
 32: 00 3c 00 00 00 00 08 37 03 03 00 01 1e 06 0a 0f
 48: 19 0f 09 01 3f 05 0b 0f 19 1a 0f 01 04 01 01 3f
 64: ff × 32
 96: 53 31 32 37 34 31 51 53 30 42 33 31 43 59 ff ff   "S12741QS0B31CY"
```

Bank 1 there: all `FF` except bytes 96–109, ASCII `SPQB00F4D028HE`.

### 8.2 Comparison with our 69 bytes (`[CAPTURE]` vs `[RESEARCH]`)

| Offset | Ours | Theirs | Used by the vendor init? |
|---|---|---|---|
| 3 | `04` | `07` | no |
| 8–10 | `0KX` | `1CY` | no (serial) |
| 51–58 | `FF` × 8 | `01 3F 05 0B 0F 19 1A 0F` | no |
| all 33 init bytes (16–50, 59–63) | identical | identical | yes |

- The two panels differ in a header byte (offset 3) and in an 8-byte block
  (51–58) that the vendor driver does not read. `[ASSUMPTION]` byte 3 is
  an OTP/layout revision and 51–58 an extra parameter set of newer
  panels. **Test:** none needed for driving the panel.
- Consequence: OTP contents vary between panels → our firmware reads the
  OTP at runtime (as the vendor does) and never hard-codes the values.
- Our bytes 69–111 were never captured. Bring-up step 3 reads them; if
  bytes 96–109 hold an `S12741QS0B3…`-type part number, that is our own
  `[CAPTURE]` evidence for the panel type (currently `[ASSUMPTION]`).

### 8.3 Orientation and colours (third party, their unit)

- Raw panel, flat cable on the left: line 0 = top edge, pixel 0 = left
  edge → native 480 wide × 800 tall in that view.
- Colours `00` black, `01` white, `10` yellow, `11` red, first pixel in the
  top bits (same as bb_epaper / earlier report).
- Their OEPL port (800 × 480 landscape, cable at the bottom): `swapXY`
  and `mirrorX = true`; cable at the top would be `mirrorX = false,
  mirrorY = true`.
- They send `E6 19` (fixed 25 °C).

Our own check: the asymmetric test frame of bring-up step 4.
