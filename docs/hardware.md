# Hardware — Bestandsaufnahme

Alles, was über das Prüfobjekt bekannt ist. Evidenz-Marker nach `CLAUDE.md` §3.

---

## Gesamtsystem

Electronic Shelf Label der **VUSION**-Familie von VusionGroup
(vormals SES-imagotag, seit 2024 umbenannt; Mehrheitseigner BOE Technology).

`[RECHERCHE]` Die VUSION-Familie arbeitet auf **2,4 GHz** und umfasst
Displaygrößen von 1,6" bis 12,2" in Schwarz/Weiß/Rot bzw. Gelb.
Die Infrastruktur besteht aus Server, Access Points und den Tags selbst.

---

## Platine

| Merkmal | Wert | Evidenz |
|---|---|---|
| Bedruckung | `imagotag  RFRTx026D` | `[FOTO]` |
| Funkband | `2,4 GHz` (aufgedruckt) | `[FOTO]` |
| Sonstige Bedruckung | `315 17 94V-0`, `13` | `[FOTO]` |
| Lagen | `1 TOP` / `2 BOT` (aufgedruckt) | `[FOTO]` |
| Seriennummer (QR) | `060RFRTX026D00A120O262007587` | `[MESSUNG]` |

Die Seriennummer enthält erkennbar die Typenbezeichnung `RFRTX026D`,
liefert darüber hinaus aber keine technische Information.

---

## MCU — Silicon Labs EFR32FG22

`[FOTO]` QFN-Marking, vierzeilig:

```
FG22
C121GG
C026ZX
2419
```

- `FG22` → Produktfamilie EFR32**FG**22 „Flex Gecko", Proprietary 2,4 GHz
- `C121` → Ausstattungsvariante
- `2419` → Datumscode **KW 19 / 2024**

`[RECHERCHE]` Eckdaten der C121-Variante laut EFR32FG22 Family Data Sheet:

| Merkmal | Wert |
|---|---|
| Kern | ARM Cortex-M33 |
| Max. Takt | 38,4 MHz |
| Flash | 512 kB |
| RAM | 32 kB |
| Max. TX-Leistung | 6 dBm |
| Protokoll | Proprietary |
| Temperaturbereich | −40 bis 85 °C |

Zwei Gehäusevarianten:

| Bestellcode | Gehäuse | GPIO |
|---|---|---|
| `EFR32FG22C121F512GM40-C` | QFN40, 5 × 5 mm | 26 |
| `EFR32FG22C121F512GM32-C` | QFN32, 4 × 4 mm | 18 |

`[ANNAHME]` Verbaut ist **QFN40**, geschätzt aus ca. 10 sichtbaren Pads pro
Seite im Foto.
→ **Prüfung:** Pads pro Seite unter Lupe zählen. 10 = QFN40, 8 = QFN32.
Das Ergebnis entscheidet, welche Pinout-Tabelle des Datenblatts gilt.

### Taktquellen

| Bauteil | Marking | Funktion | Evidenz |
|---|---|---|---|
| Quarz groß | `38.4  T4F` | HFXO, 38,4 MHz | `[FOTO]` |
| Quarz klein | `T422C` | LFXO, 32,768 kHz | `[FOTO]` |

Die 38,4 MHz passen exakt zum Referenztakt der EFR32-Serie — starke
Bestätigung der MCU-Identifikation.

### Debug-Interface

`[RECHERCHE]` EFR32 Series 2 unterstützt **ausschließlich SWD**, kein JTAG.
Die SWD-Pins liegen auf **Port A**. Die konkreten Pinnummern hängen vom
Gehäuse ab → erst nach Klärung QFN32/QFN40 aus dem Datenblatt entnehmen.

`[RECHERCHE]` Werksseitig gesperrte xG22 lassen sich entsperren, solange
„unauthenticated debug unlock" nicht deaktiviert wurde. **Der Unlock löscht
die Originalfirmware.** Werkzeug: Simplicity Commander + J-Link.

---

## Panel — E Ink EL074TS1

| Merkmal | Wert | Evidenz |
|---|---|---|
| Bezeichnung | `EL074TS1` | `[FOTO]` |
| Größe | 7,4 Zoll (aus Typenbezeichnung `074`) | `[RECHERCHE]` |
| Außenmaße | ca. 170 × 112 mm | `[MESSUNG]` |
| Farben | dreifarbig, S/W/Rot | `[MESSUNG]` |
| Seriennummer (QR) | `H7FZDSPQ0KXYZ5V00DAUAT` | `[MESSUNG]` |
| Auflösung | **unbekannt** | — |
| COG-Controller | **unbekannt** | — |
| Waveform / LUT | **unbekannt** | — |

`[RECHERCHE]` **Kein öffentliches Datenblatt auffindbar.** Gesucht wurde
direkt nach der Typenbezeichnung sowie über E-Ink- und Distributorenkataloge.
ESL-Panels werden unter NDA an OEMs geliefert.

`[ANNAHME]` Auflösung 800 × 480 — eine reine Größenplausibilität für 7,x",
**kein belastbarer Wert**.
→ **Prüfung:** Aus den Nutzdaten-Blocklängen im Mitschnitt rückrechnen.
Bei zwei Farbebenen gilt `Pixel = Blocklänge × 8` pro Ebene.

### FPC

| Merkmal | Wert | Evidenz |
|---|---|---|
| Kontakte | **24** | `[FOTO]` |
| Raster | 0,5 mm | `[FOTO]` |
| Beschriftung Kontaktende | `1` und `24` aufgedruckt | `[FOTO]` |
| Testpunkte auf dem FPC | `TP1`, `TP2`, `TP3` | `[FOTO]` |

Kontaktzahl und Raster wurden per Farbsegmentierung und FFT-Periodenanalyse
an zwei unabhängigen Fotos ermittelt, Ergebnis konsistent.

Belegung → siehe `pinout.md`.

---

## Leistungsteil (Boost für die EPD-Spannungen)

`[FOTO]` Rechts des ZIF-Steckers, Standardmuster für einen E-Ink-COG mit
integriertem DC/DC:

| Bauteil | Marking | Vermutete Funktion |
|---|---|---|
| Speicherdrossel | — | Boost-Induktivität |
| SOT-23 | `KM` | Schalt-MOSFET, gate-getrieben von `GDR` |
| SOD-Dioden | `4`, `BR`, `ZV` | Schottky-Gleichrichter für VGH/VGL/VSH/VSL |
| MLCCs (groß) | — | Stützkondensatoren der HV-Rails |

**Das ist der Grund, die Originalplatine zu behalten:** Diese Beschaltung ist
korrekt dimensioniert und richtig verdrahtet. Genau hier zerstört man sich
beim Fremdadapter das Panel.

### Weitere unklare Bauteile

`[FOTO]` SOT-23-Gehäuse mit Markings `S21`, `XDt`, `T0.`, `1R.` —
Funktion ungeklärt, vermutlich LDO, Lastschalter und/oder Pegelwandler.

---

## NFC

| Merkmal | Wert | Evidenz |
|---|---|---|
| IC | SO-8, Marking `8K417 / 0E47AH` | `[FOTO]` |
| Antenne | große Spule auf der Rückseite | `[FOTO]` |
| Beschriftung in der Spule | handschriftlich `0181` | `[FOTO]` |

`[ANNAHME]` Der SO-8 ist das NFC-Frontend.
→ **Prüfung:** Durchgang IC ↔ Antennenspule messen.

**Relevanz:** Plan B. Falls das Tag beim Batterieeinlegen keinen Refresh
zeichnet, ließe sich der Refresh unter Umständen über NFC auslösen — und
damit der Mitschnitt doch noch gewinnen.

---

## Rückseite

| Merkmal | Evidenz |
|---|---|
| NFC-Antennenspule, oberer Bereich | `[FOTO]` |
| Zwei LEDs (klar + gelb), unten mittig | `[FOTO]` |
| `2 BOT` — Lagenbezeichnung, **kein** Testpunkt | `[FOTO]` |
| Vier verlötete Vias unten links = Batteriekontakt-Lötstellen | `[FOTO]` |
| **Vier offene Vias** rechts, links neben `2 BOT` | `[FOTO]` |

`[ANNAHME]` Die vier offenen Vias sind der **SWD-Port**
(SWDIO, SWCLK, GND, VDD, ggf. RESET). Anordnung: eines links, eines rechts,
zwei dicht nebeneinander darunter, größere Bohrung darüber.
→ **Prüfung:** Messauftrag M-002.
