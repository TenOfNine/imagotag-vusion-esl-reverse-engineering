# captures — Rohmitschnitte

## Namensschema

```
YYYY-MM-DD_<tag-id>_<zweck>_<rate>.<ext>
```

Beispiele:

```
2026-09-25_tag03_boot-refresh_20MHz.csv
2026-09-25_tag03_boot-refresh_20MHz.sr
2026-09-25_tag03_overview_2MHz.sr
```

`<tag-id>` ist die laufende Nummer des Prüfobjekts. **Tag 01 ist das
Referenzexemplar** und taucht hier nie auf.

---

## Was ins Git gehört

| Typ | Git | Begründung |
|---|---|---|
| `.sr` (sigrok nativ) | ✅ wenn < 20 MB | verlustfrei und kompakt |
| `.csv` roh | ❌ | mehrere hundert MB, aus `.sr` reproduzierbar |
| `*_transactions.txt` | ✅ | das eigentliche Ergebnis, klein |
| `*_init_sequence.py` | ✅ | das eigentliche Ergebnis |
| `*_blocks.csv` | ✅ | klein |

Die `.gitignore` setzt das bereits um. Große CSVs bleiben lokal.

---

## Zu jedem Mitschnitt gehört ein Eintrag in `../HISTORY.md`

Mindestens:

- Datum, Tag-Nummer, Samplerate, Kanalbelegung
- Wie der Refresh ausgelöst wurde (Batterie / NFC / sonstiges)
- Ob überhaupt etwas kam
- Was der Decoder daraus gemacht hat

**Auch ein leerer Mitschnitt ist ein Ergebnis** und wird dokumentiert.

---

## Ablauf

Siehe `../docs/capture-protocol.md`.
