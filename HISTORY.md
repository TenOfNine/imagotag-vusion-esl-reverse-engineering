# HISTORY — Langzeitgedächtnis des Projekts

Chronologisches Protokoll aller Erkenntnisse, Versuche und Sackgassen.

**Regeln für diese Datei** (siehe auch `CLAUDE.md` §4):

- Neue Einträge werden **unten angehängt**, alte nie umgeschrieben.
- Eine Korrektur ist ein **neuer Eintrag mit Verweis** auf den alten.
- **Fehlschläge gehören rein.** Ein dokumentierter Irrweg verhindert, dass
  er wiederholt wird.
- Jede Tatsachenbehauptung trägt einen Evidenz-Marker:
  `[MESSUNG] [MITSCHNITT] [FOTO] [RECHERCHE] [ANNAHME] [WIDERLEGT]`

---

## 2026-09-22 — Session 1: Identifikation der Hardware

Ausgangspunkt: Der Maintainer hat mehr als fünf ausgemusterte ESL-Tags und möchte die
Panels mit eigenem ESP32 ansteuern. Erste Fotos von Panel und Platinenoberseite.

### Panel

- `[FOTO]` Panel trägt die Bezeichnung **`EL074TS1`** → E Ink, 7,4 Zoll.
- `[MESSUNG]` Maintainer: Außenmaße ca. **170 × 112 mm**. Passt zum üblichen
  7,x-Zoll-Rohpanel-Umriss.
- `[MESSUNG]` Maintainer: Panel ist **dreifarbig** (Schwarz/Weiß/Rot).
- `[RECHERCHE]` Zu `EL074TS1` ist **kein öffentliches Datenblatt auffindbar.**
  Gesucht wurde direkt nach der Typenbezeichnung sowie über E-Ink- und
  Distributorenkataloge. ESL-Panels werden unter NDA an OEMs geliefert.
  → Das ist die zentrale Hürde des Projekts.
- `[FOTO]` Auf dem FPC sind drei Testpunkte **`TP1`, `TP2`, `TP3`**
  aufgedruckt. Funktion unbekannt.

### Platine

- `[FOTO]` Bedruckung: **`imagotag  RFRTx026D`**, dazu `2,4 GHz`,
  `315 17 94V-0`, `13`, Lagenbezeichnungen `1 TOP` / `2 BOT`.
- `[MESSUNG]` QR-Code auf der Platine dekodiert zu
  `060RFRTX026D00A120O262007587`.
- `[MESSUNG]` QR-Code auf dem Panel dekodiert zu `H7FZDSPQ0KXYZ5V00DAUAT`.
  → Beides Seriennummern, **kein technischer Zusatznutzen**. Sackgasse.

### MCU

- `[FOTO]` QFN-Marking: **`FG22 / C121GG / C026ZX / 2419`**
  → **Silicon Labs EFR32FG22**, Datumscode KW19/2024.
- `[RECHERCHE]` Die Variante `C121` gibt es in zwei Gehäusen:
  QFN40 mit 26 GPIO und QFN32 mit 18 GPIO. Beide: Proprietary 2,4 GHz,
  6 dBm, 512 kB Flash, 32 kB RAM, ARM Cortex-M33, max. 38,4 MHz.
  Quelle: EFR32FG22 Family Data Sheet.
- `[ANNAHME]` Gehäuse ist **QFN40** (`EFR32FG22C121F512GM40`), abgeleitet aus
  ca. 10 sichtbaren Pads pro Seite im Foto.
  → **Prüfung:** Pads pro Seite unter Lupe nachzählen. 10/Seite = QFN40,
  8/Seite = QFN32.
- `[FOTO]` Zwei Quarze: **38,4 MHz** (Marking `38.4 T4F`, HFXO) und
  **32,768 kHz** (Marking `T422C`, LFXO). Die 38,4 MHz passen exakt zum
  Referenztakt der EFR32-Serie.

### Weitere Bauteile

- `[FOTO]` SO-8 mit Marking **`8K417 / 0E47AH`**.
  `[ANNAHME]` NFC-Frontend, da auf der Rückseite eine NFC-Antennenspule sitzt.
  → **Prüfung:** Durchgang von diesem IC zur Spule messen.
- `[FOTO]` Boost-Beschaltung rechts des ZIF-Steckers: Speicherdrossel,
  SOT-23-MOSFET (Marking `KM`), mehrere Schottky-Dioden (`4`, `BR`, `ZV`),
  dicke MLCCs.
  → Entspricht dem Standardmuster für einen E-Ink-COG mit integriertem DC/DC.
- `[FOTO]` Weitere SOT-23: `S21`, `XDt`, `T0.`, `1R.` — Funktion ungeklärt.

### FPC-Stecker

- `[FOTO]` **24 Kontakte, 0,5 mm Raster.** Ermittelt per Farbsegmentierung
  und FFT-Periodenanalyse an zwei unabhängigen Fotos, Ergebnis konsistent.
  Entspricht dem De-facto-Standard bei E-Paper.

### Recherche zum Ökosystem

- `[RECHERCHE]` Die VUSION-Familie (2,4 GHz) gibt es von 1,6" bis 12,2" in
  Schwarz/Weiß/Rot bzw. Gelb.
- `[RECHERCHE]` Es existieren mehrere dokumentierte Imagotag-Hacks, aber alle
  für **ältere, andere Hardware**: CC2510-basierte Vusion 2.2/2.6 BWR,
  AX8052-basierte UU340. Keiner davon passt auf `RFRTx026D`.
  → Diese Arbeiten sind methodisch nützlich, nicht direkt übertragbar.
- `[RECHERCHE]` **OpenEPaperLink** hat eine Firmware für EFR32xG22-basierte
  Tags (`Tag_FW_EFR32xG22`). Unterstützt werden bisher **Solum M3** und
  **Pricer HD150** (letzterer per Modchip). Kein Vusion-Port vorhanden.
  → Damit wäre Weg B ein **Portierungs-**, kein Neuentwicklungsprojekt.
- `[RECHERCHE]` Debug-gesperrte EFR32xG22 lassen sich entsperren, solange
  „unauthenticated debug unlock" nicht deaktiviert wurde. **Das Unlock löscht
  die Originalfirmware.** Empfohlenes Werkzeug: Simplicity Commander mit
  J-Link-basiertem Debugger.
  → Daraus folgt die Reihenfolge: **erst sniffen, dann unlocken.**

---

## 2026-09-22 — Session 1: Strategiewechsel

**Ursprünglicher Plan:** Panel vom Originalboard trennen, an ein
Waveshare-Treiberboard hängen.

**Verworfen**, weil: Die Originalplatine enthält die komplette, korrekt
dimensionierte Boost-Beschaltung für VGH/VGL/VSH/VSL/VCOM. Genau dort
zerstört man beim Fremdadapter das Panel — vertauschte VGH/VGL (±20 V)
killen es sofort. Außerdem haben ESL-FPCs die Kupferkontakte typischerweise
auf der Gegenseite gegenüber Waveshare-Displays, was ein A-B-Wendekabel
nötig macht.

**Neuer Plan:** Originalplatine als Trägerboard behalten. Nur 8 Leitungen
zum ESP32 nötig: 3V3, GND, SCK, MOSI, CS, D/C, RST, BUSY.

Zum Stilllegen des EFR32 zwei Optionen, in dieser Reihenfolge:
1. **RESETn dauerhaft auf GND** — GPIOs gehen in Hi-Z, zerstörungsfrei,
   reversibel. Zuerst probieren.
2. QFN mit Heißluft entfernen — endgültig, aber bei >5 Tags vertretbar.

---

## 2026-09-22 — Session 1: Randbedingungen des Maintainers

- `[MESSUNG]` Maintainer besitzt **mehr als 5 Tags**.
- Maintainer: Originalplatine darf geopfert werden.
- Maintainer: Zielsetzung noch offen zwischen „genau dieses Panel ansteuern" und
  „schnell ein E-Ink-Dashboard".
- `[MESSUNG]` Messtechnik vorhanden: **Sipeed SLogic Combo 8** (mit PulseView),
  **SEGGER J-Link**, FTDI-USB-Seriell-Adapter. Details in `TOOLS.md`.

### Klärung zum FTDI

Der Maintainer fragte, ob der FTDI-Adapter für den JTAG-Part genügt.

- `[RECHERCHE]` **Nein.** Erstens kann EFR32 Series 2 ausschließlich **SWD,
  kein JTAG**. Zweitens beherrschen nur FTDI-Chips mit MPSSE-Engine
  (FT2232H, FT232H, FT4232H) überhaupt SWD via OpenOCD, und das nur mit
  Widerstandstrick zwischen TDI und TDO. Klassische FT232R/FT231X können
  nur UART.
- `[RECHERCHE]` Selbst mit FT2232H bleibt das Problem: Das Unlock läuft bei
  Series 2 über den **Authentication Access Port der Secure Engine**.
  Simplicity Commander spricht dafür ausschließlich J-Link.
  → Hinfällig, da ein J-Link vorhanden ist.

---

## 2026-09-23 — Session 1: Rückseite der Platine

### Durchbruch bei der Zählrichtung

- `[FOTO]` Das **FPC ist selbst beschriftet**: am Kontaktende steht auf der
  einen Seite **`24`**, auf der anderen **`1`**.
  → Die Zählrichtung ist damit an der Quelle geklärt, keine Hypothese nötig.
- `[ANNAHME]` **Noch offen:** Welches Ende des Steckers auf der Platine Pin 1
  ist. Vorder- und Rückseite sind spiegelverkehrt; aus den bisherigen Fotos
  lässt sich das nicht zuordnen.
  → **Prüfung:** FPC einstecken und schauen, an welchem Ende die `1` sitzt.

### Weitere Beobachtungen Rückseite

- `[FOTO]` Große **NFC-Antennenspule** im oberen Bereich, mit
  handschriftlicher `0181` in der Mitte. Bestätigt indirekt den NFC-Chip.
- `[FOTO]` Zwei **LEDs** (eine klar, eine gelb) unten mittig — vermutlich die
  Locate-/Status-LEDs des Tags.
- `[FOTO]` `2 BOT` ist eine **Lagenbezeichnung**, kein Testpunkt.
- `[FOTO]` Die vier verlöteten Durchkontaktierungen unten links sind die
  **Lötstellen der Batterie-Federkontakte** von der Vorderseite.
  Keine Testpunkte. (Korrigiert eine frühere Vermutung des Maintainers.)
- `[ANNAHME]` **Vier offene, unbedeckte Vias** in der rechten Bildhälfte,
  links neben der `2 BOT`-Beschriftung: eines links, eines rechts, zwei dicht
  nebeneinander darunter, dazu eine größere Bohrung darüber.
  Anzahl und Anordnung passen zu **SWD** (SWDIO, SWCLK, GND, VDD, ggf. RESET).
  → **Prüfung:** Durchklingeln gegen Batterie-Minus, Batterie-Plus und die
  Port-A-Pins des FG22.

---

## Offener Faden am Ende von Session 1

Es wurde **noch nichts elektrisch gemessen**. Alle Pinbelegungen sind
Hypothesen auf Basis des Waveshare-Standards.

Nächster Schritt: Messauftrag **M-001** in `docs/measurement-requests.md`
(Durchklingeln des FPC-Steckers), danach der erste Mitschnitt nach
`docs/capture-protocol.md`.

## 2026-09-23 — Session 2: Übernahme in Claude Code

### Was versucht wurde
Projekt aus dem Claude-Chat nach Claude Code (Cloud-Session) übernommen.
Alle Dateien des Repos gelesen. Decoder mit dem synthetischen Mitschnitt
geprüft:

```bash
python3 analysis/make_testcapture.py <scratch>/fake.csv
python3 analysis/decode_spi.py <scratch>/fake.csv --busy D4 --rst D5 --out-prefix <scratch>/fake
```

Umgebung: Python 3.11, `numpy` und `pandas` mussten erst nachinstalliert
werden (im Repo nirgends als Abhängigkeit vermerkt).

### Ergebnis
- Decoder läuft fehlerfrei durch: 10 Transaktionen, Reset, BUSY-Phase 0,50 s,
  Fingerprint UC8179 66,7 %, zwei gleich große Blöcke à 2.400 Byte erkannt.
  Laufzeit ca. 12 s für 10,4 Mio. Samples.
  → Beweist nur, dass der Decoder seine eigene Testvorrichtung versteht.
  Über das echte Panel sagt das **nichts** aus.
- Auffällig am Testmitschnitt: `TRES` meldet `03 20 01 E0` (= 800 × 480),
  die Blöcke haben aber nur 2.400 Byte (= 19.200 Pixel). Der Decoder
  gleicht TRES und Blocklänge **nicht** gegeneinander ab. Beim echten
  Mitschnitt wäre genau dieser Abgleich ein starker Plausibilitätstest.
- Opcodes `0x15` und `0x60` werden im UC8179-Log ohne Klartext angezeigt.
- Offene Skalierungsfrage: Ein Durchgang B (40 MSa/s × 30–60 s) ergibt
  1,2–2,4 Mrd. Samples. Der Decoder lädt die CSV komplett über pandas —
  ob das im RAM des Maintainer-Rechners durchläuft, ist ungeprüft.

### Was daraus folgt
Keine neue Hardware-Erkenntnis. Stand unverändert: **nichts gemessen**,
M-001 bis M-003 offen.

### Nächster Schritt
Rückfragen an den Maintainer (Multimeter vorhanden? Betriebssystem für
PulseView? FPC-Verlängerung vorhanden?), danach M-001.

## 2026-09-23 — Session 2: Messtechnik geklärt

### Angaben des Maintainers
- Multimeter: **OWON HDS242** — Hand-Oszilloskop (2 Kanäle, 40 MHz) mit
  eingebautem Multimeter inkl. Durchgangsprüfer. Eckdaten `[RECHERCHE]`,
  Quellen in `TOOLS.md`.
- FTDI-Adapter: Angabe „FTDI1232". `[ANNAHME]` FT232R(L), also nur UART.
  → **Prüfung:** Chipaufdruck ablesen. Für das Projekt nicht kritisch.
- **Keine FPC-Verlängerung**, **keine Heißluftstation**, nur eine normale
  Lötstation.
- PulseView läuft unter **Windows**.

### Was daraus folgt
- M-001 bis M-003 sind mit dem HDS242 durchführbar.
- Mitschnitt nur über **Löten an die Vias** (Capture-Weg B).
- Samplerate-Obergrenze **20 MSa/s bei 8 Kanälen**. Bei SPI > 4 MHz auf
  4 Kanäle reduzieren.
- Mit dem Oszilloskop lassen sich **vor** dem Anklemmen des SLogic
  Logikpegel und SPI-Takt prüfen → neuer Abschnitt 2a in
  `docs/capture-protocol.md`. Das schützt den SLogic vor Pegeln > 3,6 V und
  deckt 1,8-V-Logik auf, die er nicht sehen würde.
- Auslöten des EFR32 (Weg A, Variante 2) ist ohne Heißluft **derzeit nicht
  durchführbar**. Bleibt nur RESETn auf GND (F-10).

---

## 2026-09-23 — Session 2: Korrektur von Evidenz-Markern aus Session 1

Korrigiert Einträge aus „Session 1: Identifikation der Hardware" und
„Session 1: Randbedingungen des Maintainers". Die alten Einträge bleiben
unverändert stehen.

- „Maintainer besitzt mehr als 5 Tags" und „Messtechnik vorhanden" waren
  als `[MESSUNG]` markiert. Das sind **Angaben des Maintainers**, keine
  Messungen. `CLAUDE.md` §3 hat dafür keinen eigenen Marker; sie werden ab
  hier als „Angabe des Maintainers" ohne Evidenz-Marker geführt.
- QR-Codes von Platine und Panel: als `[MESSUNG]` markiert. Wie sie
  dekodiert wurden (Scanner des Maintainers oder aus dem Foto), ist aus dem
  Repo nicht nachvollziehbar. Aus dem Foto wäre es `[FOTO]`.
  → **Offene Rückfrage an den Maintainer.**
- Außenmaße „ca. 170 × 112 mm" und „dreifarbig": als `[MESSUNG]` markiert,
  aber ohne Datum und Methode, die `CLAUDE.md` §3 verlangt.
  → **Offene Rückfrage:** Womit gemessen (Lineal, Messschieber)? Dreifarbig
  gesehen an einem angezeigten Bild?

---

## 2026-09-23 — Session 2: Decoder erweitert

### Was geändert wurde
- `analysis/requirements.txt` angelegt (`numpy`, `pandas`).
- `decode_spi.py` gleicht ein `0x61`-Kommando (TRES) jetzt gegen die
  Blocklängen ab. Zwei Payload-Layouts: 4 Byte (UC8179) und 3 Byte (IL0373).
  `[RECHERCHE]` Layouts aus dem Gedächtnis der Controller-Familien, nicht
  gegen ein Datenblatt im Repo geprüft.
- `decode_spi.py` lädt nur noch die benötigten Kanäle als `uint8`, statt
  alle Spalten als `int64`. Senkt den RAM-Bedarf grob um Faktor 10.

### Ergebnis
- Testmitschnitt: Transaktionslog, `_blocks.csv` und `_init_sequence.py`
  **bytegleich** zur Ausgabe vor der Änderung.
- Der TRES-Abgleich meldet beim Testmitschnitt korrekt `MISMATCH`
  (800 × 480 angekündigt = 48.000 Byte, Blöcke haben 2.400 Byte).
  Der Widerspruch steckt in `make_testcapture.py`, nicht im Decoder.

### Was es nicht beweist
Dass der Decoder einen echten PulseView-Export verarbeitet. Das zeigt erst
der erste echte Mitschnitt. Ein Durchgang B mit 20 MSa/s × 60 s braucht
auch nach der Änderung rund 7 GB RAM allein für die Rohdaten.

---

## 2026-09-23 — Session 2: Korrektur zu „Decoder erweitert"

Die TRES-Payload-Layouts (UC8179: 4 Byte, IL0373: 3 Byte) waren dort als
`[RECHERCHE]` markiert, ohne Quellenlink. Richtig ist `[ANNAHME]`.
→ **Prüfung:** Gegen die Datenblätter von UC8179 und IL0373 abgleichen,
oder beim echten Mitschnitt: Ergibt der Abgleich `MATCH`, stützt das das
verwendete Layout.

---

<!--
VORLAGE FÜR NEUE EINTRÄGE — kopieren und ausfüllen:

## JJJJ-MM-TT — Session N: <Titel>

### Was versucht wurde
<Aufbau, Werkzeug, Einstellungen>

### Ergebnis
- `[MARKER]` <Beobachtung>

### Was daraus folgt
<Schlussfolgerung — und was sie NICHT beweist>

### Nächster Schritt
<konkret>
-->
