# Photos

| File | Content |
|---|---|
| `panel-label-el074ts1.webp` | panel back side with type designation `EL074TS1` |
| `panel-fpc-overview.webp` | FPC with the test points `TP1`–`TP3` |
| `pcb-top-overview.webp` | complete board top side, with QR code |
| `pcb-top-zif-powerstage.webp` | ZIF connector and boost circuitry, sharp |
| `pcb-top-mcu.webp` | EFR32FG22 with marking, both crystals, NFC IC |
| `pcb-bottom.webp` | back side: NFC coil, LEDs, open vias |
| `pcb-top-annotated-pinout.webp` | top side with **hypothetical** pinout |
| `nfc-read-tag02-nfctools.png` | phone screenshot (NFC Tools PRO), NFC read of the tag, 2026-09-23 23:54 (M-010) |
| `pcb-bottom-capture-wiring-v2.webp` | tag 02 back side, current capture wiring (2026-09-23 night): black GND, white pin 9, grey 10, purple 11, blue 12, green 13, yellow 14 (maintainer statement) |
| `pcb-top-mcu-macro.webp` | EFR32FG22 macro (QFN40, 10 pads per side), crystals, `8K417` SO-8, boost diodes (2026-09-23) |
| `pcb-bottom-capture-wiring.webp` | tag 02 back side, 2026-09-23: seven wires soldered to vias for the capture (M-004/M-007). Colour → channel mapping not yet stated |

---

## ⚠ About the annotated image

`pcb-top-annotated-pinout.webp` shows the 24 contacts with the
**Waveshare standard** overlaid as a working hypothesis.

**The only things measured on it are:** contact count (24), pitch (0.5 mm)
and the position of inductor, MOSFET, HV capacitors and battery contact.

**Not measured are:** all signal names and the counting direction on the
board. The image serves as a shared coordinate system ("pin 12"), not as a
wiring template.

After M-001 is complete it will be replaced by a measured version.

---

## Requested additional photos

For a usable annotation of the back side, still missing:

- camera **perpendicular** above the board, parallel to the surface
- **diffuse light** (window without direct sun, or paper as a diffuser)
- additionally a **macro** of just the area around the four open vias
- a **macro** of the QFN package, sharp enough to count pads (→ M-003)
