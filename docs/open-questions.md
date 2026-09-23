# Offene Fragen

Der Arbeitsvorrat. Beantwortete Fragen wandern mit Ergebnis nach
`../HISTORY.md` und werden hier auf `✅` gesetzt — **nicht gelöscht**, damit
der Weg nachvollziehbar bleibt.

---

## Blockierend — ohne diese Antworten geht nichts

### 🔴 F-01 Wie ist der FPC tatsächlich belegt?

Alles Weitere hängt daran. Die Tabelle in `pinout.md` ist reine Hypothese.

→ Messauftrag **M-001**

### 🔴 F-02 Welche Auflösung hat das Panel?

`EL074TS1`, ca. 170 × 112 mm, dreifarbig. `[ANNAHME]` 800 × 480 ist eine
reine Größenplausibilität, kein Wert aus einer Quelle.

→ Aus den Nutzdaten-Blocklängen im Mitschnitt rückrechnen:
`Pixel pro Ebene = Blocklänge in Byte × 8`. Bei dreifarbig zwei Ebenen.

### 🔴 F-03 Welcher COG-Controller steckt im Panel?

Bestimmt, ob GxEPD2 direkt nutzbar ist oder ein eigener Treiber nötig wird.

→ Kommandobytes aus dem Mitschnitt gegen die üblichen Kandidaten matchen:
UC8179, SSD16xx, IL0373.

---

## Wichtig, aber nicht blockierend

### 🟡 F-04 Wird die Waveform-LUT vom MCU geschrieben oder liegt sie im OTP?

- **Vom MCU geschrieben** → steht im Mitschnitt, wir haben sie geschenkt.
- **Im OTP des COG** → brauchen wir sie gar nicht, der Controller kennt sie.

→ Fällt bei der Auswertung des Mitschnitts automatisch ab: ein auffällig
langer Datenblock direkt nach dem Init ist ein LUT-Kandidat.

### 🟡 F-05 Ist der EFR32 debug-gesperrt?

Falls **nein**: Originalfirmware auslesen und sichern. Das wäre für den
EPD-Treiber deutlich wertvoller als jeder Mitschnitt, weil die
Init-Sequenz dann im Klartext im Binary steht.

Falls **ja**: Unlock löscht sie unwiderruflich → erst sniffen.

→ `commander device info` und `commander security status`, **bevor**
irgendetwas geschrieben wird.

### 🟡 F-06 Wo liegt der SWD-Port?

→ Messauftrag **M-002**

### 🟡 F-07 QFN32 oder QFN40?

Entscheidet, welche Pinout-Tabelle des Datenblatts gilt.

→ Messauftrag **M-003**

### 🟡 F-08 Zeichnet das Tag beim Batterieeinlegen überhaupt ein Bild?

Die gesamte Sniffing-Strategie setzt das voraus. Falls nicht: Plan B über NFC.

→ Fällt beim ersten Aufnahmeversuch auf.

---

## Nachgelagert — erst nach dem Mitschnitt relevant

### ⚪ F-09 Weg A oder Weg B?

| | Weg A (ESP32 am Trägerboard) | Weg B (OpenEPaperLink-Port) |
|---|---|---|
| Funk | nein, verkabelt | ja, batteriebetrieben |
| Aufwand | mittel | hoch |
| Risiko | gering | Unlock ist irreversibel |

Die Entscheidung fällt **nach** dem Mitschnitt, wenn klar ist, wie
aufwendig der EPD-Treiber wird.

### ⚪ F-10 Lässt sich der EFR32 zerstörungsfrei stilllegen?

Hypothese: RESETn dauerhaft auf GND → GPIOs gehen in Hi-Z, SPI-Bus wird frei.

→ An **einem** Tag ausprobieren, bevor irgendwo Heißluft zum Einsatz kommt.

### ⚪ F-11 Was machen die Testpunkte TP1/TP2/TP3 auf dem FPC?

Unklar. Möglicherweise Produktionstest des Panels. Niedrige Priorität.

### ⚪ F-12 Welche Refreshrate verträgt das Panel im Dauerbetrieb?

`[RECHERCHE]` E Ink empfiehlt bei dreifarbigen Panels Mindestabstände von
einigen Minuten zwischen Updates; ein Vollbild dauert 15–30 s.

Für ein Dashboard unkritisch, für alles Dynamische ein Ausschlusskriterium.

---

## Beantwortet

*(noch leer — Einträge wandern mit Ergebnis und Datum hierher)*
