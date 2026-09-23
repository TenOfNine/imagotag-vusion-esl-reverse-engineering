# firmware — noch leer

Hier entsteht der Treibercode, **sobald der Mitschnitt vorliegt**.

Vorher ist hier nichts zu tun. Ein Treiber auf Basis einer ungeprüften
Pinbelegung wäre Zeitverschwendung im besten und Hardwareschaden im
schlechtesten Fall.

---

## Geplante Struktur, je nach Weg

### Weg A — ESP32 am Trägerboard

```
firmware/
  esp32-epd/
    platformio.ini
    src/
      main.cpp
      epd_el074ts1.h     aus analysis/*_init_sequence.py abgeleitet
      epd_el074ts1.cpp
```

Ansatz: die mitgeschnittene Init-Sequenz 1:1 nachspielen. Erst wenn ein
Bild erscheint, auf GxEPD2 umstellen — falls der Controller dort überhaupt
unterstützt wird.

Benötigte Leitungen: `3V3, GND, SCK, MOSI, CS, D/C, RST, BUSY`

### Weg B — OpenEPaperLink-Port

```
firmware/
  oepl-rfrtx026d/
    README.md            Portierungsnotizen
    patches/             Diff gegen Tag_FW_EFR32xG22
```

Basis: https://github.com/OpenEPaperLink/Tag_FW_EFR32xG22

Zu tun wäre: Board-Definition für `RFRTx026D` anlegen, GPIO-Mapping aus
M-001/M-002 eintragen, EPD-Treiber für `EL074TS1` ergänzen.

---

## Reihenfolge

1. Mitschnitt auswerten → Controller und Auflösung stehen fest
2. Entscheidung Weg A oder B (→ `docs/open-questions.md`, F-09)
3. **Dann** hier anfangen

---

## Was hier nicht hingehört

- Ausgelesene Original-Firmware-Images (urheberrechtlich geschützt)
- Herstellerdokumente unter NDA
