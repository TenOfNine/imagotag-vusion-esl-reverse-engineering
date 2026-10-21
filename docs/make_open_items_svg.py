#!/usr/bin/env python3
"""
make_open_items_svg.py - draw docs/open-items.svg, a one-page overview of
the open items in progress.md.

The content lives in COLUMNS / PARKED / SAFETY below. Edit it together with
progress.md, then run:

    python3 docs/make_open_items_svg.py

Only the standard library is used. The SVG has its own white background so
it stays readable in GitHub's light and dark themes.
"""

from __future__ import annotations

import os
import textwrap
from xml.sax.saxutils import escape

SNAPSHOT = "2026-10-21"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "open-items.svg")

# owner -> (legend label, fill, stroke, short tag on the card)
OWNERS = {
    "M": ("Maintainer", "#e8f0fe", "#1a56db", "Maintainer"),
    "C": ("Claude Code", "#e6f4ea", "#137333", "Claude"),
    "D": ("Decision (maintainer)", "#fef3e0", "#b45309", "Decision"),
    "T": ("Third party", "#f1f3f4", "#5f6368", "3rd party"),
}

# Each card: id, owner, title, body lines, footer (answers / needs), dashed
COLUMNS = [
    ("1 · Now — no hardware needed", [
        ("doc_ds", "M", "Datasheet check", [
            "Compare the QFN40 pin table in "
            "docs/oepl-pin-comparison.md §2 with the EFR32FG22 datasheet",
        ], "feeds: M-012, board definition", False),
        ("about", "M", "GitHub \"About\" text", [
            "Outdated: \"three-colour\", \"Docs in German\" "
            "(repo settings)",
        ], None, False),
        ("i2", "T", "Issue #2 — still open there", [
            "Answers 2, 4–6 received and evaluated (panel-protocol.md §8). "
            "Open: flash marking (3), public OEPL branch (7, offered early "
            "on request)",
        ], None, False),
        ("oepl3", "T", "Third-party OEPL port", [
            "Announced in issue #2, not in OEPL v43. Claude Code watches "
            "and reuses it instead of duplicating",
        ], None, False),
    ]),
    ("2 · Tag 02 — non-destructive", [
        ("m011", "M", "M-011 · SWD lock status", [
            "• Confirm vias for QFN pins 22/23 (unpowered)",
            "• Power-cycle before every attempt",
            "• J-Link: commander device info + commander security status "
            "— nothing else",
            "• Send the full text output",
            "• If not locked: back up the flash (outside the repo)",
        ], "answers: F-05 · basis for F-15 (F-17 only if unlocked)", False),
        ("eval", "C", "Evaluate lock state + flash size", [
            "After M-011: update docs/firmware-plan.md",
        ], "answers: F-17 (256 or 512 kB)", False),
        ("binary", "C", "Init sequence from the binary", [
            "Only if the chip is not locked and the flash was backed up",
        ], "answers: F-04", True),
        ("m012", "M", "M-012 · Verify the pin map", [
            "Unpowered, battery out, FPC unplugged",
            "• FPC 9–14 → QFN 28, 5, 4, 3, 2, 1",
            "• XDt gate → QFN 7",
            "• 8K417 chip (leadless, right of the EFR32) → QFN "
            "26/25/20/21, GND, VCC",
            "• LEDs → QFN / supply",
            "• Macro photo of the 8K417 chip",
        ], "answers: F-14, F-16", False),
    ]),
    ("3 · Decisions", [
        ("f15", "D", "F-15 · Unlock tag 02?", [
            "Only if the chip is locked. Erases tag 02's original "
            "firmware; tag 01 and the others keep theirs",
            "Must be written into CLAUDE.md before any unlock",
            "New basis: docs/open-questions.md F-15",
        ], "blocks: flashing (steps 1–5)", False),
        ("path", "D", "Bring-up path", [
            "Own bring-up firmware first, or wait for the third-party "
            "OEPL port? Ask its author for the early branch?",
        ], "blocks: step 5", False),
    ]),
    ("4 · Firmware on tag 02", [
        ("m013", "M", "M-013 · Run step-1 image", [
            "Image written (firmware/bringup, emulator-tested). Flash after "
            "M-011 + backup or F-15; tag 02, FPC unplugged; send the RTT "
            "report",
        ], "answers: F-17", False),
        ("tool", "C", "Toolchain", [
            "Bare-metal gcc-arm-none-eabi ready for steps 2–4; GSDK 4.4.1 "
            "/ slc for OEPL",
        ], None, False),
        ("board", "C", "Board definition", [
            "OEPL dev slot 0xF0…0xFA; display on port C (USART0?), "
            "BUSY on PA07",
        ], "needs: M-012 + datasheet check", False),
        ("s13", "C", "Bring-up steps 2–3", [
            "Panel power, reset, BUSY (1 ms quirk) · OTP read: chip ID "
            "0D04, bank check, all 112 bytes",
            "Maintainer flashes, sends RTT log + SLogic capture",
        ], "needs: F-15 · confirms the pin map", False),
        ("s4", "C", "Step 4 · first image", [
            "Vendor sequence (panel-protocol.md §7): init from the OTP, "
            "10 + 96,000 bytes, 04, 12 00, turn-off DC/DC + 6 s wait. "
            "E6 temperature from the EFR32 sensor — not ucbwry. "
            "Only after step 3",
        ], "confirms: F-02, F-03, F-13", False),
        ("s5", "C", "Step 5 · OEPL port", [
            "Board type + Pervasive driver. On a 256 kB part the app must "
            "shrink to ≤ 208 kB (v43: 233.6 kB) — or reuse the "
            "third-party port",
        ], "needs: bring-up path decision, F-17", False),
    ]),
]

ARROWS = [
    ("m011", "eval"),
    ("eval", "binary"),
    ("m011", "f15"),
    ("f15", "m013"),
    ("m013", "tool"),
    ("tool", "board"),
    ("board", "s13"),
    ("s13", "s4"),
    ("s4", "s5"),
]

PARKED = ("Parked / low priority: M-005 XDt in detail (path A only) · "
          "F-10 disable the EFR32 (path A) · F-11 FPC test points TP1–TP3 · "
          "F-12 refresh-rate limits (≈ 22 s refresh + 6 s turn-off per update)")
SAFETY = ("Safety (CLAUDE.md §5): tag 01 is never touched · no unlock "
          "before F-15 is decided and written into CLAUDE.md · FPC checks "
          "unpowered first (≈ ±20 V on the FPC, logic analyser max. 3.6 V)")

# ---------------------------------------------------------------- layout
W = 1280
MARGIN = 24
GAP = 20
COL_W = (W - 2 * MARGIN - 3 * GAP) // 4
PAD = 12
TITLE_LH = 18
BODY_LH = 16
WRAP = 40            # characters per body line at 12 px
CARD_GAP = 16
TOP = 128            # y of the column headers
FONT = "Segoe UI, Helvetica, Arial, sans-serif"


def wrap(text: str, width: int = WRAP) -> list[str]:
    indent = "  " if text.startswith("• ") else ""
    return textwrap.wrap(text, width, subsequent_indent=indent) or [""]


def card_lines(card) -> tuple[list[str], list[str]]:
    _, _, title, body, footer, _ = card
    lines = []
    for b in body:
        lines += wrap(b)
    foot = wrap(footer, WRAP + 2) if footer else []
    return lines, foot


def card_height(card) -> int:
    lines, foot = card_lines(card)
    h = PAD + TITLE_LH + 4 + len(lines) * BODY_LH
    if foot:
        h += 6 + len(foot) * BODY_LH
    return h + PAD


def build() -> str:
    boxes = {}
    out = []
    col_bottom = 0
    for ci, (header, cards) in enumerate(COLUMNS):
        x = MARGIN + ci * (COL_W + GAP)
        out.append(f'<rect x="{x}" y="{TOP}" width="{COL_W}" height="30" '
                   f'rx="6" fill="#202124"/>')
        out.append(f'<text x="{x + 12}" y="{TOP + 20}" class="col">'
                   f'{escape(header)}</text>')
        y = TOP + 30 + CARD_GAP
        for card in cards:
            cid, owner, title, _, _, dashed = card
            _, fill, stroke, tag = OWNERS[owner]
            h = card_height(card)
            boxes[cid] = (x, y, COL_W, h)
            dash = ' stroke-dasharray="6 4"' if dashed else ""
            out.append(f'<rect x="{x}" y="{y}" width="{COL_W}" height="{h}" '
                       f'rx="8" fill="{fill}" stroke="{stroke}" '
                       f'stroke-width="1.5"{dash}/>')
            out.append(f'<rect x="{x}" y="{y}" width="6" height="{h}" '
                       f'rx="3" fill="{stroke}"/>')
            ty = y + PAD + 13
            out.append(f'<text x="{x + PAD + 4}" y="{ty}" class="title">'
                       f'{escape(title)}</text>')
            out.append(f'<text x="{x + COL_W - PAD}" y="{ty}" class="owner" '
                       f'fill="{stroke}" text-anchor="end">'
                       f'{escape(tag)}</text>')
            lines, foot = card_lines(card)
            ly = ty + 4 + BODY_LH
            for line in lines:
                out.append(f'<text x="{x + PAD + 4}" y="{ly}" class="body" '
                           f'xml:space="preserve">{escape(line)}</text>')
                ly += BODY_LH
            if foot:
                ly += 6
                for line in foot:
                    out.append(f'<text x="{x + PAD + 4}" y="{ly}" '
                               f'class="foot" fill="{stroke}">'
                               f'{escape(line)}</text>')
                    ly += BODY_LH
            y += h + CARD_GAP
        col_bottom = max(col_bottom, y)

    arrows = []
    for a, b in ARROWS:
        ax, ay, aw, ah = boxes[a]
        bx, by, bw, bh = boxes[b]
        if abs(ax - bx) < 1:                       # same column: down
            x1 = ax + aw / 2
            arrows.append(f'<path d="M{x1},{ay + ah} L{x1},{by - 3}" '
                          f'class="arrow"/>')
        else:                                      # next column: right
            x1, x2 = ax + aw, bx - 3
            y1 = ay + min(ah / 2, 40)
            y2 = by + min(bh / 2, 40)
            xm = x1 + (x2 - x1) / 2
            arrows.append(f'<path d="M{x1},{y1} L{xm},{y1} L{xm},{y2} '
                          f'L{x2},{y2}" class="arrow"/>')

    # footer strips
    fy = col_bottom + 4
    foot = []
    for text, fill, stroke in ((PARKED, "#ffffff", "#9aa0a6"),
                               (SAFETY, "#fce8e6", "#c5221f")):
        lines = textwrap.wrap(text, 200)
        h = 2 * 10 + len(lines) * BODY_LH
        dash = ' stroke-dasharray="6 4"' if fill == "#ffffff" else ""
        foot.append(f'<rect x="{MARGIN}" y="{fy}" width="{W - 2 * MARGIN}" '
                    f'height="{h}" rx="8" fill="{fill}" stroke="{stroke}" '
                    f'stroke-width="1.5"{dash}/>')
        ly = fy + 10 + 12
        for line in lines:
            foot.append(f'<text x="{MARGIN + 14}" y="{ly}" class="body">'
                        f'{escape(line)}</text>')
            ly += BODY_LH
        fy += h + 10
    H = fy + MARGIN - 10

    # legend
    legend = []
    lx = MARGIN
    for key in ("M", "C", "D", "T"):
        label, fill, stroke, _ = OWNERS[key]
        legend.append(f'<rect x="{lx}" y="84" width="16" height="16" rx="4" '
                      f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        legend.append(f'<text x="{lx + 22}" y="97" class="body">'
                      f'{escape(label)}</text>')
        lx += 40 + len(label) * 7
    legend.append(f'<rect x="{lx}" y="84" width="16" height="16" rx="4" '
                  f'fill="#ffffff" stroke="#5f6368" stroke-width="1.5" '
                  f'stroke-dasharray="4 3"/>')
    legend.append(f'<text x="{lx + 22}" y="97" class="body">conditional / '
                  f'parked</text>')
    lx += 160
    legend.append(f'<path d="M{lx},92 L{lx + 34},92" class="arrow"/>')
    legend.append(f'<text x="{lx + 44}" y="97" class="body">'
                  f'leads to / unblocks</text>')

    head = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}">',
        "<title>Open items — RFRTx026D / EL074TS1</title>",
        "<style>"
        ".h1{font-size:22px;font-weight:700;fill:#202124}"
        ".sub{font-size:13px;fill:#5f6368}"
        ".col{font-size:14px;font-weight:700;fill:#ffffff}"
        ".title{font-size:13.5px;font-weight:700;fill:#202124}"
        ".owner{font-size:10.5px;font-weight:700;letter-spacing:.3px}"
        ".body{font-size:12px;fill:#3c4043}"
        ".foot{font-size:11.5px;font-style:italic}"
        ".arrow{fill:none;stroke:#5f6368;stroke-width:1.6;"
        "marker-end:url(#tip)}"
        "</style>",
        '<defs><marker id="tip" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#5f6368"/></marker></defs>',
        f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
        f'<text x="{MARGIN}" y="44" class="h1">Open items — VUSION 7.4" '
        f'BWRY (RFRTx026D / EL074TS1)</text>',
        f'<text x="{MARGIN}" y="68" class="sub">Snapshot {SNAPSHOT} · '
        f'source: progress.md (authoritative) · work tag: tag 02</text>',
    ]
    return "\n".join(head + legend + out + arrows + foot + ["</svg>"]) + "\n"


if __name__ == "__main__":
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(build())
    print(f"wrote {OUT}")
