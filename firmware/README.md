# firmware — still empty

> **Update 2026-09-25:** the capture route is exhausted (the tag never
> refreshes, `HISTORY.md`). The order at the bottom is superseded: path B
> is decided, the next steps are M-011 (SWD lock state) and M-012 (EFR32
> pin map), then the board definition and bring-up steps 1–3 of
> `../docs/firmware-plan.md`. No OEPL pin map matches our board
> (`../docs/oepl-pin-comparison.md`). The GPIO mapping comes from **M-012**,
> not from M-001/M-002.

> **Update 2026-09-23:** the maintainer chose **path B** — a custom
> firmware on the original EFR32, no ESP32. Current plan, open decisions
> and bring-up steps: `../docs/firmware-plan.md`. The path A section below
> is kept for reference.

The driver code is created here **once the capture is available**.

Until then there is nothing to do here. A driver based on an unverified
pinout would be a waste of time at best and hardware damage at worst.

---

## Planned structure, depending on the path

### Path A — ESP32 on the carrier board

```
firmware/
  esp32-epd/
    platformio.ini
    src/
      main.cpp
      epd_el074ts1.h     derived from analysis/*_init_sequence.py
      epd_el074ts1.cpp
```

Approach: replay the captured init sequence 1:1. Only once an image
appears, switch to GxEPD2 — if the controller is supported there at all.

Required lines: `3V3, GND, SCK, MOSI, CS, D/C, RST, BUSY`

### Path B — OpenEPaperLink port

```
firmware/
  oepl-rfrtx026d/
    README.md            porting notes
    patches/             diff against Tag_FW_EFR32xG22
```

Base: https://github.com/OpenEPaperLink/Tag_FW_EFR32xG22

To do: create a board definition for `RFRTx026D`, enter the GPIO mapping
from M-001/M-002, add an EPD driver for `EL074TS1`.

---

## Order

1. Evaluate the capture → controller and resolution are settled
2. Decide path A or B (→ `docs/open-questions.md`, F-09)
3. **Then** start here

---

## What does not belong here

- Read-out original firmware images (copyright-protected)
- Manufacturer documents under NDA
