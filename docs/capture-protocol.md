# Capture protocol — SPI capture of the panel refresh

The central work step of the project. Controller type, resolution, init
sequence and possibly the waveform LUT all fall out of this capture at once.

> **Prerequisite:** measurement request **M-001** (`pinout.md`) is complete.
> Nothing is connected without a confirmed pinout.

---

## 0. Safety first

- In operation the FPC carries approx. **+22 V and −20 V** — the SLogic
  tolerates max. **3.6 V**.
- Only clip onto pins that have been **verified as MCU-connected**.
- The tag runs at approx. 3 V. That fits, but leaves **zero headroom**.

---

## 1. Establishing the tap

Two ways, in this order:

> **Status 2026-09-23:** no FPC extension available → **way B
> (soldering) is the current way.** Way A remains an option if a set is
> bought.

### A — Insert an FPC extension (preferred, solder-free)

24-pin FPC extension set (adapter + cable, 0.5 mm) between panel and
board. Provides 2.54 mm test points without a single solder joint.

**Mind the cable type:** A-A or A-B, depending on which side the contacts
of the original FPC are on. See `pinout.md`, section "Note on the contact
side".

### B — Solder to the vias

The vias in the fan-out to the right of the connector, at approx. 0.3 mm,
are much more forgiving than the pads themselves.

- 0.1 mm enamelled copper wire
- Keep wires **short** (< 10 cm)
- **At least two GND leads** to the analyser

---

## 2. Channel assignment

| Channel | Signal |
|---|---|
| D0 | SCK |
| D1 | SDI / MOSI |
| D2 | CS |
| D3 | D/C |
| D4 | BUSY |
| D5 | RST |
| D6 | free |
| D7 | **tie to GND** |

**Do not leave D7 open** — known SLogic bug: an unused D7 can show a level
inversion (see `TOOLS.md`).

**The panel must stay connected.** Without the panel, BUSY behaves
differently and the tag may abort the refresh.

---

## 2a. Level check with the oscilloscope (OWON HDS242)

Before connecting the SLogic for the first time, **only on the lines
verified as MCU-connected in M-001**:

1. Power up the tag, trigger a refresh.
2. Read the high level on **SCK** with the oscilloscope.
3. If possible, also the **SCK frequency** during a data block.

| Result | Consequence |
|---|---|
| High level 2.5 – 3.6 V | SLogic can be connected directly |
| High level < 2 V (e.g. 1.8 V logic) | SLogic does not detect high (VIH > 2 V) → do **not** record, report back to Claude Code |
| High level > 3.6 V | **Do not connect the SLogic** — report back to Claude Code |
| SCK > 4 MHz | Run pass B with 4 instead of 8 channels (see `TOOLS.md`) |

⚠ Probe ground to GND, **never** near the HV pins (±20 V).

---

## 3. Recording

### Pass A — overview

| Setting | Value |
|---|---|
| Channels | 8 |
| Sample rate | **2 MSa/s** |
| Duration | approx. 60 s |
| Data volume | approx. 120 MB |

The goal is **not** decoding, but orientation:

- How fast does SCK actually clock?
- Where on the timeline is the reset, where is the data block?
- How long does BUSY hold?

### Pass B — payload

| Setting | Value |
|---|---|
| Channels | 8 |
| Sample rate | **20 MSa/s** (Windows — the maintainer's setup) or 40 MSa/s (Linux) |
| Duration | 30–60 s |
| Data volume | approx. 600 MB or 1.2 GB |

**Rule of thumb:** at least 5× SCK, better 10×. After pass A the actual SCK
frequency is known — adjust to it.

PulseView keeps everything in RAM. Free up enough beforehand.

---

## 4. Triggering the refresh

1. **Start** the recording
2. **Then** insert the battery

The tag typically transmits for a few seconds first and draws the screen
afterwards. That is why the recording is started beforehand.

### If nothing happens

- Leave the battery out for 30 s (discharge the capacitors), try again
- Try another tag
- **Plan B:** trigger the refresh via NFC. The board carries an NFC front
  end with an antenna coil (see `hardware.md`). An NFC-capable phone in
  range may be able to wake the tag.

---

## 5. Expected orders of magnitude

For plausibility checks, so that a failure is noticed early:

| Quantity | Expectation |
|---|---|
| SPI clock | 1 – 4 MHz (typical for e-paper) |
| SPI mode | Mode 0 (CPOL=0, CPHA=0), MSB first, CS active low |
| Payload at 800×480, 2 planes | approx. 96 kB |
| Pure transfer time for that at 2 MHz | approx. 0.4 s |
| Total refresh duration (three-colour) | **15 – 30 s** |

The lion's share of the time is **waiting for BUSY**, not data transfer.

---

## 6. Export and storage

Export from PulseView as **CSV, all 8 channels, raw** —
not the decoder output.

Store in `captures/` following the scheme:

```
YYYY-MM-DD_<tag-id>_<purpose>_<rate>.csv
```

Example: `2026-09-25_tag03_boot-refresh_20MHz.csv`

Also keep the native `.sr` file if available — it is lossless and much
more compact.

---

## 7. Analysis

```bash
python3 analysis/decode_spi.py captures/<file>.csv \
    --sck D0 --mosi D1 --cs D2 --dc D3 --busy D4 --rst D5
```

On Windows use the `py` launcher instead of `python3`.

See `analysis/README.md`.

---

## 8. Afterwards: entry in HISTORY.md

Mandatory, even on failure. Format: see the template at the end of
`HISTORY.md`.
