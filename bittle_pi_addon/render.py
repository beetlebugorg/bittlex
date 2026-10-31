"""Render PNG views of the pod with OpenSCAD.

The model frame is Y-up. Every scene is wrapped in rotate([90,0,0]) so that
OpenSCAD shows it Z-up (front of the robot = +Y on screen axes).
"""
import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pod  # noqa: E402

ROOT = pod.ROOT
STL = pod.OUT
REF = pod.PREF
RDIR = os.path.join(ROOT, "doc")
TMP = os.path.join(ROOT, "stl", "tmp")

C = dict(
    panel="[0.91,0.39,0.11]", body="[0.93,0.93,0.91]", cover="[0.20,0.20,0.22]",
    shoulder="[0.95,0.66,0.12]", plate="[0.13,0.13,0.14]", pizero="[0.16,0.55,0.28]",
    pisugar="[0.86,0.40,0.62]", battery="[0.30,0.48,0.85]", hdr="[0.05,0.05,0.05]", bbplug="[0.85,0.20,0.20]",
    mic="[0.85,0.2,0.2]", amp="[0.10,0.35,0.55]", plugs="[0.85,0.20,0.20]", spk="[0.45,0.30,0.70]",
    wires="[0.95,0.77,0.10]", door="[0.93,0.93,0.91]",
)


# Electronics and wires: colored sub-parts from pod.py (stl/models/parts.json)
import json  # noqa: E402
DISP = json.load(open(os.path.join(STL, "models", "parts.json")))
for _d in DISP:
    _h = _d["color"].lstrip("#")
    C[_d["model"] + "__" + _d["sub"]] = "[" + ",".join(f"{int(_h[i:i + 2], 16) / 255:.3f}" for i in (0, 2, 4)) + "]"
ELEC = [d["model"] + "__" + d["sub"] for d in DISP]
PRINTED = dict(panel="pod_panel", door="pod_door")


def imp(path, color, d=(0, 0, 0), mirror=None):
    m = f"mirror({mirror}) " if mirror else ""
    return f'translate([{d[0]},{d[1]},{d[2]}]) {m}color({color}) import("{path}");\n'


def files(cut=None):
    """Return {name: path} for all scene meshes, optionally cut by a plane."""
    src = {
        "cover": f"{STL}/installed/cover_pegs.stl",
        "body": f"{STL}/installed/pod_body.stl",
        "door": f"{STL}/installed/pod_door.stl",
        "panel": f"{STL}/installed/pod_panel.stl",
        "shoulder": f"{REF}/Bittle_SideShoulder.stl",
        "plate": f"{REF}/Bittle_FrontPlate.stl",
    }
    for d in DISP:
        src[d["model"] + "__" + d["sub"]] = f"{STL}/{d['file']}"
    if not cut:
        return src
    os.makedirs(TMP, exist_ok=True)
    normal, off = cut
    out = {}
    for k, p in src.items():
        M = pod.mesh_to_manifold(pod.load_stl(p))
        parts = [M]
        if k == "shoulder":
            parts.append(M.transform(np.diag([-1.0, 1, 1, 1])[:3, :]))
        if k == "plate":
            parts.append(M.transform(np.diag([1.0, 1, -1, 1])[:3, :]))
        for i, P in enumerate(parts):
            Q = P.trim_by_plane(normal, off)
            if Q.is_empty():
                continue
            path = f"{TMP}/{k}_{i}_{abs(hash((tuple(normal), off))) % 10**6}.stl"
            pod.save_stl(Q, path)
            out[f"{k}#{i}"] = path
    return out


def scene(show, cut=None, explode=False, robot=True):
    """explode: each part at the end of both its moves in the exploded view (pod.py explode_plan)."""
    f = files(cut)
    s = ""
    for key, path in f.items():
        k = key.split("#")[0]
        if k not in show:
            continue
        d = (0, 0, 0)
        if explode:
            plan = pod.explode_robot(PRINTED.get(k, k.split("__")[0]), k.split("__")[-1])
            if plan:
                d = tuple(a + b for a, b in zip(plan[1], plan[2]))
        s += imp(path, C[k], d)
        if not cut:
            if k == "shoulder" and robot:
                s += imp(path, C[k], mirror="[1,0,0]")
            if k == "plate" and robot:
                s += imp(path, C[k], mirror="[0,0,1]")
    return f"rotate([90,0,0]) {{\n{s}}}\n"


def render(name, scad, cam, size=(1400, 1000), ortho=False):
    os.makedirs(RDIR, exist_ok=True)
    src = os.path.join(RDIR, name + ".scad")
    png = os.path.join(RDIR, name + ".png")
    open(src, "w").write(scad)
    args = ["openscad", "-o", png, f"--imgsize={size[0]},{size[1]}", f"--camera={cam}",
            "--colorscheme=Tomorrow", "--backend=manifold"]
    if ortho:
        args.append("--projection=o")
    r = subprocess.run(args + [src], capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr[-1500:])
    os.unlink(src)
    return png


ALL = ["cover", "body", "door", "panel", "shoulder", "plate"] + [k for k in ELEC if not k.startswith("wires_")]
WIRES = [k for k in ELEC if k.startswith("wires_")]
ALL += WIRES
OPEN = [k for k in ALL if k != "panel"]
ROBOT = ["cover", "shoulder", "plate"]

JOBS = {
    # name: (show, cut, explode, camera, ortho). Camera centers on the add-on (OpenSCAD Z = model Y about 42).
    "02_addon": (ALL, None, 0, "0,-9,38,62,0,128,340", False),
    "03_rear": (ALL, None, 0, "0,-9,38,62,0,312,340", False),
    "04_top": (ALL, None, 0, "2,-4,62,35,0,200,170", False),
    "05_front_notch": (ALL, None, 0, "-4,30.0,30,78,0,200,170", False),
    "06_open": (OPEN, None, 0, "0,-9,40,48,0,150,300", False),
    "07_open_left": (OPEN, None, 0, "0,-9,40,48,0,215,300", False),
    "08_section": (ALL, ((0, 0, 1.0), 18.0), 0, "0,-18,44,90,0,180,230", True),
    "09_wires": (OPEN, None, 0, "0,-9,40,60,0,140,300", False),
    "10_exploded": (ALL, None, True, "0,-9,185,72,0,128,960", False),
    "11_wires_top": (OPEN, None, 0, "4,-9,45,0,0,180,300", False),
    "12_wires_left": (OPEN, None, 0, "-14,-9,42,40,0,270,220", False),
}


def main(which=None):
    for name, (show, cut, ex, cam, ortho) in JOBS.items():
        if which and not any(w in name for w in which):
            continue
        print(render(name, scene(show, cut, ex), cam, ortho=ortho))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
