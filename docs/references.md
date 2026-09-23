# Sources

Everything that has been researched. `[RESEARCH]` markers in other
documents refer to here.

---

## Silicon Labs EFR32FG22

- **EFR32FG22 Wireless Gecko SoC Family Data Sheet**
  https://www.silabs.com/documents/public/data-sheets/efr32fg22-datasheet.pdf
  → Order codes, package variants, pinout, clock sources.
  Relevant: `EFR32FG22C121F512GM40-C` (QFN40, 26 GPIO) vs.
  `EFR32FG22C121F512GM32-C` (QFN32, 18 GPIO).

- **Simplicity Commander**
  https://www.silabs.com/developers/simplicity-studio/simplicity-commander
  → Tool for `device info`, `security status`, `device unlock`.
  Supports J-Link only.

---

## OpenEPaperLink

- **Project page** — https://openepaperlink.de/
- **Tag_FW_EFR32xG22** — https://github.com/OpenEPaperLink/Tag_FW_EFR32xG22
  → Firmware for EFR32xG22-based tags. Supports Solum M3 (autodetect)
  and Pricer HD150 (via modchip). **No Vusion port.**
  Contains the note that unlocking factory-locked devices requires a
  J-Link-based debugger and that the unlock erases the original firmware.
- **Wiki: Flashing SiLabs-based M3/Newton Displays**
  https://github.com/OpenEPaperLink/OpenEPaperLink/wiki/Flashing-SiLabs-based-M3-Newton-Displays
- **Issue #358** — custom ESL with ESP32 and 7.5" display
  https://github.com/OpenEPaperLink/OpenEPaperLink/issues/358

---

## Prior work on Imagotag hardware

⚠ **All for other, older hardware.** Methodologically useful, not directly
transferable to `RFRTx026D`.

- **Jirka Balhar — Hacking SES imagotag E-ink Price Tag**
  https://blog.jirkabalhar.cz/2023/12/hacking-sesimagotag-e-ink-price-tag/
  → Vusion 2.6 BWR GU140, CC2510. Very good description of the methodical
  approach, including the search for the panel type designation.
- **BeatSkip — SES-Imagotag-UU340**
  https://github.com/BeatSkip/SES-Imagotag-UU340
  → AX8052-based variant of the Vusion 2.6 BWR.
- **Hackaday — Driving Three-Color E-Paper Pricetags With An Arduino**
  https://hackaday.com/2022/10/28/driving-three-color-e-paper-pricetags-with-an-arduino/
  → Describes exactly the strategy chosen here: capture the protocol, then
  remove one of the microcontrollers and replace it with an ESP32.
- **Epongenoir — Reverse engineering a Imagotag retail 2.6 RED NFC**
  https://epongenoir.blogspot.com/2017/07/reverse-engineering-imagotag-retail-26.html
- **Furrtek — Reverse-engineering infrared-based electronic shelf labels**
  https://www.furrtek.org/?a=esl
  → Different system (IR), but a good overview of the ESL infrastructure.

---

## Standard 24-pin e-paper pinout

Three independent sources, consistent:

- **Waveshare E-Paper Driver HAT Schematic**
  https://files.waveshare.com/upload/8/87/E-Paper-Driver-HAT-Schematic.pdf
- **Electronic Assembly ePaper 2.0" with SSD1606**
  https://docs.rs-online.com/4fa6/0900766b81607b97.pdf
- **Midas MDE0154A152152RBW Specification**
  https://www.farnell.com/datasheets/2693678.pdf

In addition, on the contact-side issue:

- **Tindie — Display driver board for epaper shelf label**
  https://www.tindie.com/products/electronics-by-nic/display-driver-board-for-epaper-shelf-label/
  → "These Electronic Shelf Label displays have the copper contacts of the
  FPC Connector at the bottom of the cable (in contrast with Waveshare
  epaper displays, who have the exposed copper contacts at the top)."

---

## Instruments

- **Sipeed Wiki — SLogic Combo 8, Using as a Logic Analyzer**
  https://wiki.sipeed.com/hardware/en/logic_analyzer/combo8/use_logic_function.html
  → Rate limits per OS, GND routing, D7 inversion bug.
- **Product data SLogic Combo 8**
  https://www.youyeetoo.com/products/usb-logic-analyser-slogic-combo-8
  → Input range 0–3.6 V, VIH > 2 V, VIL < 0.8 V, streaming mode.
- **OWON HDS242 — retailer listings**
  https://vishaworld.com/products/owon-hds242-handheld-digital-oscilloscope-bandwidth-40-mhz-2-channel-sample-rate-250-msa-s-single-channel-125-msa-s-dual-channel
  https://toolboom.com/en/handheld-digital-oscilloscope-owon-hds242/
  → 2 channels, 40 MHz, 250/125 MSa/s, 8 k record length, multimeter with
  continuity.

---

## Manufacturer / product family

- **VusionGroup (formerly SES-imagotag)** — https://www.vusion.com/
- **SES-imagotag VUSION ESL — Product Overview and Specifications**
  → 2.4 GHz, sizes 1.6" to 12.2", B/W/red or yellow.
- **Wikipedia — VusionGroup**
  https://en.wikipedia.org/wiki/VusionGroup
  → Renamed from SES-imagotag in 2024; BOE Technology holds 79.94 %.

---

## Not found

- **Datasheet `EL074TS1`** — does not exist publicly. Searched directly for
  the type designation as well as via E Ink and distributor catalogues.
  ESL panels are supplied to OEMs under NDA.
- **Schematic or documentation for `RFRTx026D`** — not public.
