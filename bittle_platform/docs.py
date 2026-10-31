"""Bittle X platform: drawings, renders, interface.json, SPEC.md and the PDF.

Run build.py first, then:  python docs.py
README.md and bittle_platform_spec.pdf come from the same content list (CONTENT), so they agree.
"""
import datetime
import json
import re
import os
import subprocess
import sys

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, PathPatch, Polygon, Rectangle
from matplotlib.path import Path

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import interface as I            # noqa: E402
import build as B                # noqa: E402

DOC = os.path.join(HERE, "doc")
TITLE = f"Bittle X Platform v{I.VERSION} - Interface Specification"
FOOTER = f"Bittle X Platform v{I.VERSION}"
DATE = datetime.date.today().isoformat()
CHECKS = json.load(open(os.path.join(HERE, "checks.json")))


# --------------------------------------------------------------------------
# Drawings
# --------------------------------------------------------------------------
def tear_patch(px, pz, r, tip=1.0, deg=None, **kw):
    """Teardrop outline in a plan drawing (horizontal = Z, vertical = X)."""
    q = B.tear_outline(r, 240, tip, deg)
    return Polygon(np.c_[q[:, 1] + pz, q[:, 0] + px], closed=True, **kw)


def plan_drawing(path):
    fig, a = plt.subplots(figsize=(11, 7.2))
    v = B.ref_tris(I.COVER_STL).reshape(-1, 3)
    from scipy.spatial import ConvexHull
    pts = v[:, [2, 0]]
    h = ConvexHull(pts)
    a.add_patch(Polygon(pts[h.vertices], closed=True, color="0.88", label="stock cover (plan)"))
    fx, fz = I.COVER_FLAT["x"], I.COVER_FLAT["z"]
    a.add_patch(Rectangle((fz[0], fx[0]), fz[1] - fz[0], fx[1] - fx[0], fill=False, color="0.35", lw=1.2, ls="--"))
    a.annotate(f"flat top (dashed) Y {I.COVER_TOP}:\nX {fx[0]:g}..{fx[1]:g}, Z {fz[0]:g}..{fz[1]:g}", (fz[0], fx[1] - 2), (-37, 21),
               fontsize=7, color="0.3", va="top", arrowprops=dict(arrowstyle="->", color="0.5", lw=0.6))
    lp = B.logo_pts()
    a.scatter(lp[:, 1], lp[:, 0], s=0.15, color="0.55")
    a.annotate(f"raised logo (top Y {I.LOGO['top']})", (-3.5, -7.0), (-36, -22), fontsize=7, color="0.4",
               arrowprops=dict(arrowstyle="->", color="0.5", lw=0.6))
    S, H = I.SLOT_WIDE, I.HDR
    a.add_patch(Rectangle((S["z0"], S["x0"]), S["z1"] - S["z0"], S["x1"] - S["x0"], color="0.6"))
    a.add_patch(Rectangle((H["z0"], H["x0"]), H["z1"] - H["z0"], H["x1"] - H["x0"], color="tab:red", alpha=0.8))
    a.add_patch(Rectangle((H["z0"] - I.SLIDE - 0.4, H["x0"] - 0.4), H["z1"] - H["z0"] + I.SLIDE + 0.8, H["x1"] - H["x0"] + 0.8,
                          fill=False, color="tab:red", ls=":", lw=1))
    a.text(S["z1"] + 1, (S["x0"] + S["x1"]) / 2, "Pi slot + BiBoard header\n(dotted: keep-out swept 7)", fontsize=7, color="tab:red", va="center")
    for px, pz in I.PEGS:
        a.add_patch(tear_patch(px, pz, I.PEG_COLLAR_D / 2, color="tab:blue", alpha=0.25))
        a.add_patch(tear_patch(px, pz, I.PEG_HEAD_D / 2, I.HEAD_TIP, I.HEAD_TIP_DEG, fill=False, color="tab:blue", lw=1.2))
        a.add_patch(tear_patch(px, pz, I.PEG_SHAFT_D / 2, color="tab:blue"))
        a.add_patch(tear_patch(px, pz - I.SLIDE, I.PEG_HEAD_D / 2 + I.KEY_HOLE_GAP, I.HEAD_TIP, I.HEAD_TIP_DEG,
                               fill=False, color="tab:green", ls="--", lw=1))
        a.text(pz, px + (4.3 if px > 0 else -4.3), f"({px:g}, {pz:g})", ha="center", va="center", fontsize=7.5, color="tab:blue")
    dz = I.PEGS[1][1] - I.PEGS[0][1]
    zm = (I.PEGS[0][1] + I.PEGS[1][1]) / 2
    a.annotate("", (zm - dz / 2, -19.5), (zm + dz / 2, -19.5), arrowprops=dict(arrowstyle="<->", lw=0.8))
    a.text(zm, -20.2, f"{dz:g}", ha="center", va="top", fontsize=8)
    a.annotate("", (-15, -12), (-15, 12), arrowprops=dict(arrowstyle="<->", lw=0.8))
    a.text(-15.6, 0, "24", ha="right", va="center", fontsize=8)
    a.text(-27.5, -16.5, "drop-in hole\nof the add-on (-7)", fontsize=6.5, color="tab:green", ha="left", va="center")
    E = I.ENVELOPE
    for z in E["z"]:
        a.axvline(z, color="goldenrod", lw=0.9, ls="-.")
    a.text(E["z"][0] - 0.5, 36, f"pod front Z {E['z'][0]}", rotation=90, ha="right", va="top", fontsize=7, color="goldenrod")
    a.text(E["z"][1] - 0.5, 36, f"pod rear Z {E['z'][1]}", rotation=90, ha="right", va="top", fontsize=7, color="goldenrod")
    a.axhline(E["half_w_low"], color="goldenrod", lw=0.9, ls="-."); a.axhline(-E["half_w_low"], color="goldenrod", lw=0.9, ls="-.")
    a.text(60, E["half_w_low"] + 0.6, f"|X| {E['half_w_low']}", fontsize=7, color="goldenrod")
    a.annotate("FRONT (head)", (-64, 0), (-52, 0), arrowprops=dict(arrowstyle="->"), va="center", fontsize=8)
    a.plot([0], [0], "k+", ms=10)
    a.text(0.6, 0.6, "origin", fontsize=7)
    a.set_xlim(-66, 80); a.set_ylim(-40, 40); a.set_aspect("equal"); a.grid(True, lw=0.3)
    a.set_xlabel("Z (mm)   - = front (head end), + = rear"); a.set_ylabel("X (mm)   + = robot right side")
    a.set_title("Plan view (from above): platform, pegs, keep-outs")
    plt.tight_layout(); plt.savefig(path, dpi=160); plt.close(fig)


def keyhole_drawing(path):
    fig, (a, b) = plt.subplots(1, 2, figsize=(11.5, 4.9), gridspec_kw=dict(width_ratios=[1, 1.15]))
    D = I.DET
    px, pz = I.PEGS[1]
    zb = -I.SLIDE
    # the starter plate around one keyhole, at mid thickness (holes cut out)
    sec = B.to_m(B.starter_plate()).transform(np.array([[1.0, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0]])).slice(-(I.MOUNT_Y0 + I.MOUNT_T / 2))
    verts, codes = [], []
    for poly in sec.to_polygons():
        q = np.array(poly)
        q = np.c_[q[:, 1] - pz, q[:, 0] - px]
        verts += list(q) + [q[0]]
        codes += [Path.MOVETO] + [Path.LINETO] * (len(q) - 1) + [Path.CLOSEPOLY]
    a.add_patch(PathPatch(Path(verts, codes), facecolor="goldenrod", alpha=0.45, edgecolor="k", lw=0.6))
    a.add_patch(tear_patch(0, 0, I.PEG_HEAD_D / 2, I.HEAD_TIP, I.HEAD_TIP_DEG, fill=False, color="tab:blue", lw=1.2, ls="--"))
    a.add_patch(tear_patch(0, 0, I.PEG_SHAFT_D / 2, color="tab:blue", alpha=0.6))
    for sx in (1, -1):
        a.add_patch(Circle((-B.DET_DZ, sx * B.DET_DX), D["bump_r"], fill=False, color="tab:red", lw=0.8))
    a.annotate("", (0, -6.4), (zb, -6.4), arrowprops=dict(arrowstyle="<->"))
    a.text(zb / 2, -6.9, f"SLIDE {I.SLIDE:g}", ha="center", va="top", fontsize=8)
    a.text(zb - 1.0, -4.9, f"drop-in hole: head + {I.KEY_HOLE_GAP:g}", ha="center", va="top", fontsize=7.5)
    a.text(3.0, 4.9, "head (dashed): point to the rear", color="tab:blue", fontsize=7.5, ha="center")
    a.annotate(f"two bumps R{D['bump_r']:g}: they push the\nshaft into the V stop", (-B.DET_DZ, -B.DET_DX + D["bump_r"] - 0.3),
               (5.0, -4.6), color="tab:red", fontsize=7.5, arrowprops=dict(arrowstyle="->", color="tab:red", lw=0.7))
    a.text(-15.5, 6.9, f"beams {D['beam_w']:g} wide, arm {D['arm']:g}, slits {D['slit_w']:g}", color="0.3", fontsize=7.5)
    a.annotate("", (-8, 8.3), (0, 8.3), arrowprops=dict(arrowstyle="->", lw=1.2))
    a.text(0.5, 8.3, "add-on slides -Z (forward) to lock", fontsize=7.5, va="center")
    a.set_xlim(-16, 10); a.set_ylim(-8.5, 9.2); a.set_aspect("equal")
    a.set_xlabel("Z (mm, relative to peg)   - = front"); a.set_ylabel("X (mm, relative to peg)")
    a.set_title("Keyhole in the add-on mount plate (top view)")
    a.grid(True, lw=0.3)
    # section of a peg with the mount plate
    yt = I.COVER_TOP
    b.add_patch(Rectangle((-13, I.COVER_INNER_AT_PEGS), 26, yt - I.COVER_INNER_AT_PEGS, color="0.3"))
    b.text(-12.6, I.COVER_INNER_AT_PEGS + 0.35, "cover wall", color="w", fontsize=7.5)
    b.add_patch(Rectangle((-I.PEG_SHAFT_D / 2, I.PEG_ROOT_Y), I.PEG_SHAFT_D, I.PEG_HEAD_Y0 - I.PEG_ROOT_Y, color="tab:blue", alpha=0.6))
    c = I.PEG_HEAD_CHAMFER
    r = I.PEG_HEAD_D / 2
    b.add_patch(Polygon([(-r, I.PEG_HEAD_Y0), (r, I.PEG_HEAD_Y0), (r, I.PEG_HEAD_Y1 - c), (r - c, I.PEG_HEAD_Y1),
                         (-r + c, I.PEG_HEAD_Y1), (-r, I.PEG_HEAD_Y1 - c)], color="tab:blue", alpha=0.6))
    b.add_patch(Rectangle((-I.PEG_COLLAR_D / 2, yt - 0.3), I.PEG_COLLAR_D, I.PEG_COLLAR_Y1 - yt + 0.3, color="tab:blue", alpha=0.6))
    for sx in (1, -1):
        x0 = I.KEY_SLOT_W / 2
        b.add_patch(Rectangle((x0 if sx > 0 else -13, I.MOUNT_Y0), 13 - x0, I.MOUNT_T, color="goldenrod", alpha=0.8))
    b.text(4.0, I.MOUNT_Y0 + 0.5, "add-on mount plate", fontsize=7)
    levels = [(I.HEAD_CLEAR_Y, f"{I.HEAD_CLEAR_Y:g} keep-out top over the head sweep"),
              (I.PEG_HEAD_Y1, f"{I.PEG_HEAD_Y1:g} head top ({c:g} chamfer)"),
              (I.PEG_HEAD_Y0, f"{I.PEG_HEAD_Y0:g} head underside"),
              (I.MOUNT_Y1, f"{I.MOUNT_Y1:g} plate top (max)"),
              (I.MOUNT_Y0, f"{I.MOUNT_Y0:g} plate bottom = mount face"),
              (I.PEG_COLLAR_Y1, f"{I.PEG_COLLAR_Y1:g} collar top"),
              (yt, f"{yt:g} cover top"),
              (I.PEG_ROOT_Y, f"{I.PEG_ROOT_Y:g} shaft root"),
              (I.COVER_INNER_AT_PEGS, f"{I.COVER_INNER_AT_PEGS:g} cover inner surface")]
    ys = np.linspace(I.COVER_INNER_AT_PEGS - 0.1, I.HEAD_CLEAR_Y + 0.2, len(levels))[::-1]
    for (y, t), yl in zip(levels, ys):
        b.plot([5.5, 13.5, 14.2], [y, y, yl], color="0.5", lw=0.4)
        b.text(14.4, yl, t, va="center", fontsize=7)
    b.set_xlim(-13, 32); b.set_ylim(23.4, 29.8); b.set_aspect(2.4)
    b.set_xlabel("X (mm, relative to peg)"); b.set_ylabel("Y (mm, up)")
    b.set_title("Peg section with the mount plate (Y scale x2.4)")
    plt.tight_layout(); plt.savefig(path, dpi=160); plt.close(fig)


# --------------------------------------------------------------------------
# Renders (OpenSCAD)
# --------------------------------------------------------------------------
COL = dict(cover="[0.22,0.22,0.24]", plate="[0.98,0.74,0.10]", outr="[0.55,0.56,0.60]", shoulder="[0.95,0.66,0.12]",
           fplate="[0.13,0.13,0.14]", keep="[0.85,0.20,0.20,0.35]", hdr="[0.85,0.2,0.2]")


def scad(items):
    s = "".join(f'color({c}) import("{p}");\n' for p, c in items)
    return f"rotate([90,0,0]) {{\n{s}}}\n"


def render(name, items, cam, size=(1400, 950), ortho=False):
    os.makedirs(DOC, exist_ok=True)
    src, png = os.path.join(DOC, name + ".scad"), os.path.join(DOC, name + ".png")
    open(src, "w").write(scad(items))
    args = ["openscad", "-o", png, f"--imgsize={size[0]},{size[1]}", f"--camera={cam}", "--colorscheme=Tomorrow"]
    if ortho:
        args.append("--projection=o")
    r = subprocess.run(args + [src], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-800:])
    os.unlink(src)
    return png


def renders():
    st = os.path.join(HERE, "stl", "installed")
    inst = lambda k: os.path.join(st, k + ".stl")
    tmp = os.path.join(DOC, "tmp")
    os.makedirs(tmp, exist_ok=True)
    robot = []
    for k, t in B.robot_meshes().items():
        p = os.path.join(tmp, k + ".stl")
        B.MU.save_stl(B.MU.mesh_to_manifold(t), p)
        robot.append((p, COL["shoulder"] if "shoulder" in k else COL["fplate"]))
    render("r2_starter", robot + [(inst("cover_pegs"), COL["cover"]), (inst("starter_plate"), COL["plate"])],
           "0,-10,6,55,0,220,300")
    import shutil
    shutil.rmtree(tmp)


# --------------------------------------------------------------------------
# Content (one source for SPEC.md and the PDF)
# --------------------------------------------------------------------------
def fmt(v):
    return f"{v:g}" if isinstance(v, float) else str(v)


def content():
    D, E, H = I.DET, I.ENVELOPE, I.HDR
    cl = CHECKS["clearances"]
    DF = CHECKS["detent"]
    pegs = ", ".join(f"({x:g}, {z:g})" for x, z in I.PEGS)
    X = []
    h = lambda t: X.append(("h", t))
    p = lambda t: X.append(("p", t))
    tbl = lambda rows, w: X.append(("table", rows, w))
    img = lambda f, w=1.0, cap="": X.append(("img", f, w, cap))
    lst = lambda items: X.append(("list", items))

    p(f"Version {I.VERSION}, {DATE}. The platform is the stock Petoi Bittle X back cover with 4 teardrop pegs on its top. "
      f"An add-on has a plate with 4 keyholes. Put it on the pegs, slide it {I.SLIDE:g} mm forward, and it clicks. "
      f"To remove it, slide it {I.SLIDE:g} mm rearward and lift it. It comes off closed: the head is not in the way. "
      "The keyholes have the shape of the pegs, so the add-on goes on in one direction only. "
      "No tools, glue or tape are necessary. interface.json has all the numbers in machine-readable form.")
    p("Version 3.0 is not compatible with earlier versions: the pegs have a new shape and place, and the slide goes the other way. "
      "Version 3.1 adds a notch in the front edge of the cover, left side, for the Grove plug on the BiBoard (the head camera cable). "
      "Version 3.2 turns the cover model 180 deg to match the robot: the Pi slot (the BiBoard header) is at the front left, and the notch is on the "
      "front left, as on the robot. Reprint the cover: the pegs and the keyholes are the same as in 3.0. "
      "Keep add-on parts out of the plug space (GROVE_PLUG, in keepout.stl). "
      f"Version 3.3 cuts the Pi slot wider toward the center ({I.SLOT_WIDE['x1'] - I.SLOT_WIDE['x0']:g} mm, was {I.SLOT['x1'] - I.SLOT['x0']:g} mm): "
      "the BiBoard Dupont plugs did not fit. "
      f"It also makes the click travel smaller ({I.DET['travel']:g} mm, was 0.28 mm): the add-on slides on and off with less force. "
      "Reprint the cover and the add-on plate. The pegs do not change.")
    img("iso/platform-light.png", 0.6, "The platform (white) on the robot, with the starter plate on the pegs.")

    h("1. Key numbers")
    tbl([["Item", "Value (mm)"],
         ["Frame", "X lateral (+X = robot right), Y up, Z along the body (-Z = head end). Origin: center line, middle of the cover."],
         ["Pegs (X, Z)", f"{pegs}: a centered 24 x {I.PEGS[1][1] - I.PEGS[0][1]:g} rectangle"],
         ["Peg", f"teardrops with the point to the rear (+Z). Head: R{I.PEG_HEAD_D / 2:g}, point {I.HEAD_TIP_DEG * 2:g} deg, Y {I.PEG_HEAD_Y0:g} to {I.PEG_HEAD_Y1:g}. "
                 f"Shaft: R{I.PEG_SHAFT_D / 2:g}, point {I.TIP_DEG * 2:g} deg"],
         ["Add-on plate", f"bottom at Y {I.MOUNT_Y0:g}, {I.MOUNT_T:g} thick at the keyholes"],
         ["Keyhole", f"drop-in hole {I.SLIDE:g} mm in front of the peg = the head teardrop + {I.KEY_HOLE_GAP:g}; slot {I.KEY_SLOT_W:g} wide back to a V stop at the peg; {I.KEY_LEAD:g} lead-in chamfers top and bottom"],
         ["Fit", f"put the add-on on {I.SLIDE:g} mm behind its place, then slide it {I.SLIDE:g} mm forward until it clicks. Remove: slide it rearward and lift"],
         ["Click (detent)", f"two {D['beam_w']:g} wide spring beams, one on each side of each slot, freed by {D['slit_w']:g} U slits (fixed at the rear end only). "
                            f"Bumps R{D['bump_r']:g} at {B.DET_DZ:.2f} in front of the peg, {D['travel']:g} into the shaft path. They push the shaft point into the V stop, which centers it."],
         ["Click force", f"about {DF['lock_N']:g} N to slide on and {DF['unlock_N']:g} N to slide off (all {2 * len(I.PEGS)} beams, PLA estimate); beam strain {DF['strain_pct']:g} %"],
         ["Keep clear", f"the peg heads as they slide; the BiBoard header in the cover slot (X {H['x0']:g}..{H['x1']:g}, Z {H['z0']:g}..{H['z1']:g}, top Y {H['top']:g})"],
         ["Size", f"the pod fits in Z {E['z'][0]:g}..{E['z'][1]:g}, |X| <= {E['half_w_low']:g}; outside that, check the legs and the head"],
         ], [30, 140])
    img("keyhole.png", 0.95, "Left: keyhole and click beams in the add-on plate (top view, locked). Right: the peg and the plate (side section).")
    img("plan.png", 0.78, "Plan view: pegs (blue), drop-in holes (green), BiBoard header (red), pod size (gold).")

    h("2. Design an add-on")
    lst(["Start from cad/starter_plate.step. It has the keyholes and the click beams.",
         "Add your part on top of the plate, in the same print. You can also screw parts to the M3 holes.",
         "Keep your part out of stl/installed/keepout.stl. This keeps it clear of the robot, the peg heads and the header.",
         f"Keep heavy parts low and near the pegs. Keep the center of mass of the add-on within {I.ENVELOPE['com_z_max']:g} mm of Z 0, near X 0.",
         "Keep the weight low and near the center line. The pegs carry the whole add-on.",
         "For a plate of a different shape: subtract cad/keyhole_cutter.step, then add cad/detent_bumps.step. Both are in position."])

    h("3. Printing")
    p("One Cura profile prints every part: \"Bittle X\" (cura/Bittle_X.curaprofile in the repository; import it in Cura). "
      "cura/install_profiles.py installs it, and a copy with the size compensation of each spool that the tolerance app measured.")
    tbl([["Part", "Orientation", "Supports"],
         ["cover_pegs (no foot, recommended)", "stand on the rear end", "turn on tree supports from the bed and a 14-line brim"],
         ["cover_pegs_foot (alternative)", "stand on the rear end, foot on the bed", "none: the foot is the support. Snap it off after the print."],
         ["starter_plate and add-ons", "plate bottom on the bed", "none"],
         ], [50, 55, 65])
    tbl([["Setting", "Bittle X"],
         ["Layer", "0.20 (first layer 0.25)"],
         ["Walls / infill", "3 / 20 % gyroid"],
         ["Outer wall / inner wall / infill speed", "25 / 40 / 55 mm/s"],
         ["Outer wall acceleration", "500 mm/s²"],
         ["Supports / brim", "off / 6 lines"],
         ["Nozzle", "220 C (PLA)"],
         ], [80, 90])
    lst(["Material: PLA works. Use PETG for add-ons that you remove often or that get warm.",
         "Standing on its end, the cover prints the pegs with layers along their length. This makes them strong. The shaft and collar points are down, so they need no supports.",
         "The cover stands on a thin strip, and its center of mass is past that strip. The foot is a 3-layer plate with 7 fins under the leaning face. It increases the first layer from 53 to about 1000 mm². The fins touch the cover only at 21 small teeth, each one layer tall at 0.20 mm layers. Twist the foot off after the print. "
         "The no-foot print is the recommended one: the foot teeth leave a spot on the cover where they break off.",
         "In add-ons, keep overhangs at 45 deg or less. Use chamfers, not round edges, on the bottom side.",
         f"The fits use {I.KEY_SLOT_GAP:g} (slot), {I.KEY_HOLE_GAP:g} (drop-in hole) and {I.PEG_HEAD_Y0 - I.MOUNT_Y1:.1f} (under the heads) clearance. Calibrate your printer if the plate does not slide on."])

    h("4. Files")
    tbl([["File", "Content"],
         ["stl/print/", "the parts to print, in print orientation"],
         ["cad/starter_plate.step", "the start point for an add-on"],
         ["cad/pegs.step, keyhole_cutter.step, detent_bumps.step", "the interface parts, in position (robot frame)"],
         ["stl/installed/", "all parts and keepout.stl in the robot frame"],
         ["interface.json / interface.py", "all numbers"],
         ["build.py, docs.py", "rebuild the parts and this document (build123d, manifold3d)"],
         ], [70, 100])
    p("Open items: the BiBoard header height is an estimate from photos. The legs, the head and the robot balance are not modeled. "
      "The Petoi cover is a mesh, so cover_pegs is STL only.")

    h("5. Bittle X V2 back touch sensor")
    lst(["On a Bittle X V2, the back touch sensor is a flexible circuit that is glued to the inside of the cover top. "
         "It has touch areas on the left, the right, the center and near the tail "
         "(docs.petoi.com/extensible-modules/back-touch-sensor).",
         "The peg roots stop inside the 1.4 mm wall, so the inside of the cover does not change, except at the Grove notch at the front-left edge. "
         "Move the circuit from the stock cover to cover_pegs in the same way as on the stock cover.",
         "An add-on on the platform covers most of the touch areas. Disable the back touch mode (serial command Xb) "
         "when an add-on is on the robot.",
         "For this reason, the platform has no parts under the cover top. A cover that prints flat without supports "
         "needs pegs held from inside the cover, where the circuit is. A later interface with sockets in a thicker top can avoid this."])
    img("petoi_touch_areas.png", 0.45, "Bittle X V2 touch areas (red boxes). Image: Petoi, docs.petoi.com/extensible-modules/back-touch-sensor.")

    h("6. License")
    p("The designs and this document are CC BY 4.0, and the code is MIT (Jeremy Collins). "
      "The cover, the side shoulder and the front plate are Petoi files from github.com/PetoiCamp/NonCodeFiles. "
      "Petoi publishes them without a stated license, and cover_pegs.stl is made from the Petoi cover. "
      "LICENSE.md and ATTRIBUTION.md in the repository give the details.")
    return X


def interface_dict():
    d = {k: getattr(I, k) for k in dir(I) if k.isupper()}
    d = json.loads(json.dumps(d))
    d["frame"] = "X lateral (+X robot right), Y up, Z length (-Z head end); mm; origin on the center line at the middle of the cover"
    d["fit_sequence"] = (f"place {I.SLIDE:g} mm rearward (+Z) of the locked place, lower onto the pegs, slide {I.SLIDE:g} mm forward (-Z) "
                         f"until the detents click; remove: slide {I.SLIDE:g} mm rearward and lift")
    d["keyholes"] = [dict(peg=[x, z], slot=[[x, z - I.SLIDE], [x, z]], drop_in_center=[x, z - I.SLIDE],
                          bump_centers=[[x + B.DET_DX, z - B.DET_DZ], [x - B.DET_DX, z - B.DET_DZ]])
                     for x, z in I.PEGS]
    d["clearances"] = CHECKS["clearances"]
    return rnd(d)


def rnd(o):
    if isinstance(o, float):
        return round(o, 3)
    if isinstance(o, dict):
        return {k: rnd(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [rnd(v) for v in o]
    return o


def compact_json(o):
    """Indented JSON, but lists of numbers stay on one line."""
    import re
    t = json.dumps(o, indent=1)
    return re.sub(r"\[[\s\d.,\-\[\]]+\]", lambda m: re.sub(r"\s+", "", m.group(0)).replace(",", ", "), t)


# --------------------------------------------------------------------------
# Writers
# --------------------------------------------------------------------------
def write_md(X, path):
    out = [f"# {TITLE}\n"]
    for b in X:
        k = b[0]
        if k == "h":
            out.append(f"\n## {b[1]}\n")
        elif k == "p":
            out.append(b[1] + "\n")
        elif k == "list":
            out += [f"{i + 1}. {t}" for i, t in enumerate(b[1])] + [""]
        elif k == "table":
            rows = b[1]
            out.append("| " + " | ".join(rows[0]) + " |")
            out.append("|" + "---|" * len(rows[0]))
            out += ["| " + " | ".join(str(c).replace("|", "\\|") for c in r) + " |" for r in rows[1:]]
            out.append("")
        elif k == "img":
            out.append(f"![{b[3]}](doc/{b[1]})\n")
        elif k == "code":
            out.append("```\n" + b[1] + "\n```\n")
    open(path, "w").write("\n".join(out) + "\n")


def write_pdf(X, path):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Preformatted, SimpleDocTemplate,
                                    Spacer, Table, TableStyle, ListFlowable, ListItem)
    from PIL import Image as PImg
    ss = getSampleStyleSheet()
    H1 = ParagraphStyle("h1", parent=ss["Heading1"], fontSize=16, spaceAfter=4)
    H2 = ParagraphStyle("h2", parent=ss["Heading2"], fontSize=12.5, spaceBefore=8, spaceAfter=3)
    P = ParagraphStyle("p", parent=ss["BodyText"], fontSize=9, leading=11.8)
    CAP = ParagraphStyle("c", parent=P, fontSize=7.8, leading=9.5, textColor=colors.HexColor("#555555"))
    T8 = ParagraphStyle("t", parent=P, fontSize=8, leading=9.8)
    TH = ParagraphStyle("th", parent=T8, fontName="Helvetica-Bold")
    CODE = ParagraphStyle("code", parent=P, fontName="Courier", fontSize=6.8, leading=8.0)
    W = A4[0] - 30 * mm
    esc = lambda t: str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Markdown links [text](url) become PDF links.
    link = lambda t: re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
                            r'<link href="\2" color="#1a5fb4"><u>\1</u></link>', esc(t))
    story = [Paragraph(esc(TITLE), H1)]
    for b in X:
        k = b[0]
        if k == "h":
            story.append(Paragraph(esc(b[1]), H2))
        elif k == "p":
            story.append(Paragraph(link(b[1]), P))
            story.append(Spacer(1, 2))
        elif k == "list":
            story.append(ListFlowable([ListItem(Paragraph(link(t), P), leftIndent=12) for t in b[1]],
                                      bulletType="1", bulletFontSize=8.5, leftIndent=12))
        elif k == "table":
            rows, w = b[1], b[2]
            sc = W / (sum(w) * mm)
            data = [[Paragraph(link(c), TH if i == 0 else T8) for c in r] for i, r in enumerate(rows)]
            t = Table(data, colWidths=[x * mm * sc for x in w], repeatRows=1)
            t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                   ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#bbbbbb")),
                                   ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f3d27a")),
                                   ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
            story += [t, Spacer(1, 4)]
        elif k == "img":
            f = os.path.join(DOC, b[1])
            iw, ih = PImg.open(f).size
            w = W * b[2]
            story.append(KeepTogether([Image(f, width=w, height=w * ih / iw), Paragraph(esc(b[3]), CAP), Spacer(1, 4)]))
        elif k == "code":
            story += [Preformatted(b[1], CODE), Spacer(1, 4)]
        elif k == "break":
            story.append(PageBreak())

    def foot(c, d):
        c.saveState()
        c.setFont("Helvetica", 7)
        c.drawString(15 * mm, 8 * mm, f"{FOOTER} - {DATE}")
        c.drawRightString(A4[0] - 15 * mm, 8 * mm, f"page {d.page}")
        c.restoreState()

    SimpleDocTemplate(path, pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=13 * mm, bottomMargin=14 * mm,
                      title=TITLE, author="Bittle X platform").build(story, onFirstPage=foot, onLaterPages=foot)


def main(skip_renders=False):
    os.makedirs(DOC, exist_ok=True)
    plan_drawing(os.path.join(DOC, "plan.png"))
    keyhole_drawing(os.path.join(DOC, "keyhole.png"))
    if not skip_renders:
        renders()
    open(os.path.join(HERE, "interface.json"), "w").write(compact_json(dict(interface_dict(), checks=rnd(CHECKS))) + "\n")
    X = content()
    write_md(X, os.path.join(HERE, "README.md"))
    write_pdf(X, os.path.join(HERE, "bittle_platform_spec.pdf"))
    print("docs ready")


if __name__ == "__main__":
    main(skip_renders="--no-renders" in sys.argv)
