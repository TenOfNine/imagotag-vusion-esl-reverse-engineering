# Capture-Protokoll — SPI-Mitschnitt des Panel-Refresh

Der zentrale Arbeitsschritt des Projekts. Aus diesem Mitschnitt fallen
Controller-Typ, Auflösung, Init-Sequenz und ggf. die Waveform-LUT auf einmal ab.

> **Voraussetzung:** Messauftrag **M-001** (`pinout.md`) ist abgeschlossen.
> Ohne bestätigte Pinbelegung wird nichts angeklemmt.

---

## 0. Sicherheit zuerst

- Am FPC liegen im Betrieb ca. **+22 V und −20 V** — der SLogic verträgt
  max. **3,6 V**.
- Nur an Pins klemmen, die als **MCU-verbunden verifiziert** sind.
- Das Tag läuft auf ca. 3 V. Das passt, hat aber **null Reserve** nach oben.

---

## 1. Abgriff herstellen

Zwei Wege, in dieser Reihenfolge:

### A — FPC-Verlängerung einschleifen (bevorzugt, lötfrei)

24-poliges FPC-Verlängerungsset (Adapter + Kabel, 0,5 mm) zwischen Panel und
Platine. Liefert 2,54-mm-Testpunkte ohne einen einzigen Lötpunkt.

**Kabeltyp beachten:** A-A oder A-B, je nachdem auf welcher Seite die
Kontakte des Original-FPC liegen. Siehe `pinout.md`, Abschnitt
„Hinweis zur Kontaktseite".

### B — An die Durchkontaktierungen löten

Die Vias in der Auffächerung rechts des Steckers sind mit ca. 0,3 mm
deutlich dankbarer als die Pads selbst.

- 0,1 mm Kupferlackdraht
- Drähte **kurz halten** (< 10 cm)
- **Mindestens zwei GND-Leitungen** zum Analyzer

---

## 2. Kanalbelegung

| Kanal | Signal |
|---|---|
| D0 | SCK |
| D1 | SDI / MOSI |
| D2 | CS |
| D3 | D/C |
| D4 | BUSY |
| D5 | RST |
| D6 | frei |
| D7 | **auf GND legen** |

**D7 nicht offen lassen** — bekannter SLogic-Bug: unbenutztes D7 kann eine
Pegelinversion zeigen (siehe `TOOLS.md`).

**Das Panel muss angesteckt bleiben.** Ohne Panel verhält sich BUSY anders
und das Tag bricht den Refresh womöglich ab.

---

## 3. Aufnahme

### Durchgang A — Übersicht

| Einstellung | Wert |
|---|---|
| Kanäle | 8 |
| Samplerate | **2 MSa/s** |
| Dauer | ca. 60 s |
| Datenmenge | ca. 120 MB |

Ziel ist **nicht** das Dekodieren, sondern die Orientierung:

- Wie schnell taktet SCK tatsächlich?
- Wo im Zeitstrahl liegt der Reset, wo der Datenblock?
- Wie lange hängt BUSY?

### Durchgang B — Nutzdaten

| Einstellung | Wert |
|---|---|
| Kanäle | 8 |
| Samplerate | **20 MSa/s** (Windows) bzw. **40 MSa/s** (Linux) |
| Dauer | 30–60 s |
| Datenmenge | ca. 600 MB bzw. 1,2 GB |

**Faustregel:** mindestens 5× SCK, besser 10×. Nach Durchgang A ist die
tatsächliche SCK-Frequenz bekannt — danach richten.

PulseView hält alles im RAM. Vorher genug frei machen.

---

## 4. Refresh auslösen

1. Aufnahme **starten**
2. **Dann** Batterie einlegen

Das Tag funkt typischerweise erst ein paar Sekunden und zeichnet den Screen
danach. Deshalb die Aufnahme vorher starten.

### Wenn nichts passiert

- Batterie 30 s draußen lassen (Elkos entladen), erneut versuchen
- Anderes Tag probieren
- **Plan B:** Refresh über NFC auslösen. Auf der Platine sitzt ein
  NFC-Frontend mit Antennenspule (siehe `hardware.md`). Ein NFC-fähiges
  Telefon in Reichweite kann das Tag unter Umständen aufwecken.

---

## 5. Erwartete Größenordnungen

Zur Plausibilitätskontrolle, damit ein Fehlschlag früh auffällt:

| Größe | Erwartung |
|---|---|
| SPI-Takt | 1 – 4 MHz (typisch bei E-Paper) |
| SPI-Modus | Mode 0 (CPOL=0, CPHA=0), MSB first, CS active low |
| Nutzdaten bei 800×480, 2 Ebenen | ca. 96 kB |
| Reine Übertragungszeit dafür bei 2 MHz | ca. 0,4 s |
| Gesamtdauer Refresh (dreifarbig) | **15 – 30 s** |

Der Löwenanteil der Zeit ist **Warten auf BUSY**, nicht Datenübertragung.

---

## 6. Export und Ablage

Aus PulseView exportieren als **CSV, alle 8 Kanäle, roh** —
nicht die Decoder-Ausgabe.

Ablage in `captures/` nach dem Schema:

```
YYYY-MM-DD_<tag-id>_<zweck>_<rate>.csv
```

Beispiel: `2026-09-25_tag03_boot-refresh_20MHz.csv`

Zusätzlich die native `.sr`-Datei aufheben, falls vorhanden — sie ist
verlustfrei und deutlich kompakter.

---

## 7. Auswertung

```bash
python3 analysis/decode_spi.py captures/<datei>.csv \
    --sck D0 --mosi D1 --cs D2 --dc D3 --busy D4 --rst D5
```

Siehe `analysis/README.md`.

---

## 8. Danach: Eintrag in HISTORY.md

Pflicht, auch bei Fehlschlag. Format siehe Vorlage am Ende von `HISTORY.md`.
