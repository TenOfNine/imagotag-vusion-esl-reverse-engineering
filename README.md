# ESL E-Ink Reverse Engineering

Reverse engineering of a **VusionGroup / SES-imagotag** Electronic Shelf Label
in order to drive its built-in (probably three-colour) e-ink panel under our
own control.

```
Board     RFRTx026D  (imagotag, 2.4 GHz)
MCU       Silicon Labs EFR32FG22  (marking: FG22 / C121GG / C026ZX / 2419)
Panel     E Ink EL074TS1, approx. 170 × 112 mm, probably three-colour (B/W/red, unconfirmed)
Interface 24-pin FPC, 0.5 mm pitch
```

---

## Why this repo exists

There is **no public datasheet** for this panel. ESL panels are supplied to
OEMs under NDA; neither the pinout nor the resolution, controller type or
waveform is documented.

The way there is therefore the capture: the original tag draws an image
when the battery is inserted. This refresh is captured on the SPI bus, and
the init sequence, geometry and controller type are reconstructed from it.

---

## Two possible end goals

| Path | Result | Effort |
|---|---|---|
| **A — original board as carrier** | Disable the EFR32, connect our own ESP32 to the existing ZIF connector. The boost circuitry is kept. | medium |
| **B — OpenEPaperLink port** | Reflash the EFR32. The tag stays battery-powered and wireless. | high, but elegant |

Both paths need the same groundwork: **the capture**. The decision is
therefore still open and will be made once the init sequence is available.

---

## Current status

See `HISTORY.md` for the full history and `docs/open-questions.md` for
what is still open.

Short version (end of session 2, 2026-09-23): FPC pinout measured (signal
lines on pins 9–14), first captures taken on tag 02. BUSY, RST, D/C and CS
behave as expected; **SCK and the data line are not yet captured cleanly**
because of wiring problems (M-007). The exact resume point is the entry
"Open thread at the end of session 2" in `HISTORY.md`.

---

## Getting started for Claude Code

1. Read `CLAUDE.md` — working rules, especially the evidence markers
2. Read `HISTORY.md` — what has happened so far
3. Read `docs/open-questions.md` — what is being worked on
4. Read `TOOLS.md` — which instruments are available

**Important:** Claude Code has no hardware access. Missing measurements are
written as a measurement request in `docs/measurement-requests.md`, not
estimated.

---

## Getting started for the maintainer

The next concrete step is always at the top of
`docs/measurement-requests.md`.

Captures go into `captures/`, measured values into
`hardware/measurements.md`.

---

## Analysis

```bash
python3 -m pip install -r analysis/requirements.txt
python3 analysis/decode_spi.py captures/<file>.csv --sck D0 --mosi D1 --cs D2 --dc D3
```

On Windows use `py` instead of `python3`.

The decoder splits the capture into commands and data blocks, determines
the block lengths and derives candidate panel resolutions from them.
Details in `analysis/README.md`.

---

## Licence

Not decided yet. The captures and analyses are our own work; firmware
images or manufacturer documents do **not** belong in this repo.
