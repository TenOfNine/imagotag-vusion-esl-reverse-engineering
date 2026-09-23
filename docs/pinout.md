# Pinout — 24-poliger FPC

> **⚠ Nichts in diesem Dokument ist gemessen.**
> Die Tabelle unten ist der Waveshare-/Good-Display-Standard als
> Arbeitshypothese. ESL-Panels weichen davon regelmäßig ab.
> Solange die Spalte „gemessen" leer ist, darf **kein** Treiber und **keine**
> Verdrahtung darauf aufgebaut werden.

---

## Hypothese: Standardbelegung 24-Pin E-Paper

`[RECHERCHE]` Übereinstimmend aus Waveshare E-Paper Driver HAT Schematic,
Electronic Assembly ePaper-Datenblatt und Midas MDE0154A152152RBW Spec.

| Pin | Signal | Bedeutung | Klasse |
|---:|---|---|---|
| 1 | HLT_CTL | Halt Control | sonstig |
| 2 | **GDR** | N-Ch MOSFET Gate Drive Control | Boost |
| 3 | **RESE** | Current Sense Input (Shunt) | Boost |
| 4 | VGL | negative Gate-Spannung, ca. −20 V | ⚡ HV |
| 5 | VGH | positive Gate-Spannung, ca. +22 V | ⚡ HV |
| 6 | TSCL | I²C-Takt Temperatursensor | sonstig |
| 7 | TSDA | I²C-Daten Temperatursensor | sonstig |
| 8 | BS | Bus Selector | sonstig |
| 9 | **BUSY** | Busy-Ausgang | 🟢 digital |
| 10 | **RST** | Reset, active low | 🟢 digital |
| 11 | **D/C** | Data (high) / Command (low) | 🟢 digital |
| 12 | **CS** | Chip Select, active low | 🟢 digital |
| 13 | **SCK** | SPI-Takt | 🟢 digital |
| 14 | **SDI** | SPI-Daten (MOSI) | 🟢 digital |
| 15 | VDDIO | Versorgung I/O-Logik | 🔵 Power |
| 16 | VCI | Versorgung Displaytreiber | 🔵 Power |
| 17 | VSS | Ground | 🔵 Power |
| 18 | VDD | Versorgung | 🔵 Power |
| 19 | VPP | OTP-Programmierspannung | sonstig |
| 20 | VSH | positive Source-Spannung | ⚡ HV |
| 21 | PREVGH | Versorgung für VGH/VSH | ⚡ HV |
| 22 | VSL | negative Source-Spannung | ⚡ HV |
| 23 | PREVGL | Versorgung für VCOM/VGL/VSL | ⚡ HV |
| 24 | VCOM | Common-Elektrode | ⚡ HV |

**⚡ HV = Hochspannung.** Der SLogic verträgt max. 3,6 V. Ein abgerutschter
Tastkopf zerstört ihn.

---

## Was bereits geklärt ist

`[FOTO]` Das **FPC ist selbst beschriftet**: am Kontaktende steht auf einer
Seite `24`, auf der anderen `1`. Die Zählrichtung des Kabels ist damit
eindeutig.

`[ANNAHME]` **Noch offen:** an welchem Ende des Steckers auf der Platine Pin 1
liegt. Vorder- und Rückseite sind spiegelverkehrt.
→ FPC einstecken und nachsehen, an welchem Ende die `1` sitzt.

---

## Verifikation — Messauftrag M-001

Alles stromlos, Batterie entfernt, Multimeter auf Durchgang.

### Schritt 1 — Ankerpunkte finden

| Suche | Erkennungsmerkmal | Erwartung bei Standard |
|---|---|---|
| **GND** | Durchgang zum Batterie-Minuspol | Pin 17 (VSS) |
| **RESE** | ca. 0,5 – 3 Ω gegen GND (der kleine Shunt) | Pin 3 |
| **GDR** | Durchgang zum **Gate** des SOT-23 `KM` | Pin 2 |
| **HV-Pins** | enden an den dicken MLCCs | 4, 5, 20–24 |

### Schritt 2 — Digitalleitungen identifizieren

Die entscheidende Messung: **Welche FPC-Pins haben Durchgang direkt zu einem
QFN-Pin des FG22?**

Es sollten **genau 6** sein: BUSY, RST, D/C, CS, SCK, SDI.

- Liegen sie **zusammenhängend auf 9–14** → Standard bestätigt, der Rest der
  Tabelle ist glaubwürdig.
- Liegen sie **woanders** → Hypothese verwerfen, Belegung komplett aus den
  Messwerten rekonstruieren.

### Schritt 3 — Plausibilitätsprobe

Ist GND der **8. Pin von einem Ende**, ist dieses Ende Pin 24 — dann ist die
Zählrichtung auf der Platine gespiegelt gegenüber der Annahme.

---

## Messergebnis

Wird in `../hardware/measurements.md` eingetragen. Sobald dort die
Digitalleitungen bestätigt sind, wird **diese Datei** mit `[MESSUNG]`-Markern
aktualisiert und die Hypothesenwarnung oben entfernt.

---

## Hinweis zur Kontaktseite

`[RECHERCHE]` ESL-Displays haben die Kupferkontakte des FPC typischerweise
auf der **Unterseite**, Waveshare-Displays auf der **Oberseite**.

Relevant, falls doch ein Fremdadapter oder ein FPC-Verlängerungskabel zum
Einsatz kommt: Dann wird ein **A-B-Kabel** („D-Type") als Wender gebraucht,
kein A-A-Kabel. Vor dem Kauf prüfen, auf welcher Seite die Kontakte liegen.
