# Quellen

Alles, was recherchiert wurde. Bei `[RECHERCHE]`-Markern in anderen
Dokumenten hierher verweisen.

---

## Silicon Labs EFR32FG22

- **EFR32FG22 Wireless Gecko SoC Family Data Sheet**
  https://www.silabs.com/documents/public/data-sheets/efr32fg22-datasheet.pdf
  → Bestellcodes, Gehäusevarianten, Pinout, Taktquellen.
  Relevant: `EFR32FG22C121F512GM40-C` (QFN40, 26 GPIO) vs.
  `EFR32FG22C121F512GM32-C` (QFN32, 18 GPIO).

- **Simplicity Commander**
  https://www.silabs.com/developers/simplicity-studio/simplicity-commander
  → Werkzeug für `device info`, `security status`, `device unlock`.
  Spricht ausschließlich J-Link.

---

## OpenEPaperLink

- **Projektseite** — https://openepaperlink.de/
- **Tag_FW_EFR32xG22** — https://github.com/OpenEPaperLink/Tag_FW_EFR32xG22
  → Firmware für EFR32xG22-basierte Tags. Unterstützt Solum M3 (autodetect)
  und Pricer HD150 (per Modchip). **Kein Vusion-Port.**
  Enthält den Hinweis, dass zum Entsperren werksseitig gesperrter Geräte ein
  J-Link-basierter Debugger nötig ist und das Unlock die Originalfirmware
  löscht.
- **Wiki: Flashing SiLabs-based M3/Newton Displays**
  https://github.com/OpenEPaperLink/OpenEPaperLink/wiki/Flashing-SiLabs-based-M3-Newton-Displays
- **Issue #358** — Custom ESL mit ESP32 und 7,5"-Display
  https://github.com/OpenEPaperLink/OpenEPaperLink/issues/358

---

## Vorarbeiten an Imagotag-Hardware

⚠ **Alle für andere, ältere Hardware.** Methodisch nützlich, nicht direkt
übertragbar auf `RFRTx026D`.

- **Jirka Balhar — Hacking SES imagotag E-ink Price Tag**
  https://blog.jirkabalhar.cz/2023/12/hacking-sesimagotag-e-ink-price-tag/
  → Vusion 2.6 BWR GU140, CC2510. Sehr gute Beschreibung des methodischen
  Vorgehens inkl. der Suche nach der Panel-Typenbezeichnung.
- **BeatSkip — SES-Imagotag-UU340**
  https://github.com/BeatSkip/SES-Imagotag-UU340
  → AX8052-basierte Variante der Vusion 2.6 BWR.
- **Hackaday — Driving Three-Color E-Paper Pricetags With An Arduino**
  https://hackaday.com/2022/10/28/driving-three-color-e-paper-pricetags-with-an-arduino/
  → Beschreibt genau die hier gewählte Strategie: Protokoll mitschneiden,
  dann einen der Mikrocontroller entfernen und durch einen ESP32 ersetzen.
- **Epongenoir — Reverse engineering a Imagotag retail 2.6 RED NFC**
  https://epongenoir.blogspot.com/2017/07/reverse-engineering-imagotag-retail-26.html
- **Furrtek — Reverse-engineering infrared-based electronic shelf labels**
  https://www.furrtek.org/?a=esl
  → Anderes System (IR), aber gute Übersicht über die ESL-Infrastruktur.

---

## 24-Pin E-Paper Standardbelegung

Drei unabhängige Quellen, übereinstimmend:

- **Waveshare E-Paper Driver HAT Schematic**
  https://files.waveshare.com/upload/8/87/E-Paper-Driver-HAT-Schematic.pdf
- **Electronic Assembly ePaper 2.0" mit SSD1606**
  https://docs.rs-online.com/4fa6/0900766b81607b97.pdf
- **Midas MDE0154A152152RBW Specification**
  https://www.farnell.com/datasheets/2693678.pdf

Zusätzlich zur Kontaktseiten-Problematik:

- **Tindie — Display driver board for epaper shelf label**
  https://www.tindie.com/products/electronics-by-nic/display-driver-board-for-epaper-shelf-label/
  → „These Electronic Shelf Label displays have the copper contacts of the
  FPC Connector at the bottom of the cable (in contrast with Waveshare
  epaper displays, who have the exposed copper contacts at the top)."

---

## Messtechnik

- **Sipeed Wiki — SLogic Combo 8, Using as a Logic Analyzer**
  https://wiki.sipeed.com/hardware/en/logic_analyzer/combo8/use_logic_function.html
  → Ratenlimits pro OS, GND-Führung, D7-Inversionsbug.
- **Produktdaten SLogic Combo 8**
  https://www.youyeetoo.com/products/usb-logic-analyser-slogic-combo-8
  → Eingangsbereich 0–3,6 V, VIH > 2 V, VIL < 0,8 V, Streaming-Modus.

---

## Hersteller / Produktfamilie

- **VusionGroup (ehem. SES-imagotag)** — https://www.vusion.com/
- **SES-imagotag VUSION ESL — Product Overview and Specifications**
  → 2,4 GHz, Größen 1,6" bis 12,2", S/W/Rot bzw. Gelb.
- **Wikipedia — VusionGroup**
  https://en.wikipedia.org/wiki/VusionGroup
  → 2024 Umbenennung von SES-imagotag; BOE Technology hält 79,94 %.

---

## Nicht auffindbar

- **Datenblatt `EL074TS1`** — existiert nicht öffentlich. Gesucht wurde
  direkt nach der Typenbezeichnung sowie über E-Ink- und
  Distributorenkataloge. ESL-Panels laufen unter NDA an OEMs.
- **Schaltplan oder Doku zu `RFRTx026D`** — nicht öffentlich.
