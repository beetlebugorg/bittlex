"""The build guide: an A4 HTML page set with step renders and cable diagrams, printed to PDF with Chromium.

Run after pod.py (it reads stl/, wires.json and checks.json):  python guide.py [--no-render]
  doc/iso/*.png               step figures (iso_render.py; --no-render uses the ones there)
  guide/index.html            the guide (also on the site)
  bittle_pi_addon_guide.pdf   the guide, printed by Chromium (headless)
The PDF and the HTML are committed: the site build (GitHub Actions) only copies them.
"""
import html
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import pod      # noqa: E402
import render   # noqa: E402
import docs     # noqa: E402
from bittle_platform import interface as PI   # noqa: E402

GDIR = os.path.join(HERE, "guide")
WIRES = json.load(open(os.path.join(pod.OUT, "wires.json")))
CHECKS = json.load(open(os.path.join(pod.OUT, "checks.json")))
W = {(w["group"], w["wire"]): w for w in WIRES["wires"]}
VIEWER = docs.VIEWER
E = html.escape

# --------------------------------------------------------------------------
# The parts of each step (render.py keys)
# --------------------------------------------------------------------------


def keys(*models):
    return [k for k in render.ELEC if k.split("__")[0] in models]


def sub(model, pred):
    return [k for k in render.ELEC if k.split("__")[0] == model and pred(k.split("__")[1])]


ROBOT = ["shoulder", "plate", "cover", "biboard_header__header"]
SPK = keys("speaker")
MIC = keys("mic_sph0645") + sub("wires_mic", lambda s: s.endswith("_dev"))
AMP = keys("amp_ns4168", "wires_speaker")
STACK = keys("pisugar_s", "pizero", "battery", "sd_card", "stack_screws", "pi_plugs")
SPLICE = keys("wires_splice")
UART_PI = sub("wires_uart", lambda s: not s.endswith("_dev"))
UART_DEV = sub("wires_uart", lambda s: s.endswith("_dev"))
AMPW = keys("wires_amp")
MICW = sub("wires_mic", lambda s: not s.endswith("_dev"))
PANEL = ["panel"]

# The build steps: title, the parts in place before, the new parts, camera, lift, text (one idea per line), check
STEPS = []


def step(title, new, cam, lines, check=None, lift=None, note=None, only=None, base=None):
    """only: show just these parts of the ones already in place (a clear view into a crowded corner).
    base: parts that come in with this step but do not move in its figure (the body under its inserts).
    iso_render.py draws the figure of each step from before and new (cam and lift are not used there)."""
    before = sum((s["new"] + s["base"] for s in STEPS), list(ROBOT)) + list(base or [])
    if only is not None:
        before = list(ROBOT) + [k for k in before if k in only]
    STEPS.append(dict(title=title, before=before, new=new, cam=cam, lines=lines, check=check, lift=lift, note=note, base=list(base or [])))


def build_steps():
    STEPS.clear()
    step("Inserts or nuts", ["mount_inserts", "panel_inserts"], "high",
         ["Put an insert or a nut into each of the 6 bosses: 4 in the floor, 2 on the speaker posts.",
          "FDM (PLA): press each M3 heat-set insert in flush with a soldering iron.",
          "Resin: put an M2.5 nut into each hex pocket, with a drop of superglue on its edge."],
         note="Page 4 has the hardware, the tools and the steps for each way.", base=["body"])
    step("Screw the body to the cover", ["mount_screws"], "below",
         ["Put the empty body on the cover for screws, the grille to the rear.",
          "From inside the cover, put a screw up through each of the 4 rings into the insert or the nut: M3 x 4 (FDM) or M2.5 x 4 (resin).",
          "Tighten the 4 screws. The floor is on the rings."])
    step("Clip onto the robot", [], "iso",
         ["Remove the stock back cover of the Bittle X.",
          "Clip the cover and the body onto the robot as one unit, in place of the stock cover.",
          "The BiBoard header comes up through the opening in the cover and the notch at the front of the left well."])
    step("Speaker", SPK, "rear",
         ["Push the two wings of the speaker down into the side grooves at the rear.",
          "The speaker body goes to the rear, toward the grille."])
    step("Mic", MIC, "mic",
         ["Plug the six mic jumpers onto the mic header. Use 15 cm jumpers on GND and 3V.",
          "Drop the mic into the slots in the post and the ledge on the right wall, near the front.",
          "The port faces the wall. The header is at the front edge, the plugs point into the body."],
         check="The board sits in both slots. The post, the ledge and a stop hold it.")
    step("Amp and speaker lead", AMP, "amp",
         ["Plug the speaker lead into the 2-pin connector at the rear end of the amp.",
          "Plug the flat amp cable into the 5-pin connector at the front end. G is at the top.",
          "Put the bottom edge of the amp into the slot along the right wall, parts to the inside.",
          "Tilt the top edge under the two nubs. Set it with a dab of glue.",
          "Two forks under the panel hold the top edge later.",
          "Let the amp cable hang out of the top. It goes in after the BiBoard jumpers."])
    step("Pi + PiSugar S stack", STACK, "stack",
         ["Set the PiSugar AUTO switch first: it is under the cell.",
          "Push the stack down into the grooves of the two end posts until it stops.",
          "The ports are up, the 40-pin header down and toward the left wall, the SD card at the rear."],
         check="If the stack is not fully down, the panel does not slide on later.")
    step("Splices (BCLK and LRCLK)", SPLICE, "well",
         ["Plug the Pi end of each splice: BCLK on pin 12, LRCLK on pin 35.",
          "The LRCLK sleeve stands beside the BiBoard plugs, the BCLK sleeve at the middle of the left well."],
         note="Each splice is a Y: one Pi end, one mic end, one amp end. See the cable cards.")
    step("BiBoard jumpers: Pi ends", UART_PI, "well",
         ["Push the female end of each BiBoard jumper onto the Pi: TX2 (gray) on pin 10, RX2 (white) on pin 8, GND (black) on pin 6.",
          "Lay the excess of each one in a loop by the left wall.",
          "Leave the male ends free. They go onto the BiBoard last."])
    step("Amp cable", AMPW, "ampcable",
         ["Lay the flat amp cable on edge, as it leaves the plug, G on top. Do not twist it.",
          "It steps down, runs forward to the front wall and across under the mic plugs. Past the front post it turns rearward, "
          "runs across behind the front-left notch, and turns rearward along the left well.",
          "Peel off each wire at its own height: DIN onto pin 40, LRC and BCLK into the free sockets of their splices, G onto pin 14, V onto pin 2."])
    step("Mic jumpers", MICW, "micw",
         ["Run the mic jumpers straight across behind the front wall, then rearward along the left well.",
          "Plug them from the lowest up: 3V on pin 1, GND on pin 9, BCLK and LRCL into their splices, DOUT on pin 38, SEL on pin 39."])
    step("BiBoard ends", UART_DEV, "bbend",
         ["Push the male ends of the three BiBoard jumpers into the BiBoard socket: TX2, RX2, GND.",
          "Reach the plugs from the side, through the door opening in the left wall.",
          "The two +5V sockets stay empty: the PiSugar powers the Pi."], only=["body"] + STACK + UART_PI,
         note="The other wires are not shown here, for a clear view into the front-left corner.")
    step("Door", ["door"], "door",
         ["Slide the door down into the two grooves of the opening in the left wall.",
          "It stands on the wall under it. The panel holds it down."])
    step("Panel", ["panel", "panel_screws"], "iso",
         [f"Put the panel down {pod.LID_SLIDE:g} mm behind its place, and slide it forward.",
          "Put the two panel screws down through the panel into the speaker posts: M3 x 12 (FDM) or M2.5 x 12 (resin).",
          "The PiSugar power switch is in the HDMI opening, beside the plug. Move it with a pen tip or a toothpick.",
          "Press the PiSugar button through the large opening with a fingertip or a pen tip."],
         check="To open: take out the two screws and slide the panel rearward.")


def images():
    """The figures of iso_render.py (light theme, transparent background), relative to guide/."""
    out = {k: f"../doc/iso/{k}-light.png" for k in ("hero", "exploded")}
    out.update({i: f"../doc/iso/step{i:02d}-light.png" for i in range(1, len(STEPS) + 1)})
    return out


# --------------------------------------------------------------------------
# Vector diagrams (SVG)
# --------------------------------------------------------------------------
INK, MUTE, LINE = "#16181a", "#80868d", "#e2e2dc"


def _t(x, y, s, size=11, w=400, anchor="start", col=INK, mono=False):
    fam = "JetBrains Mono, monospace" if mono else "Noto Sans, sans-serif"
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-size="{size}" font-weight="{w}" '
            f'text-anchor="{anchor}" fill="{col}">{E(s)}</text>')


def dupont(x, y, male=False, angle_right=True):
    """A Dupont housing (black), 9 x 26 px, its mouth at x. male: a pin sticks out."""
    d = 1 if angle_right else -1
    x0 = x if d > 0 else x - 26
    s = f'<rect x="{x0}" y="{y - 4.5}" width="26" height="9" rx="1.5" fill="#202124"/>'
    if male:
        px = x0 + 26 if d > 0 else x0 - 9
        s += f'<rect x="{px}" y="{y - 1}" width="9" height="2" fill="#c9a227"/>'
    else:
        hx = x0 + 22 if d > 0 else x0 + 1
        s += f'<rect x="{hx}" y="{y - 1.6}" width="3" height="3.2" fill="#6b6b6b"/>'
    return s


def wire(x0, y0, x1, y1, col):
    edge = ' stroke-opacity="1"' if col.lower() not in ("#f2f2ef",) else ""
    outline = f'<path d="M{x0},{y0} C{(x0 + x1) / 2},{y0} {(x0 + x1) / 2},{y1} {x1},{y1}" stroke="#9a9a9e" stroke-width="5" fill="none"/>' \
        if col.lower() in ("#f2f2ef", "#9ea0a4") else ""
    return outline + f'<path d="M{x0},{y0} C{(x0 + x1) / 2},{y0} {(x0 + x1) / 2},{y1} {x1},{y1}" stroke="{col}" stroke-width="3.6" fill="none"{edge}/>'


def cable_card(title, left, rows, right_note="", height=None):
    """left: (kind, label) at the shared end, or None for single wires. rows: [(color, wire name, left label, right label,
    right kind)] kind = 'f', 'm', 'ph', 'sleeve'."""
    n = len(rows)
    h = height or max(62, 22 + n * 18)
    w = 560
    s = f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg">'
    ys = [h / 2 + (i - (n - 1) / 2) * 18 for i in range(n)]
    xl, xr = 150, 420
    if left and left[0] == "ph":                           # one PH2.0 plug: every wire leaves it
        y0, y1 = ys[0] - 11, ys[-1] + 11
        s += f'<rect x="{xl - 26}" y="{y0}" width="26" height="{y1 - y0}" rx="3" fill="#efe6d2" stroke="#bfb39a"/>'
        s += _t(xl - 34, h / 2 - 4, left[1], 11, 600, "end") + _t(xl - 34, h / 2 + 11, left[2], 9.5, 400, "end", MUTE)
        for i, (col, name, ll, rl, rk) in enumerate(rows):
            yp = ys[i]
            s += wire(xl, yp, xr, yp, col)
            s += _t(xl + 8, yp - 5, name, 9, 600, col=MUTE)
    else:
        for i, (col, name, ll, rl, rk) in enumerate(rows):
            yp = ys[i]
            s += dupont(xl, yp, male=(ll == "m"), angle_right=False)
            s += _t(xl - 40, yp + 3.5, name, 10.5, 600, "end")
            s += wire(xl, yp, xr, yp, col)
    for i, (col, name, ll, rl, rk) in enumerate(rows):
        yp = ys[i]
        if rk == "sleeve":
            s += f'<rect x="{xr}" y="{yp - 5}" width="22" height="10" rx="5" fill="#f2f2ef" stroke="#9a9a9e"/>'
        else:
            s += dupont(xr, yp, male=(rk == "m"))
        s += _t(xr + (44 if rk != "m" else 48), yp + 4, rl, 11, 500)
    if right_note:
        s += _t(w - 4, h - 6, right_note, 9.5, 400, "end", MUTE)
    return s + "</svg>"


def splice_card():
    """The Y splice: a Pi end, a mic end and an amp end joined in a white sleeve."""
    w, h = 560, 120
    s = f'<svg viewBox="0 0 {w} {h}" width="100%" xmlns="http://www.w3.org/2000/svg">'
    for k, (col, name, pin) in enumerate((("#3a6fd8", "BCLK", "pin 12"), ("#2e9b4f", "LRCLK", "pin 35"))):
        y = 34 + k * 52
        s += _t(20, y + 4, name, 11, 700)
        s += dupont(150, y, angle_right=False) + _t(112, y + 4, pin, 10.5, 500, "end")
        s += wire(150, y, 280, y, col)
        s += f'<rect x="280" y="{y - 6}" width="34" height="12" rx="6" fill="#f2f2ef" stroke="#9a9a9e"/>'
        s += wire(314, y, 420, y - 12, col) + wire(314, y, 420, y + 12, col)
        s += dupont(420, y - 12) + _t(462, y - 8, "mic " + ("BCLK" if k == 0 else "LRCL"), 10.5, 500)
        s += dupont(420, y + 12, male=True) + _t(466, y + 16, "amp cable " + ("BCLK" if k == 0 else "LRC"), 10.5, 500)
    return s + "</svg>"


def pi_header_svg():
    """The 2 x 20 header seen from the component face, pin 1 at the SD card end (rear). The used pins are in the
    color of their wire."""
    used = {}
    for (g, lab), w in W.items():
        if w["to"].startswith("pin "):
            used[int(w["to"].split()[1])] = (w["color"], f"{w['from']}")
    for t, n in (("bclk", 12), ("lrclk", 35)):
        used[n] = (W[("splice", t)]["color"], f"{t.upper()} splice")
    names = {1: "3V3", 2: "5V", 4: "5V", 6: "GND", 9: "GND", 14: "GND", 20: "GND", 25: "GND", 30: "GND", 34: "GND", 39: "GND",
             17: "3V3", 8: "TXD", 10: "RXD", 12: "G18", 35: "G19", 38: "G20", 40: "G21"}
    w_, h_ = 640, 250
    s = f'<svg viewBox="0 0 {w_} {h_}" width="100%" xmlns="http://www.w3.org/2000/svg">'
    p0, dx = 40, 28
    s += f'<rect x="{p0 - 16}" y="88" width="{19 * dx + 32}" height="60" rx="4" fill="#1d1d1f"/>'
    for n in range(1, 41):
        col_i = (n - 1) // 2
        x = p0 + col_i * dx
        y = 104 if n % 2 else 132
        c, lab = used.get(n, ("#5f6166", ""))
        s += f'<circle cx="{x}" cy="{y}" r="8" fill="{c}" stroke="{"#9a9a9e" if c.lower() in ("#f2f2ef", "#9ea0a4") else "none"}"/>'
        s += _t(x, y + 3.2, str(n), 7.5, 700, "middle", "#ffffff" if c.lower() not in ("#f2f2ef", "#f0c419", "#9ea0a4") else INK)
        if lab:
            ty = 70 if n % 2 else 168
            s += f'<line x1="{x}" y1="{y + (-9 if n % 2 else 9)}" x2="{x}" y2="{ty + (6 if n % 2 else -10)}" stroke="{LINE}"/>'
            s += (f'<text transform="translate({x + 3},{ty}) rotate(-50)" font-family="Noto Sans" font-size="9.5" font-weight="600" fill="{INK}">'
                  f'{E(lab)}</text>' if n % 2 else
                  f'<text transform="translate({x + 3},{ty}) rotate(50)" font-family="Noto Sans" font-size="9.5" font-weight="600" fill="{INK}">'
                  f'{E(lab)}</text>')
    s += _t(p0 - 16, 240, "Pin 1 is at the SD card end (rear). Odd pins: inner row (top). Even pins: board edge (bottom).", 10, 400, col=MUTE)
    return s + "</svg>"


def board_pins_svg(title, pins, note):
    """pins: [(label, color)] in the order printed on the board, top to bottom."""
    n = len(pins)
    h = 40 + n * 24
    s = f'<svg viewBox="0 0 250 {h}" width="100%" xmlns="http://www.w3.org/2000/svg">'
    s += f'<rect x="20" y="16" width="70" height="{n * 24 + 8}" rx="6" fill="#1f2a36"/>'
    for i, (lab, col) in enumerate(pins):
        y = 32 + i * 24
        s += f'<rect x="78" y="{y - 6}" width="18" height="12" rx="2" fill="#c9a227"/>'
        s += _t(70, y + 4, lab, 10.5, 700, "end", "#ffffff")
        if col:
            s += wire(96, y, 160, y, col) + dupont(160, y)
    s += _t(125, h - 4, note, 9.5, 400, "middle", MUTE)
    return s + "</svg>"


# --------------------------------------------------------------------------
# The pages
# --------------------------------------------------------------------------
CSS = r"""
@page { size: A4; margin: 0; }
:root { --grid: linear-gradient(#ecece6 1px, transparent 1px), linear-gradient(90deg, #ecece6 1px, transparent 1px); }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font-family: "Noto Sans", sans-serif; color: #16181a; font-size: 9.6pt; line-height: 1.45; background: #e9e9ec; }
.page { width: 210mm; height: 297mm; padding: 16mm 17mm 18mm; position: relative; background: #fff; overflow: hidden;
        page-break-after: always; margin: 0 auto 8mm; }
@media print { body { background: #fff; } .page { margin: 0; } }
.folio { position: absolute; bottom: 9mm; left: 17mm; right: 17mm; display: flex; justify-content: space-between;
         font: 7pt/1.4 "JetBrainsMono Nerd Font", "Noto Sans Mono", monospace; color: #80868d; border-top: .4pt solid #e2e2dc; padding-top: 2.5mm; }
h1 { font-size: 30pt; font-weight: 800; letter-spacing: -.02em; line-height: 1.05; margin: 0 0 3mm; }
h2 { font-size: 17pt; font-weight: 700; letter-spacing: -.01em; margin: 0 0 4mm; }
h3 { font-size: 10.5pt; font-weight: 700; margin: 5mm 0 1.5mm; }
.kicker { font: 600 7.5pt/1.3 "JetBrainsMono Nerd Font", "Noto Sans Mono", monospace; letter-spacing: .08em; text-transform: uppercase; color: #0a7f63; margin-bottom: 2mm; }
.lead { font-size: 11pt; line-height: 1.5; color: #4a4f55; font-weight: 300; }
.muted { color: #80868d; }
.cover { padding: 0; }
.cover .art { position: absolute; inset: 0 0 92mm 0; padding: 12mm 20mm 4mm; background-color: #fbfbf9; background-image: var(--grid); background-size: 24px 24px; }
.cover .art img { width: 100%; height: 100%; object-fit: contain; }
.cover .title { position: absolute; left: 17mm; right: 17mm; bottom: 26mm; }
.cover .title h1 { font-size: 40pt; }
.cover .meta { display: flex; gap: 10mm; margin-top: 6mm; font-size: 8.5pt; color: #80868d; }
.cover .meta b { display: block; color: #16181a; font-size: 9.5pt; }
.bar { position: absolute; left: 0; right: 0; bottom: 0; height: 3mm; background: #0a7f63; }
.grid2 { display: grid; grid-template-columns: 1fr 1fr; gap: 6mm; }
.grid3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 5mm; }
table { width: 100%; border-collapse: collapse; font-size: 8.6pt; }
th { text-align: left; font: 600 7pt/1.3 "JetBrainsMono Nerd Font", "Noto Sans Mono", monospace; letter-spacing: .06em; text-transform: uppercase; color: #80868d;
     border-bottom: .8pt solid #16181a; padding: 1.6mm 2mm 1.6mm 0; }
td { border-bottom: .4pt solid #e2e2dc; padding: 1.8mm 2mm 1.8mm 0; vertical-align: top; }
td.n { white-space: nowrap; font-variant-numeric: tabular-nums; }
.sw { display: inline-block; width: 9pt; height: 9pt; border-radius: 50%; vertical-align: -1.5pt; margin-right: 1.5mm; border: .5pt solid #b0b0b5; }
.card { border: .5pt solid #e2e2dc; border-radius: 3mm; padding: 3mm 4mm 2mm; margin-bottom: 3.2mm; break-inside: avoid; }
.card h4 { margin: 0 0 .5mm; font-size: 9.6pt; }
.card p { margin: 0 0 1mm; font-size: 8.4pt; color: #4a4f55; }
.tag { display: inline-block; font: 600 6.8pt/1.3 "JetBrainsMono Nerd Font", "Noto Sans Mono", monospace; padding: .3mm 2mm;
       border-radius: 9mm; border: .5pt solid #c9c9c1; color: #4a4f55; margin-left: 1.5mm; vertical-align: 1pt; }
.tag.o { border-color: #0a7f63; color: #0a7f63; }
.step { display: grid; grid-template-columns: 1fr; gap: 3mm; margin-bottom: 5mm; break-inside: avoid; }
.step .shot { background-color: #fbfbf9; background-image: var(--grid); background-size: 24px 24px; border: .5pt solid #e2e2dc;
              border-radius: 3mm; overflow: hidden; height: 80mm; padding: 4mm 6mm; display: flex; align-items: center; justify-content: center; }
.step .shot img { width: 100%; height: 100%; object-fit: contain; }
.step .head { display: flex; align-items: baseline; gap: 3mm; }
.num { font: 600 20pt/1 "JetBrainsMono Nerd Font", "Noto Sans Mono", monospace; color: #0a7f63; min-width: 12mm; }
.step h3 { margin: 0; font-size: 13pt; }
.step ol { margin: 1mm 0 0 15mm; padding: 0; }
.step li { margin: 0 0 1mm; }
.check { margin: 1.5mm 0 0 15mm; font-size: 8.4pt; padding: 1.6mm 3mm; border-left: 2pt solid #0a7f63; background: #e3f3ee; }
.note { margin: 1.5mm 0 0 15mm; font-size: 8.4pt; padding: 1.6mm 3mm; border-left: 2pt solid #80868d; background: #f2f2ee; }
.full { background-color: #fbfbf9; background-image: var(--grid); background-size: 24px 24px; border: .5pt solid #e2e2dc; border-radius: 3mm; padding: 4mm; }
.full img { width: 100%; max-height: 190mm; object-fit: contain; }
.callout { font-size: 8.4pt; padding: 2.5mm 3.5mm; background: #f2f2ee; border-radius: 2.5mm; }
.toc div { display: flex; justify-content: space-between; border-bottom: .4pt dotted #c9c9c1; padding: 1.6mm 0; font-size: 10pt; }
"""


def page(body, n, cls=""):
    return (f'<section class="page {cls}">{body}<div class="folio"><span>Bittle X Pi Add-on v{docs.VERSION} · Build guide</span>'
            f'<span>{n}</span></div></section>')


def swatch(c):
    return f'<span class="sw" style="background:{c}"></span>'


def cover(img):
    return (f'<section class="page cover"><div class="art"><img src="{img}"></div><div class="title">'
            f'<div class="kicker">Build guide</div><h1>Bittle X<br>Pi Add-on</h1>'
            f'<div class="lead">A Raspberry Pi Zero 2 W with a battery, a speaker and a microphone, in one rounded box '
            f'that screws to a new back cover of the Petoi Bittle X.</div>'
            f'<div class="meta"><div><b>Add-on v{docs.VERSION}</b>{docs.DATE}</div><div><b>4 + 2 screws</b>M3 inserts (FDM) or M2.5 nuts (resin)</div>'
            f'<div><b>{CHECKS["balance"]["mass_g"]:.0f} g</b>with the electronics</div><div><b>No supports</b>for the add-on parts (FDM)</div></div>'
            f'</div><div class="bar"></div></section>')


def overview(img, n):
    n_steps = (len(STEPS) + 1) // 2                      # build_html: 2 steps on each page, from page 7
    rows = "".join(f"<div><span>{t}</span><span>{p}</span></div>" for t, p in (
        ("What you build", 2), ("Parts to print", 3), ("Inserts or nuts", 4), ("Electronics and cables", 5), ("Pin maps and hardware", 6),
        ("Assembly", 7), ("Wire table", 7 + n_steps), ("Checks, opening and removal", 8 + n_steps)))
    body = (f'<div class="kicker">Overview</div><h2>What you build</h2>'
            f'<div class="grid2"><div><p class="lead">The add-on is a body that screws to a cover for screws, and a slide-on top panel with two screws. '
            f'The cover and the body clip onto the robot as one unit, in place of the stock cover. Every part goes into the body from the top, in the order of this guide. '
            f'You need a screwdriver, a soldering iron for the splices (and the inserts of an FDM print), and a dab of glue for the amp.</p>'
            f'<h3>Directions in this guide</h3><p>Front is the head end of the robot. Left and right are the robot\'s left and right. '
            f'The Pi plugs and the BiBoard header are in the <b>left well</b>. The amp and the mic are on the <b>right wall</b>. '
            f'The speaker is at the rear.</p>'
            f'<h3>Contents</h3><div class="toc">{rows}</div>'
            f'<p class="callout" style="margin-top:5mm">The 3D viewer shows every step with animation: '
            f'<b>{E(VIEWER)}</b></p></div>'
            f'<div class="full"><img src="{img}"></div></div>')
    return page(body, n)


def print_parts(n):
    R = json.load(open(os.path.join(pod.OUT, "plates", "resin_check.json")))
    vol = sum(v["cup_volume_mm3"] for v in R.values())
    cups = ("The resin check found no cups (trapped resin) in these orientations." if vol == 0 else
            f"The resin check found cups (trapped resin, {vol:g} mm³ in total). See resin_check.json.")
    rows = [("pod_body_screw", "pod_body", "Body", "3mf", "floor on the bed"),
            ("pod_panel_screw", "pod_panel", "Top panel (second color)", "stl", "upside down: top on the bed"),
            ("pod_door", "pod_door", "Door", "stl", "flat on its outer face"),
            ("cover_screw", "cover_screw", "Cover for screws", "stl", "on its rear end: tree supports, 14-line brim")]
    tr = "".join(f"<tr><td><b>{t}</b><br><span class='muted'>stl/print/{f}.{x}</span></td><td>{o}</td>"
                 f"<td class='n'>{docs.pod_mass(m)} g</td></tr>" for f, m, t, x, o in rows)
    RF = pod.RESIN_FIT
    body = (f'<div class="kicker">1</div><h2>Parts to print</h2>'
            f'<p class="lead">Print the parts in PLA, in the orientation of the files in stl/print/. '
            f'Each file is for 0.20 mm layers. For 0.10 mm layers, print the *_fine file of the same name.</p>'
            f'<table><tr><th>Part</th><th>On the bed</th><th>Mass</th></tr>{tr}</table>'
            f'<h3>Settings</h3><div class="grid2"><p>Slice with the profiles in profiles/taz-workhorse-se: pla-0.20-standard, or pla-0.10-fine for the *_fine files. '
            f'Use a brim. printdeck.yml has the settings of each part. Walls 2 mm: 4 lines of 0.5 mm. '
            f'The fine panel has smaller hook gaps ({pod.LID_SCREW["gap"]:g} mm).</p>'
            f'<p>pod_body_screw.3mf has support blockers on the two amp nubs: with support on, the nubs get none. '
            f'The panel prints top down: its openings are on the bed. starter_plate_screw.stl (optional) has the same 4 bosses: '
            f'use it to test the inserts or nuts on the cover.</p></div>'
            f'<h3>Print plates</h3>'
            f'<p>stl/plates/ has every part on one bed, in its print orientation. Each 3MF has one object for each part.</p>'
            f'<table><tr><th>Printer</th><th>File</th><th>Orientation</th></tr>'
            f'<tr><td>FDM: LulzBot TAZ Workhorse, 0.5 mm nozzle</td><td>fdm_taz.3mf</td>'
            f'<td>The screw parts as in stl/print/. The cover stands on its rear end: turn on tree supports and a 14-line brim.</td></tr>'
            f'<tr><td>Resin: Peopoly Phenom (first model)</td><td>resin_phenom.3mf</td>'
            f'<td>The resin parts with nut pockets. The body, the panel, the door and the starter plate are tipped 45 deg. '
            f'The cover stands on its rear end. Lift the parts 5 mm in the slicer and add supports. stl/print/resin/ has each part alone.</td></tr></table>'
            f'<div class="grid2"><div><h3>Resin supports</h3><ul style="margin:0;padding-left:5mm">'
            f'<li>Body: the floor is toward the plate. Put the supports on the floor underside, off the screw holes. Sand the marks flat.</li>'
            f'<li>Panel: the open side is toward the plate. The top face has no marks.</li>'
            f'<li>Cover: it stands on its rear end. Put the supports on the rear edge only.</li>'
            f'<li>Door: the outer face is up, tipped 45 deg. The supports go on the inner face and the ears.</li>'
            f'<li>{cups}</li></ul></div>'
            f'<div><h3>Resin fits</h3><ul style="margin:0;padding-left:5mm">'
            f'<li>The resin parts use glued nuts in place of inserts (page 4).</li>'
            f'<li>Door gap {RF["door_gap"]:g} mm, amp slot gap {RF["amp_clr"]:g} mm (a best guess).</li>'
            f'<li>Print the starter plate first to test the nut pockets.</li>'
            f'<li>Wash the parts in IPA and post-cure them before the fit test.</li></ul></div></div>')
    return page(body, n)


def fasteners(n):
    SM, NM = pod.SCREW_MOUNT, pod.NUT_MOUNT
    tip, nut_top = pod.FLOOR_Y0 - SM["web"] + 4.0, NM["floor_y"] + NM["t"]
    body = (f'<div class="kicker">2</div><h2>Inserts or nuts</h2>'
            f'<p class="lead">Six bosses hold the threads for the screws: 4 in the floor for the cover screws, '
            f'and 2 on the speaker posts for the panel screws. An FDM print (PLA) uses M3 heat-set inserts. '
            f'A resin print uses M2.5 nuts with superglue.</p>'
            f'<table><tr><th></th><th>FDM print (PLA): heat-set inserts</th><th>Resin print: glued nuts</th></tr>'
            f'<tr><td><b>Parts</b></td><td>stl/print/: pod_body_screw, pod_panel_screw, cover_screw</td>'
            f'<td>stl/print/resin/, or the resin plate</td></tr>'
            f'<tr><td><b>In the bosses</b></td><td>6 x M3 heat-set insert. Holes {SM["insert_d"]:g} mm, {SM["insert_depth"]:g} mm deep: too big for M2.5 inserts. Bosses {SM["boss_d"]:g} mm.</td>'
            f'<td>6 x M2.5 hex nut, {NM["af"]:g} mm across the flats, {NM["t"]:g} mm thick. Hex pockets. Bosses {NM["boss_d"]:g} mm.</td></tr>'
            f'<tr><td><b>Screws</b></td><td>4 x M3 x 4 button or pan head (cover). 2 x M3 x 12 (panel).</td><td>4 x M2.5 x 4 button or pan head (cover). 2 x M2.5 x 12 (panel).</td></tr>'
            f'<tr><td><b>Tools</b></td><td>Soldering iron (an insert tip helps), screwdriver</td><td>Superglue, screwdriver</td></tr></table>'
            f'<div class="grid2"><div><h3>Heat-set inserts (FDM)</h3><ol>'
            f'<li>Put an insert on the hole of a boss.</li>'
            f'<li>Heat it with the soldering iron, and press it in straight until it is flush with the top of the boss.</li>'
            f'<li>Do the 4 floor bosses and the 2 speaker post bosses.</li>'
            f'<li>Let the plastic cool before you put in a screw.</li></ol></div>'
            f'<div><h3>Glued nuts (resin)</h3><ol>'
            f'<li>Put a nut flat into the hex pocket at the top of a boss, and push it to the bottom.</li>'
            f'<li>Put a drop of superglue on the edge of the nut. Keep the glue off the thread.</li>'
            f'<li>Do the 4 floor bosses and the 2 speaker post bosses.</li>'
            f'<li>Let the glue set before you put in a screw.</li></ol></div></div>'
            f'<p class="callout" style="margin-top:4mm">Floor nuts: the nut is at the bottom of its pocket. The M2.5 x 4 cover screw goes fully '
            f'through it (screw tip at Y {tip:.1f}, nut top at Y {nut_top:.1f}). Speaker post nuts: the panel column is over the nut and holds it in its pocket.</p>')
    return page(body, n)


def cables(n):
    amp_rows = [(W[("amp", k)]["color"], k, "", t, "f" if k in ("G", "V", "DIN") else "m") for k, t in
                (("G", "Pi pin 14"), ("V", "Pi pin 2 (5V)"), ("BCLK", "BCLK splice"), ("LRC", "LRCLK splice"), ("DIN", "Pi pin 40"))]
    amp_rows = [(c, k, l, t, "f") for c, k, l, t, _ in amp_rows]
    uart = [(W[("uart", k)]["color"], k, "f", f"BiBoard {k}", "m") for k in ("TX2", "RX2", "GND")]
    uart = [(c, f"Pi pin {W[('uart', k)]['to'].split()[1]}", "f", t, m) for (c, k, l, t, m), k in zip(uart, ("TX2", "RX2", "GND"))]
    mic = [(W[("mic", k)]["color"], k, "f", f"Pi {W[('mic', k)]['to']}" if W[("mic", k)]["to"].startswith("pin") else W[("mic", k)]["to"], "f")
           for k in ("3V", "GND", "BCLK", "DOUT", "LRCL", "SEL")]
    mic = [(c, f"mic {k}", "f", t + (" · 15 cm" if k in ("3V", "GND") else ""), "f") for (c, k, l, t, m) in mic]
    body = (f'<div class="kicker">3</div><h2>Electronics and cables</h2>'
            f'<p class="lead">Each cable below shows its two ends. Some have one plug at one end and many at the other: '
            f'match each end before you plug it in.</p>'
            f'<div class="card"><h4>Amp cable <span class="tag o">1 plug → 5 sockets</span></h4>'
            f'<p>Comes with the NULLLAB NS4168 amp: one 5-pin PH2.0 plug at the amp, five single female Dupont sockets at the other end. '
            f'The wires are bonded flat. Keep the cable on edge: do not twist it.</p>'
            f'{cable_card("", ("ph", "PH2.0 5-pin", "into the amp I2S"), amp_rows)}</div>'
            f'<div class="card"><h4>BiBoard jumpers <span class="tag">3 single jumpers</span> <span class="tag o">female → male</span></h4>'
            f'<p>The female end goes onto the Pi pin. The male end goes into the BiBoard socket, which is female.</p>'
            f'{cable_card("", None, uart)}</div>'
            f'<div class="card"><h4>Mic jumpers <span class="tag">6 single jumpers</span> <span class="tag">female → female</span></h4>'
            f'<p>One per mic pin. BCLK and LRCL end in the free female ends of the splices; cut them to length when you make the splices.</p>'
            f'{cable_card("", None, mic)}</div>'
            f'<div class="grid2"><div class="card"><h4>Splices <span class="tag o">1 → 2</span></h4>'
            f'<p>Each clock signal feeds two boards. Make a Y from three jumper ends: solder, then cover with white heat shrink.</p>'
            f'{splice_card()}</div>'
            f'<div><div class="card"><h4>Speaker lead</h4><p>The 2-wire lead of the speaker ends in a 2-pin PH2.0 plug: it goes into the '
            f'rear end of the amp.</p></div></div></div>')
    return page(body, n)


def pin_maps(n):
    mic = [(lab, W[("mic", lab)]["color"]) for lab in ("SEL", "LRCL", "DOUT", "BCLK", "GND", "3V")]
    amp = [(lab, W[("amp", lab)]["color"]) for lab in ("G", "V", "BCLK", "LRC", "DIN")]
    bb = [("TX2", W[("uart", "TX2")]["color"]), ("RX2", W[("uart", "RX2")]["color"]), ("GND", W[("uart", "GND")]["color"]),
          ("+5V", None), ("+5V", None)]
    body = (f'<div class="kicker">4</div><h2>Pin maps and hardware</h2>'
            f'<p class="lead">Every pin in use, in the color of its wire.</p>'
            f'<h3>Pi Zero 2 W, 40-pin header</h3>{pi_header_svg()}'
            f'<div class="grid3" style="margin-top:4mm">'
            f'<div><h3>Mic (as mounted)</h3>{board_pins_svg("mic", mic, "SEL at the top, 3V at the bottom")}</div>'
            f'<div><h3>Amp I2S plug</h3>{board_pins_svg("amp", amp, "G at the top (the amp stands upright)")}</div>'
            f'<div><h3>BiBoard socket</h3>{board_pins_svg("bb", bb, "male ends in; +5V stays empty")}</div></div>'
            f'<p class="callout" style="margin-top:4mm">TX and RX cross: BiBoard TX2 goes to Pi RXD (pin 10), BiBoard RX2 to Pi TXD (pin 8). '
            f'SEL to GND puts the mic on the left channel. The PiSugar S powers the Pi through its contact pins.</p>'
            f'<h3>Hardware</h3><table><tr><th>Item</th><th>Count</th><th>Use</th></tr>'
            f'<tr><td>Female-to-male Dupont jumper, 10 cm</td><td class="n">3 + 2</td><td>BiBoard serial link (3) and the amp ends of the splices (2)</td></tr>'
            f'<tr><td>Female-female Dupont jumper, 10 cm</td><td class="n">4 + 2</td><td>mic (4) and the Pi ends of the splices (2)</td></tr>'
            f'<tr><td>Female-female Dupont jumper, 15 cm</td><td class="n">2</td><td>mic GND and 3V</td></tr>'
            f'<tr><td>Heat shrink, white</td><td class="n">2</td><td>splice sleeves</td></tr>'
            f'<tr><td>Glue (a dab)</td><td class="n"></td><td>amp</td></tr>'
            f'<tr><td>Screws, and inserts or nuts</td><td class="n">6 + 6</td><td>M3 (FDM) or M2.5 (resin): page 4</td></tr></table>')
    return page(body, n)


def step_html(i, s, img):
    lines = "".join(f"<li>{E(t)}</li>" for t in s["lines"])
    chk = f'<div class="check">{E(s["check"])}</div>' if s["check"] else ""
    note = f'<div class="note">{E(s["note"])}</div>' if s["note"] else ""
    return (f'<div class="step"><div class="shot"><img src="{img}"></div><div><div class="head"><div class="num">{i}</div>'
            f'<h3>{E(s["title"])}</h3></div><ol>{lines}</ol>{chk}{note}</div></div>')


def wire_table(n):
    order = [("uart", k) for k in ("TX2", "RX2", "GND")] + [("amp", k) for k in ("G", "V", "BCLK", "LRC", "DIN")] + \
            [("splice", "bclk"), ("splice", "lrclk")] + [("mic", k) for k in ("3V", "GND", "BCLK", "DOUT", "LRCL", "SEL")] + \
            [("speaker", "+"), ("speaker", "-")]
    tr = "".join(f"<tr><td>{swatch(W[k]['color'])}{E(W[k]['from'])}</td><td>{E(W[k]['to'])}</td>"
                 f"<td>{E(k[0])}</td><td class='n'>{W[k]['length_mm']:.0f} mm</td><td>{E(W[k].get('slack') or '')}</td></tr>" for k in order)
    body = (f'<div class="kicker">6</div><h2>Wire table</h2><p class="lead">Every wire, from end to end. Lengths are between the '
            f'housings, as modeled; a jumper longer than the route lays its excess in the loop shown.</p>'
            f'<table><tr><th>From</th><th>To</th><th>Group</th><th>Length</th><th>Excess</th></tr>{tr}</table>')
    return page(body, n)


def checks_page(n):
    B = CHECKS["balance"]
    mo = json.load(open(os.path.join(pod.OUT, "motion.json")))
    h0, h1 = mo["head"]["free"]
    body = (f'<div class="kicker">7</div><h2>Checks, opening and removal</h2>'
            f'<div class="grid2"><div><h3>What the model checks</h3><ul>'
            f'<li>No printed part and no board touch, except where a fit is meant to touch.</li>'
            f'<li>Every part goes in from the top, in the order of this guide.</li>'
            f'<li>No two wires pass through each other. No designed bend is tighter than {pod.R_BEND:g} mm.</li>'
            f'<li>The head turns from {h0} to {h1} deg without contact.</li>'
            f'<li>The cover and the body go straight down onto the robot together. Each screw is clear of the boards.</li>'
            f'<li>Mass {B["mass_g"]:.0f} g; center of mass {abs(B["com"][2]):.1f} mm from the robot center.</li></ul></div>'
            f'<div><h3>Open the panel</h3><p>Take out the two panel screws, slide the panel '
            f'{pod.LID_SLIDE:g} mm rearward and lift it.</p>'
            f'<h3>Remove the add-on</h3><p>Open the panel. Lift the door out of the left wall. Pull the three BiBoard plugs off from the side. Unclip the cover from the robot: the body comes off with it. '
            f'To take the body off the cover, take out the 4 screws from inside the cover.</p>'
            f'<h3>Change the SD card</h3><p>Open the panel and lift the speaker out of its grooves; the card is at the rear end of the Pi.</p>'
            f'<h3>Files</h3><p class="muted">stl/print: the parts to print (stl/print/resin: the resin parts). stl/plates: the print plates. cad/: STEP files. README.md: the full reference. '
            f'Designs CC BY 4.0, code MIT; see LICENSE.md and ATTRIBUTION.md.</p></div></div>')
    return page(body, n)


def build_html(imgs):
    pages = [cover(imgs["hero"]), overview(imgs["exploded"], 2), print_parts(3), fasteners(4), cables(5), pin_maps(6)]
    n = 7
    per = 2
    for k in range(0, len(STEPS), per):
        chunk = "".join(step_html(i + 1, STEPS[i], imgs[i + 1]) for i in range(k, min(k + per, len(STEPS))))
        head = '<div class="kicker">5</div><h2>Assembly</h2>' if k == 0 else ""
        pages.append(page(head + chunk, n))
        n += 1
    pages.append(wire_table(n))
    pages.append(checks_page(n + 1))
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>Bittle X Pi Add-on build guide</title><style>{CSS}</style></head><body>{"".join(pages)}</body></html>')


def main(render_images=True):
    build_steps()
    if render_images:
        import iso_render
        iso_render.main()
    imgs = images()
    os.makedirs(GDIR, exist_ok=True)
    path = os.path.join(GDIR, "index.html")
    open(path, "w").write(build_html(imgs))
    pdf = os.path.join(HERE, "bittle_pi_addon_guide.pdf")
    chrome = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
    r = subprocess.run([chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
                        f"--print-to-pdf={pdf}", "file://" + path], capture_output=True, text=True)
    if r.returncode:
        print(r.stderr[-1500:])
    print("guide ready:", pdf)


if __name__ == "__main__":
    main("--no-render" not in sys.argv)
