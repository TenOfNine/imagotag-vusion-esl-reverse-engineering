# ESL E-Ink Reverse Engineering

Reverse engineering of a **VusionGroup / SES-imagotag** Electronic Shelf Label
in order to drive its built-in (probably four-colour B/W/R/Y) e-ink panel
under our own control.

```
Board     RFRTx026D  (imagotag, 2.4 GHz)
MCU       Silicon Labs EFR32FG22  (marking: FG22 / C121GG / C026ZX / 2419)
Panel     E Ink EL074TS1, approx. 170 × 112 mm, product VUSION 7.4 BWRY → probably four-colour (unconfirmed)
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

**Decided 2026-09-23 (maintainer): path B** — custom firmware on the
original EFR32, the board stays standard. The display refresh could not be
captured (the tag never refreshes without its base station), so the plan
now depends on the SWD lock state. See `docs/firmware-plan.md`.

---

## Current status

See `progress.md` for the checklist of what is done and what is open,
`HISTORY.md` for the full history and `docs/open-questions.md` for the
open questions.

Short version (session 4, 2026-09-25): FPC pinout measured and all six
signal roles confirmed by captures; the tag's boot sequence is decoded
(panel ID/OTP read, 800 × 480 assumed). The tag never refreshes without its
base station, so the display init cannot be sniffed. **Path B chosen: custom
firmware on the original EFR32** — plan in `docs/firmware-plan.md`. Waiting
for the SWD lock check (M-011) and the EFR32 pin map (M-012); photos
suggest the display lines end on QFN pads 1–8, and no OpenEPaperLink pin
map matches our board (`docs/oepl-pin-comparison.md`).

---

## Getting started for Claude Code

1. Read `CLAUDE.md` — working rules, especially the evidence markers
2. Read `HISTORY.md` — what has happened so far
3. Read `progress.md` — what is done and what is open
4. Read `docs/open-questions.md` — what is being worked on
5. Read `TOOLS.md` — which instruments are available

**Important:** Claude Code has no hardware access. Missing measurements are
written as a measurement request in `docs/measurement-requests.md`, not
estimated.

---

## Getting started for the maintainer

The next concrete steps are in `progress.md` ("Open — maintainer") and in
the status table at the top of `docs/measurement-requests.md`.

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
