# analysis — Auswertung der Mitschnitte

## decode_spi.py

Zerlegt einen PulseView-CSV-Export in Kommandos und Datenblöcke.

```bash
python3 analysis/decode_spi.py captures/<datei>.csv \
    --sck D0 --mosi D1 --cs D2 --dc D3 --busy D4 --rst D5 \
    --out-prefix analysis/out/2026-09-25_tag03
```

### Optionen

| Option | Default | Zweck |
|---|---|---|
| `--sck --mosi --cs --dc` | D0–D3 | Kanalzuordnung |
| `--busy --rst` | D4, D5 | optional, für BUSY-Dauer und Reset-Erkennung |
| `--mode` | 0 | SPI-Modus 0–3 |
| `--lsb-first` | aus | falls LSB zuerst |
| `--cs-active-high` | aus | falls CS invertiert |
| `--rate` | aus CSV | Samplerate in Hz, falls nicht im Header |
| `--out-prefix` | — | schreibt Reportdateien |

### Was ausgegeben wird

**Auf der Konsole:**

1. **Capture-Übersicht** — Dauer, geschätzter SPI-Takt, Reset-Flanken, lange
   BUSY-Phasen. Warnt, wenn die Samplerate unter dem 5-fachen SPI-Takt liegt.
2. **Controller-Fingerprint** — wie viele der bekannten Opcodes je
   Controller-Familie vorkommen (UC8179, IL0373, SSD16xx).
3. **Kommandolog** — jede Transaktion mit Opcode, Klartextbedeutung und Payload.
4. **Frame-Blöcke** — alle Datenblöcke ≥ 1024 Byte, plus **Auflösungs-
   kandidaten** durch Faktorisierung von `Blocklänge × 8`.
5. **LUT-Kandidaten** — Blöcke zwischen 20 und 512 Byte. Wenn hier die
   Waveform drinsteckt, muss sie nicht aus dem OTP rekonstruiert werden.

**Als Dateien** (mit `--out-prefix`):

| Datei | Inhalt |
|---|---|
| `*_transactions.txt` | vollständiges Log, kleine Payloads im Klartext |
| `*_init_sequence.py` | nachspielbare Sequenz, Bilddaten als `FRAME`-Platzhalter |
| `*_blocks.csv` | Tabelle aller Transaktionen für eigene Auswertung |

---

## Wichtige Einschränkung

> Das Skript prüft die **Pinzuordnung nicht**. Sind die Kanäle falsch
> zugeordnet, ist die Ausgabe überzeugend und falsch.

Der Fingerprint ist ein **Hinweis, kein Beweis**. Ein Treffer von 60 % heißt
nur, dass viele Opcodes zu einer Familie passen — die Familien überlappen
sich stark (UC8179 und IL0373 teilen fast alle Opcodes).

Belastbar wird das erst, wenn:

- die Auflösung aus den Blocklängen zu den physischen Panelmaßen passt, und
- ein Replay der Sequenz auf der Hardware tatsächlich ein Bild zeichnet.

---

## make_testcapture.py

Erzeugt einen **synthetischen** Mitschnitt, um den Decoder ohne Hardware zu
prüfen:

```bash
python3 analysis/make_testcapture.py /tmp/fake.csv
python3 analysis/decode_spi.py /tmp/fake.csv
```

Simuliert einen UC8179-artigen dreifarbigen Refresh: Reset, Init, zwei
Farbebenen, DRF, lange BUSY-Phase.

**Das ist eine Testvorrichtung.** Sie beweist, dass der Decoder funktioniert
— über das echte Panel sagt sie nichts aus.

---

## Erwartete Werte beim echten Mitschnitt

Zur Plausibilitätskontrolle:

| Größe | Erwartung |
|---|---|
| SPI-Takt | 1 – 4 MHz |
| SPI-Modus | 0 (CPOL=0, CPHA=0), MSB first, CS low-aktiv |
| Frame-Blöcke | 2 gleich große (S/W-Ebene + Rot-Ebene) |
| Blockgröße bei 800×480 | 48.000 Byte je Ebene |
| BUSY-Phase nach DRF | 15 – 30 s |

Weichen die gemessenen Werte davon ab, ist das **eine Erkenntnis** und
gehört nach `HISTORY.md` — nicht ein Grund, die Parameter so lange zu
drehen, bis das erwartete Ergebnis herauskommt.
