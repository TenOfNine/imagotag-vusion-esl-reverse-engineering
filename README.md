# ESL E-Ink Reverse Engineering

Reverse Engineering eines **VusionGroup / SES-imagotag** Electronic Shelf Label,
um das verbaute (vermutlich dreifarbige) E-Ink-Panel unter eigener Kontrolle anzusteuern.

```
Platine   RFRTx026D  (imagotag, 2,4 GHz)
MCU       Silicon Labs EFR32FG22  (Marking: FG22 / C121GG / C026ZX / 2419)
Panel     E Ink EL074TS1, ca. 170 × 112 mm, vermutlich dreifarbig (S/W/Rot, unbestätigt)
Interface 24-poliger FPC, 0,5 mm Raster
```

---

## Warum es dieses Repo gibt

Zu diesem Panel gibt es **kein öffentliches Datenblatt**. ESL-Panels laufen
unter NDA an OEMs; weder Pinbelegung noch Auflösung, Controller-Typ oder
Waveform sind dokumentiert.

Der Weg dorthin führt deshalb über den Mitschnitt: Das Originaltag zeichnet
beim Einlegen der Batterie ein Bild. Dieser Refresh wird auf dem SPI-Bus
mitgeschnitten und daraus die Init-Sequenz, die Geometrie und der
Controller-Typ rekonstruiert.

---

## Zwei mögliche Endziele

| Weg | Ergebnis | Aufwand |
|---|---|---|
| **A — Originalplatine als Trägerboard** | EFR32 stilllegen, eigenen ESP32 an den vorhandenen ZIF-Stecker. Boost-Beschaltung bleibt erhalten. | mittel |
| **B — OpenEPaperLink-Port** | EFR32 neu flashen. Tag bleibt batteriebetrieben und funkt drahtlos. | hoch, aber elegant |

Beide Wege brauchen dieselbe Vorarbeit: **den Mitschnitt**. Deshalb ist die
Entscheidung noch offen und wird erst getroffen, wenn die Init-Sequenz
vorliegt.

---

## Aktueller Stand

Siehe `HISTORY.md` für den vollständigen Verlauf und
`docs/open-questions.md` für das, was noch offen ist.

Kurzfassung: Hardware ist identifiziert, **es wurde noch nichts gemessen**.
Der nächste Schritt ist der erste Mitschnitt nach
`docs/capture-protocol.md`.

---

## Einstieg für Claude Code

1. `CLAUDE.md` lesen — Arbeitsregeln, besonders die Evidenz-Kennzeichnung
2. `HISTORY.md` lesen — was bisher geschah
3. `docs/open-questions.md` lesen — woran gearbeitet wird
4. `TOOLS.md` lesen — was an Messtechnik da ist

**Wichtig:** Claude Code hat keinen Hardwarezugriff. Fehlende Messwerte
werden als Messauftrag in `docs/measurement-requests.md` formuliert, nicht
geschätzt.

---

## Einstieg für den Maintainer

Der nächste konkrete Schritt steht immer oben in
`docs/measurement-requests.md`.

Mitschnitte landen in `captures/`, Messwerte in `hardware/measurements.md`.

---

## Auswertung

```bash
python3 analysis/decode_spi.py captures/<datei>.csv --sck D0 --mosi D1 --cs D2 --dc D3
```

Der Decoder zerlegt den Mitschnitt in Kommandos und Datenblöcke, ermittelt
die Blocklängen und leitet daraus Kandidaten für die Panelauflösung ab.
Details in `analysis/README.md`.

---

## Lizenz

Noch nicht festgelegt. Die Mitschnitte und Analysen sind eigene Arbeit;
Firmware-Images oder Herstellerdokumente gehören **nicht** in dieses Repo.
