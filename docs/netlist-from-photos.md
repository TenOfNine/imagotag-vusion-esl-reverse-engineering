# Netlist from photos — partial, unverified

Status 2026-09-24. **Everything here is `[PHOTO]` or `[ASSUMPTION]`.** Per
`CLAUDE.md` §2 nothing in this file may be used as a pinout without a
continuity measurement. The purpose is to make those measurements short and
targeted.

---

## Method

1. The bottom photos are mirrored and rotated by 90° relative to the top
   overview. Both were brought into one frame with an affine transform fitted
   on the **three holes visible on both sides** (Hough circle detection):
   `analysis/register_photos.py`.
2. Result: `hardware/photos/derived/pcb-bottom-registered.jpg` (bottom side,
   seen *through* the board from the top), `pcb-top-bottom-blend.jpg`
   (50/50 blend) and `pcb-netlist-annotated.jpg` (findings below marked).
3. The capture-wire solder points from `pcb-bottom-capture-wiring-v2.webp`
   (colour mapping known) were transformed into the same frame → known
   start points for FPC pins 9–14.
4. Traces were then followed by eye on side-by-side crops.
5. **Set 2 (2026-09-24, ruler photos, full-resolution originals from a
   ZIP):** `pcb-top-ruler.jpg` (3202 × 2402) and `pcb-bottom-ruler.jpg`
   (3112 × 2334), ≈ 32.5 px/mm. Same three-hole affine fit, residual
   3.9 px ≈ 0.12 mm. Outputs: `derived/pcb-bottom-ruler-registered.jpg`,
   `derived/pcb-ruler-top-bottom-blend.jpg`,
   `derived/pcb-ruler-netlist-annotated.jpg`. **From here on set 2 is the
   reference frame**; set 1 is kept for traceability.

**Accuracy:** board outline, holes, NFC coil and LEDs overlay well; local
error roughly 0.5–1.5 mm (worst near the connector). Enough to follow a
trace from via to via; **not** enough to tell neighbouring 0.4 mm QFN pads
or 0.5 mm connector pads apart.

---

## Findings

### Layer count
- `[PHOTO]` Silkscreen only names two layers: `1 TOP`, `2 BOT`.
  `[ASSUMPTION]` Two-layer board (maintainer's assumption as well). Inner
  layers cannot be seen on photos.

### Display lines FPC 9–14
- `[PHOTO]` Each of FPC 9, 11, 13, 14 has an **exposed (untented) via** close
  to the connector on the bottom side — the capture wires sit on them.
- `[PHOTO]` From there a **bundle of ~10 parallel traces** runs on the
  **bottom** along the left edge of the connector block, down under the QR
  label (where the exposed vias of FPC 10 and FPC 12 sit on the bundle),
  then turns right and ends in a **row of vias directly below the EFR32**.
- ~~`[PHOTO]` On the top, short traces run from the EFR32's bottom row of
  pads down to vias in that area.~~
- ~~`[ASSUMPTION]` The six display lines go to QFN pads on the bottom side
  of the chip — pins 11–20.~~
  **Superseded 2026-09-24 by the set-2 photos (photo re-evaluation, not a
  measurement).** Cause: the set-1 top overview is rotated by 90° relative
  to the macro, so its "bottom row" is the chip's **left** pad column.
- `[PHOTO]` (set 2) The bundle ends in **eight vias V1–V8** left of the
  EFR32 (coordinates in the `pcb-top-ruler.jpg` frame, px): V1 (1222,1513),
  V2 (1250,1545), V3 (1277,1573), V4 (1287,1465), V5 (1301,1497),
  V6 (1328,1531), V7 (1356,1475), V8 (1366,1516). On the top, short
  parallel traces run from these vias into the EFR32's **left pad column**
  (pin-1 dot top left, the same orientation as
  `pcb-top-mcu-macro.webp`).
- `[ASSUMPTION]` The six display lines end on QFN pins **1–10** (left
  column, counted top→bottom). Which via reaches which pad cannot be
  resolved reliably from the photos (0.4 mm pitch, traces cross between
  via row and pads). The bundle has more traces than six, so other signals
  share it.
  → **Test:** M-012 items 1–6, starting with pins 1–10.

### NFC
- `[PHOTO]` The NFC coil sits on the bottom under the empty left "wing".
  On the top, two long traces run from the wing (one ends in a via on the
  wing) to a **small 6-pin IC** at the left edge of the populated area.
- `[ASSUMPTION]` That small IC is the NFC tag (NXP NTAG-type, matches the
  phone read). Consequence: the SO-8 `8K417` is probably **not** the NFC
  chip → candidate for **external SPI flash** (F-16).
  → **Test:** M-012 item 9 (SO-8 pins → EFR32 / GND / VDD).

### LEDs
- `[PHOTO]` The upper LED on the bottom edge has several pads; three of them
  go via short traces to three vias; on the top, three traces continue from
  there towards the EFR32 / SO-8 area. The lower (white) LED's routing is
  not clear on the photos.
  → **Test:** M-012 item 8.

### Test points
- `[PHOTO]` The bottom side has many **exposed silver vias** among the tented
  ones. The capture wires for FPC 9–14 and GND all sit on such vias.
  `[ASSUMPTION]` They are production test points — the best places to
  probe or solder for further nets.

---

## Photo guidelines for the next round (2026-09-24)

Maintainer: a flatbed scan does not work — the components hold the board
too far from the glass. Better camera photos instead.

- **Transfer caveat (2026-09-24):** images pasted into the chat can arrive
  **downscaled** — the ruler photos came in at 2000 × 1500 WebP instead of
  ~3000 × 2300. Earlier photos (e.g. the EFR32 macro) arrived at full
  resolution. Check the size reported back; if in doubt, attach the file
  itself or pack the originals into a ZIP.
- **Resolution is not the limit on my side:** images are processed at full
  resolution with code (cropping, registration); only the preview I look at
  is downscaled. Send **original files, not resized** (JPEG at highest
  quality or PNG/TIFF). A 5953 × 5004 px / 3.5 MB JPEG worked; the upload
  limit of the chat is not known.
- **Target: ≥ 50 px per mm** on the board (a 0.1 mm trace ≈ 5 px). For the
  ~110 × 75 mm board that means **tiles**: 2 × 2 per side, **~30 % overlap**,
  each tile containing at least one hole or large via as a reference.
- Extra macro of the EFR32 area on **both sides** at ≥ 100 px/mm.
- **Camera perpendicular** to the board (tripod or fixed stand), same
  distance for all tiles; no zoom change between tiles.
- **Diffuse light** from two sides; avoid glare on the solder mask. One
  extra set with **low-angle light** makes traces under the mask stand out.
- A **ruler** in one tile per side gives the scale.
- Remove the capture wires if possible, or photograph once with and once
  without.

## What would make a real schematic possible

Phone photos (perspective, glare, shadows) limit this. A **flatbed scan of
both sides at 600–1200 dpi** would give an orthographic, evenly lit image
with a known scale — traces and pads could then be followed pad by pad,
and the two sides registered to ~0.1 mm. Components stay on; lay the board
on the glass with a sheet of paper behind it.
