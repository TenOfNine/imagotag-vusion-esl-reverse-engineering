# analysis — evaluating the captures

## Installation

```bash
python3 -m pip install -r analysis/requirements.txt
```

On Windows: `py -m pip install -r analysis/requirements.txt`

---

## decode_spi.py

Splits a PulseView CSV export into commands and data blocks.

```bash
python3 analysis/decode_spi.py captures/<file>.csv \
    --sck D0 --mosi D1 --cs D2 --dc D3 --busy D4 --rst D5 \
    --out-prefix analysis/out/2026-09-25_tag03
```

### Options

| Option | Default | Purpose |
|---|---|---|
| `--sck --mosi --cs --dc` | D0–D3 | channel mapping |
| `--busy --rst` | D4, D5 | optional, for BUSY duration and reset detection |
| `--mode` | 0 | SPI mode 0–3 |
| `--lsb-first` | off | if LSB comes first |
| `--cs-active-high` | off | if CS is inverted |
| `--rate` | from CSV | sample rate in Hz, if not in the header |
| `--bpp` | 1 | bits per pixel for the resolution candidates (2 for a four-colour BWRY panel) |
| `--out-prefix` | — | writes report files |

### What is output

**On the console:**

1. **Capture overview** — duration, estimated SPI clock, reset edges, long
   BUSY phases. Warns if the sample rate is below 5× the SPI clock.
2. **Controller fingerprint** — how many of the known opcodes per
   controller family occur (UC8179, IL0373, SSD16xx).
3. **Command log** — every transaction with opcode, plain-text meaning and
   payload.
4. **Frame blocks** — all data blocks ≥ 1024 bytes, plus **resolution
   candidates** by factorising `block length × 8`.
5. **TRES check** — if a `0x61` command occurs: the resolution announced
   there is checked against the block lengths (`MATCH` / `MISMATCH`).
   A `MISMATCH` is a finding, not an error.
6. **LUT candidates** — blocks between 20 and 512 bytes. If the waveform is
   in here, it does not need to be reconstructed from the OTP.

**As files** (with `--out-prefix`):

| File | Content |
|---|---|
| `*_transactions.txt` | full log, small payloads in plain text |
| `*_init_sequence.py` | replayable sequence, image data as a `FRAME` placeholder |
| `*_blocks.csv` | table of all transactions for your own evaluation |

---

## Important limitation

> The script does **not check the pin mapping**. If the channels are
> mapped wrongly, the output is convincing and wrong.

The fingerprint is a **hint, not proof**. A 60 % hit only means that many
opcodes fit a family — the families overlap heavily (UC8179 and IL0373
share almost all opcodes).

It only becomes reliable when:

- the resolution from the block lengths matches the physical panel
  dimensions, and
- a replay of the sequence on the hardware actually draws an image.

---

## Memory requirements

The decoder loads only the required channels, 1 byte per sample each.
Rule of thumb: **samples × channel count** bytes, plus working memory for
the evaluation. A pass B at 20 MSa/s × 60 s × 6 channels therefore needs
about **7 GB** for the raw data alone. If the computer does not have that:
cut the recording shorter (in PulseView, export only the region around the
refresh).

---

## sr_overview.py

Timeline overview of a PulseView `.sr` session, read directly (no CSV
export needed). Meant for the low-rate overview pass A: per-channel
activity plus a chronological edge list with fast bursts collapsed.

```bash
python3 analysis/sr_overview.py captures/<file>.sr
```

At a low sample rate fast clocks alias — pulse counts inside a burst are
only trustworthy well above the SPI clock.

---

## sr_spi_frames.py

Decodes SPI **per CS frame** directly from a `.sr` file. Built for this
tag: every byte has its own CS pulse, writes and reads use different clock
speeds on the same (bidirectional) data line.

```bash
python3 analysis/sr_spi_frames.py captures/<file>.sr \
    --sck Pin13 --data Pin14 --cs Pin12 --dc Pin11 --start 6.70 --end 6.71
```

Channel names as stored in the `.sr` file (or `D0`..`D7`). A `!` marks
bytes where rising- and falling-edge sampling disagree — a sign that the
sample rate is too low. Run from the `analysis/` directory or with it on
`PYTHONPATH` (it imports `sr_overview`).

---

## make_testcapture.py

Generates a **synthetic** capture to test the decoder without hardware:

```bash
python3 analysis/make_testcapture.py /tmp/fake.csv
python3 analysis/decode_spi.py /tmp/fake.csv
```

Simulates a UC8179-style three-colour refresh: reset, init, two colour
planes, DRF, long BUSY phase.

**This is a test fixture.** It proves that the decoder works — it says
nothing about the real panel.

---

## Expected values for the real capture

For plausibility checks:

| Quantity | Expectation |
|---|---|
| SPI clock | 1 – 4 MHz |
| SPI mode | 0 (CPOL=0, CPHA=0), MSB first, CS active low |
| Frame blocks | three-colour: 2 of equal size (B/W + red plane, 1bpp); **four-colour BWRY (our panel, `[ASSUMPTION]`): 1 block at 2bpp** |
| Block size at 800×480 | 48,000 bytes per 1bpp plane; **96,000 bytes at 2bpp** |
| BUSY phase after DRF | 15 – 30 s |

If the measured values deviate from these, that is **an insight** and
belongs in `HISTORY.md` — not a reason to keep turning the parameters until
the expected result comes out.
