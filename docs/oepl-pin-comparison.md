# OpenEPaperLink pin maps vs. our board

Status 2026-09-25. Question from the maintainer: does one of the EFR32
board definitions in OpenEPaperLink match our `RFRTx026D` layout?

**Short answer: no.** None of the OEPL display pin maps fits the photo
evidence (the display bundle ends on the chip's left pad column). A board
definition of our own is needed. Everything below is `[RESEARCH]`,
`[PHOTO]` or `[ASSUMPTION]` — no pad of our board is measured yet.

---

## 1. Source: OEPL board table

`[RESEARCH]` `firmware/oepl_efr32_hwtypes.c` in
https://github.com/OpenEPaperLink/Tag_FW_EFR32xG22 (commit `ecd2915`,
read 2026-09-25). Four configurations exist:

| Signal | Solum M3 (autodetect) | Modchip HD150 | BRD4402B + EPD (dev kit) |
|---|---|---|---|
| SPI USART | USART1 | USART1 | USART1 |
| MOSI / SDA | PA03 | PA04 | PA05 |
| SCK | PA04 | PB00 | PA06 |
| nCS | PB00 | PA00 (nCS2 PA03) | PB03 |
| D/C | PA06 | PD01 | PD02 |
| BUSY | PA08 | PB02 | PB02 |
| nRST | PA07 | PD00 | PC03 |
| panel enable | PA00 (idle low) | PA06 (idle low) | — |
| MISO | unused | unused | unused |
| SPI flash (USART0) | PC00 MISO, PC01 MOSI, PC02 SCK, PC03 nCS | same as Solum | PC00/01/02/04 |
| LEDs | PC05 blue, PC06 red, PC07 green | — | PD03 |
| NFC | I2C0 SDA PD03, SCL PD01, power PD00, field detect PD02 | — | — |
| UART debug | TX PB02, RX PB03 | TX PA05 | PA05/PA06 |

The BRD4402B memory-LCD config is left out (not an e-paper panel).

## 2. GPIO → QFN40 package pin

`[RESEARCH]` **Weak source.** silabs.com and the datasheet mirrors are
blocked for this environment, so the EFR32xG22 datasheet PDF itself was
**not** opened. The mapping below comes from web-search result snippets
(2026-09-25) that quote the EFR32BG22 datasheet / Silicon Labs radio-board
schematics (BRD4182A, BRD4184B), and is consistent with the earlier
snippet PA01 = pin 22, PA02 = pin 23 (M-011):

| QFN40 pins | Function |
|---|---|
| 1–8 | PC00 … PC07 |
| 9 / 10 | HFXTAL_I / HFXTAL_O |
| 11 | RESETn |
| 12 / 13 / 14 | RF supply / RF ground / RF 2.4 GHz I/O (snippet) |
| 16–20 | PB04 … PB00 (descending) |
| 21–29 | PA00 … PA08 |
| 30 | DECOUPLE (snippet) |
| 32 | VREGVDD (snippet) |
| 37–40 | PD03 … PD00 (descending) |
| 15, 31, 33–36 | not in the snippets |

**Test:** the maintainer checks this against the "QFN40 Device Pinout"
table of the EFR32FG22 datasheet
(https://www.silabs.com/documents/public/data-sheets/efr32fg22-datasheet.pdf).
It becomes usable only after that check. The snippets are for BG22;
`[ASSUMPTION]` FG22 in QFN40 has the same pinout.

## 3. What our board shows

- `[PHOTO]` `pcb-top-ruler.jpg`: the left pad column has 10 pads (pin-1
  dot top left). Pads **1–8** each have their own trace to the via field
  V1–V8 where the FPC 9–14 bundle ends. Pads **9–10** connect to
  the wide copper that leads down to the **38.4 MHz crystal** directly
  below the chip corner.
- That fits the table: pads 9/10 = HFXTAL_I/O, the crystal is the
  38.4 MHz HFXO. It is a **consistency check, not proof** of the table.

**If the table holds:** `[ASSUMPTION]` the eight traces are
**PC00–PC07**, and the six display lines (BUSY, RST, D/C, CS, SCK, SDA)
are six of them. The other two could be the panel supply switch (`XDt`
gate) or something else. → **Test:** M-012 items 1–7.

## 4. Comparison

| Board | Where the display lines are | Match with ours |
|---|---|---|
| Solum M3 | PA03/PA04/PA06/PA07/PA08/PB00 = pins 24/25/27/28/29/20 (right side and bottom) | **no** |
| Modchip HD150 | PA00/PA03/PA04/PA06, PB00/PB02, PD00/PD01 | **no** |
| BRD4402B EPD | PA05/PA06, PB02/PB03, PC03, PD02 | **no** |

On Solum, port C (pins 1–4) carries the **SPI flash** and PC05–PC07 the
LEDs. On our board the same pads apparently lead to the FPC. So our
layout is not a Solum clone. `[ASSUMPTION]` If `8K417` is a flash, it sits
on other pins, most likely on port A/B.

## 5. Consequences for the custom firmware (all `[ASSUMPTION]` until checked)

1. **New board entry needed** in `oepl_efr32_hwtypes.c` (a dev slot
   `0xF0…0xFA`, see `docs/firmware-plan.md`). The table structure fits:
   USART, MOSI/MISO/SCK/nCS/DC/BUSY/nRST/enable as port + pin.
2. **USART routing:** if the display is on port C, the USART has to be
   routable to port C. `[ASSUMPTION]` On EFR32xG22 only USART0 reaches
   ports C/D, USART1 only ports A/B → the display would need USART0.
   OEPL uses USART0 for the flash. If the flash is on other pins, it
   could go to USART1 or be bit-banged. **Test:** DBUS routing table in
   the EFR32FG22 datasheet / reference manual (not reachable from here).
3. **BUSY on port C cannot wake the chip from EM2.** `[RESEARCH]` OEPL
   comment in the Solum config: "Ports C and D are not available for IRQ
   generation in regular sleep." → poll BUSY, or keep the chip in EM1
   while waiting. Not critical, only costs power.
4. **3-wire SPI:** all OEPL configs have `MISO` unused (write only). Our
   original firmware reads from the panel over the bidirectional SDA line
   (`[CAPTURE]` boot sequence: `0x70`, `0x92`, `0xA2` reads). OEPL does
   not need reads to draw. For bring-up step 3 (replay of the boot
   reads), the SDA pin has to be switched to input for reads, or the
   USART has to be used in half-duplex mode.

## 6. Next steps

- Maintainer: check the table in section 2 against the datasheet.
- Maintainer: M-012 continuity FPC 9–14 → pads 1–8 (with an `XDt` gate
  check against the two remaining pads).
- Claude Code: after both, write the board entry.
