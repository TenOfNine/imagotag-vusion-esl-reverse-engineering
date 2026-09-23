#!/usr/bin/env python3
"""
sr_spi_frames.py - decode per-CS-frame SPI bytes directly from a .sr file.

The tag frames every single byte with its own CS pulse and switches between
a fast write clock and a slow read clock on the same data line, so this
decoder works frame by frame: for each CS-low window it samples the data
line on the SCK rising edges (and, as a cross-check, just before the
falling edges) and reports D/C, clock period and the byte value.

Usage:
    python3 analysis/sr_spi_frames.py captures/<file>.sr \
        --sck Pin13 --data Pin14 --cs Pin12 --dc Pin11 [--start 6.70 --end 6.71]

Channel arguments are the channel names stored in the .sr file (as set in
PulseView) or D0..D7.

Columns: time, CS-low width, D/C, clock count, mean SCK period, byte,
'!' if rising/falling-edge sampling disagree (sample rate too low).

NOTE: bits are assembled MSB first. Whether a byte was written by the MCU
or driven by the panel (read) cannot be told from the logic levels alone.
"""

from __future__ import annotations

import argparse

import numpy as np

from sr_overview import load_sr


def channel_bit(spec: str, names: dict[int, str]) -> int:
    for bit, name in names.items():
        if name == spec:
            return bit
    if spec.upper().startswith("D") and spec[1:].isdigit():
        return int(spec[1:])
    raise SystemExit(f"channel {spec!r} not found; names in file: {names}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("session")
    ap.add_argument("--sck", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--cs", required=True)
    ap.add_argument("--dc", required=True)
    ap.add_argument("--start", type=float, default=None, help="seconds")
    ap.add_argument("--end", type=float, default=None, help="seconds")
    a = ap.parse_args(argv)

    data, rate, names = load_sr(a.session)
    s0 = int(a.start * rate) if a.start is not None else 0
    s1 = int(a.end * rate) if a.end is not None else len(data)
    d = data[s0:s1]

    bit = {k: channel_bit(getattr(a, k), names) for k in ("sck", "data", "cs", "dc")}
    sck = ((d >> bit["sck"]) & 1).astype(np.int8)
    sda = (d >> bit["data"]) & 1
    cs = ((d >> bit["cs"]) & 1).astype(np.int8)
    dc = (d >> bit["dc"]) & 1

    lo = np.flatnonzero(np.diff(cs) == -1) + 1
    hi = np.flatnonzero(np.diff(cs) == 1) + 1
    rise = np.flatnonzero(np.diff(sck) == 1) + 1
    fall = np.flatnonzero(np.diff(sck) == -1) + 1

    print(f"# {a.session}  rate {rate:,.0f} Hz  "
          f"sck={a.sck} data={a.data} cs={a.cs} dc={a.dc}")
    print("# time_s        cs_low_us  dc  clk  period_us  byte")
    n = 0
    for s in lo:
        h = hi[hi > s]
        if not len(h):
            continue
        e = h[0]
        rr = rise[(rise > s) & (rise < e)]
        ff = fall[(fall > s) & (fall < e)]
        br = [int(sda[i]) for i in rr]
        bf = [int(sda[i - 1]) for i in ff]
        per = np.diff(rr).mean() / rate * 1e6 if len(rr) > 1 else float("nan")
        mid = min(s + (e - s) // 2, len(dc) - 1)
        val = "--"
        if len(br) == 8:
            val = f"{int(''.join(map(str, br)), 2):02X}"
        flag = "" if br == bf else "  !"
        print(f"{(s0 + s) / rate:12.7f}  {(e - s) / rate * 1e6:9.2f}  {dc[mid]:2d}  "
              f"{len(br):3d}  {per:9.3f}  {val}{flag}")
        n += 1
    print(f"# {n} frames")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
