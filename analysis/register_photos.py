#!/usr/bin/env python3
"""
register_photos.py - bring the bottom-side PCB photos into the frame of the
top-side overview photo, so that both copper layers can be compared at the
same coordinates (the bottom photos are mirrored and rotated by 90 degrees
relative to the top one).

The transform is an affine fit on the three mounting / through holes that
are visible on both sides. Hole centres were found with a Hough circle
search (see HISTORY.md, session 3). Accuracy is roughly 0.5-1.5 mm, worst
near the board edges - good enough to follow traces, not to identify single
0.5 mm-pitch pads.

Usage:
    python3 analysis/register_photos.py hardware/photos hardware/photos/derived

Writes:
    pcb-bottom-ruler-registered.jpg set 2: bottom ruler photo in the top frame
    pcb-ruler-top-bottom-blend.jpg  set 2: 50/50 blend
    pcb-bottom-registered.jpg       set 1: bottom photo warped into the top frame
    pcb-top-bottom-blend.jpg        set 1: 50/50 blend
"""

from __future__ import annotations

import sys
from pathlib import Path

import cv2
import numpy as np

# --- set 2 (2026-09-24, preferred): ruler photos, camera perpendicular ---
# pcb-bottom-ruler.jpg -> pcb-top-ruler.jpg; residual on a 4th, independent
# hole: 3.9 px (~0.12 mm at ~32.5 px/mm).
TOP2_HOLES = np.float32([[1110.8, 1627.2], [2835.4, 1839.2], [873.6, 379.2]])
BOTTOM2_HOLES = np.float32([[1018.6, 713.2], [2744.4, 489.4], [788.4, 1956.6]])

# --- set 1 (2026-09-23): phone photos ---
# hole centres in full-resolution pixel coordinates
TOP_HOLES = np.float32([[1854.4, 1015.4], [1866.2, 3077.2], [356.2, 3409.4]])
BOTTOM_HOLES = {
    "pcb-bottom.webp": np.float32([[648.0, 2119.8], [2685.6, 2058.2], [2903.8, 581.6]]),
    "pcb-bottom-capture-wiring-v2.webp": np.float32(
        [[884.4, 3393.4], [4805.4, 3316.8], [5227.2, 542.6]]),
}


def transform(bottom_name: str) -> np.ndarray:
    return cv2.getAffineTransform(BOTTOM_HOLES[bottom_name], TOP_HOLES)


def transform2() -> np.ndarray:
    return cv2.getAffineTransform(BOTTOM2_HOLES, TOP2_HOLES)


def main(argv: list[str]) -> int:
    src, out = Path(argv[1]), Path(argv[2])
    out.mkdir(parents=True, exist_ok=True)
    # set 2 (preferred)
    top = cv2.imread(str(src / "pcb-top-ruler.jpg"))
    bot = cv2.imread(str(src / "pcb-bottom-ruler.jpg"))
    warped = cv2.warpAffine(bot, transform2(), (top.shape[1], top.shape[0]))
    cv2.imwrite(str(out / "pcb-bottom-ruler-registered.jpg"), warped, [cv2.IMWRITE_JPEG_QUALITY, 90])
    cv2.imwrite(str(out / "pcb-ruler-top-bottom-blend.jpg"),
                cv2.addWeighted(top, 0.5, warped, 0.5, 0), [cv2.IMWRITE_JPEG_QUALITY, 90])
    # set 1
    top = cv2.imread(str(src / "pcb-top-overview.webp"))
    bot = cv2.imread(str(src / "pcb-bottom.webp"))
    warped = cv2.warpAffine(bot, transform("pcb-bottom.webp"), (top.shape[1], top.shape[0]))
    cv2.imwrite(str(out / "pcb-bottom-registered.jpg"), warped, [cv2.IMWRITE_JPEG_QUALITY, 88])
    cv2.imwrite(str(out / "pcb-top-bottom-blend.jpg"),
                cv2.addWeighted(top, 0.5, warped, 0.5, 0), [cv2.IMWRITE_JPEG_QUALITY, 88])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
