"""Motion checks: the robot head, legs and tail against the add-on (bittle_platform/robot.py).

Run after pod.py:  python motion.py  ->  stl/motion.json

Angles are in degrees, relative to the standing pose of robot.py.
  head: contact volume with the add-on for each head turn angle.
  legs: hip x knee grid. A pose is "addon" when the leg touches the body or the panel
        and does not touch the robot body. It is "body" when the leg touches the robot body.
  tail: the Petoi tail against the add-on, in place and at the drop-on place.
"""
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ROOT))
from bittle_platform import robot as RB          # noqa: E402
from bittle_platform import interface as PI      # noqa: E402
import pod                                       # noqa: E402

STL = os.path.join(ROOT, "stl")
HIPS = range(-180, 180, 15)
KNEES = range(-150, 151, 15)


def load(rel):
    return pod.mesh_to_manifold(pod.load_stl(os.path.join(STL, rel)))


def main():
    R = RB.Robot()
    addon = load("installed/pod_body.stl") + load("installed/pod_panel.stl")
    out = {}

    # head turn
    head = R.parts["head"]
    rows = []
    for a in range(-90, 91, 5):
        H = head.transform(RB.rot(R.joints["head"]["axis"], a, R.joints["head"]["p"]))
        rows.append([a, round((H ^ addon).volume(), 2), round(H.min_gap(addon, 10), 2)])
    free = [a for a, v, g in rows if v < 0.05]
    out["head"] = dict(rows=rows, free=[min(free), max(free)], gap0=[g for a, v, g in rows if a == 0][0])
    print("head: no contact from", min(free), "to", max(free), "deg; gap straight ahead", out["head"]["gap0"], "mm")

    # tail: in place and at the drop-on place (SLIDE rearward)
    tail = R.parts["tail"]
    out["tail"] = dict(contact=round((tail ^ addon).volume(), 2), gap=round(tail.min_gap(addon, 10), 2),
                       drop_on_contact=round((tail ^ addon.translate([0, 0, PI.SLIDE])).volume(), 2),
                       drop_on_gap=round(tail.min_gap(addon.translate([0, 0, PI.SLIDE]), 10), 2))
    print("tail:", out["tail"])

    # legs: one front and one rear leg on each side; the grid is the same for left and right
    # the robot body (the thigh horn sits on the hip servo spline: the hip servos are not in it)
    body = (pod.mesh_to_manifold(pod.load_stl(os.path.join(ROOT, "stl", "installed", "cover_pegs.stl")))
            + R.parts["rear_plate"] + R.parts["neck_mount"])
    for n, rp in pod.robot_parts().items():
        if n in ("shoulder_r", "shoulder_l", "front_plate"):
            body += pod.flip_x(rp)                     # robot_parts() is in the design frame
    legs = {}
    for end in ("front", "rear"):
        grid = {}
        for side in ("l", "r"):
            k = side + end[0]
            th = R.parts[f"thigh_{k}"].simplify(0.1)
            sh = R.parts[f"shank_{k}"].simplify(0.1)
            for a in HIPS:
                for b in KNEES:
                    ang = {f"hip_{k}": a, f"knee_{k}": b}
                    L = th.transform(R.matrix(f"thigh_{k}", ang)) + sh.transform(R.matrix(f"shank_{k}", ang))
                    if (L ^ body).volume() > 0.5:
                        grid[(a, b)] = "body" if grid.get((a, b)) != "addon" else "addon"
                    elif (L ^ addon).volume() > 0.05:
                        grid[(a, b)] = "addon"
        legs[end] = dict(addon=sorted(list(p) for p, v in grid.items() if v == "addon"),
                         body=sorted(list(p) for p, v in grid.items() if v == "body"))
        print(f"{end} legs: {len(legs[end]['addon'])} poses touch the add-on, {len(legs[end]['body'])} touch the robot body "
              f"(of {len(HIPS) * len(KNEES)})")
    out["legs"] = dict(hips=[HIPS.start, HIPS.stop, HIPS.step], knees=[KNEES.start, KNEES.stop, KNEES.step], **legs)
    json.dump(out, open(os.path.join(STL, "motion.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
