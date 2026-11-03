"""Build site/: a home page with the package downloads, and a three.js viewer.

The viewer page is web/viewer.html, with the line-art look of web/lineart.js. They go to site/viewer/ with the
installed-frame STLs (site/viewer/models) and site/viewer/manifest.json.
It uses only the Python standard library and the committed package files,
so GitHub Actions runs it without the CAD tools. Preview with:
  python3 -m http.server 8800 --bind 0.0.0.0 --directory site
"""
import datetime
import json
import os
import shutil
import zipfile

PROJ = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(PROJ, "bittle_pi_addon")
SITE = os.path.join(PROJ, "site", "viewer")
MD = os.path.join(SITE, "models")

# id, label, group, source file, colour, explode offset (dx, dy, dz), extra transform
PARTS = [
    ("panel", "Top panel (second color)", "Printed", "stl/screw/installed/pod_panel.stl", "#e8641b", (0, 45, 0), None),
    ("body", "Add-on body", "Printed", "stl/screw/installed/pod_body.stl", "#f2f2ef", (0, 10, 0), None),
    ("door", "Door (left wall)", "Printed", "stl/screw/installed/pod_door.stl", "#f2f2ef", (0, 10, 0), None),
    ("cover", "Screw cover", "Printed", "stl/screw/installed/cover_screw.stl", "#34363b", (0, 0, 0), None),
    ("mount_screws", "Cover screws M3 x 4 (resin: M2.5)", "Hardware", "stl/screw/installed/mount_screws.stl", "#5b5e66", (0, 0, 0), None),
    ("mount_inserts", "Floor inserts M3 or nuts M2.5", "Hardware", "stl/screw/installed/mount_inserts.stl", "#c9a227", (0, 0, 0), None),
    ("panel_screws", "Panel screws M3 x 12 (resin: M2.5)", "Hardware", "stl/screw/installed/panel_screws.stl", "#5b5e66", (0, 0, 0), None),
    ("panel_inserts", "Post inserts M3 or nuts M2.5", "Hardware", "stl/screw/installed/panel_inserts.stl", "#c9a227", (0, 0, 0), None),
    ("shoulder_r", "Side shoulder R", "Robot", "../bittle_platform/reference/Bittle_SideShoulder.stl", "#f2a71c", (0, 0, 0), None),
    ("shoulder_l", "Side shoulder L", "Robot", "../bittle_platform/reference/Bittle_SideShoulder.stl", "#f2a71c", (0, 0, 0), "mirror_x"),
    ("front_plate", "Front plate", "Robot", "../bittle_platform/reference/Bittle_FrontPlate.stl", "#26272b", (0, 0, 0), None),
    ("rear_plate", "Rear plate", "Robot", "../bittle_platform/stl/robot/rear_plate.stl", "#26272b", (0, 0, 0), None),
    ("head", "Head (turns)", "Robot", "../bittle_platform/stl/robot/head.stl", "#3a3b40", (0, 0, 0), None),
    ("neck_mount", "Neck servo horn", "Robot", "../bittle_platform/stl/robot/neck_mount.stl", "#26272b", (0, 0, 0), None),
    ("hip_servos", "Hip servos", "Robot", "../bittle_platform/stl/robot/hip_servos.stl", "#26272b", (0, 0, 0), None),
    ("robot_battery", "Robot battery", "Robot", "../bittle_platform/stl/robot/battery.stl", "#4a4c52", (0, 0, 0), None),
    ("tail", "Tail (Petoi model)", "Robot", "../bittle_platform/stl/robot/tail.stl", "#3a3b40", (0, 0, 0), None),
] + [(f"{p}_{k}", f"{n} {k.upper()}", "Robot", f"../bittle_platform/stl/robot/{p}_{k}.stl", c, (0, 0, 0), None)
     for k in ("lf", "rf", "lr", "rr") for p, n, c in (("thigh", "Thigh", "#f2a71c"), ("shank", "Shank", "#2c2d31"))]

# Electronics and wires: colored sub-parts from pod.py (stl/models/parts.json). ALIAS: pod.py model -> viewer id.
ALIAS = dict(pizero="pizero", pisugar_s="pisugar", battery="battery", sd_card="sd_card", pi_plugs="pi_plugs", amp_ns4168="amp",
             speaker="speaker", mic_sph0645="mic", biboard_header="header", biboard_plug="bb_plug")
# Exploded view (pod.py explode_plan): a stage (reverse build order), a lift out of the open top, then a move aside.
EXPLODE = json.load(open(os.path.join(ROOT, "stl", "screw", "explode.json")))     # the screw version (pod.py write_screw_parts)
PARTS = [p[:5] + (EXPLODE["parts"].get(os.path.basename(p[3])[:-4]),) + p[6:] for p in PARTS]
GROUPS = {}
for _d in json.load(open(os.path.join(ROOT, "stl", "models", "parts.json"))):
    _a = ALIAS.get(_d["model"], "wires")
    _id = _d["model"] + "__" + _d["sub"]
    GROUPS.setdefault(_a, []).append(_id)
    PARTS.append((_id, _d["label"][0].upper() + _d["label"][1:], "Robot" if _a == "header" else "Wires" if _a == "wires" else "Components",
                  "stl/" + _d["file"], _d["color"], _d.get("explode"), None))


# Line-art finish of each part (web/lineart.js): printed, bought, dark (the robot) or clear.
DARK_MODELS = ("biboard_header",)
# One tag name for all sub-parts of a board (the tags in the step views)
TAGS = dict(pizero="Pi + PiSugar S", pisugar_s="Pi + PiSugar S", battery="Pi + PiSugar S", sd_card="Pi + PiSugar S", stack_screws="Pi + PiSugar S",
            pi_plugs="Pi header plugs", amp_ns4168="Amp", speaker="Speaker", mic_sph0645="Mic", biboard_header="BiBoard header",
            wires_speaker="Speaker lead", wires_splice="Splices", wires_amp="Amp cable",
            panel="Top panel", body="Body", door="Door", cover="Screw cover", mount_screws="Cover screws",
            mount_inserts="Inserts or nuts", panel_screws="Panel screws", panel_inserts="Inserts or nuts")


def finish(pid, group):
    if group == "Printed":
        return "print"
    if group == "Robot" or pid.split("__")[0] in DARK_MODELS:
        return "dark"
    return "buy"


def tag(pid, label):
    """The short name on the tag of a part: its board, or its wire without the housing."""
    model = pid.split("__")[0]
    if model in TAGS:
        return TAGS[model]
    if model.startswith("wires_"):
        return label.split(":")[0].replace("Uart wire", "BiBoard").replace("Mic wire", "Mic")
    return label


def expand(ids):
    """Viewer ids of a step: a model name stands for all its sub-parts."""
    out = []
    for i in ids:
        out += GROUPS.get(i, [i])
    return out


# Checks of pod.py and the peg cover (the forces in the part cards and the steps). Standard library only.
CHECKS = json.load(open(os.path.join(ROOT, "stl", "checks.json")))
ADDON_V = "0.26"
PLATFORM_V = json.load(open(os.path.join(PROJ, "bittle_platform", "interface.json")))["VERSION"]

# Text for the part card in the viewer: what the part is, how it attaches, downloads (relative to site/viewer/).
PF, AF = "../files/platform/", "../files/addon/"
INFO = {
    "cover": dict(text="The screw cover: the stock Petoi back cover with a ring on its flat top at each of the 4 peg places of the peg cover, "
                       "24 x 20 mm on the center line. An M3 x 4 screw (M2.5 x 4 for the resin version) goes up through each ring from inside the cover, and its head is in a pocket in the cover wall. "
                       "The Grove notch and the Pi slot are one opening at the front left.",
                  attach="Screw the body to it from inside the cover. Then clip the cover and the body onto the robot as one unit, in place of the stock cover.",
                  files=[("Print STL", AF + "cover_screw.stl"), ("Print STL, 0.10 mm layers", AF + "cover_screw_fine.stl"),
                         ("Peg interface spec PDF", PF + "bittle_peg_spec.pdf")]),
    "body": dict(text="The body of the pod: one rounded box with a flat floor. The floor has a boss at each of the 4 peg places, for an M3 "
                      "heat-set insert (FDM) or a glued M2.5 nut (resin). Inside: grooves for the speaker and the Pi stack, a post and a ledge with slots for the mic, and a slot bar for the amp. "
                      "The speaker posts have a boss for the panel screws. "
                      "The BiBoard header comes up through a notch in the floor, at the front of the left well. "
                      "Two nubs on the right wall hold the amp. The only cable hole at the base is the notch at the front left, over the opening in the cover. "
                      "A door in the left wall is over the BiBoard plugs: lift it out, and a finger reaches them from the side. "
                      "It prints floor down.",
                 attach="Put in the 6 inserts or nuts. Then screw the empty body to the cover with 4 screws from inside the cover (M3 x 4, or M2.5 x 4 for nuts). "
                        "To remove the add-on, take the panel off, lift the door out and pull the BiBoard plugs off. Then unclip the cover from the robot.",
                 files=[("Print 3MF", AF + "pod_body_screw.3mf"), ("Print 3MF, 0.10 mm layers", AF + "pod_body_screw_fine.3mf")]),
    "panel": dict(text="The top panel, in a second color. It has the soft top edge and openings shaped to each plug body. "
                       "The Pi power, Pi data and PiSugar charge ports and the PiSugar button share one rounded rectangle: press the button with a fingertip or a pen tip. "
                       "It slides on: hooks under it go under lugs in the front and side walls. Two M3 x 12 screws (M2.5 x 12 for the resin version) go down through it into the speaker posts. "
                       "Forks under it hold the Pi stack, the speaker and the amp down. "
                       "It prints upside down on its top.",
                  attach="Put it down 5 mm behind its place, slide it forward, and put in the two panel screws. "
                         "To open, take out the two screws, slide it 5 mm rearward and lift it.",
                  files=[("Print STL", AF + "pod_panel_screw.stl"), ("Print STL, 0.10 mm layers", AF + "pod_panel_screw_fine.stl"),
                         ("Build guide PDF", AF + "bittle_pi_addon_guide.pdf")]),
    "door": dict(text="The door: a piece of the left wall over the BiBoard plugs. An ear on each end goes down a groove in a post inside the body. "
                      "The panel holds it down. It prints on its top edge, so its outer face prints as a wall, the same as the body walls.",
                 attach="Slide it down into the two grooves before the panel goes on. "
                        "To reach the BiBoard plugs, take the panel off and lift the door out.",
                 files=[("Print STL", AF + "pod_door.stl"), ("Print STL, 0.10 mm layers", AF + "pod_door_fine.stl")]),
    "pizero": dict(text="Raspberry Pi Zero 2 W, on its long edge: ports up, GPIO header down to the left (toward the BiBoard), SD card to the rear. Model: PiSugar (GPL-3.0).",
                   attach="With the PiSugar S it slides down into the groove of the two end posts. The screw heads go down channels in the posts."),
    "pisugar": dict(text="PiSugar S battery board. Its USB-C charge port, button and power switch are at the top. Its AUTO switch is under the cell. "
                         "Fit model drawn from the PiSugar PCB drawing (part heights estimated).",
                    attach="It is screwed to the Pi. The two boards go into the end grooves together."),
    "battery": dict(text="The 1200 mAh cell of the PiSugar S, on the right side of the stack.",
                    attach="It is on the PiSugar S, on two metal discs. It stands 0.3 mm above the floor boss under it."),
    "pi_plugs": dict(text="The soldered 2x20 Pi header with Dupont housings on the 12 pins in use (pin map: the wiring blueprint).",
                     attach="Push the jumpers onto the Pi header before the stack goes in."),
    "amp": dict(text="NULLLAB NS4168 I2S amp, on edge along the right wall, upright, its screw terminal at the top. Its parts face the battery.",
                attach="Put its bottom edge into the slot of the bar on the floor, tilt its top edge under the two nubs on the wall, and set it with a dab of glue. "
                       "Forks under the panel also hold its top edge."),
    "speaker": dict(text="NULLLAB 3 W 4 ohm speaker at the rear, with a 3 mm ear plate. The sound goes out of the grille in the rear face.",
                    attach="Push the ends of the ear plate down into the two side grooves, body to the rear."),
    "mic": dict(text="HiLetgo SPH0645 I2S mic board, high on the right wall near the front, away from the speaker. The port faces 7 holes in the right side. "
                     "Its straight header is on its front edge: the plugs point inward, and the wires go straight across behind the front wall.",
                attach="Plug the six jumpers onto its header. Drop it into the slots in the post and the ledge on the right wall, "
                       "port to the wall."),
    "header": dict(text="The 5-pin BiBoard header (TX2, RX2, GND, +5V, +5V) in the Pi slot of the cover. The height is an estimate.",
                   attach="It is part of the robot."),
    "bb_plug": dict(text="Three straight Dupont plugs on the BiBoard header (TX2, RX2, GND), at the front of the left well. +5V is not wired.",
                    attach="Plug them in from the top last, after the other wires (the panel is off)."),
    "sd_card": dict(text="The microSD card. About 2.5 mm of it stands out of the holder at the rear end of the Pi (not measured).",
                    attach="To change it, lift the stack out."),
    "wires": dict(text="The jumper wires (1.4 mm), on the routes that pod.py checks: no wire touches a printed part or another board. "
                       "BCLK (pin 12) and LRCLK (pin 35) each go to a soldered splice (black sleeve) and on to the mic and the amp. "
                       "The jumpers are longer than shown: fold the slack into the left well.",
                  attach="Each jumper goes from its Pi header pin to the part. See the wiring table in the guide."),
    "wire_paths": dict(text="The free paths for the wires: the BiBoard wires in the left well, the I2S wires under the stack to the amp, "
                            "the mic wires beside the BiBoard plugs, and the speaker wires over the amp. "
                            "The check in pod.py keeps every part out of them.",
                       attach="Lay the wires in these paths before the panel goes on."),
    "shoulder_r": dict(text="Petoi side shoulder, right. Model: Petoi.", attach="Part of the robot."),
    "shoulder_l": dict(text="Petoi side shoulder, left (mirror). Model: Petoi.", attach="Part of the robot."),
    "front_plate": dict(text="Petoi front plate. Model: Petoi.", attach="Part of the robot."),
    "rear_plate": dict(text="Petoi rear plate, from the Petoi ROS model.", attach="Part of the robot."),
    "head": dict(text="The Petoi head on the neck servo. It turns about an axis 30 deg from vertical. "
                      "Use the Head turn slider or the Turn the head button to see it against the add-on.", attach="Part of the robot."),
    "tail": dict(text="The Petoi tail (Bittle_tail.stl), at the rear of the cover. It is in the Petoi ROS model. "
                      "It is 3.2 mm under the add-on, and 0.05 mm at the drop-on place.", attach="Part of the robot."),
    "robot_battery": dict(text="The robot battery under the body.", attach="Part of the robot."),
}

# One build step for each wire (the plug order of the guide, stl/wires.json)
WIRES = json.load(open(os.path.join(ROOT, "stl", "wires.json")))
_W = {(w["group"], w["wire"]): (i, w) for i, w in enumerate(WIRES["wires"], 1)}


STACK = ["battery", "pisugar", "pizero", "sd_card", "pi_plugs"]


def _wire_step(key, title=None, text=""):
    """One wire step: the wire comes in with its Dupont housings on it (a jumper comes that way)."""
    i, w = _W[key]
    new = [w["id"]] + list(w["housings"])
    under = False
    if w.get("pack"):
        text = text or f"Plug a {w.get('len_cm', 10):g} cm jumper from {w['from']} to the Pi {w['to']}. Lay its excess in {('an' if w['slack'][0] in 'aeiou' else 'a')} {w['slack']} as shown."
    return dict(title=title or f"{w['from']} \u2192 {'Pi ' if w['to'].startswith('pin') else ''}{w['to']}", view="build" if under else "wires",
                show=new, highlight=new, ghost=["body", "panel"] + (STACK[:4] if under else []), start={k: [0, 22, 0] for k in new},
                text=(text or f"Plug {w['from']} onto the Pi {w['to']}.") + f" (Wire {i} in the route table of the guide.)")


AMP_SPLICE = ["wires_amp__bclk", "wires_amp__lrc"]
AMP_IDS = ["wires_amp__" + k for k in ("g", "v", "bclk", "lrc", "din")]
SPLICE_IDS = ["wires_splice__sleeves", "wires_splice__bclk", "wires_splice__bclk_pi", "wires_splice__lrclk", "wires_splice__lrclk_pi"]

AMP_HOUSINGS = ["wires_amp__" + k + "_pi" for k in ("g", "v", "din")]
WIRE_STEPS = [
    dict(title="Splices", view="build", ghost=["body", "panel"] + STACK[:4], highlight=SPLICE_IDS,
         show=SPLICE_IDS, start={k: [0, 22, 0] for k in SPLICE_IDS},
         text="The BCLK and LRCLK splices: a short wire from Pi pin 12 (35) into the bottom of each sleeve. "
              "The LRCLK splice stands beside the BiBoard plugs, the BCLK splice at the middle of the left well."),
] + [_wire_step(tuple(k), text=f"Plug a 10 cm jumper onto Pi {_W[tuple(k)][1]['to']}. Lay its excess in "
                                f"{('an' if _W[tuple(k)][1]['slack'][0] in 'aeiou' else 'a')} {_W[tuple(k)][1]['slack']} by the left wall. "
                                "Push its other end onto the BiBoard header last, after the mic jumpers.")
     for k in WIRES["order"] if tuple(k)[0] == "uart"] + [
    dict(title="Amp cable", view="wires", ghost=["body", "panel"], highlight=AMP_IDS + AMP_HOUSINGS, show=AMP_IDS + AMP_HOUSINGS,
         start={k: [0, 22, 0] for k in AMP_IDS + AMP_HOUSINGS},
         text="Lay the flat amp cable on edge, the way it leaves the plug (G on top): down a step, forward to the front wall, "
              "across under the mic plugs and rearward along the left well, over the BiBoard jumpers. Then each wire in turn: "
              "DIN onto Pi pin 40, LRC and BCLK into the bottoms of their splice sleeves, G onto pin 14, V onto pin 2.")] + \
    [_wire_step(tuple(k)) for k in WIRES["order"] if tuple(k)[0] == "mic"]

# Build steps: parts that appear, where they start (offset in mm) and where they stop.
STEPS = [
    dict(title="The robot", show=["shoulder_r", "shoulder_l", "front_plate", "rear_plate", "header", "head", "neck_mount", "hip_servos",
                                  "robot_battery", "tail"] + [f"{p}_{k}" for k in ("lf", "rf", "lr", "rr") for p in ("thigh", "shank")], view="stepiso",
         text="The Bittle X without its back cover: the head is at the front, the tail at the rear. The BiBoard header stands up at the front left."),
    dict(title="Inserts or nuts", view="stepiso", show=["body", "mount_inserts", "panel_inserts"],
         start={"body": [0, 40, 0], "mount_inserts": [0, 75, 0], "panel_inserts": [0, 75, 0]},
         end={"body": [0, 40, 0], "mount_inserts": [0, 40, 0], "panel_inserts": [0, 40, 0]},
         text="Put an insert or a nut into each of the 4 floor bosses and the 2 speaker post bosses. "
              "FDM: press each M3 heat-set insert in flush with a soldering iron. Resin: put an M2.5 nut into each hex pocket with a drop of superglue."),
    dict(title="Screw the body to the cover", view="stepiso", show=["cover", "mount_screws"],
         start={"cover": [0, 20, 0], "mount_screws": [0, 0, 0]}, end={"cover": [0, 40, 0], "mount_screws": [0, 40, 0]},
         text="Put the empty body on the cover, grille to the rear. Put a screw up through each ring from inside the cover (M3 x 4, or M2.5 x 4 for nuts), "
              "into the insert or the nut, and tighten it."),
    dict(title="Clip onto the robot", view="stepiso", start={k: [0, 40, 0] for k in ["body", "mount_inserts", "panel_inserts", "cover", "mount_screws"]},
         text="Clip the cover and the body onto the robot as one unit, in place of the stock cover. "
              "The BiBoard header comes up through the opening in the cover and the notch at the front of the left well."),
    dict(title="Speaker", view="build", show=["speaker"], start={"speaker": [0, 40, 0]},
         text="Push the speaker down into the two side grooves at the rear, body to the rear (to the grille)."),
    dict(title="Mic", view="buildfront", show=["mic"], start={"mic": [0, 40, 0]},
         text="Plug the six jumpers onto the mic header (15 cm on GND and 3V) and let them hang out of the top. "
              "Drop the mic into the slots in the post and the ledge on the right wall, port to the wall, header at the front. "
              "No tools are necessary. Each jumper shows in the step where its other end goes onto the Pi."),
    dict(title="Amp", view="build", show=["amp", "wires_speaker__pos", "wires_speaker__neg"],
         start={k: [0, 40, 0] for k in ["amp", "wires_speaker__pos", "wires_speaker__neg"]},
         text="Plug the speaker lead into the 2-pin connector at the rear end of the amp and the amp cable into the I2S connector at its front end. "
              "Put the bottom edge of the amp into the slot along the right wall, parts to the inside, tilt its top edge under the two nubs and set it with a dab of glue. "
              "Let the flat amp cable hang out of the top: it goes in after the BiBoard jumpers."),
    dict(title="Pi stack", view="build", show=STACK, start={k: [0, 45, 0] for k in STACK},
         text="Set the PiSugar AUTO switch (it is under the cell). Push the Pi + PiSugar S stack down into the end grooves: ports up, header down to the left, SD card to the rear. "
              "Then plug the wires one at a time, as the next steps show."),
] + WIRE_STEPS + [
    dict(title="Door", view="build", show=["door"], highlight=["door"], start={"door": [0, 40, 0]},
         text="Slide the door down into the two grooves of the opening in the left wall. "
              "It stands on the wall under it. The panel holds it down."),
    dict(title="Panel", view="build", show=["panel", "panel_screws"], start={"panel": [0, 35, 5], "panel_screws": [0, 60, 5]},
         text="Put the panel down 5 mm behind its place, slide it forward, and put in the two panel screws (M3 x 12, or M2.5 x 12 for nuts). "
              "The PiSugar power switch is in the HDMI opening, beside the plug: move it with a pen tip or a toothpick. The forks under the panel hold "
              "the stack, the speaker and the amp. The ports are in the shaped openings. Press the PiSugar button through the large opening with a fingertip or a pen tip. "
              "To open, take out the two screws and slide the panel rearward."),
]


def main():
    shutil.rmtree(SITE, ignore_errors=True)
    os.makedirs(MD, exist_ok=True)
    shutil.copy2(os.path.join(os.path.dirname(ROOT), "web", "viewer.html"), os.path.join(SITE, "index.html"))
    shutil.copy2(os.path.join(os.path.dirname(ROOT), "web", "lineart.js"), os.path.join(SITE, "lineart.js"))
    out = []
    copied = {}
    for pid, label, group, src, color, ex, tf in PARTS:
        path = os.path.join(ROOT, src)
        if not os.path.exists(path):
            print("missing", src)
            continue
        name = copied.get(src)
        if name is None:
            name = os.path.basename(os.path.dirname(src)) + "_" + os.path.basename(src)
            shutil.copy2(path, os.path.join(MD, name))
            copied[src] = name
        info = INFO.get(pid) or INFO.get(next((a for a, ids in GROUPS.items() if pid in ids), ""), {})
        out.append(dict(id=pid, label=label, group=group, file="models/" + name, finish=finish(pid, group), tag=tag(pid, label),
                        color=color, explode=(ex or [0, [0, 0, 0], [0, 0, 0]]), transform=tf, **info))
    checks = json.load(open(os.path.join(ROOT, "stl", "checks.json")))["rows"]
    pi = json.load(open(os.path.join(PROJ, "bittle_platform", "interface.json")))
    E = pi["ENVELOPE"]
    meta = dict(
        title=f"Pod for Bittle X Robot v{ADDON_V}, peg interface v{PLATFORM_V}",
        explode_stages=EXPLODE["stages"],
        envelope=dict(width=2 * E["half_w_low"], length=round(E["z"][1] - E["z"][0], 1), top=E["top"],
                      above_cover=round(E["top"] - pi["COVER_TOP"], 1)),
        bounds=dict(x=[-40, 40], z=[-70, 80], y=[-12, 70]),
        checks=[dict(a=a, b=b, v=round(v, 2)) for a, b, v in checks],
    )
    robot = json.load(open(os.path.join(PROJ, "bittle_platform", "stl", "robot", "robot.json")))
    robot["motion"] = json.load(open(os.path.join(ROOT, "stl", "motion.json")))
    steps = []
    for st in STEPS:
        st = dict(st)
        if "show" in st:
            st["show"] = expand(st["show"])
        for k in ("highlight", "ghost"):
            if k in st:
                st[k] = expand(st[k])
        for k in ("start", "end"):
            if k in st:
                st[k] = {i: v for key, v in st[k].items() for i in expand([key])}
        steps.append(st)
    json.dump(dict(parts=out, meta=meta, steps=steps, robot=robot), open(os.path.join(SITE, "manifest.json"), "w"), indent=1)
    print("site ready:", len(out), "parts")


# --------------------------------------------------------------------------
# Home page: the two packages with their downloads, and a link to the viewer
# --------------------------------------------------------------------------
HOME = os.path.join(PROJ, "site")
LEGAL = ["LICENSE.md", "ATTRIBUTION.md", "LICENSES"]
PACKAGES = [
    dict(key="platform", name=f"Peg cover v{PLATFORM_V}", dir="bittle_platform", zip=f"bittle_platform_v{PLATFORM_V}.zip",
         pdf="bittle_peg_spec.pdf", img="doc/iso/platform-light.png",
         text="The stock Petoi Bittle X back cover with 4 pegs on its top. Add-ons drop onto the pegs, "
              "slide 7 mm forward and click into place. No tools, glue or tape are necessary. "
              "The spec gives every number that you need to design an add-on.",
         extra=["interface.json"]),
    dict(key="addon", name=f"Pod for Bittle X Robot v{ADDON_V}", dir="bittle_pi_addon", zip=f"bittle_pi_addon_v{ADDON_V}.zip",
         pdf="bittle_pi_addon_guide.pdf", img="doc/iso/hero-light.png", img2="doc/iso/open-light.png",
         text="The pod: Raspberry Pi Zero 2 W, PiSugar S (1200 mAh), NS4168 amp with a 3 W speaker, "
              "and an SPH0645 mic, in a rounded box with a slide-on top panel. "
              "On FDM, the add-on parts print without supports. Print plates for an FDM and a resin printer are in the downloads.",
         extra=[]),
]


def esc(t):
    return str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def size(path):
    n = os.path.getsize(path)
    return f"{n / 1e6:.1f} MB" if n > 1e6 else f"{n / 1e3:.0f} kB"


def make_zip(P, path):
    """Zip of the package folder with the license files of the repository."""
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        base = os.path.join(PROJ, P["dir"])
        for d, dirs, files in os.walk(base):
            dirs[:] = sorted(x for x in dirs if x not in ("__pycache__", "tmp"))
            for f in sorted(files):
                if f == "assembly.step":      # local build output; the package has assembly_step.zip
                    continue
                full = os.path.join(d, f)
                z.write(full, os.path.join(P["dir"], os.path.relpath(full, base)))
        for item in LEGAL:
            full = os.path.join(PROJ, item)
            if os.path.isdir(full):
                for f in sorted(os.listdir(full)):
                    z.write(os.path.join(full, f), os.path.join(P["dir"], item, f))
            else:
                z.write(full, os.path.join(P["dir"], item))


def build_home():
    files = os.path.join(HOME, "files")
    shutil.rmtree(files, ignore_errors=True)
    for item in LEGAL:
        src, dst = os.path.join(PROJ, item), os.path.join(HOME, item)
        if os.path.isdir(src):
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
    cards = []
    for P in PACKAGES:
        src = os.path.join(PROJ, P["dir"])
        dst = os.path.join(files, P["key"])
        os.makedirs(dst, exist_ok=True)
        links = []

        def put(rel, label, cls=""):
            name = os.path.basename(rel)
            if rel == P["zip"]:
                s_ = os.path.join(dst, name)
                make_zip(P, s_)
            else:
                s_ = os.path.join(src, rel)
                shutil.copy2(s_, os.path.join(dst, name))
            links.append(f'<a class="dl {cls}" href="files/{P["key"]}/{name}" download><span>{esc(label)}</span>'
                         f'<small>{esc(name)} &middot; {size(s_)}</small></a>')
        put(P["pdf"], "Specification (PDF)" if P["key"] == "platform" else "Build guide (PDF)", "primary")
        put(P["zip"], "Full package (zip)", "primary")
        for f in sorted(os.listdir(os.path.join(src, "stl", "print"))):
            if not os.path.isfile(os.path.join(src, "stl", "print", f)):
                continue                                    # stl/print/resin/: the resin parts are in the plates
            note = {"cover_pegs.stl": " (no foot, recommended)", "cover_pegs_foot.stl": " (alternative)"}.get(f, "")
            put(os.path.join("stl", "print", f), f"Print: {f[:-4]}{note}")
        plates = os.path.join(src, "stl", "plates")
        if os.path.isdir(plates):
            for f, label in (("fdm_taz.3mf", "Plate: FDM, TAZ Workhorse (3MF)"), ("fdm_taz_plate.stl", "Plate: FDM, TAZ Workhorse (STL)"),
                             ("resin_phenom.3mf", "Plate: resin, Phenom (3MF)"), ("resin_phenom_plate.stl", "Plate: resin, Phenom (STL)")):
                if os.path.exists(os.path.join(plates, f)):
                    put(os.path.join("stl", "plates", f), label)
        for f in sorted(os.listdir(os.path.join(src, "cad"))):
            if f == "assembly_step.zip":
                put(os.path.join("cad", f), "CAD: full assembly (STEP, zipped)", "primary")
            elif f.endswith(".step") and f != "assembly.step":
                put(os.path.join("cad", f), f"CAD: {f[:-5]}")
        for f in P["extra"]:
            put(f, f"Data: {f}")
        imgs = [P["img"]] + ([P["img2"]] if P.get("img2") else [])
        figs = ""
        for im in imgs:
            name = os.path.basename(im)
            shutil.copy2(os.path.join(src, im), os.path.join(dst, name))
            figs += f'<img src="files/{P["key"]}/{name}" alt="{esc(P["name"])}" loading="lazy">'
        cards.append(f'''<section class="card">
  <div class="figs">{figs}</div>
  <div class="body">
    <h2>{esc(P["name"])}</h2>
    <p>{esc(P["text"])}</p>
    <div class="links">{"".join(links)}</div>
  </div>
</section>''')
    html = PAGE.replace("{{CARDS}}", "\n".join(cards)).replace("{{DATE}}", datetime.date.today().isoformat())
    open(os.path.join(HOME, "index.html"), "w").write(html)
    print("home ready")


PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pod for Bittle X Robot</title>
<style>
:root { --bg:#fbfbf9; --fg:#16181a; --muted:#4a4f55; --card:#ffffff; --line:#e2e2dc; --accent:#0a7f63; --accent-fg:#ffffff; --grid:#ecece6; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) { --bg:#0f1112; --fg:#eceeed; --muted:#b2b8b6; --card:#161a1c; --line:#262b2d; --accent:#3fd1a6; --accent-fg:#062018; --grid:rgba(236,238,237,0.04); } }
:root[data-theme="dark"] { --bg:#0f1112; --fg:#eceeed; --muted:#b2b8b6; --card:#161a1c; --line:#262b2d; --accent:#3fd1a6; --accent-fg:#062018; --grid:rgba(236,238,237,0.04); }
* { box-sizing:border-box; }
body { margin:0; background:var(--bg); color:var(--fg); font:16px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width:1040px; margin:0 auto; padding:32px 16px 48px; }
header h1 { margin:0 0 6px; font-size:clamp(1.6rem, 4vw, 2.2rem); letter-spacing:-0.01em; }
header p { margin:0 0 20px; color:var(--muted); max-width:62ch; }
.viewer { display:inline-flex; align-items:center; gap:8px; padding:10px 16px; border-radius:10px; background:var(--accent); color:var(--accent-fg); font-weight:600; text-decoration:none; margin-bottom:28px; }
.card { background:var(--card); border:1px solid var(--line); border-radius:14px; overflow:hidden; margin-bottom:24px; display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1.1fr); }
.figs { display:grid; gap:1px; background:var(--line); }
.figs img { width:100%; height:100%; object-fit:contain; display:block; min-height:180px; padding:12px; box-sizing:border-box;
  background-color:#fbfbf9; background-image:linear-gradient(#ecece6 1px, transparent 1px), linear-gradient(90deg, #ecece6 1px, transparent 1px); background-size:24px 24px; }
.body { padding:20px 22px; }
.body h2 { margin:0 0 8px; font-size:1.3rem; }
.body p { margin:0 0 16px; color:var(--muted); }
.links { display:grid; grid-template-columns:repeat(auto-fill, minmax(200px, 1fr)); gap:8px; }
.dl { display:flex; flex-direction:column; padding:9px 12px; border:1px solid var(--line); border-radius:9px; text-decoration:none; color:var(--fg); min-width:0; }
.dl:hover { border-color:var(--accent); }
.dl span { font-weight:600; font-size:0.93rem; }
.dl small { color:var(--muted); font-size:0.78rem; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.dl.primary { border-color:var(--accent); }
footer { color:var(--muted); font-size:0.85rem; margin-top:12px; }
footer a { color:inherit; }
@media (max-width:760px) { .card { grid-template-columns:1fr; } .figs img { max-height:260px; } }
</style>
</head>
<body>
<main>
<header>
  <h1>Pod for Bittle X Robot</h1>
  <p>The 3D model for the Bittle X hardware and software of <a href="https://github.com/LineChef">LineChef</a>
  (<a href="https://github.com/LineChef/BittleX">LineChef/BittleX</a>).</p>
  <p>A 3D-printed pod for the Petoi Bittle X. It holds a Raspberry Pi Zero 2 W, a PiSugar S battery, an amp, a speaker and a mic. The repository also has a peg cover for other add-ons. This is an independent community project. It is not affiliated with or endorsed by Petoi. Bittle and Petoi are trademarks of Petoi LLC. Download the documents, the print files and the CAD below.</p>
</header>
<a class="viewer" href="viewer/">Open the 3D viewer &rarr;</a>
{{CARDS}}
<footer>Updated {{DATE}}. Code: MIT. Designs and documents: CC BY 4.0, Jeremy Collins.
The cover, side shoulder and front plate models are by <a href="https://github.com/PetoiCamp/NonCodeFiles">Petoi</a>, published without a stated license.
The Pi Zero fit model is by <a href="https://github.com/PiSugar/PiSugar">PiSugar</a> (GPL-3.0).
See <a href="LICENSE.md">LICENSE.md</a> and <a href="ATTRIBUTION.md">ATTRIBUTION.md</a>.</footer>
</main>
</body>
</html>
"""


if __name__ == "__main__":
    main()
    build_home()
