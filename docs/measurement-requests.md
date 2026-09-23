# Messaufträge

Claude Code kann nicht messen. Fehlende physikalische Information wird hier
als Auftrag formuliert, den der Maintainer abarbeitet.

**Für Claude Code:** Neue Aufträge unten anhängen, fortlaufend nummeriert
(`M-003`, `M-004`, …). Jeder Auftrag muss beantworten: *Was genau messen?
Womit? Und was folgt aus welchem Ergebnis?* Ein Auftrag, dessen Ergebnis
nichts entscheidet, ist überflüssig.

**Für den Maintainer:** Ergebnisse nach `../hardware/measurements.md`, dann den Auftrag
hier auf `✅ erledigt` setzen.

---

## Status

| ID | Thema | Status | Blockiert |
|---|---|---|---|
| M-001 | FPC-Pinbelegung durchklingeln | 🔴 offen | **alles** |
| M-002 | Vier offene Vias = SWD? | 🔴 offen | J-Link-Zugriff |
| M-003 | QFN-Gehäuse: 32 oder 40 Pins? | 🔴 offen | SWD-Pinnummern |

---

## M-001 — FPC-Pinbelegung durchklingeln

**Priorität: höchste.** Ohne dieses Ergebnis geht nichts weiter.

**Werkzeug:** Multimeter mit Durchgangsprüfer
**Zustand:** stromlos, Batterie entfernt

### Aufgabe

Für jeden der 24 FPC-Pins bestimmen, wohin er führt. Tabelle in
`../hardware/measurements.md` ausfüllen.

Reihenfolge des Vorgehens:

1. **Zählrichtung klären.** FPC einstecken, nachsehen, an welchem Ende des
   Steckers die aufgedruckte `1` sitzt. Ergebnis notieren.
2. **GND finden:** Durchgang zum Batterie-Minuspol.
3. **RESE finden:** ca. 0,5 – 3 Ω gegen GND (der kleine Shunt).
4. **GDR finden:** Durchgang zum Gate des SOT-23 mit Marking `KM`.
5. **Digitalleitungen finden:** welche Pins haben Durchgang **direkt zu einem
   QFN-Pin des FG22**? Die QFN-Pinnummer mitnotieren.
6. Rest als „endet an MLCC" oder „unklar" markieren.

### Entscheidungsregel

| Ergebnis | Folge |
|---|---|
| Genau 6 Digitalleitungen, zusammenhängend auf 9–14 | Waveshare-Standard bestätigt → `pinout.md` wird zu `[MESSUNG]` |
| 6 Digitalleitungen, aber woanders | Standard verwerfen, Belegung aus Messwerten rekonstruieren |
| Nicht 6 | Annahme über den Controller-Typ überdenken, Rückmeldung an Claude Code |

### ⚠ Sicherheit

Mehrere Pins führen im Betrieb ±20 V. **Nur stromlos messen.** Erst nach
dieser Messung darf der Logic Analyzer angeklemmt werden.

---

## M-002 — Sind die vier offenen Vias der SWD-Port?

**Werkzeug:** Multimeter
**Zustand:** stromlos

### Aufgabe

Auf der Rückseite, rechts neben der `2 BOT`-Beschriftung, liegen vier offene
Vias (eines links, eines rechts, zwei dicht nebeneinander darunter) plus eine
größere Bohrung darüber.

Für jedes Via prüfen:

| Test | Bedeutung |
|---|---|
| Durchgang zu Batterie-Minus | GND |
| Durchgang zu Batterie-Plus | VDD |
| Durchgang zu einem FG22-Pin | Kandidat für SWDIO / SWCLK / RESET |

Bei Treffern auf FG22-Pins: **QFN-Pinnummer notieren** und gegen die
Port-A-Belegung im EFR32FG22-Datenblatt prüfen (Port A trägt bei xG22 die
SWD-Funktion).

### Entscheidungsregel

| Ergebnis | Folge |
|---|---|
| GND + VDD + 2 Port-A-Pins gefunden | SWD-Port bestätigt → J-Link kann dort angeschlossen werden |
| Nur GND/VDD, keine Port-A-Pins | Andere Funktion (z. B. Testpunkte der Produktion) → SWD direkt an den QFN-Pins abgreifen |

### Hinweis

Für den J-Link zusätzlich **VTref** verbinden (an VDD) — ohne VTref
verweigert der J-Link den Dienst.

---

## M-003 — QFN-Gehäuse: 32 oder 40 Pins?

**Werkzeug:** Lupe oder Mikroskop, gutes Seitenlicht

### Aufgabe

Pads pro Seite am EFR32FG22 zählen.

| Ergebnis | Typ | GPIO |
|---|---|---|
| 8 pro Seite = 32 gesamt | `EFR32FG22C121F512GM32-C` | 18 |
| 10 pro Seite = 40 gesamt | `EFR32FG22C121F512GM40-C` | 26 |

### Warum das zählt

Die Pinout-Tabellen der beiden Gehäuse sind **nicht identisch**. Ohne diese
Information lassen sich die SWD-Pins nicht sicher zuordnen — und ein
falscher Anschluss des J-Link kann den Chip beschädigen.

---

<!--
VORLAGE:

## M-00N — <Titel>

**Priorität:** <hoch/mittel/niedrig>
**Werkzeug:** <Gerät>
**Zustand:** <stromlos / in Betrieb>

### Aufgabe
<was genau zu tun ist, Schritt für Schritt>

### Entscheidungsregel
| Ergebnis | Folge |
|---|---|
| <Fall A> | <was dann passiert> |
| <Fall B> | <was dann passiert> |

### ⚠ Sicherheit
<falls relevant>
-->
