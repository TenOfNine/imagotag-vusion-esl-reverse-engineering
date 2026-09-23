# CLAUDE.md — Arbeitsregeln für dieses Projekt

Diese Datei ist verbindlich. Sie wird von Claude Code bei jedem Sessionstart gelesen.

---

## 1. Was dieses Projekt ist

Reverse Engineering eines **VusionGroup/SES-imagotag Electronic Shelf Label**
(Platine `RFRTx026D`, MCU Silicon Labs EFR32FG22, E-Ink-Panel `EL074TS1`)
mit dem Ziel, das Panel unter eigener Kontrolle anzusteuern.

**Für Claude Code ist das ein reines Software-Projekt.** Die Hardware liegt
beim Maintainer auf dem Tisch. Claude Code schreibt Decoder, analysiert Mitschnitte,
rekonstruiert Protokolle und baut Treibercode — aber misst nichts selbst.

---

## 2. Die wichtigste Regel: Claude Code misst nicht

Claude Code hat **keinen Zugriff auf Messgeräte, Platinen oder Panels**.
Jede physikalische Information kommt ausschließlich vom Maintainer.

**Verboten:**

- Messwerte erfinden, schätzen oder „plausibel annehmen"
- Aus einem Foto eine Pinbelegung *ableiten* und als Fakt behandeln
- Behaupten, etwas sei „bestätigt", wenn es nur recherchiert oder vermutet ist
- Einen Treiber schreiben, der auf einer ungeprüften Pinbelegung basiert,
  ohne das im Code und in der Antwort deutlich zu kennzeichnen

**Stattdessen:** Wenn eine Information fehlt, formuliere einen
**Messauftrag** nach dem Schema in `docs/measurement-requests.md` und
lege ihn dort ab. Der Maintainer arbeitet ihn ab und trägt die Ergebnisse in
`hardware/measurements.md` ein.

---

## 3. Evidenz-Kennzeichnung

Jede Tatsachenbehauptung in diesem Repo trägt genau einen Marker:

| Marker | Bedeutung |
|---|---|
| `[MESSUNG]` | Der Maintainer hat es mit einem Gerät gemessen. Datum + Methode dazu. |
| `[MITSCHNITT]` | Aus einer Aufzeichnung in `captures/` abgeleitet. Dateiname dazu. |
| `[FOTO]` | Aus einem Bild in `hardware/photos/` abgelesen (Beschriftung, Bauteilzahl). |
| `[RECHERCHE]` | Aus einem Datenblatt oder einer Quelle. Link dazu. |
| `[ANNAHME]` | Vermutung. Muss einen Test nennen, der sie prüfen würde. |
| `[WIDERLEGT]` | War mal angenommen, ist gemessen widerlegt. **Nicht löschen** — stehen lassen, damit der Irrweg nicht wiederholt wird. |

Eine `[ANNAHME]` wird **nur** durch `[MESSUNG]` oder `[MITSCHNITT]` zu einem
Fakt. Nicht durch Plausibilität, nicht durch Wiederholung, nicht dadurch,
dass drei Quellen dasselbe behaupten.

---

## 4. HISTORY.md ist das Langzeitgedächtnis

`HISTORY.md` ist der wichtigste Zustand dieses Projekts. Claude Code hat
zwischen Sessions kein Gedächtnis — diese Datei ersetzt es.

**Regeln:**

- Bei **Sessionstart**: `HISTORY.md` und `docs/open-questions.md` lesen,
  bevor irgendetwas anderes passiert.
- Bei **jedem Erkenntnisgewinn**: sofort einen Eintrag anhängen. Nicht am
  Ende der Session sammeln — Sessions brechen ab.
- **Auch Fehlschläge eintragen.** Ein dokumentierter Sackgassenweg ist
  genauso wertvoll wie ein Erfolg. „Panel reagierte nicht auf Init-Variante X"
  gehört rein.
- Einträge werden **angehängt, nie umgeschrieben**. Korrekturen kommen als
  neuer Eintrag mit Verweis auf den alten.

---

## 5. Sicherheitsregeln (nicht verhandelbar)

Diese Regeln schützen Hardware, die nicht nachbestellbar ist.

1. **Ein Tag bleibt unangetastet** als Referenzexemplar. Kein Löten, kein
   Flashen, kein Unlock. Claude Code schlägt niemals vor, das Referenzexemplar
   anzufassen.
2. **Sniffen vor Unlock.** Das Entsperren des EFR32 löscht die
   Originalfirmware unwiderruflich. Solange die Init-Sequenz des Panels nicht
   mitgeschnitten und gesichert ist, wird kein Unlock vorgeschlagen.
3. **Hochspannung am FPC.** Mehrere Pins des 24-poligen Steckers führen im
   Betrieb ca. +22 V / −20 V. Der Logic Analyzer verträgt max. 3,6 V.
   Claude Code weist bei jedem Messauftrag, der den FPC betrifft, explizit
   darauf hin, vorher stromlos durchzuklingeln.
4. **Keine Pinbelegung ohne Messung.** Siehe Regel 2.

---

## 6. Arbeitsweise

- **Deutsch** in Fließtext und Dokumentation. Code, Bezeichner und
  Commit-Messages auf Englisch.
- **Keine Gefälligkeitszustimmung.** Wenn ein Ansatz des Maintainers technisch
  fragwürdig ist, sag das mit Begründung. Widerspruch ist hier nützlicher
  als Zustimmung.
- **Unsicherheit benennen.** „Ich weiß nicht, ob das Panel 800×480 hat"
  ist eine bessere Antwort als eine erfundene Zahl mit Nachkommastellen.
- **Kleine Schritte.** Lieber eine geprüfte Erkenntnis als fünf vermutete.
- Wenn etwas unklar ist: **nachfragen**, statt zu raten. Der Maintainer hat womöglich
  nur vergessen, eine Information mitzuliefern.

---

## 7. Repo-Struktur

```
CLAUDE.md                  diese Datei
README.md                  Projektüberblick
HISTORY.md                 Langzeitgedächtnis, chronologisch
TOOLS.md                   verfügbare Messtechnik
docs/
  hardware.md              Bauteil- und Plattformwissen
  pinout.md                FPC-Belegung: Hypothese + Verifikation
  capture-protocol.md      Anleitung für den Logic-Analyzer-Mitschnitt
  measurement-requests.md  offene Messaufträge an den Maintainer
  open-questions.md        was ungeklärt ist
  references.md            Quellen
captures/                  Rohmitschnitte (.sr, .csv) — nicht im Git
analysis/                  Decoder und Auswertungsskripte
hardware/
  measurements.md          Messprotokoll (vom Maintainer ausgefüllt)
  photos/                  Platinenfotos
firmware/                  späterer Treiber-/Firmwarecode
```

---

## 8. Definition of Done für eine Erkenntnis

Eine Erkenntnis gilt als gesichert, wenn:

1. sie in `HISTORY.md` steht, mit Datum und Methode,
2. sie einen Evidenz-Marker aus Abschnitt 3 trägt,
3. bei `[MITSCHNITT]` die Rohdatei in `captures/` reproduzierbar vorliegt,
4. bei `[MESSUNG]` die Zeile in `hardware/measurements.md` ausgefüllt ist.

Alles andere ist eine Hypothese und wird auch so genannt.
