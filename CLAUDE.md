# CLAUDE.md — Working rules for this project

This file is binding. Claude Code reads it at the start of every session.

---

## 1. What this project is

Reverse engineering of a **VusionGroup/SES-imagotag Electronic Shelf Label**
(board `RFRTx026D`, MCU Silicon Labs EFR32FG22, e-ink panel `EL074TS1`)
with the goal of driving the panel under our own control.

**For Claude Code this is a pure software project.** The hardware is on the
maintainer's bench. Claude Code writes decoders, analyses captures,
reconstructs protocols and builds driver code — but measures nothing itself.

---

## 2. The most important rule: Claude Code does not measure

Claude Code has **no access to instruments, boards or panels**.
All physical information comes exclusively from the maintainer.

**Forbidden:**

- Inventing, estimating or "plausibly assuming" measured values
- *Deriving* a pinout from a photo and treating it as fact
- Claiming something is "confirmed" when it has only been researched or guessed
- Writing a driver based on an unverified pinout without clearly flagging
  that in the code and in the reply

**Instead:** When information is missing, write a
**measurement request** following the scheme in `docs/measurement-requests.md`
and file it there. The maintainer works through it and enters the results in
`hardware/measurements.md`.

---

## 3. Evidence markers

Every factual claim in this repo carries exactly one marker:

| Marker | Meaning |
|---|---|
| `[MEASUREMENT]` | The maintainer measured it with an instrument. Include date + method. |
| `[CAPTURE]` | Derived from a recording in `captures/`. Include the file name. |
| `[PHOTO]` | Read from an image in `hardware/photos/` (marking, part count). |
| `[RESEARCH]` | From a datasheet or a source. Include the link. |
| `[ASSUMPTION]` | A guess. Must name a test that would check it. |
| `[REFUTED]` | Was once assumed, has been refuted by measurement. **Do not delete** — leave it in place so the dead end is not walked again. |

An `[ASSUMPTION]` becomes a fact **only** through `[MEASUREMENT]` or
`[CAPTURE]`. Not through plausibility, not through repetition, not because
three sources say the same thing.

Statements the maintainer makes without having measured them (e.g. "I own
more than 5 tags") are written as **"maintainer statement"** and carry no
evidence marker.

---

## 4. HISTORY.md is the long-term memory

`HISTORY.md` is the most important state of this project. Claude Code has
no memory between sessions — this file replaces it.

**Rules:**

- At **session start**: read `HISTORY.md` and `docs/open-questions.md`
  before anything else happens.
- On **every new insight**: append an entry immediately. Do not collect them
  for the end of the session — sessions get cut off.
- **Record failures too.** A documented dead end is just as valuable as a
  success. "Panel did not respond to init variant X" belongs in there.
- Entries are **appended, never rewritten**. Corrections come as a new
  entry referring to the old one.

One-time exception: on 2026-09-23 the maintainer approved translating the
whole repo into English, including existing `HISTORY.md` entries. The
unaltered German original is kept in `docs/archive/HISTORY.de.md`.

### progress.md — the living checklist

`progress.md` (repo root) lists what has been done and what is still open,
with an owner per item (maintainer / Claude Code). It is **separate** from
`HISTORY.md` and does not replace it (maintainer decision, 2026-09-25):
`HISTORY.md` is the append-only chronology with evidence, `progress.md` is
the current checklist and is **edited in place**.

**Rules:**

- At **session start**: read `progress.md` together with `HISTORY.md` and
  `docs/open-questions.md`, and take its open items into account when
  planning the session.
- **Keep it current in the same commit** as the change that alters the
  state: tick finished items, add new open items (new measurement request,
  new decision, new to-do), remove nothing silently — finished items move
  to "Done".
- Update the "Last updated" line and the one-paragraph summary when the
  overall state changes.
- A ticked item means "done", not "confirmed" — evidence markers stay in
  `HISTORY.md` and the docs.
- Before ending a session: check that `progress.md` matches the
  last `HISTORY.md` entries.

---

## 5. Safety rules (not negotiable)

These rules protect hardware that cannot be re-ordered.

1. **One tag stays untouched** as the reference unit. No soldering, no
   flashing, no unlock. Claude Code never suggests touching the reference
   unit.
2. **Sniff before unlock.** Unlocking the EFR32 irrevocably erases the
   original firmware. As long as the panel's init sequence has not been
   captured and saved, no unlock is suggested.
3. **High voltage on the FPC.** Several pins of the 24-pin connector carry
   about +22 V / −20 V in operation. The logic analyser tolerates max.
   3.6 V. For every measurement request that involves the FPC, Claude Code
   explicitly points out that continuity must be checked unpowered first.
4. **No pinout without measurement.** See rule 2.

---

## 6. Way of working

- **Language:**
  - **Chat** with the maintainer: **German**.
  - **Everything stored in the repo** — documentation, `HISTORY.md`,
    measurement requests, code, identifiers, comments, commit messages:
    **English**.
- **Git workflow:**
  - Commit and **push directly to `main`**. No pull requests needed.
  - **Ask first for large changes**, for example: changes to the rules in
    this file, restructuring or deleting files, rewriting existing content
    (as opposed to appending), mass edits across many files, or
    architectural changes to the analysis tools.
  - Small, self-contained changes (a new `HISTORY.md` entry, a new
    measurement request, a bug fix, a doc correction) are pushed without
    asking.
- **No agreeing for the sake of it.** If one of the maintainer's approaches
  is technically questionable, say so and give reasons. Disagreement is more
  useful here than agreement.
- **Name uncertainty.** "I don't know whether the panel is 800×480" is a
  better answer than an invented number with decimal places.
- **Small steps.** Better one verified insight than five guessed ones.
- If something is unclear: **ask** instead of guessing. The maintainer may
  simply have forgotten to provide a piece of information.

---

## 7. Repo structure

```
CLAUDE.md                  this file
README.md                  project overview
HISTORY.md                 long-term memory, chronological
progress.md                living checklist: done / open, per owner
TOOLS.md                   available instruments
docs/
  hardware.md              component and platform knowledge
  pinout.md                FPC pinout: hypothesis + verification
  capture-protocol.md      instructions for the logic analyser capture
  measurement-requests.md  open measurement requests to the maintainer
  open-questions.md        what is unresolved
  firmware-plan.md         custom firmware on the EFR32 (path B)
  netlist-from-photos.md   traces reconstructed from PCB photos
  oepl-pin-comparison.md   OpenEPaperLink pin maps vs. our board
  references.md            sources
  archive/                 superseded originals (e.g. German HISTORY)
captures/                  raw captures (.sr, .csv) — not in git
analysis/                  decoders and evaluation scripts
  requirements.txt         Python dependencies
hardware/
  measurements.md          measurement log (filled in by the maintainer)
  photos/                  board photos
firmware/                  later driver / firmware code
```

---

## 8. Definition of done for an insight

An insight counts as established when:

1. it is in `HISTORY.md`, with date and method,
2. it carries an evidence marker from section 3,
3. for `[CAPTURE]`, the raw file is reproducibly available in `captures/`,
4. for `[MEASUREMENT]`, the row in `hardware/measurements.md` is filled in.

Everything else is a hypothesis and is called that.
