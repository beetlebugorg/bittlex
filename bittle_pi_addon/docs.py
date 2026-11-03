"""Pod for Bittle X Robot: README.md and the wiring figures. guide.py makes the PDF guide.

Run pod.py and render.py first, then:  python docs.py
"""
import datetime
import json

import numpy as np
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import pod                                   # noqa: E402
from bittle_platform import docs as PD       # noqa: E402  (writers shared with the peg interface spec)
from bittle_platform import interface as PI  # noqa: E402

VERSION = "0.26"
DATE = datetime.date.today().isoformat()
TITLE = f"Pod for Bittle X Robot v{VERSION} - Build Guide"
VIEWER = "https://beetlebugorg.github.io/bittlex/viewer/"
CHECKS = json.load(open(os.path.join(pod.OUT, "checks.json")))


def content():
    pr = CHECKS["printing"]
    MO = json.load(open(os.path.join(pod.OUT, "motion.json")))
    X = []
    h = lambda t: X.append(("h", t))
    p = lambda t: X.append(("p", t))
    tbl = lambda rows, w: X.append(("table", rows, w))
    img = lambda f, w=1.0, cap="": X.append(("img", f, w, cap))
    lst = lambda items: X.append(("list", items))

    SM, NM = pod.SCREW_MOUNT, pod.NUT_MOUNT
    p(f"Version {VERSION}, {DATE}. This is an independent community project. It is not affiliated with or endorsed by Petoi. Bittle and Petoi are trademarks of Petoi LLC. It goes on the robot with the cover for screws (peg interface v{PI.VERSION}, ../bittle_platform). "
      "It holds a Raspberry Pi Zero 2 W with a PiSugar S (1200 mAh), an NS4168 I2S amp with a 3 W speaker, and an SPH0645 I2S mic. "
      "The case is one rounded box (the body) and a slide-on top panel. The body screws to a cover for screws, and the cover and the body clip onto "
      "the robot as one unit, in place of the stock cover. Every part goes in from the top. Two screws hold the panel. A dab of glue sets the amp.")
    img("iso/hero-light.png", 0.5, "The add-on on the robot: the port windows in the panel. The mic holes are in the right side, near the front.")

    h("1. Parts to print")
    tbl([["File (stl/print/)", "Material", "Orientation", "Mass"],
         ["pod_body_screw.3mf (or .stl)", "PLA", "floor on the bed", f"{pod_mass('pod_body')} g"],
         ["pod_panel_screw.stl", "PLA, second color", "upside down: top on the bed", f"{pod_mass('pod_panel')} g"],
         ["pod_door.stl", "PLA", "on its top edge, with a brim", f"{pod_mass('pod_door')} g"],
         ["cover_screw.stl", "PLA", "stand on the rear end, tree supports, 14-line brim", f"{pod_mass('cover_screw')} g"],
         ["starter_plate_screw.stl (optional)", "PLA", "plate bottom on the bed", f"{pod_mass('starter_plate_screw', ('print',))} g"],
         ], [62, 34, 58, 16])
    p("Each part has a file for 0.20 mm layers and a *_fine file for 0.10 mm layers, for example pod_panel_screw.stl and pod_panel_screw_fine.stl. "
      f"The fine panel has smaller hook gaps ({pod.LID_SCREW['gap']:g} mm). The other fine files are the same as the 0.20 mm files now. "
      "Slice them with the profiles in ../profiles/taz-workhorse-se (pla-0.20-standard and pla-0.10-fine) and a brim. "
      "printdeck.yml in the repository root has the profile and the settings of each part. "
      "The old Cura profile \"Bittle X\" (../cura/Bittle_X.curaprofile; 0.20 mm layers) also works for the 0.20 mm files.")
    p("pod_body_screw.3mf has support blockers on the two amp nubs and at the middle of the rear wall. "
      "The nubs print without support, and the tall, narrow support under them fails. Open the 3MF in Cura and turn on support as usual. "
      "starter_plate_screw.stl is the starter plate of the peg interface with the same 4 bosses: use it to start an add-on of your own, or to test the inserts or nuts on the cover.")

    h("Inserts or nuts")
    p("Each of the 6 bosses holds a threaded part for a screw: 4 in the floor (the cover screws) and 2 on the speaker posts (the panel screws). "
      "The FDM parts use M3 heat-set inserts: the holes are too big for M2.5 inserts. The resin parts use M2.5 nuts with superglue.")
    tbl([["", "FDM print (PLA): heat-set inserts", "Resin print: glued nuts"],
         ["Files", "stl/print/: pod_body_screw, pod_panel_screw, cover_screw", "stl/print/resin/, or the resin plate (stl/plates/resin_phenom)"],
         ["In the bosses", f"6 x M3 heat-set insert ({SM['insert_d']:g} mm holes, {SM['insert_depth']:g} mm deep; bosses {SM['boss_d']:g} mm)",
          f"6 x M2.5 hex nut ({NM['af']:g} mm across the flats, {NM['t']:g} mm thick) in hex pockets; bosses {NM['boss_d']:g} mm"],
         ["Screws", "4 x M3 x 4 button or pan head (cover), 2 x M3 x 12 (panel)", "4 x M2.5 x 4 button or pan head (cover), 2 x M2.5 x 12 (panel)"],
         ["Tools", "soldering iron (an insert tip helps), screwdriver", "superglue, screwdriver"],
         ], [24, 73, 73])
    lst(["FDM: heat each insert with the soldering iron and press it in straight, flush with the top of the boss. Let it cool before you put in a screw.",
         "Resin: put a nut flat into the hex pocket at the top of each boss and push it to the bottom. Put a drop of superglue on its edge. Keep the glue off the thread. Let the glue set.",
         f"Floor: the nut is at the bottom of its pocket. The M2.5 x 4 cover screw goes fully through the nut (the screw tip is at Y {pod.FLOOR_Y0 - SM['web'] + 4:.1f}, the nut top at Y {NM['floor_y'] + NM['t']:.1f}).",
         "Speaker posts: the panel column is over the nut and holds it in its pocket. The M2.5 x 12 panel screw goes through the nut."])

    h("Click-on version")
    p("The click-on version has no screws: pod_body.3mf, pod_body_fine.3mf and pod_panel.stl click onto cover_pegs.stl (../bittle_platform). "
      "Put the body on the pegs 7 mm behind its place and slide it forward until it clicks; a latch at the rear holds the panel. "
      "At 0.10 mm layers, print pod_body_fine in place of pod_body: it has a smaller slot gap (0.10 mm a side) and more click travel (0.375 mm). "
      "The fit test plates are in ../bittle_platform/stl/fit_fine/ (test 14). With the full pod on it, the click-on body is loose: the screw version replaces it.")
    p(f"Print quality. The body and panel walls are 2.0 mm: with the offsets of the body profile, Cura slices 4 full lines of 0.5 mm. "
      "The body walls are vertical and its floor is on the bed. The only overhangs are the flat undersides of the two amp nubs (1.5 x 4 mm). "
      "The front-left cable notch is a 45 deg chamfer. The grille holes and the mic holes are teardrops (round, with a 45 deg point on top), so they print without bridges. "
      "The panel top edge round ends in a 45 deg chamfer at the bed, the port openings have 45 deg chamfers, and the lid hooks and the lugs in the body have 45 deg faces. "
      "The holes in the cover are teardrops, because the cover prints on its rear end. "
      "The door prints on its top edge: its outer face is a wall with the layers of the body walls, and the 45 deg strip at its bottom hangs on its inner face. "
      "The top ends of its ears slope at 45 deg. The door is 27 mm tall on a 2 mm edge: use a brim.")

    h("Print plates")
    p("stl/plates/ has every part on one bed, in its print orientation. "
      "Each 3MF has one object for each part. Each plate folder has one STL for each part.")
    tbl([["Printer", "File", "Orientation"],
         ["FDM: LulzBot TAZ Workhorse (280 x 280 x 300), 0.5 mm nozzle", "fdm_taz.3mf or fdm_taz_plate.stl",
          "The screw parts as in stl/print/ (0.20 mm files). The cover stands on its rear end: turn on tree supports and a 14-line brim."],
         ["Resin: Peopoly Phenom, first model (276 x 155 x 400)", "resin_phenom.3mf or resin_phenom_plate.stl",
          "The screw version with nuts: the body, the panel, the door and the starter plate are tipped 45 deg, and the cover stands on its rear end. "
          "The lowest point is at Z 0. Lift the parts 5 mm in the slicer and add supports. stl/print/resin/ has each part alone."],
         ], [50, 40, 80])
    RC = json.load(open(os.path.join(pod.OUT, "plates", "resin_check.json")))
    vol = sum(v["cup_volume_mm3"] for v in RC.values())
    lst(["Body (resin): the floor is toward the plate. Put the supports on the floor underside, off the screw holes. Sand the marks flat: the floor is on the cover rings.",
         "Panel (resin): the open side is toward the plate. The top face has no support marks.",
         "Cover (resin): it stands on its rear end. Put the supports on the rear edge only.",
         "Door (resin): the outer face is up, tipped 45 deg. The supports go on the inner face and the ears.",
         ("The resin check found no cups (trapped resin) in these orientations." if vol == 0 else
          f"The resin check found cups (trapped resin, {vol:g} mm³). See stl/plates/resin_check.json."),
         f"The resin fit (pod.py RESIN_FIT, a best guess; stl/installed/resin/): door gap {pod.RESIN_FIT['door_gap']:g} mm, door post gap {pod.RESIN_FIT['door_clr']:g} mm, "
         f"amp slot gap {pod.RESIN_FIT['amp_clr']:g} mm. The panel has the hook gaps for 0.10 mm layers ({pod.LID_SCREW['gap']:g} mm).",
         "The starter plate (resin) has the same nut bosses. Print it first to test the nut pockets on the cover.",
         "Wash the parts in IPA and post-cure them before the fit test."])

    h("2. Electronics")
    tbl([["Part", "Place"],
         ["Raspberry Pi Zero 2 W + PiSugar S, 1200 mAh", f"On the long edge over the robot center, {pod.STACK_DX:g} mm left of the center line so the battery is near it: ports and PiSugar controls up, "
          "GPIO header down to the left (toward the BiBoard), SD card to the rear. Two end posts hold the boards in one groove, the same depth for both boards; "
          "the M2.5 screw heads go down channels in the posts. The pin-fin heatsink on the SoC points into the left well (14 x 14 x 6.5 mm, estimated)."],
         ["Dupont jumpers", "3 female-to-male jumpers to the BiBoard (female on the Pi pin, male into the BiBoard socket). 6 female-female jumpers to the mic (2 of them through the splices): 10 cm, but 15 cm for GND and 3V."],
         ["NULLLAB NS4168 I2S amp", "38.4 x 22.4 mm board, on edge along the right wall, parts to the inside, in a slot bar on the floor, "
          "upright with its screw terminal at the top. Two nubs and two forks under the panel hold its top edge. "
          "Its PH2.0 connectors are side entry: the I2S cable plugs in at the front end, the speaker at the rear end."],
         ["NULLLAB 3 W 4 ohm speaker", f"At the rear, sound to the grille in the rear face. Body {pod.SPK['body_l']:g} wide, {pod.SPK['h']:g} deep. Two tapered wings ({pod.SPK['l']:g} across, "
          f"{pod.SPK['ear_t']:g} thick) at the middle of the body depth stand in two side grooves."],
         ["HiLetgo SPH0645 I2S mic", f"{pod.MIC['w']:g} x {pod.MIC['l']:g} board, high on the right wall near the front, port to the wall (holes in the right side). "
          "Its straight 6-pin header is along its front edge: the plugs point inward, and the wires go straight across behind the front wall. "
          "3V is the lowest pin, SEL the highest. It drops into a slot in a post (rear edge) and a ledge (bottom edge). No tools."],
         ], [52, 118])

    B = CHECKS["balance"]
    x, y, z = B["com"]
    p(f"Balance. The add-on weighs {B['mass_g']:.0f} g (weighed parts; printed parts at 50 % fill). "
      f"Its center of mass is {z:.1f} mm behind the robot center and {abs(x):.1f} mm {'left' if x < 0 else 'right'} of the center line, "
      f"{y - PI.COVER_TOP:.0f} mm above the cover top. With the add-on, the center of mass of the robot is about 4 mm behind the midpoint "
      "of the front and rear paws (110 mm apart), and on the center line. The side is the limit when the robot tips: keep heavy parts low. "
      "Put your own masses in MASS_G in pod.py and run pod.py again.")

    h("3. Assembly")
    st = lambda n: f" ([viewer step {n}]({VIEWER}#step={n}))"
    p(f"The 3D viewer shows each step with animation: [{VIEWER}#step=1]({VIEWER}#step=1). "
      "Grooves in the floor are under the amp cable and the mic wire run. "
      "The door is a piece of the left wall over the BiBoard plugs. With the panel off, lift the door out: a finger reaches the plugs from the side.")
    lst(["Put the 6 inserts or nuts into the bosses: 4 in the floor and 2 on the speaker posts (see Inserts or nuts)." + st(2),
         "Put the empty body on the cover for screws, grille to the rear. Put a screw up through each of the 4 rings from inside the cover (M3 x 4 for inserts, M2.5 x 4 for nuts), "
         "into the insert or the nut, and tighten it." + st(3),
         "Remove the stock back cover. Clip the cover and the body onto the robot as one unit. "
         "The BiBoard header comes up through the opening in the cover and the notch at the front of the left well." + st(4),
         "Push the speaker down into the two side grooves at the rear, body to the rear." + st(5),
         "Plug the six mic jumpers onto the mic header: 15 cm jumpers on GND and 3V. Drop the mic into the slots in the post and the ledge "
         "on the right wall near the front, port to the wall, header at the front." + st(6),
         "Plug the flat amp cable into the I2S connector at the front end of the amp and the speaker into its rear end. Put the bottom edge of the amp into the slot along the right wall, "
         "parts to the inside, tilt its top edge under the two nubs, and set it with a dab of glue. Let the amp cable hang out of the top." + st(7),
         "Set the PiSugar AUTO switch before the cell goes on the board: it is under the cell. Push the Pi + PiSugar S stack down into the end grooves." + st(8),
         "Plug the wires one at a time, in the order of section 5: the splices, the Pi ends of the BiBoard jumpers, the amp cable, the mic jumpers, "
         "then the BiBoard ends. The viewer has one step for each wire." + st(9) + st(19),
         "Slide the door down into the two grooves of the opening in the left wall. The panel holds it down." + st(20),
         f"Put the panel down {pod.LID_SLIDE:g} mm behind its place, then slide it forward. The hooks under the panel go under the lugs in the walls. "
         "Put the two panel screws down through the panel into the speaker posts (M3 x 12 for inserts, M2.5 x 12 for nuts)." + st(21),
         f"Open: take out the two panel screws, slide the panel {pod.LID_SLIDE:g} mm rearward and lift it. "
         "Remove: open the panel, lift the door out, pull the BiBoard plugs off from the side, and unclip the cover from the robot. "
         "To take the body off the cover, take out the 4 screws from inside the cover."])
    import guide
    guide.build_steps()
    for i, s in enumerate(guide.STEPS, 1):
        img(f"iso/step{i:02d}-light.png", 0.6, f"Step {i} of the build guide: {s['title']}. The parts of the step are green.")
    p(f"On the top: the port openings are shaped to the plug bodies of common cables (plug + {pod.PORT_CLR:g} mm). The Pi power, the Pi data and the PiSugar charge ports share one plain rounded rectangle. "
      "The HDMI opening also shows the PiSugar power switch, beside the plug. The lever is 5.7 mm under the panel: move it with a pen tip or a toothpick. "
      "The PiSugar button is in that rectangle too: press it with a fingertip or a pen tip.")
    img("iso/top-light.png", 0.42, "The top: one opening for HDMI and the power switch, and one for the Pi power, data USB, PiSugar charge and the PiSugar button.")

    h("4. Wiring")
    tbl([["Board pin", "Pi pin", "Signal"],
         ["BiBoard TX2 / RX2 / GND", "10 / 8 / 6", "RXD / TXD / GND (TX and RX cross). BiBoard +5V: not wired"],
         ["Amp V / G", "2 / 14", "5V / GND"],
         ["Mic 3V / GND / SEL", "1 / 9 / 39", "3V3 / GND / GND (left channel)"],
         ["Amp BCLK + mic BCLK", "12 (splice)", "GPIO18: one wire from the pin to a soldered splice, then one wire to each board"],
         ["Amp LRC + mic LRCL", "35 (splice)", "GPIO19: the same, a second splice"],
         ["Amp DIN / mic DOUT", "40 / 38", "GPIO21 / GPIO20"],
         ["Speaker", "-", "amp 2-pin PH2.0 at the rear end of the amp"],
         ], [44, 26, 100])
    p("Pin map from the wiring blueprint (reference/g2-wiring-blueprint.html; that blueprint wins if they differ). "
      "PiSugar S touches pins 2, 4, 5, 6 and 9 from below with its pogo pins. It uses pin 5 (SCL) for its button and auto start: with its AUTO switch ON, I2C cannot be used. Pins 11, 17-20 and 22-24 are kept free for a screen.")
    h("5. Cable routing")
    WR = json.load(open(os.path.join(pod.OUT, "wires.json")))
    ws = WR["wires"]
    pack = [w for w in ws if w.get("pack")]
    p(f"The BiBoard wires are female-to-male jumpers (the male end goes into the BiBoard socket), the mic wires female-female; {WR['pack_l'] / 10:g} cm, but the mic GND and 3V jumpers are {WR['long_l'] / 10:g} cm. The amp keeps its own cable, "
      "and the two splices are cut from pack jumpers. pod.py models every wire "
      f"({WR['wire_d']:g} mm) at its real length and checks it: no wire touches a printed part or a board, no two wires pass through each "
      f"other ({len(WR['crossings'])} found), and no bend is smaller than {WR['r_bend']:g} mm radius ({WR['r_slack']:g} mm in the slack). "
      "A pack jumper is longer than its route, so its excess is an arch or a coil (a service loop) in free space. "
      "The pages below show each module: its pins, then its wires in the case.")
    for i, mod in enumerate(MODULES):
        img(f"15_wiring_{i}.png", 0.95, "")
    cells = []
    for i, w in enumerate(ws, 1):
        key = (w["group"], w["wire"])
        extra = f" ({w['slack']})" if w.get("pack") else ""
        cells.append([str(i), WIRE_FROM[key], WIRE_TO[key] + extra, f"{w['length_mm']:.0f}"])
    half = (len(cells) + 1) // 2
    rows = [["#", "From", "To (excess)", "mm"] * 2]
    for k in range(half):
        rows.append(cells[k] + (cells[k + half] if k + half < len(cells) else ["", "", "", ""]))
    tbl(rows, [6, 24, 34, 8] * 2)
    order = [tuple(k) for k in WR["order"]]
    num = {(w["group"], w["wire"]): i for i, w in enumerate(ws, 1)}
    p("Plug the jumpers one at a time, in this order. Each wire goes to its place before the next one, so the later wires lie over the earlier ones:")
    lst([f"#{num[k]}: {WIRE_FROM[k]} to {WIRE_TO[k]}" + (f". Put its excess in a {[w for w in ws if (w['group'], w['wire']) == k][0]['slack']} as in the drawing."
                                                          if k in {(w['group'], w['wire']) for w in pack} else ". Cut to length.")
         for k in order] + ["Last, push the BiBoard ends of #%d, #%d and #%d onto the BiBoard header." % tuple(num[k] for k in order if k[0] == "uart")])
    lst(["The mic has a straight header along its front edge. Plug the six mic jumpers onto it before the mic goes in. "
         "Mic wires: " + ROUTE["mic"] + ".",
         "Amp cable: " + ROUTE["amp"] + ". Lay it after the BiBoard jumpers: its V wire runs over their Pi ends.",
         "Splices: the LRCLK splice stands beside the BiBoard plugs, the BCLK splice at the middle of the left well.",
         "The BiBoard wires go in first, from the lowest: TX2, RX2, then GND. Their BiBoard ends go on last: a Pi housing for the mic slides off its pin past them.",
         "The mic wires go in from the lowest of the stack: 3V, GND, BCLK, DOUT, LRCL, then SEL."])
    img("iso/wires-light.png", 0.5, "From the left, panel off, the body see-through: the wires in 3D.")

    h("6. Checks")
    h0, h1 = MO["head"]["free"]
    T = MO["tail"]
    lst(["Mount: the cover and the body go straight down onto the robot together. The body has no contact on the way. "
         "The cover touches the shoulders only at its clips, the same as the cover with the pegs. "
         "Each cover screw goes through the cover and the floor into its insert or nut, clear of the boards. The floor is on the 4 cover rings.",
         f"Panel: it goes down {pod.LID_SLIDE:g} mm behind its place and slides forward without contact. "
         "Each panel screw goes down through the panel column and the post boss, clear of the boards.",
         "Install: the speaker and the stack each go straight down 40 mm without contact. The mic drops into its slots; the post, the ledge and a stop hold it. "
         "The amp tilts in under its nubs. "
         "Each wire, in its order, goes in from 40 mm above without contact with the parts and wires already in place "
         "(small contacts of 2 to 3 mm³ stay where a wire slides under a loose service loop). Each Dupont housing slides off its pin without contact.",
         "Door: it slides down its grooves from 45 mm up without contact. Pushed 0.3 mm in any direction, it touches the body. "
         "Lifted 0.3 mm, it touches the panel. With the door out, a finger tip has space over the BiBoard plug.",
         "Switch and button: the switch lever is under the HDMI opening over its full travel. The PiSugar button is under the large opening.",
         f"Robot: the head turns from {h0} to {h1} deg without contact. {len(MO['legs']['front']['addon'])} front and "
         f"{len(MO['legs']['rear']['addon'])} rear leg poses (of 504) touch the add-on, only when a thigh swings up over the back. "
         f"The Petoi tail is {T['gap']:g} mm under the add-on."])
    p("Open items: the BiBoard header height is an estimate (measure it). The speaker size is a ruler measurement. "
      "The mic port is assumed at the board center; the 7 holes cover ±2.2 mm. The SD card is assumed 2.5 mm out of its holder. "
      "The heatsink and the screw heads (4.6 x 1.8 mm) are estimates. PiSugar has no 3D model of the PiSugar S: its fit model is drawn from the PCB drawing in the PiSugar docs. The part heights, the cell gap (3.3 mm) and the cell size (taken from the PiSugar 2 cell) are estimates. "
      "To change the SD card, lift the stack out. The Pi power port and the PiSugar charge port are side by side: use one of them at a time.")

    h("7. Files and license")
    tbl([["File", "Content"],
         ["stl/print/", "the parts in print orientation (the screw version, and the click-on version)"],
         ["stl/print/resin/", "the resin parts (glued nuts), each one alone in its resin orientation"],
         ["stl/assembly/", "the assemblies of the Parts tab in Printdeck: each model in its place, Z up (python pod.py assembly, after pod.py)"],
         ["stl/screw/", "the screw version in the robot frame, with the screws and the inserts (desktop viewer: --stl stl/screw)"],
         ["stl/plates/", "print plates for the FDM and the resin printer (3MF, STL), plates.json, resin_check.json"],
         ["cad/*.step", "the parts as STEP (from the mesh)"],
         ["cad/assembly_step.zip", "one STEP file with the robot, the pegged cover and the pod in place, with named and colored parts"],
         ["stl/installed/, stl/models/", "the parts and the electronics in the robot frame"],
         ["pod.py, motion.py, plates.py, render.py, docs.py", "dimensions, build and checks; robot motion; print plates; pictures; this guide"],
         ], [62, 108])
    p("The printed parts, the drawings and this guide are CC BY 4.0, and the code is MIT (Jeremy Collins). "
      "The Pi Zero fit model is from github.com/PiSugar/PiSugar (GPL-3.0). "
      "The Petoi parts are from github.com/PetoiCamp/NonCodeFiles, without a stated license. "
      "LICENSE.md and ATTRIBUTION.md in the repository give the details.")
    return X


WIRE_FROM, WIRE_TO = pod.WIRE_FROM, pod.WIRE_TO
MX = lambda r: (-r[1], -r[0])          # pod.py numbers are in its design frame (X turned over): to the robot frame
ROUTE = dict(uart="left well: up out of the BiBoard plugs to the left wall, rearward (each wire at its own height), down, into the Pi header",
             amp="a flat cable on edge (G on top), with no twist: out of the plug, down a step, forward to the front wall, across behind it under the mic plugs, rearward along the left well; each wire turns in at its own height into its pin or splice (DIN first, V last)",
             mic="straight inward out of the mic plugs, across behind the front wall in front of the stack, "
                 "then rearward as a flat stack in the left well beside the BiBoard plugs; each wire stays at the height of its pin",
             splice="short wire in the left well, up into the bottom of the splice sleeve",
             speaker="a pair: up the right side behind the amp, over the ear plate, into the top of the speaker")


def routing_figures():
    """Top view and right-well side view of the wire routes (stl/wires.json), numbered as in the route table."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle, Circle
    W = json.load(open(os.path.join(pod.OUT, "wires.json")))["wires"]
    def parts(a, view):
        boxes = [("battery", MX(pod.BAT["x"]), pod.BAT["z"], pod.BAT["y"], "#4a78d8"),
                 ("Pi + PiSugar", MX(pod.PCB_X), (pod.STACK_ZF, pod.STACK_ZR), (pod.STACK_Y0, 60.0), "#2e9b4f"),
                 ("Pi header plugs", MX((pod.HDR_BASE_X[0], pod.HOUSING_END)), pod.PI_PLUGS["z"], pod.PI_PLUGS["y"], "#555"),
                 ("BiBoard plugs", MX(pod.BB_PLUG["x"]), sorted((pod.bb_pin_z(0) + 1.25, pod.bb_pin_z(2) - 1.25)), pod.BB_PLUG["y"], "#d83a34"),
                 ("amp", MX((pod.AMP_X[0], pod.AMP_X[1] + 10.0)), pod.AMP_Z, (pod.AMP_Y0, pod.AMP_Y0 + pod.AMP["h"]), "#1f5f8f"),
                 ("mic", MX(pod.MIC_X), (pod.MIC["z0"], pod.MIC["z0"] + pod.MIC["w"]), (pod.MIC["y0"], pod.MIC["y0"] + pod.MIC["l"]), "#d83a34"),
                 ("speaker", (-pod.SPK["l"] / 2, pod.SPK["l"] / 2), (pod.SPK_ZE, pod.SPK_ZE + pod.SPK["ear_t"] + pod.SPK["h"]),
                  (pod.SPK_Y0, pod.SPK_Y0 + pod.SPK["d"]), "#7a52b8")]
        for name, xr, zr, yr, col in boxes:
            if view == "top":
                a.add_patch(Rectangle((zr[0], xr[0]), zr[1] - zr[0], xr[1] - xr[0], fc=col, alpha=0.18, ec=col, lw=0.6))
                a.text((zr[0] + zr[1]) / 2, (xr[0] + xr[1]) / 2, name, ha="center", va="center", fontsize=6, color=col, alpha=0.9)
            elif xr[0] < -15:
                a.add_patch(Rectangle((zr[0], yr[0]), zr[1] - zr[0], yr[1] - yr[0], fc=col, alpha=0.15, ec=col, lw=0.6))
                a.text((zr[0] + zr[1]) / 2, yr[1] - 1.2, name, ha="center", va="top", fontsize=6, color=col)
        for t in ("bclk", "lrclk"):
            x, z = pod.SPLICE[t]
            x = -x
            if view == "top":
                a.add_patch(Circle((z, x), pod.SPLICE["r"], fc="#222", alpha=0.6))
            else:
                a.add_patch(Rectangle((z - pod.SPLICE["r"], pod.SPLICE["y"][0]), 2 * pod.SPLICE["r"], 6.0, fc="#222", alpha=0.6))
    for view, fn in (("top", "13_routing_top.png"), ("side", "14_routing_side.png")):
        fig, a = plt.subplots(figsize=(7.2, 4.0 if view == "top" else 3.3), dpi=200)
        if view == "top":
            pl = pod.plan(pod.WALL)
            a.plot(np.r_[pl[:, 1], pl[0, 1]], np.r_[pl[:, 0], pl[0, 0]], color="0.4", lw=0.8)
            a.set_xlabel("Z (mm), front at the left"); a.set_ylabel("X (mm), robot right up")
            a.set_title("Wire routes from the top (numbers: route table)", fontsize=8)
        else:
            a.axhline(pod.FLOOR_Y1, color="0.4", lw=0.8); a.axhline(pod.PANEL_IN, color="0.4", lw=0.8, ls="--")
            a.text(-37, pod.PANEL_IN - 1.5, "panel underside", fontsize=6, color="0.4")
            a.set_xlabel("Z (mm), front at the left"); a.set_ylabel("Y (mm), up")
            a.set_title("Left well, seen from the left side (wires with X < -17)", fontsize=8)
        parts(a, view)
        for i, w in enumerate(W, 1):
            P = np.array(w["points"])
            if view == "side":
                keep = P[:, 0] < -17.0
                if not keep.any():
                    continue
                P = np.where(keep[:, None], P, np.nan)
            u, v = (P[:, 2], P[:, 0]) if view == "top" else (P[:, 2], P[:, 1])
            a.plot(u, v, color=w["color"] if w["color"] not in ("#f2f2ef",) else "#999", lw=1.4, solid_capstyle="round")
            ok = ~np.isnan(u)
            j = np.flatnonzero(ok)[len(np.flatnonzero(ok)) // 2]
            a.text(u[j], v[j], str(i), fontsize=5.5, ha="center", va="center",
                   bbox=dict(boxstyle="circle,pad=0.15", fc="white", ec=w["color"] if w["color"] != "#f2f2ef" else "#999", lw=0.6))
        a.set_aspect("equal"); a.tick_params(labelsize=6)
        a.set_xlim(-40, 58)
        if view == "side":
            a.set_ylim(25, 63)
        fig.tight_layout()
        fig.savefig(os.path.join(HERE, "doc", fn)); plt.close(fig)


# Wiring guide for each module: (title, wire groups, connector pins in order (label, Pi pin or splice), note)
MODULES = [
    ("BiBoard serial link", ("uart",), "BiBoard header", [("TX2", 10), ("RX2", 8), ("GND", 6), ("+5V", None), ("+5V", None)],
     "TX and RX cross. The +5V pins are not wired: the PiSugar S powers the Pi."),
    ("Amp: I2S and power", ("amp", "splice"), "amp I2S plug", [("G", 14), ("V", 2), ("BCLK", "bclk"), ("LRC", "lrclk"), ("DIN", 40)],
     "BCLK and LRC go to the splices: one wire from Pi pin 12 (35) feeds the amp and the mic."),
    ("Mic", ("mic", "splice"), "mic pins", [("3V", 1), ("GND", 9), ("BCLK", "bclk"), ("DOUT", 38), ("LRCL", "lrclk"), ("SEL", 39)],
     "SEL to GND sets the left channel. BCLK and LRCL go to the splices."),
    ("Speaker", ("speaker",), "amp speaker plug", [("+", "spk+"), ("-", "spk-")],
     "A two-wire lead from the 2-pin plug at the rear end of the amp to the speaker."),
]
SPLICE_PIN = dict(bclk=12, lrclk=35)


def _fonts():
    import matplotlib
    from matplotlib import font_manager
    for f in ("NotoSans-Regular.ttf", "NotoSans-Medium.ttf", "NotoSans-Bold.ttf", "NotoSansMono-Regular.ttf"):
        path = os.path.join("/usr/share/fonts/noto", f)
        if os.path.exists(path):
            font_manager.fontManager.addfont(path)
    matplotlib.rcParams.update({"font.family": "Noto Sans", "font.size": 7, "axes.titlesize": 8, "axes.titleweight": "medium",
                                "axes.edgecolor": "#c8ccd2", "axes.linewidth": 0.6})


def _wire_col(c):
    return "#a9adb3" if c.lower() in ("#f2f2ef", "#ffffff") else c


def _rpath(pts, r=0.45):
    P, _ = pod.round_corners([(x, y, 0.0) for x, y in pts], r)
    return P[:, 0], P[:, 1]


def module_figure(mod, path):
    """One block for each module: the pin diagram (its connector to the Pi header) and its routes in the case."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import patheffects as pe
    from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
    _fonts()
    title, groups, conn, pins, note = mod
    g0 = groups[0]
    W = json.load(open(os.path.join(pod.OUT, "wires.json")))["wires"]
    col_of = {(w["group"], w["wire"]): _wire_col(w["color"]) for w in W}
    casing = [pe.Stroke(linewidth=3.6, foreground="white"), pe.Normal()]
    ink, mute, line = "#1b1f27", "#6b717b", "#c9cdd3"
    fig = plt.figure(figsize=(7.4, 5.0), dpi=220)
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.1], width_ratios=[1.0, 1.0], hspace=0.22, wspace=0.06,
                          left=0.02, right=0.98, top=0.93, bottom=0.02)
    fig.text(0.02, 0.965, title, fontsize=10.5, fontweight="bold", color=ink, va="center")
    fig.text(0.98, 0.965, note, fontsize=6.6, color=mute, va="center", ha="right")
    # ---- pin diagram
    a = fig.add_subplot(gs[0, :])
    a.set_axis_off()
    a.set_xlim(-14.5, 52.5)
    a.set_ylim(-8.4, 11.4)
    X0, PITCH, Y_ODD, Y_EVEN, H = 13.0, 1.95, 5.0, 3.0, 0.78
    px = lambda n: X0 + ((n - 1) // 2) * PITCH
    py = lambda n: Y_ODD if n % 2 else Y_EVEN
    cy = [1.1 - 1.45 * i for i in range(len(pins))]
    used_all = {int(v.split()[1]) for v in WIRE_TO.values() if v.startswith("pin ")}
    if g0 != "speaker":
        mine = {}
        for lab, t in pins:
            if t is not None:
                mine[SPLICE_PIN[t] if isinstance(t, str) else t] = col_of[(g0, lab)]
        a.add_patch(FancyBboxPatch((X0 - 1.3, Y_EVEN - 1.3), 19 * PITCH + 2.6, Y_ODD - Y_EVEN + 2.6,
                                   boxstyle="round,pad=0,rounding_size=0.5", fc="#26292f", ec="none", zorder=1))
        for n in range(1, 41):
            fill = mine.get(n)
            fc = fill if fill else ("#3c4048" if n in used_all else "#2f3239")
            a.add_patch(FancyBboxPatch((px(n) - H, py(n) - H), 2 * H, 2 * H, boxstyle="round,pad=0,rounding_size=0.22",
                                       fc=fc, ec="white" if fill else "#454a53", lw=0.8 if fill else 0.5, zorder=2))
            a.text(px(n), py(n), str(n), ha="center", va="center", fontsize=5.6, zorder=3,
                   color="white" if fill else "#8d939c", fontweight="bold" if fill else "normal")
        a.text(X0 - 1.6, Y_ODD, "odd", ha="right", va="center", fontsize=5.6, color=mute)
        a.text(X0 - 1.6, Y_EVEN, "even", ha="right", va="center", fontsize=5.6, color=mute)
        n_odd = sum(1 for _, t in pins if t is not None and (SPLICE_PIN[t] if isinstance(t, str) else t) % 2)
        ycap = Y_ODD + 2.4 + 0.6 * n_odd
        a.text(X0 - 1.3, ycap + 1.0, "Pi Zero 2 W header, as it stands in the case", fontsize=7, color=ink, fontweight="medium")
        a.text(X0 - 1.3, ycap, "pin 1 at the SD card end (rear), even row at the board edge (down)", fontsize=6, color=mute)
    # connector
    a.add_patch(FancyBboxPatch((-13.8, cy[-1] - 1.0), 8.2, cy[0] - cy[-1] + 2.0, boxstyle="round,pad=0,rounding_size=0.6",
                               fc="#f4f5f7", ec=line, lw=0.8, zorder=1))
    a.text(-13.8, cy[0] + 1.6, conn, fontsize=7, color=ink, fontweight="medium")
    odd_j = 0
    for (lab, t), y in zip(pins, cy):
        col = col_of.get((g0, lab), "#b9bdc4") if t is not None else "#b9bdc4"
        a.text(-13.0, y, lab, va="center", fontsize=7.2, fontweight="medium", color=ink, zorder=3)
        a.add_patch(Circle((-6.6, y), 0.42, fc=col if t is not None else "white", ec=col, lw=0.9, zorder=4))
        if t is None:
            a.text(-5.7, y, "not wired", va="center", fontsize=6, color="#9aa0a8")
            continue
        if g0 == "speaker":
            xs, ys = [-6.2, 28.0], [y, y]
            a.plot(xs, ys, color=col, lw=2.4, solid_capstyle="round", path_effects=casing, zorder=3)
            a.add_patch(Circle((28.4, y), 0.42, fc=col, ec=col, zorder=4))
            a.text(29.4, y, "speaker " + lab, va="center", fontsize=7.2, color=ink)
            continue
        n = SPLICE_PIN[t] if isinstance(t, str) else t
        if n % 2 == 0:                                     # even pins: along the lane, up into the pin
            pts = [(-6.2, y), (px(n), y), (px(n), Y_EVEN - H)]
            node = (px(n), y)
        else:                                              # odd pins: up at the left, over the header, down into the pin
            xt, yt = X0 - 4.6 - 0.7 * odd_j, Y_ODD + 1.6 + 0.6 * odd_j
            odd_j += 1
            pts = [(-6.2, y), (xt, y), (xt, yt), (px(n), yt), (px(n), Y_ODD + H)]
            node = (px(n), yt)
        xs, ys = _rpath(pts)
        a.plot(xs, ys, color=col, lw=2.2, solid_capstyle="round", path_effects=casing, zorder=5)
        if isinstance(t, str):                             # the splice joins this wire, the Pi wire and the other board
            other = "mic" if g0 == "amp" else "amp"
            sgn = -1 if node[0] > 38 else 1                  # near the right edge: the stub and the label go to the left
            ex, ey = node[0] + sgn * 2.6, node[1] + (-1.2 if n % 2 == 0 else 0.9)
            a.plot([node[0], ex], [node[1], ey], color=col, lw=1.6, ls=(0, (2, 1.2)), zorder=4)
            a.add_patch(Circle(node, 0.5, fc="#1b1f27", ec="white", lw=0.9, zorder=6))
            a.text(ex + sgn * 0.3, ey, f"splice, to the {other}", va="center", ha="left" if sgn > 0 else "right", fontsize=5.8, color=mute)
    # ---- route views
    mineW = [w for w in W if w["group"] in groups]
    allP = np.concatenate([np.array(w["points"]) for w in mineW])
    side_x = (lambda P: P[:, 0] < -17.0) if g0 != "speaker" else (lambda P: P[:, 0] > 9.0)
    for ci, view in enumerate(("top", "side")):
        b = fig.add_subplot(gs[1, ci])
        b.set_xticks([]); b.set_yticks([])
        for sp in b.spines.values():
            sp.set_visible(False)
        if view == "top":
            pl = pod.plan(pod.WALL)
            b.fill(pl[:, 1], pl[:, 0], fc="#fafbfc", ec="#b3b8c0", lw=0.9, zorder=0)
            b.set_title("From the top, panel off (front at the left)", loc="left", color=ink, fontsize=7.4)
        else:
            b.add_patch(Rectangle((pod.ZF_IN, pod.FLOOR_Y1), pod.ZR_IN - pod.ZF_IN, pod.PANEL_IN - pod.FLOOR_Y1, fc="#fafbfc", ec="#b3b8c0", lw=0.9, zorder=0))
            b.set_title(("Left well, seen from the left" if g0 != "speaker" else "Right side, seen from the right") + " (front at the left)",
                        loc="left", color=ink, fontsize=7.4)
        _parts(b, view, left=(g0 == "speaker"))
        for w in W:
            P = np.array(w["points"])
            if view == "side":
                P = np.where(side_x(P)[:, None], P, np.nan)
            u, v = (P[:, 2], P[:, 0]) if view == "top" else (P[:, 2], P[:, 1])
            if w["group"] in groups:
                b.plot(u, v, color=_wire_col(w["color"]), lw=2.0, solid_capstyle="round", zorder=4, path_effects=casing)
                ok = np.flatnonzero(~np.isnan(u))
                if not len(ok):
                    continue
                if view == "side" and w["group"] != "speaker" and side_x(np.array(w["points"])[-1:])[0]:
                    k = ok[-1]
                    lbl = WIRE_TO[(w["group"], w["wire"])].replace("pin ", "")
                    if not lbl.endswith("splice"):
                        b.annotate(lbl, (u[k], v[k]), xytext=(0, -7), textcoords="offset points", ha="center", fontsize=5.4,
                                   color=ink, bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=_wire_col(w["color"]), lw=0.6), zorder=6)
            else:
                b.plot(u, v, color="#e1e4e8", lw=1.0, zorder=2)
        b.set_aspect("equal")
        if view == "top":
            b.set_xlim(-39, 57); b.set_ylim(-31, 31)
        else:
            Q = allP[side_x(allP)]
            z0, z1 = (Q[:, 2].min() - 6, Q[:, 2].max() + 6) if len(Q) else (-39, 57)
            b.set_xlim(max(z0, -39), min(z1, 57)); b.set_ylim(26, 63)
    fig.savefig(path)
    plt.close(fig)


def _parts(a, view, left=False):
    """Light silhouettes of the parts, for the route views (side views: the parts on that side)."""
    from matplotlib.patches import FancyBboxPatch
    boxes = [("battery", MX(pod.BAT["x"]), pod.BAT["z"], pod.BAT["y"]),
             ("Pi + PiSugar", MX(pod.PCB_X), (pod.STACK_ZF, pod.STACK_ZR), (pod.STACK_Y0, 60.0)),
             ("Pi header", MX((pod.HDR_BASE_X[0], pod.HOUSING_END)), pod.PI_PLUGS["z"], pod.PI_PLUGS["y"]),
             ("BiBoard", MX(pod.BB_PLUG["x"]), sorted((pod.bb_pin_z(0) + 1.25, pod.bb_pin_z(2) - 1.25)), pod.BB_PLUG["y"]),
             ("amp", MX((pod.AMP_X[0], pod.AMP_X[1] + 10.0)), pod.AMP_Z, (pod.AMP_Y0, pod.AMP_Y0 + pod.AMP["h"])),
             ("mic", MX(pod.MIC_X), (pod.MIC["z0"], pod.MIC["z0"] + pod.MIC["w"]), (pod.MIC["y0"], pod.MIC["y0"] + pod.MIC["l"])),
             ("speaker", (-pod.SPK["l"] / 2, pod.SPK["l"] / 2), (pod.SPK_ZE, pod.SPK_ZE + pod.SPK["ear_t"] + pod.SPK["h"]),
              (pod.SPK_Y0, pod.SPK_Y0 + pod.SPK["d"]))]
    for t in ("bclk", "lrclk"):
        x, z = pod.SPLICE[t]
        x = -x
        r, (y0, y1) = pod.SPLICE["r"], pod.SPLICE["y"]
        rect = (z - r, x - r, 2 * r, 2 * r) if view == "top" else (z - r, y0, 2 * r, y1 - y0)
        if view == "top" or not left:
            a.add_patch(FancyBboxPatch(rect[:2], rect[2], rect[3], boxstyle="round,pad=0,rounding_size=0.6", fc="#2a2d33", ec="white",
                                       lw=0.6, zorder=5))
    for name, xr, zr, yr in boxes:
        if view == "top":
            r = (zr[0], xr[0], zr[1] - zr[0], xr[1] - xr[0])
        elif (xr[1] > 9 if left else xr[0] < -15):
            r = (zr[0], yr[0], zr[1] - zr[0], yr[1] - yr[0])
        else:
            continue
        a.add_patch(FancyBboxPatch(r[:2], r[2], r[3], boxstyle="round,pad=0,rounding_size=0.8", fc="#eceef1", ec="#d3d7dc", lw=0.5, zorder=1))
        a.text(r[0] + r[2] / 2, r[1] + r[3] / 2, name, ha="center", va="center", fontsize=5.6, color="#8a9099", zorder=1, clip_on=True)


def pod_mass(name, folder=("screw", "installed")):
    """The mass of a part in g (solid PLA), from stl/screw/installed/ (the screw version) or another folder."""
    M = pod.mesh_to_manifold(pod.load_stl(os.path.join(pod.OUT, *folder, f"{name}.stl")))
    return f"{M.volume() * 1.24e-3:.0f}"


def main():
    PD.DOC = os.path.join(HERE, "doc")
    routing_figures()
    for i, mod in enumerate(MODULES):
        module_figure(mod, os.path.join(HERE, "doc", f"15_wiring_{i}.png"))
    PD.TITLE = TITLE
    PD.DATE = DATE
    X = content()
    PD.write_md(X, os.path.join(HERE, "README.md"))
    import guide
    guide.main()
    print("docs ready")


if __name__ == "__main__":
    main()
