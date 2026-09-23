# Messprotokoll

Wird vom **Maintainer** ausgefüllt. Claude Code trägt hier nichts ein —
es sei denn, der Maintainer diktiert Werte.

Jede ausgefüllte Zeile ist eine `[MESSUNG]` im Sinne von `CLAUDE.md` §3 und
darf ab dann als Fakt behandelt werden.

---

## M-001 — FPC-Pinbelegung

**Datum:** ⬜ noch nicht gemessen
**Werkzeug:** ⬜
**Tag-Nr.:** ⬜

### Zählrichtung

> FPC einstecken, nachsehen, an welchem Ende die aufgedruckte `1` sitzt.

| Frage | Antwort |
|---|---|
| Pin 1 liegt … | ⬜ nahe dem Panel-Ende / ⬜ nahe der Platinenkante |
| Kontakte des FPC zeigen … | ⬜ nach oben / ⬜ nach unten |

### Pintabelle

Spalte „Ziel": `GND`, `VDD`, `MLCC`, `Gate KM`, `Shunt`, `FG22 Pin nn`, `offen`, `?`

| Pin | Ziel (gemessen) | Widerstand ggü. GND | Erkannt als | Standard wäre |
|---:|---|---|---|---|
|  1 | ⬜ | ⬜ | ⬜ | HLT_CTL |
|  2 | ⬜ | ⬜ | ⬜ | GDR |
|  3 | ⬜ | ⬜ | ⬜ | RESE |
|  4 | ⬜ | ⬜ | ⬜ | VGL ⚡ |
|  5 | ⬜ | ⬜ | ⬜ | VGH ⚡ |
|  6 | ⬜ | ⬜ | ⬜ | TSCL |
|  7 | ⬜ | ⬜ | ⬜ | TSDA |
|  8 | ⬜ | ⬜ | ⬜ | BS |
|  9 | ⬜ | ⬜ | ⬜ | BUSY 🟢 |
| 10 | ⬜ | ⬜ | ⬜ | RST 🟢 |
| 11 | ⬜ | ⬜ | ⬜ | D/C 🟢 |
| 12 | ⬜ | ⬜ | ⬜ | CS 🟢 |
| 13 | ⬜ | ⬜ | ⬜ | SCK 🟢 |
| 14 | ⬜ | ⬜ | ⬜ | SDI 🟢 |
| 15 | ⬜ | ⬜ | ⬜ | VDDIO |
| 16 | ⬜ | ⬜ | ⬜ | VCI |
| 17 | ⬜ | ⬜ | ⬜ | VSS (GND) |
| 18 | ⬜ | ⬜ | ⬜ | VDD |
| 19 | ⬜ | ⬜ | ⬜ | VPP |
| 20 | ⬜ | ⬜ | ⬜ | VSH ⚡ |
| 21 | ⬜ | ⬜ | ⬜ | PREVGH ⚡ |
| 22 | ⬜ | ⬜ | ⬜ | VSL ⚡ |
| 23 | ⬜ | ⬜ | ⬜ | PREVGL ⚡ |
| 24 | ⬜ | ⬜ | ⬜ | VCOM ⚡ |

### Auswertung

| Frage | Antwort |
|---|---|
| Anzahl gefundener Digitalleitungen | ⬜ (erwartet: 6) |
| Liegen sie zusammenhängend? | ⬜ ja / ⬜ nein |
| Auf welchen Pins? | ⬜ |
| **Standard bestätigt?** | ⬜ ja / ⬜ nein |

---

## M-002 — Vier offene Vias auf der Rückseite

**Datum:** ⬜ noch nicht gemessen

Lage: rechte Bildhälfte, links neben der `2 BOT`-Beschriftung.

| Via | Position | Durchgang zu | FG22-Pin | Vermutlich |
|---|---|---|---|---|
| A | links | ⬜ | ⬜ | ⬜ |
| B | rechts | ⬜ | ⬜ | ⬜ |
| C | unten links | ⬜ | ⬜ | ⬜ |
| D | unten rechts | ⬜ | ⬜ | ⬜ |
| E | große Bohrung oben | ⬜ | ⬜ | ⬜ |

**Ergebnis:** ⬜ SWD-Port bestätigt / ⬜ andere Funktion / ⬜ unklar

---

## M-003 — QFN-Gehäuse

**Datum:** ⬜ noch nicht gemessen

| Frage | Antwort |
|---|---|
| Pads pro Seite | ⬜ |
| Gesamtzahl | ⬜ |
| **Typ** | ⬜ QFN32 (`…GM32-C`) / ⬜ QFN40 (`…GM40-C`) |

---

## Sonstige Messungen

> Freies Feld für alles, was nicht in einem Auftrag stand.

| Datum | Was gemessen | Ergebnis |
|---|---|---|
| Session 1 (≤ 2026-09-22) | Außenmaße Panel, **Messschieber** (Angabe Maintainer 2026-09-23) | ca. 170 × 112 mm |
| ⬜ | ⬜ | ⬜ |
