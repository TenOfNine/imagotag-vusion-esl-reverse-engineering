# TOOLS — verfügbare Messtechnik

Was physikalisch auf dem Labortisch liegt. Claude Code darf **nur** Messaufträge
formulieren, die mit dieser Ausstattung durchführbar sind — oder explizit
sagen, dass ein Gerät fehlt und welches gebraucht würde.

Legende: **✅ vorhanden** · **❓ unklar** · **❌ fehlt**

---

## ✅ Sipeed SLogic Combo 8 — Logic Analyzer

Das zentrale Werkzeug dieses Projekts.

| Eigenschaft | Wert |
|---|---|
| Kanäle | 8 |
| Max. Samplerate | 80 MHz |
| Übertragungsbandbreite | 320 Mb/s |
| Sampling-Modus | **Streaming** (kein Onboard-Speicher) |
| Eingangsbereich | 0 – 3,6 V |
| Pegelschwellen | VIH > 2 V, VIL < 0,8 V |
| Software | PulseView (sigrok) |

**Praktisch nutzbare Raten** (limitiert durch USB-Stabilität):

| OS | Konfiguration |
|---|---|
| Linux | 80 MHz @ 4 Kanäle · **40 MHz @ 8 Kanäle** |
| Windows | 80 MHz @ 2 Kanäle · **20 MHz @ 8 Kanäle** |

→ **Linux bevorzugen**, wenn verfügbar.

**Stand 2026-09-23:** Maintainer nutzt PulseView unter **Windows**.
→ Praktische Grenze für dieses Projekt: **20 MSa/s bei 8 Kanälen.**
Bei einem SPI-Takt bis 4 MHz sind das 5 Samples pro Takt — gerade an der
Grenze. Liegt der Takt höher, auf 4 Kanäle reduzieren (SCK, MOSI, CS, D/C)
oder Linux (z. B. Live-USB) in Betracht ziehen.

### Konsequenzen für die Nutzung

- **Streaming** heißt: alles geht live über USB ins RAM. Lange Aufnahmen
  (30–60 s) sind möglich, während ein speicherbasierter Analyzer längst voll
  wäre. Preis: RAM-Verbrauch und meist **kein Hardware-Trigger**.
  → Bei 20 MSa/s × 8 Kanälen × 30 s ≈ 600 MB. Bei 40 MSa/s ≈ 1,2 GB.
- **Bekannter Bug:** Wird D7 während der Aufnahme nicht benutzt, kann auf
  diesem Kanal eine **Pegelinversion** auftreten.
  → D7 immer auf GND legen oder belegen.
- **GND-Führung:** Die Masseleitung so nah wie möglich an den Messpunkt.
  Laut Hersteller kann schon 1 cm näher die Signalqualität verbessern.
  → Mindestens zwei GND-Strippen verwenden.
- **Kein Spannungsschutz.** 3,6 V ist das Ende. Am FPC liegen daneben
  ±20 V. Siehe Sicherheitsregel 3 in `CLAUDE.md`.

### Kanalbelegung (Standard für dieses Projekt)

| Kanal | Signal |
|---|---|
| D0 | SCK |
| D1 | SDI / MOSI |
| D2 | CS |
| D3 | D/C |
| D4 | BUSY |
| D5 | RST |
| D6 | frei |
| D7 | **auf GND** (siehe Bug oben) |

---

## ✅ SEGGER J-Link — SWD-Debugger

Für Zugriff auf den EFR32FG22.

- **Wichtig:** EFR32 Series 2 kann **nur SWD, kein JTAG**.
- Verkabelung: `SWCLK`, `SWDIO`, `GND` und **`VTref`**.
  → Ohne VTref rührt sich der J-Link nicht. Häufigster Anfängerfehler.
  `RESET` ist optional, hilft aber bei Connect-under-Reset.
- Software: **Simplicity Commander** (Silicon Labs, kostenlos).
- Unlock-Kommando: `commander device unlock`
  **Löscht die Originalfirmware.** Erst nach erfolgreichem Mitschnitt
  verwenden — siehe `CLAUDE.md` §5.2.
- Zustand vorher abfragen: `commander device info`, `commander security status`
  → Möglicherweise ist der Chip gar nicht gesperrt. Dann kann die
  Originalfirmware **ausgelesen und gesichert** werden, was für den
  EPD-Treiber wertvoller wäre als jeder Mitschnitt.

---

## ❓ FTDI USB-Seriell-Adapter

Angabe des Maintainers (2026-09-23): **„FTDI1232"**. Einen FTDI-Chip mit
genau dieser Bezeichnung kenne ich nicht. `[ANNAHME]` Gemeint ist ein
**FT232R(L)**-Modul — das wäre reines UART.
Maintainer (2026-09-23): „hat nur UART, soweit ich weiß".
→ Für das Projekt **nicht relevant**, da ein J-Link vorhanden ist. Wird nur
dann weiter geklärt, falls der Adapter doch für SWD gebraucht würde.

- **FT232R / FT231X / FT230X** → nur UART. Für SWD unbrauchbar.
- **FT2232H / FT232H / FT4232H** → haben MPSSE, können SWD via OpenOCD
  (mit Widerstandstrick TDI↔TDO, ~470 Ω–1 kΩ).

→ Für dieses Projekt **nicht kritisch**, da ein J-Link vorhanden ist.
Nur relevant, falls parallel eine UART-Debugausgabe mitgelesen werden soll.

---

## ✅ OWON HDS242 — Hand-Oszilloskop mit Multimeter

Angabe des Maintainers (2026-09-23). Deckt **Multimeter und Oszilloskop** ab.

`[RECHERCHE]` Eckdaten laut Händlerangaben
(https://vishaworld.com/products/owon-hds242-handheld-digital-oscilloscope-bandwidth-40-mhz-2-channel-sample-rate-250-msa-s-single-channel-125-msa-s-dual-channel,
https://toolboom.com/en/handheld-digital-oscilloscope-owon-hds242/):

| Eigenschaft | Wert |
|---|---|
| Kanäle | 2 |
| Bandbreite | 40 MHz |
| Samplerate | 250 MSa/s (1 Kanal), 125 MSa/s (2 Kanäle) |
| Speichertiefe | 8 k Punkte |
| Multimeter | 20.000 Counts, Spannung, Strom, Widerstand, Kapazität, Diode, **Durchgang** |
| Versorgung | 18650-Akku, USB-C |

### Konsequenzen für die Nutzung

- **Durchgangsprüfer vorhanden** → M-001 bis M-003 sind durchführbar.
- **Oszilloskop vorhanden** → damit lassen sich vor dem Anklemmen des
  SLogic die **Logikpegel** und der **SPI-Takt** kontrollieren, und
  diagnostisch die Boost-Spannungen (VGH/VGL).
- **8 k Punkte Speicher** → zum Mitschneiden eines ganzen Refresh
  **ungeeignet**. Das bleibt Aufgabe des SLogic.
- Maximale Eingangsspannung der Oszilloskop-Eingänge bei 1×/10×-Tastkopf
  **nicht recherchiert** → vor Messungen an den HV-Rails im Handbuch
  nachsehen und 10× verwenden.

## ✅ Lötstation

Angabe des Maintainers (2026-09-23): normale Lötstation, **keine
Heißluft**. Reicht für Kupferlackdraht an Vias (Capture-Weg B).

---

## Prüfobjekte

| Position | Menge | Status |
|---|---|---|
| ESL-Tags `RFRTx026D` | > 5 | verfügbar |
| davon **Referenzexemplar** | 1 | **unangetastet**, siehe `CLAUDE.md` §5.1 |

---

## ❌ Nützlich, aber nicht vorhanden

Claude Code darf das vorschlagen, wenn es einen Schritt entscheidend
vereinfacht — aber keinen Arbeitsplan darauf aufbauen.

| Gerät | Wofür | Grobpreis |
|---|---|---|
| 24-pol. FPC-Verlängerungsset (0,5 mm, Adapter + Kabel) | Abgriff am FPC **ohne Löten**. Achtung: A-A vs. A-B je nach Kontaktseite. **Bestätigt nicht vorhanden** (2026-09-23). | 10–20 € |
| Heißluftstation | Auslöten des EFR32 (Weg A, Variante 2). **Bestätigt nicht vorhanden** (2026-09-23) → Variante 2 derzeit nicht durchführbar. | — |
| Mikroskop / Lupe mit Beleuchtung | Pads am QFN zählen, Markings lesen | — |

---

## Werkzeuge, die Claude Code selbst hat

Zur Klarstellung, was **ohne** Hardwarezugriff möglich ist:

- Auswertung von Mitschnitten (CSV/sigrok) mit Python
- Decoder- und Treibercode schreiben
- Datenblätter und fremde Reverse-Engineering-Arbeiten recherchieren
- Fotos analysieren: Bauteil-Markings lesen, Kontakte zählen, QR-Codes
  dekodieren, Geometrie vermessen

**Nicht** möglich: irgendeine elektrische Messung, irgendein Zugriff auf
Hardware.
