#!/usr/bin/env python3
"""
sr_overview.py - timeline overview of a sigrok/PulseView .sr session.

Meant for the low-rate overview pass (capture protocol, pass A): shows per
channel activity and a chronological edge list in which fast bursts (e.g.
SPI bytes) are collapsed into one line.

Usage:
    python3 analysis/sr_overview.py captures/<file>.sr [--burst-gap-us 20]

It reads the .sr zip directly (metadata + logic-1-N chunks), so no CSV
export is needed. Only logic channels with unitsize 1 are supported.

NOTE: at a low sample rate, fast clocks alias. Pulse counts inside a burst
are only trustworthy if the sample rate is well above the SPI clock.
"""

from __future__ import annotations

import argparse
import configparser
import re
import zipfile

import numpy as np


def load_sr(path: str) -> tuple[np.ndarray, float, dict[int, str]]:
    z = zipfile.ZipFile(path)
    meta = configparser.ConfigParser()
    meta.read_string(z.read("metadata").decode())
    dev = meta["device 1"]

    if dev.get("unitsize", "1") != "1":
        raise SystemExit("only unitsize=1 (up to 8 logic channels) is supported")

    m = re.match(r"([\d.]+)\s*([kMG]?)Hz", dev["samplerate"])
    if not m:
        raise SystemExit(f"cannot parse samplerate {dev['samplerate']!r}")
    rate = float(m.group(1)) * {"": 1, "k": 1e3, "M": 1e6, "G": 1e9}[m.group(2)]

    names = {}
    for key, val in dev.items():
        if key.startswith("probe"):
            names[int(key[5:]) - 1] = val        # probe1 -> bit 0

    prefix = dev.get("capturefile", "logic-1")
    chunks = sorted(
        (n for n in z.namelist() if n.startswith(prefix + "-")),
        key=lambda n: int(n.rsplit("-", 1)[1]),
    )
    data = np.concatenate([np.frombuffer(z.read(n), dtype=np.uint8) for n in chunks])
    return data, rate, names


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("session", help=".sr file from PulseView")
    ap.add_argument("--burst-gap-us", type=float, default=20.0,
                    help="edges closer than this are merged into one burst line")
    a = ap.parse_args(argv)

    data, rate, names = load_sr(a.session)
    label = {b: f"D{b} ({names[b]})" if b in names else f"D{b}" for b in range(8)}

    print(f"samples      {len(data):,}")
    print(f"sample rate  {rate:,.0f} Hz")
    print(f"duration     {len(data) / rate:.3f} s")
    print()
    print("CHANNELS")
    edges = []
    for b in range(8):
        x = ((data >> b) & 1).astype(np.int8)
        idx = np.flatnonzero(np.diff(x)) + 1
        print(f"  {label[b]:<14} start={x[0]} end={x[-1]} "
              f"high={x.mean() * 100:6.2f} %  edges={len(idx)}")
        edges += [(int(i), b, int(x[i])) for i in idx]
    edges.sort()

    print()
    print("TIMELINE   (bursts: edges less than "
          f"{a.burst_gap_us:g} us apart are collapsed)")
    gap = a.burst_gap_us * 1e-6 * rate
    i = 0
    while i < len(edges):
        j = i
        while j + 1 < len(edges) and edges[j + 1][0] - edges[j][0] <= gap:
            j += 1
        t0 = edges[i][0] / rate
        if j == i:
            s, b, v = edges[i]
            print(f"  {t0:12.6f} s  {label[b]} -> {v}")
        else:
            span = (edges[j][0] - edges[i][0]) / rate * 1e6
            count = {}
            for _, b, v in edges[i:j + 1]:
                if v == 1:
                    count[b] = count.get(b, 0) + 1
            per = ", ".join(f"{label[b]}: {n} rising" for b, n in sorted(count.items()))
            print(f"  {t0:12.6f} s  burst {span:8.1f} us, {j - i + 1} edges  [{per}]")
        i = j + 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
