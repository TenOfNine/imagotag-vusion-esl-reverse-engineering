#!/usr/bin/env python3
"""
decode_spi.py - decode a PulseView CSV capture of the ESL panel SPI bus.

Reconstructs the EPD refresh from a raw logic analyser capture:
splits the stream into transactions, classifies every byte as command or
data via the D/C line, measures data block lengths, derives candidate panel
resolutions and fingerprints the COG controller.

Usage:
    python3 decode_spi.py CAPTURE.csv --sck D0 --mosi D1 --cs D2 --dc D3

See analysis/README.md for details.

NOTE: every conclusion this script prints is derived from the capture alone.
It does NOT verify the pin mapping - if the channels are assigned wrongly,
the output is confidently wrong. Confirm the mapping first (M-001).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Controller fingerprints
# --------------------------------------------------------------------------
# Command opcodes characteristic for each family. Scoring is "how many of
# these opcodes appear in the capture", normalised. Purely a hint - never
# treat the top match as established fact.

FINGERPRINTS: dict[str, dict[int, str]] = {
    "UC8179 / UC8179C (7.5\" family)": {
        0x00: "PSR  panel setting",
        0x01: "PWR  power setting",
        0x02: "POF  power off",
        0x04: "PON  power on",
        0x06: "BTST booster soft start",
        0x10: "DTM1 data start transmission 1 (B/W)",
        0x12: "DRF  display refresh",
        0x13: "DTM2 data start transmission 2 (RED)",
        0x30: "PLL  control",
        0x50: "CDI  VCOM and data interval",
        0x61: "TRES resolution setting",
        0x65: "GSST gate/source start",
    },
    "IL0373 / IL91874 family": {
        0x00: "PSR  panel setting",
        0x01: "PWR  power setting",
        0x02: "POF  power off",
        0x04: "PON  power on",
        0x06: "BTST booster soft start",
        0x10: "DTM1 data start transmission 1",
        0x11: "DSP  data stop",
        0x12: "DRF  display refresh",
        0x13: "DTM2 data start transmission 2",
        0x16: "PFS  power off sequence",
        0x20: "LUT1 vcom lut",
        0x21: "LUTWW",
        0x22: "LUTBW",
        0x23: "LUTWB",
        0x24: "LUTBB",
        0x30: "PLL  control",
        0x50: "CDI  vcom/data interval",
        0x61: "TRES resolution",
        0x71: "GDS  get status",
    },
    "SSD16xx / SSD1680 family": {
        0x01: "driver output control",
        0x03: "gate driving voltage",
        0x04: "source driving voltage",
        0x0C: "booster soft start",
        0x11: "data entry mode",
        0x12: "SW reset",
        0x18: "temperature sensor control",
        0x1A: "temperature register write",
        0x20: "master activation",
        0x21: "display update control 1",
        0x22: "display update control 2",
        0x24: "write RAM (B/W)",
        0x26: "write RAM (RED)",
        0x32: "write LUT register",
        0x3C: "border waveform control",
        0x44: "set RAM X range",
        0x45: "set RAM Y range",
        0x4E: "set RAM X counter",
        0x4F: "set RAM Y counter",
    },
}

# Opcodes that, in each family, introduce a full-frame pixel block.
FRAME_OPCODES: dict[str, set[int]] = {
    "UC8179 / UC8179C (7.5\" family)": {0x10, 0x13},
    "IL0373 / IL91874 family": {0x10, 0x13},
    "SSD16xx / SSD1680 family": {0x24, 0x26},
}


# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------

@dataclass
class Transaction:
    """One CS-low window."""
    index: int
    start_sample: int
    end_sample: int
    cmd: int | None = None            # first byte if D/C was low
    data: bytes = b""                 # bytes sent while D/C was high
    trailing: bytes = b""             # further D/C-low bytes (unusual)

    @property
    def n_data(self) -> int:
        return len(self.data)


@dataclass
class Capture:
    rate: float | None
    samples: int
    channels: list[str]
    transactions: list[Transaction] = field(default_factory=list)
    busy_waits: list[tuple[int, int]] = field(default_factory=list)
    rst_pulses: list[int] = field(default_factory=list)


# --------------------------------------------------------------------------
# CSV loading
# --------------------------------------------------------------------------

def sniff_header(path: str) -> tuple[int, list[str], float | None]:
    """Find the header row, channel names and (if present) the sample rate."""
    rate: float | None = None
    header_line = 0
    names: list[str] = []

    with open(path, "r", errors="replace") as fh:
        for i, raw in enumerate(fh):
            line = raw.strip()
            if not line:
                header_line = i + 1
                continue
            if line.startswith((";", "#")):
                low = line.lower()
                # PulseView writes e.g. "; Sample rate: 20 MHz" or
                # ";Sample rate,20000000"
                if "rate" in low:
                    rate = _parse_rate(line)
                header_line = i + 1
                continue
            # First non-comment line: header if it is non-numeric.
            parts = [p.strip() for p in line.split(",")]
            try:
                float(parts[0])
                # numeric -> no header row, synthesise names
                names = [f"col{j}" for j in range(len(parts))]
                return i, names, rate
            except ValueError:
                names = parts
                return i + 1, names, rate
            finally:
                header_line = i

    raise SystemExit(f"{path}: no data rows found")


def _parse_rate(line: str) -> float | None:
    """Pull a sample rate out of a PulseView comment line.

    Deliberately strict: the word 'rate' also hides inside 'Generated',
    so a bare 'rate' match is not enough.
    """
    import re

    if not re.search(r"\bsample\s*rate\b|\bsamplerate\b", line, re.IGNORECASE):
        return None

    for pattern, scaled in (
        (r"([\d.]+)\s*([kMG]?)Hz", True),
        (r"rate\s*[:,=]\s*([\d.]+)", False),
    ):
        m = re.search(pattern, line, re.IGNORECASE)
        if not m:
            continue
        try:
            value = float(m.group(1))
        except ValueError:
            continue
        if scaled:
            value *= {"": 1, "k": 1e3, "m": 1e6, "g": 1e9}[m.group(2).lower()]
        if value > 0:
            return value
    return None


def load(
    path: str, wanted: list[str], optional: list[str] = ()
) -> tuple[pd.DataFrame, float | None]:
    skip, names, rate = sniff_header(path)

    missing = [c for c in wanted if c not in names]
    if missing:
        raise SystemExit(
            f"channel(s) {missing} not in CSV.\n"
            f"available columns: {names}\n"
            f"pass the right names via --sck/--mosi/--cs/--dc"
        )

    # Only load the channels we decode, as uint8. A 60 s capture at
    # 20 MSa/s has 1.2e9 rows - loading every column as int64 would need
    # tens of GB of RAM.
    keep = set(wanted) | {c for c in optional if c in names}

    header_arg = 0 if skip > 0 else None
    df = pd.read_csv(
        path,
        skiprows=skip - 1 if skip > 0 else 0,
        header=header_arg,
        comment=";",
        engine="c",
        usecols=lambda c: str(c).strip() in keep,
        dtype=np.uint8,
    )
    df.columns = [str(c).strip() for c in df.columns]

    for c in wanted:
        df[c] = (pd.to_numeric(df[c], errors="coerce").fillna(0) > 0).astype(np.uint8)

    return df, rate


# --------------------------------------------------------------------------
# SPI decoding
# --------------------------------------------------------------------------

def decode(
    df: pd.DataFrame,
    sck: str,
    mosi: str,
    cs: str,
    dc: str,
    busy: str | None,
    rst: str | None,
    cpol: int,
    cpha: int,
    lsb_first: bool,
    cs_active_high: bool,
    rate: float | None,
) -> Capture:
    s_sck = df[sck].to_numpy()
    s_mosi = df[mosi].to_numpy()
    s_cs = df[cs].to_numpy()
    s_dc = df[dc].to_numpy()

    cap = Capture(rate=rate, samples=len(df), channels=list(df.columns))

    # --- sampling edge --------------------------------------------------
    # Mode 0/3 (cpol==cpha) sample on rising, mode 1/2 on falling.
    want_rise = (cpol == cpha)
    d = np.diff(s_sck.astype(np.int8))
    edges = np.flatnonzero(d == (1 if want_rise else -1)) + 1
    if edges.size == 0:
        raise SystemExit(
            "no clock edges found on the SCK channel - wrong channel, "
            "or the capture holds no traffic"
        )

    # --- CS windows ------------------------------------------------------
    active = s_cs.astype(bool) if cs_active_high else ~s_cs.astype(bool)
    da = np.diff(active.astype(np.int8))
    starts = np.flatnonzero(da == 1) + 1
    ends = np.flatnonzero(da == -1) + 1
    if active[0]:
        starts = np.insert(starts, 0, 0)
    if active[-1]:
        ends = np.append(ends, len(active))
    n_win = min(len(starts), len(ends))
    starts, ends = starts[:n_win], ends[:n_win]

    if n_win == 0:
        raise SystemExit(
            "CS never goes active - check --cs channel and --cs-active-high"
        )

    bits = s_mosi[edges]
    dcs = s_dc[edges]

    # bucket each clock edge into its CS window
    win = np.searchsorted(starts, edges, side="right") - 1
    valid = (win >= 0) & (win < n_win) & (edges < ends[np.clip(win, 0, n_win - 1)])

    for w in range(n_win):
        sel = valid & (win == w)
        if not sel.any():
            continue
        wb = bits[sel]
        wd = dcs[sel]
        nbytes = len(wb) // 8
        if nbytes == 0:
            continue

        wb = wb[: nbytes * 8].reshape(nbytes, 8)
        wd = wd[: nbytes * 8].reshape(nbytes, 8)

        if lsb_first:
            wb = wb[:, ::-1]
        vals = np.packbits(wb.astype(np.uint8), axis=1).ravel()
        # a byte counts as "data" if D/C was high for the majority of its bits
        is_data = wd.mean(axis=1) > 0.5

        tx = Transaction(index=w, start_sample=int(starts[w]), end_sample=int(ends[w]))
        if not is_data[0]:
            tx.cmd = int(vals[0])
            rest, rest_dc = vals[1:], is_data[1:]
        else:
            rest, rest_dc = vals, is_data

        tx.data = bytes(int(v) for v, f in zip(rest, rest_dc) if f)
        tx.trailing = bytes(int(v) for v, f in zip(rest, rest_dc) if not f)
        cap.transactions.append(tx)

    # --- BUSY ------------------------------------------------------------
    if busy and busy in df.columns:
        b = df[busy].to_numpy().astype(bool)
        # a "wait" is a long constant stretch; report both polarities and let
        # the human decide which level means busy
        db = np.diff(b.astype(np.int8))
        tr = np.flatnonzero(db != 0) + 1
        bounds = np.concatenate(([0], tr, [len(b)]))
        for a, z in zip(bounds[:-1], bounds[1:]):
            if z - a > (rate or 1e6) * 0.2:      # > 200 ms
                cap.busy_waits.append((int(a), int(z)))

    # --- RST -------------------------------------------------------------
    if rst and rst in df.columns:
        r = df[rst].to_numpy().astype(np.int8)
        cap.rst_pulses = [int(i) + 1 for i in np.flatnonzero(np.diff(r) == -1)]

    return cap


# --------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------

def estimate_clock(df: pd.DataFrame, sck: str, rate: float | None) -> float | None:
    if not rate:
        return None
    s = df[sck].to_numpy().astype(np.int8)
    rises = np.flatnonzero(np.diff(s) == 1)
    if rises.size < 100:
        return None
    # median period across the busiest stretch
    per = np.diff(rises)
    per = per[per < np.percentile(per, 90)]
    if per.size == 0:
        return None
    return rate / float(np.median(per))


def divisor_pairs(pixels: int, lo: int = 64, hi: int = 4096) -> list[tuple[int, int]]:
    """Plausible (width, height) pairs for a given pixel count."""
    out = []
    for w in range(lo, min(hi, pixels) + 1):
        if pixels % w:
            continue
        h = pixels // w
        if lo <= h <= hi:
            out.append((w, h))
    # prefer landscape-ish, 8-aligned, sane aspect ratios
    out.sort(key=lambda p: (p[0] % 8 != 0, abs((p[0] / p[1]) - 1.55)))
    return out


def fingerprint(cap: Capture) -> list[tuple[str, float, int]]:
    seen = {t.cmd for t in cap.transactions if t.cmd is not None}
    scored = []
    for name, table in FINGERPRINTS.items():
        hits = len(seen & set(table))
        scored.append((name, hits / len(table), hits))
    scored.sort(key=lambda x: -x[1])
    return scored


def big_blocks(cap: Capture, min_bytes: int = 1024) -> list[Transaction]:
    return [t for t in cap.transactions if t.n_data >= min_bytes]


def declared_resolutions(cap: Capture) -> list[tuple[int, int, int, str]]:
    """Resolutions announced via a 0x61 (TRES) command.

    Returns (transaction index, width, height, layout) tuples. Two payload
    layouts are known:
      4 bytes  UC8179:  HRES[9:8] HRES[7:0] VRES[9:8] VRES[7:0]
      3 bytes  IL0373:  HRES[7:3]           VRES[8]   VRES[7:0]
    0x61 means something else in the SSD16xx family, so a hit here is only
    meaningful if the controller really is UC8179/IL0373-like.
    """
    out = []
    for t in cap.transactions:
        if t.cmd != 0x61:
            continue
        d = t.data
        if len(d) == 4:
            out.append((t.index, (d[0] << 8) | d[1], (d[2] << 8) | d[3], "UC8179"))
        elif len(d) == 3:
            out.append((t.index, d[0], (d[1] << 8) | d[2], "IL0373"))
    return out


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------

def report(cap: Capture, clock: float | None, prefix: str | None) -> None:
    p = print
    p("=" * 72)
    p("CAPTURE")
    p("=" * 72)
    p(f"  samples          {cap.samples:,}")
    p(f"  sample rate      {cap.rate:,.0f} Hz" if cap.rate else "  sample rate      unknown")
    if cap.rate:
        p(f"  duration         {cap.samples / cap.rate:.3f} s")
    if clock:
        p(f"  SPI clock        ~{clock / 1e6:.2f} MHz")
        if cap.rate and cap.rate < clock * 5:
            p("  !! sample rate below 5x SPI clock - decode may be unreliable")
    p(f"  transactions     {len(cap.transactions):,}")
    if cap.rst_pulses:
        p(f"  RST falling      {len(cap.rst_pulses)} at sample(s) "
          f"{cap.rst_pulses[:5]}{' ...' if len(cap.rst_pulses) > 5 else ''}")
    if cap.busy_waits:
        p(f"  long BUSY holds  {len(cap.busy_waits)}")
        for a, z in cap.busy_waits[:6]:
            secs = (z - a) / cap.rate if cap.rate else float("nan")
            p(f"      sample {a:>12,} .. {z:>12,}   {secs:6.2f} s")

    # ---- controller -----------------------------------------------------
    p("")
    p("=" * 72)
    p("CONTROLLER FINGERPRINT   (hint only - not proof)")
    p("=" * 72)
    for name, frac, hits in fingerprint(cap):
        bar = "#" * int(frac * 30)
        p(f"  {frac * 100:5.1f}%  ({hits:2d} opcodes)  {bar:<30}  {name}")

    best = fingerprint(cap)[0][0]
    table = FINGERPRINTS[best]

    # ---- command log ----------------------------------------------------
    p("")
    p("=" * 72)
    p(f"COMMAND LOG   (decoded against: {best})")
    p("=" * 72)
    for t in cap.transactions:
        if t.cmd is None:
            p(f"  [{t.index:5d}] (no command byte)          {t.n_data:>9,} data bytes")
            continue
        meaning = table.get(t.cmd, "")
        if t.n_data > 64:
            payload = f"<{t.n_data:,} bytes>"
        else:
            payload = " ".join(f"{b:02X}" for b in t.data) or "-"
        p(f"  [{t.index:5d}] 0x{t.cmd:02X}  {meaning:<38} {payload}")

    # ---- frame blocks ---------------------------------------------------
    blocks = big_blocks(cap)
    p("")
    p("=" * 72)
    p("FRAME BLOCKS   (>= 1024 data bytes)")
    p("=" * 72)
    if not blocks:
        p("  none found - either the capture missed the image transfer,")
        p("  or D/C is mapped to the wrong channel.")
    else:
        for t in blocks:
            cmd = f"0x{t.cmd:02X}" if t.cmd is not None else "----"
            p(f"  cmd {cmd}   {t.n_data:>10,} bytes   = {t.n_data * 8:>12,} pixels (1bpp)")

        sizes = sorted({t.n_data for t in blocks})
        p("")
        p("  RESOLUTION CANDIDATES")
        p("  " + "-" * 68)
        for s in sizes:
            n = sum(1 for t in blocks if t.n_data == s)
            p(f"  block size {s:,} bytes  (x{n})")
            pairs = divisor_pairs(s * 8)
            if not pairs:
                p("      no plausible width x height factorisation")
            for w, h in pairs[:6]:
                p(f"      {w:>5} x {h:<5}   aspect {w / h:5.2f}")
            p("")

        if len(blocks) >= 2 and len({t.n_data for t in blocks}) == 1:
            p(f"  -> {len(blocks)} equally sized blocks: consistent with a")
            p("     multi-plane (e.g. B/W + RED) three-colour panel.")

    # ---- TRES vs. block length ------------------------------------------
    declared = declared_resolutions(cap)
    if declared:
        p("")
        p("=" * 72)
        p("DECLARED RESOLUTION (0x61) vs. FRAME BLOCKS")
        p("=" * 72)
        sizes = sorted({t.n_data for t in blocks})
        for idx, w, h, layout in declared:
            expect = (w * h + 7) // 8
            p(f"  [{idx:5d}] 0x61 as {layout} layout: {w} x {h}"
              f"  -> {expect:,} bytes per 1bpp plane")
            if not sizes:
                p("      no frame blocks to compare against")
            elif expect in sizes:
                p("      MATCH: a frame block has exactly this length")
            else:
                p(f"      MISMATCH: frame blocks are {', '.join(f'{s:,}' for s in sizes)}"
                  " bytes")
                p("      -> partial update, other bit depth, wrong layout guess,")
                p("         or 0x61 is not TRES on this controller. Investigate.")

    # ---- LUT candidates -------------------------------------------------
    luts = [t for t in cap.transactions if 20 <= t.n_data <= 512]
    if luts:
        p("")
        p("=" * 72)
        p("LUT / WAVEFORM CANDIDATES   (20..512 data bytes)")
        p("=" * 72)
        for t in luts[:20]:
            cmd = f"0x{t.cmd:02X}" if t.cmd is not None else "----"
            p(f"  cmd {cmd}   {t.n_data:>4} bytes")
        p("")
        p("  If these carry the waveform, the panel's LUT is in this capture")
        p("  and does NOT need to be recovered from the COG's OTP.")

    # ---- files ----------------------------------------------------------
    if prefix:
        _write_outputs(cap, table, prefix)
        p("")
        p(f"written: {prefix}_transactions.txt")
        p(f"written: {prefix}_init_sequence.py")
        p(f"written: {prefix}_blocks.csv")


def _write_outputs(cap: Capture, table: dict[int, str], prefix: str) -> None:
    with open(f"{prefix}_transactions.txt", "w") as fh:
        for t in cap.transactions:
            cmd = f"0x{t.cmd:02X}" if t.cmd is not None else "----"
            fh.write(f"[{t.index:6d}] {cmd} "
                     f"{('' if t.cmd is None else table.get(t.cmd, '')):<38} "
                     f"{t.n_data:>10,} bytes\n")
            if 0 < t.n_data <= 256:
                fh.write("         " + " ".join(f"{b:02X}" for b in t.data) + "\n")

    with open(f"{prefix}_init_sequence.py", "w") as fh:
        fh.write('"""Auto-generated from a logic analyser capture.\n\n'
                 'Frame payloads are replaced by a FRAME placeholder.\n'
                 'UNVERIFIED - replaying this has not been tested on hardware.\n'
                 '"""\n\n')
        fh.write("FRAME = object()  # substitute your own image data\n\n")
        fh.write("INIT_SEQUENCE = [\n")
        for t in cap.transactions:
            if t.cmd is None:
                continue
            note = table.get(t.cmd, "")
            if t.n_data >= 1024:
                fh.write(f"    (0x{t.cmd:02X}, FRAME),"
                         f"{'  # ' + note if note else ''}\n")
            else:
                payload = ", ".join(f"0x{b:02X}" for b in t.data)
                fh.write(f"    (0x{t.cmd:02X}, [{payload}]),"
                         f"{'  # ' + note if note else ''}\n")
        fh.write("]\n")

    rows = [
        {
            "index": t.index,
            "cmd": f"0x{t.cmd:02X}" if t.cmd is not None else "",
            "meaning": "" if t.cmd is None else table.get(t.cmd, ""),
            "data_bytes": t.n_data,
            "start_sample": t.start_sample,
            "end_sample": t.end_sample,
        }
        for t in cap.transactions
    ]
    pd.DataFrame(rows).to_csv(f"{prefix}_blocks.csv", index=False)


# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Decode a PulseView CSV capture of the ESL panel SPI bus.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("capture", help="CSV exported from PulseView (raw channels)")
    ap.add_argument("--sck", default="D0")
    ap.add_argument("--mosi", default="D1")
    ap.add_argument("--cs", default="D2")
    ap.add_argument("--dc", default="D3")
    ap.add_argument("--busy", default="D4")
    ap.add_argument("--rst", default="D5")
    ap.add_argument("--mode", type=int, default=0, choices=[0, 1, 2, 3],
                    help="SPI mode (default 0)")
    ap.add_argument("--lsb-first", action="store_true")
    ap.add_argument("--cs-active-high", action="store_true")
    ap.add_argument("--rate", type=float, default=None,
                    help="sample rate in Hz, if not in the CSV header")
    ap.add_argument("--out-prefix", default=None,
                    help="write report files with this path prefix")
    a = ap.parse_args(argv)

    cpol, cpha = (a.mode >> 1) & 1, a.mode & 1

    wanted = [a.sck, a.mosi, a.cs, a.dc]
    optional = [c for c in (a.busy, a.rst) if c]

    df, rate = load(a.capture, wanted, optional)
    rate = a.rate or rate
    for c in optional:
        if c not in df.columns:
            print(f"note: optional channel {c!r} not present, skipping",
                  file=sys.stderr)

    clock = estimate_clock(df, a.sck, rate)
    cap = decode(df, a.sck, a.mosi, a.cs, a.dc,
                 a.busy if a.busy in df.columns else None,
                 a.rst if a.rst in df.columns else None,
                 cpol, cpha, a.lsb_first, a.cs_active_high, rate)
    report(cap, clock, a.out_prefix)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
