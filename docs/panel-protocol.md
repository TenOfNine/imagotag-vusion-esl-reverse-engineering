# Panel protocol — EL074TS1 controller, OTP and init sequence

Status 2026-10-21. Written after the project review in session 5.
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
  the same according to issue #2). The **offsets** are `[ASSUMPTION]`:
  found by value matching, not read from the app note.
  **Test:** compare with the offset table of the Pervasive app note
  (maintainer, the site is blocked for Claude Code).
- Consequence: the panel-specific part of the init sequence (the part
  `CLAUDE.md` §5.2 wants captured before an unlock) **is in our own
  capture**. What is not captured is the order and the fixed bytes;
  these come from two public sources.
- `[ASSUMPTION]` The original firmware reads 69 of the 112 OTP bytes
  because offset 63 is the last one it needs.

## 3. Full update sequence (as published, not tested by us)

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

- Offsets in section 2 → Pervasive app note (maintainer).
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
