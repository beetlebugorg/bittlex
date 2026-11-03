"""Line-art PNGs of the add-on in the style of the beetlebug.org explode viewer, light and dark.

Run after pod.py:  python iso_render.py [name ...]
  doc/iso/<name>-light.png, doc/iso/<name>-dark.png   transparent background
  hero          the finished build on the robot
  exploded      every part out of the open top (pod.py explode_plan)
  stepNN        one figure per step of the build guide (guide.py STEPS): the parts of the step in the accent,
                exploded along their insert direction, with a dashed guide line from their place
  top, open, wires   figures for README.md and the site home page
The page iso/render.html draws each figure with three.js (iso/node_modules, from iso/package.json: npm install)
and the look of web/lineart.js, which the viewer also uses. Headless Chromium runs the page.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, PROJ)
import build_site as BS   # noqa: E402  (part list, finishes, tags; standard library only)
import guide              # noqa: E402  (the build steps)
import pod                # noqa: E402
from bittle_platform import interface as PI   # noqa: E402

OUT = os.path.join(HERE, "doc", "iso")
PLATFORM_OUT = os.path.join(PROJ, "bittle_platform", "doc", "iso")   # the peg cover figure (job "platform")
THEMES = ("light", "dark")

# View directions in the Y-up model frame (X right, Y up, +Z rear). The site uses (1.3, 1.5, 1.0) in its Z-up frame
# for this project: from the front right, above.
ISO = (1.3, 1.0, -1.5)
DIRS = dict(iso=ISO, high=(1.0, 1.9, -1.3), rear=(0.7, 1.9, -1.4), mic=(-1.0, 1.7, 0.9), amp=(-1.4, 1.8, -0.5),
            well=(-1.5, 1.25, 0.35), front_left=(-1.2, 1.6, -1.1), top=(0.35, 2.4, -0.9), door=(1.5, 1.1, -0.7),
            below=(1.3, -1.1, -1.5))


COVER_DIR = (1.6, 0.9, -0.8)       # the cover picture of the Printdeck project: more from the side, for a 4:3 tile
COVER = os.path.join(HERE, "doc", "cover.png")


def make_cover(src=os.path.join(OUT, "cover-light.png"), size=(1200, 900)):
    """The cover of the project for printdeck.yml: the cover render (transparent), padded to 4:3 and scaled to size."""
    from PIL import Image
    im = Image.open(src).convert("RGBA")
    im = im.crop(im.getchannel("A").getbbox())
    w, h = im.size
    W, H = (w, round(w * 3 / 4)) if w * 3 >= h * 4 else (round(h * 4 / 3), h)
    pad = round(0.03 * W)
    canvas = Image.new("RGBA", (W + 2 * pad, H + 2 * pad), (0, 0, 0, 0))
    canvas.paste(im, ((W + 2 * pad - w) // 2, (H + 2 * pad - h) // 2), im)
    canvas.resize(size, Image.LANCZOS).save(COVER, optimize=True)
    return COVER


# --------------------------------------------------------------------------
# Parts: the viewer part list (build_site.py) and the starter plate
# --------------------------------------------------------------------------
def part_table():
    parts = {}
    for pid, label, group, src, color, ex, tf in BS.PARTS:
        path = os.path.normpath(os.path.join(HERE, src))
        if os.path.exists(path):
            parts[pid] = dict(file=os.path.relpath(path, PROJ), finish=BS.finish(pid, group), tag=BS.tag(pid, label),
                              transform=tf, explode=ex, color=color)
    parts["starter_plate"] = dict(file="bittle_platform/stl/installed/starter_plate.stl", finish="print", tag="Starter plate",
                                  transform=None, explode=None)
    parts["cover_pegs"] = dict(file="bittle_platform/stl/installed/cover_pegs.stl", finish="print", tag="Peg cover",
                               transform=None, explode=None)          # the peg cover figure (the site shows the screw cover)
    return parts


PARTS = part_table()
ROBOT = [p[0] for p in BS.PARTS if p[2] == "Robot" and not p[0].startswith("biboard_header")]
TRUNK = ["shoulder_r", "shoulder_l", "front_plate", "rear_plate", "biboard_header__header"]
PRINTED = ["cover", "body", "door", "panel"]
HARDWARE = ["mount_screws", "mount_inserts", "panel_screws", "panel_inserts"]
INSIDE = [k for k in PARTS if "__" in k and not k.startswith("biboard_header")]
ALL = ROBOT + PRINTED + HARDWARE + ["biboard_header__header"] + INSIDE
PANEL = ["panel"]


def ids(keys):
    """guide.py part keys to viewer ids (the guide uses one shoulder and one plate mesh, mirrored)."""
    out = []
    for k in keys:
        out += dict(shoulder=["shoulder_r", "shoulder_l"], plate=["front_plate", "rear_plate"]).get(k, [k])
    return [k for k in out if k in PARTS]


# --------------------------------------------------------------------------
# The build steps (guide.py): how each step moves its parts in, and the view
# --------------------------------------------------------------------------
UP = lambda h, back=0.0: (0.0, h, back)      # noqa: E731  up h mm, back mm toward the rear (+Z)

# title: (offset of the new parts, view, extra moving parts, ghost the body, show the robot trunk)
MOVES = {
    "Inserts or nuts": (UP(30), "high", [], False, False),
    "Screw the body to the cover": (UP(-22), "below", [], False, False),
    "Clip onto the robot": (UP(40), "iso", ["cover", "body"] + HARDWARE[:2] + ["panel_inserts"], False, True),
    "Speaker": (UP(45), "rear", [], False, True),
    "Mic": (UP(42), "mic", [], False, True),
    "Amp and speaker lead": (UP(48), "amp", [], False, True),
    "Pi + PiSugar S stack": (UP(55), "high", [], False, True),
    "Splices (BCLK and LRCLK)": (UP(34), "well", [], True, False),
    "BiBoard jumpers: Pi ends": (UP(34), "well", [], True, False),
    "Amp cable": (UP(34), "well", [], True, False),
    "Mic jumpers": (UP(34), "well", [], True, False),
    "BiBoard ends": (UP(34), "front_left", [], True, False),
    "Door": (UP(40), "door", [], False, True),
    "Panel": (UP(40, pod.LID_SLIDE), "iso", [], False, True),
}
# One tag for all the parts of a step (else one tag for each name)
STEP_TAG = {"Mic": "Mic", "Pi + PiSugar S stack": "Pi + PiSugar S", "Clip onto the robot": "Add-on on its cover"}


def step_jobs():
    guide.build_steps()
    jobs = []
    for i, s in enumerate(guide.STEPS, 1):
        off, view, extra, ghost, trunk = MOVES[s["title"]]
        before, new = ids(s["before"]), ids(s["new"])
        move = new + [k for k in extra if k not in new]
        show = [k for k in dict.fromkeys(before + new) if trunk or k not in TRUNK]
        if not trunk:
            show = [k for k in show if k not in ("shoulder_r", "shoulder_l", "front_plate", "rear_plate")]
        job = dict(name=f"step{i:02d}", show=show, focus=move, offset={k: off for k in move},
                   ghost=["body"] if ghost else [], dir=DIRS[view], width=2000, height=1250)
        if s["title"] in STEP_TAG:
            job["tag"] = {k: STEP_TAG[s["title"]] for k in move}
        if ghost:                                    # wire steps: fit to the body and the wires
            job["frame"] = ["body"] + move
        jobs.append(job)
    return jobs


def figure_jobs():
    ex = {}
    for k in ALL:
        e = PARTS[k]["explode"]
        if e:
            ex[k] = [a + b for a, b in zip(e[1], e[2])]
    open_ = ROBOT + ["cover", "body", "door", "biboard_header__header"] + HARDWARE[:2] + ["panel_inserts"] + INSIDE
    return [
        dict(name="hero", show=ALL, dir=ISO, width=1500, height=2000),
        dict(name="hero-color", show=ALL, dir=ISO, width=1500, height=2000, color=True),   # each part in its own color
        dict(name="exploded", show=ALL, offset=ex, dir=ISO, width=1600, height=2200),
        dict(name="top", show=[k for k in ALL if k not in ROBOT], dir=DIRS["top"], width=1600, height=1300,
             frame=["body", "panel"]),
        dict(name="open", show=open_, dir=ISO, width=1600, height=1600),
        dict(name="wires", show=["cover", "body"] + INSIDE, ghost=["body"], dir=DIRS["well"], width=1600, height=1300,
             frame=["body"]),
        dict(name="cover", show=ALL, dir=COVER_DIR, width=1600, height=1200),
        dict(name="platform", show=ROBOT + ["cover_pegs", "starter_plate"], dir=ISO, width=1600, height=1600, out=PLATFORM_OUT),
    ]


# --------------------------------------------------------------------------
# Render: a local server for the page, the STLs and the PNGs it posts back
# --------------------------------------------------------------------------
def run(jobs):
    os.makedirs(OUT, exist_ok=True)
    if not os.path.exists(os.path.join(HERE, "iso", "node_modules", "three")):
        subprocess.run(["npm", "install", "--no-audit", "--no-fund"], cwd=os.path.join(HERE, "iso"), check=True)
    full, dest = [], {}
    for j in jobs:
        j = dict(j)
        out = j.pop("out", OUT)
        os.makedirs(out, exist_ok=True)
        for t in THEMES:
            full.append(dict(j, name=f"{j['name']}-{t}", theme=t, tag_scale=3.0))
            dest[f"{j['name']}-{t}.png"] = out
    cfg = json.dumps(dict(parts=PARTS, jobs=full)).encode()
    done = threading.Event()
    saved = []

    class H(SimpleHTTPRequestHandler):
        def __init__(self, *a, **k):
            super().__init__(*a, directory=PROJ, **k)

        def log_message(self, *a):
            pass

        def do_GET(self):
            if self.path == "/iso/jobs.json":
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(cfg)))
                self.end_headers()
                self.wfile.write(cfg)
                return
            super().do_GET()

        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(n)
            if self.path.startswith("/iso/save/"):
                name = os.path.basename(self.path)
                path = os.path.join(dest.get(name, OUT), name)
                open(path, "wb").write(body)
                saved.append(path)
            elif self.path == "/iso/done":
                done.set()
            self.send_response(204)
            self.end_headers()

        def guess_type(self, path):
            return "text/javascript" if path.endswith(".js") else super().guess_type(path)

    srv = ThreadingHTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://127.0.0.1:{srv.server_address[1]}/bittle_pi_addon/iso/render.html"
    chrome = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
    prof = tempfile.mkdtemp(prefix="iso_chrome_")
    p = subprocess.Popen([chrome, "--headless=new", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist",
                          "--no-first-run", "--no-default-browser-check", f"--user-data-dir={prof}", "--remote-debugging-port=0",
                          "--window-size=800,600", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        ok = done.wait(timeout=60 + 20 * len(full))
    finally:
        p.terminate()
        p.wait(timeout=20)
        srv.shutdown()
        shutil.rmtree(prof, ignore_errors=True)
    if not ok:
        raise SystemExit(f"iso render timed out after {len(saved)} of {len(full)} images")
    crop(saved)
    return saved


def crop(paths, margin=24):
    """Cut each PNG to its drawn area plus a margin (the background is transparent)."""
    from PIL import Image
    for path in paths:
        im = Image.open(path)
        box = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
        if box:
            x0, y0, x1, y1 = box
            im.crop((max(x0 - margin, 0), max(y0 - margin, 0), min(x1 + margin, im.width), min(y1 + margin, im.height))).save(path, optimize=True)


def main(which=None):
    jobs = figure_jobs() + step_jobs()
    if which:
        jobs = [j for j in jobs if any(w in j["name"] for w in which)]
    for p in run(jobs):
        print(os.path.relpath(p, HERE))
    if any(j["name"] == "cover" for j in jobs):
        print(os.path.relpath(make_cover(), HERE))


if __name__ == "__main__":
    main(sys.argv[1:] or None)
