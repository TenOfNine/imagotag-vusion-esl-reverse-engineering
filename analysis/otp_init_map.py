#!/usr/bin/env python3
"""
otp_init_map.py - compare the panel OTP bytes from our boot capture with a
published init table for the Pervasive Displays E2741QS0B3 (7.4" BWRY).

Input is a frames file written by sr_spi_frames.py. The script takes the
bytes read after command 0x92 (OTP read), drops the first one (dummy byte,
per the Pervasive Displays "BWRY Medium" OTP read procedure) and checks, for
every OTP-derived parameter of the reference init table, whether our OTP
holds the same bytes at the given offset.

Usage:
    python3 analysis/otp_init_map.py \
        analysis/out/2026-09-23_tag02_boot-init-4ch_20MHz_frames.txt

Reference values: bitbank2/bb_epaper, pull request #44, commit 61de1cf,
table `epd74yr_init_full` ("Register values dumped from the panel's COG OTP
memory"), https://github.com/bitbank2/bb_epaper/pull/44

The OTP offsets below were first found by value matching (2026-10-21).
Update 2026-10-21: they are identical to the offsets used by Pervasive
Displays' own driver (PervasiveDisplays/Pervasive_BWRY_Medium, commit
d877f73, COG_initial()), so they are [RESEARCH] now. Note that the vendor
driver sends 0x04 (power on) after the image data, not at the end of the
init as in the bb_epaper table.
"""

from __future__ import annotations

import argparse
import sys

# (command, reference parameter bytes, OTP offset of the first byte or None
# if the value is not taken from the OTP)
REFERENCE = [
    (0xE6, [0x19], None),          # temperature, host-supplied (25 C)
    (0xE0, [0x02], None),
    (0xA5, [], None),
    (0x01, [0x07], 16),            # PWR
    (0x00, [0x07, 0xAB], 26),      # PSR, first write
    (0x61, [0x01, 0xE0, 0x03, 0x20], 19),  # TRES
    (0x00, [0x07, 0x2B], 17),      # PSR, second write
    (0x06, [0x40, 0x40, 0x40], 23),  # BTST_P
    (0x03, [0x00, 0x00, 0x00], 30),  # PFS
    (0xE7, [0x3C], 33),
    (0x65, [0x00, 0x00, 0x00, 0x00], 34),
    (0x30, [0x08], 38),            # PLL
    (0x50, [0x37], 39),            # CDI
    (0x60, [0x03, 0x03], 40),      # TCON
    (0xE3, [0x00], 42),            # PWS
    (0xFF, [0xA5], None),
    (0xEF, [0x01, 0x1E, 0x06, 0x0A, 0x0F, 0x19, 0x0F, 0x09], 43),
    (0xDC, [0x01], 59),
    (0xDD, [0x04], 60),
    (0xDE, [0x01], 61),
    (0xE8, [0x01], 62),
    (0xDA, [0x3F], 63),
    (0xFF, [0xE3], None),
    (0xE9, [0x01], None),
    (0x04, [], None),              # power on
]


def read_frames(path: str) -> list[tuple[int, int]]:
    """Return (dc, byte) for every frame line of an sr_spi_frames.py file."""
    frames = []
    with open(path) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            cols = line.split()
            frames.append((int(cols[2]), int(cols[5], 16)))
    return frames


def otp_after_0x92(frames: list[tuple[int, int]]) -> list[int]:
    for i, (dc, value) in enumerate(frames):
        if dc == 0 and value == 0x92:
            data = []
            for dc2, value2 in frames[i + 1:]:
                if dc2 == 0:
                    break
                data.append(value2)
            return data
    raise SystemExit("no 0x92 command found")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("frames", help="frames file from sr_spi_frames.py")
    args = parser.parse_args()

    raw = otp_after_0x92(read_frames(args.frames))
    dummy, otp = raw[0], raw[1:]
    print(f"read after 0x92: {len(raw)} bytes, dummy 0x{dummy:02X}, "
          f"{len(otp)} OTP bytes (offsets 0..{len(otp) - 1})")
    print(f"OTP[0] = 0x{otp[0]:02X} "
          f"({'bank 0 marker 0xA5' if otp[0] == 0xA5 else 'not 0xA5'})")
    print()
    print("cmd  reference params              OTP offset  our OTP bytes             match")

    mismatches = 0
    for cmd, ref, offset in REFERENCE:
        ref_s = " ".join(f"{b:02X}" for b in ref)
        if offset is None:
            print(f"{cmd:02X}   {ref_s:<28}  fixed")
            continue
        ours = otp[offset:offset + len(ref)]
        ours_s = " ".join(f"{b:02X}" for b in ours)
        ok = ours == ref
        mismatches += not ok
        print(f"{cmd:02X}   {ref_s:<28}  {offset:>3}..{offset + len(ref) - 1:<4}  "
              f"{ours_s:<24}  {'yes' if ok else 'NO'}")

    used = sorted({o + k for _, ref, o in REFERENCE if o is not None
                   for k in range(len(ref))})
    unused = [i for i in range(len(otp)) if i not in used]
    print()
    print("OTP offsets not used by the reference table: "
          + " ".join(f"{i}:{otp[i]:02X}" for i in unused))
    print(f"\n{mismatches} mismatch(es)")
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
