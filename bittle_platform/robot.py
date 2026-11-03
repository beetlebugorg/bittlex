"""The Bittle X robot around the peg cover: head, legs, battery and tail, in the robot frame (interface.py).

Source: Petoi's ROS model (reference/petoi_ros/, MIT). Its meshes are in one world frame, in mm:
x = forward, y = left, z = up. Body frame = (-y, z - 22, -x). Check: the ROS front plate is at
the place of reference/Bittle_FrontPlate.stl. The joint origins and axes come from bittle.xacro.

Run:  python robot.py      -> stl/robot/*.stl (standing pose) and stl/robot/robot.json (joints)

Joint angles (deg) are relative to the standing pose. All leg joints turn about +X:
a positive angle turns the thigh (hip) or the shank (knee) toward the head.
The head turns about the neck axis (30 deg from vertical): a positive angle turns it to the right.
"""
import json
import math
import os
import sys
import xml.etree.ElementTree as ET

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import meshutil as MU            # noqa: E402

ROS = os.path.join(HERE, "reference", "petoi_ros")
OUT = os.path.join(HERE, "stl", "robot")
R0 = np.array([[0, -1, 0], [0, 0, 1], [-1, 0, 0]], float)
T0 = np.array([0.0, -22.0, 0.0])

HEAD = ["servo_neck__1", "jaw_1", "head__1"]      # turn with the neck servo
HEAD_YAW0 = -40.0      # the ROS model has the head turned: -40 deg makes it symmetric about X 0
# leg: hip joint, knee joint, thigh meshes, shank meshes (with the knee servo), hip servo (fixed)
LEGS = dict(
    lf=("shlfs_joint", "shlft_joint", ["c_thlf_1", "th_lf_1", "tho_lf_1", "c_tholf_1", "tube_lf_1"],
        ["servos_lf_1", "shank_lf_1"], "servo_lfs_1"),
    rf=("shrfs_joint", "shrft_joint", ["c_thrf__1", "th_rf_1", "tho_rf__1", "c_thorf_1", "tube__1"],
        ["servos_rf_1", "shank_rf_1"], "servo_rfs_1"),
    lr=("shlrs_joint", "shlrt_joint", ["c_thlr_1", "th_lr__1", "tho_lr_1", "c_tholr__1", "tube_lr_1"],
        ["servos_lr_1", "shank_lr_1"], "servo_lrs__1"),
    rr=("shrrs_joint", "shrrt_joint", ["c_thrr_1", "th_rr_1", "tho_rr_1", "c_thorr_1", "tube_rr_1"],
        ["servos_rr_1", "shank_rr_1"], "servo_rrs__1"),
)
# standing pose: thigh and shank angles from straight down (+ = toward the head).
# Thigh -30, shank +30: the knee points to the rear and the foot is under the hip.
STAND = dict(thigh=-30.0, shank=30.0)


def to_body(p):
    return np.asarray(p) @ R0.T + T0


def load(name):
    t = MU.load_stl(os.path.join(ROS, name + ".stl"))
    return MU.mesh_to_manifold(to_body(t.reshape(-1, 3)).reshape(-1, 3, 3))


def joints():
    """Moving joints of the ROS model in the body frame: name -> (point, axis)."""
    root = ET.parse(os.path.join(ROS, "bittle.xacro")).getroot()
    vis = {l.get("name"): np.array([float(v) for v in l.find("visual/origin").get("xyz").split()]) * 1000
           for l in root.iter("link") if l.find("visual/origin") is not None}
    out = {}
    for j in root.iter("joint"):
        if j.get("type") == "fixed":
            continue
        o = np.array([float(v) for v in j.find("origin").get("xyz").split()]) * 1000
        p = -vis[j.find("parent").get("link")] + o        # the link frame is at -(visual origin)
        ax = np.array([float(v) for v in j.find("axis").get("xyz").split()])
        out[j.get("name")] = (to_body(p), ax @ R0.T)
    return out


def rot(axis, deg, p):
    """3x4 rotation by deg about the axis through p."""
    a = np.asarray(axis, float) / np.linalg.norm(axis)
    t = math.radians(deg)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    R = np.eye(3) + math.sin(t) * K + (1 - math.cos(t)) * K @ K
    return np.hstack([R, (np.asarray(p) - R @ np.asarray(p))[:, None]])


def compose(A, B):
    """A after B (3x4 matrices)."""
    return np.hstack([A[:, :3] @ B[:, :3], (A[:, :3] @ B[:, 3] + A[:, 3])[:, None]])


def angle_from_down(v):
    """Angle of a YZ vector from straight down (-Y), + = toward the head (-Z)."""
    return math.degrees(math.atan2(-v[2], -v[1]))


class Robot:
    """The robot parts in the standing pose, and the joints to pose them."""

    def __init__(self):
        J = joints()
        self.neck = J["neck_joint"]
        head = [load(n) for n in HEAD]
        T = rot(self.neck[1], HEAD_YAW0, self.neck[0])
        self.parts = dict(head=sum(head[1:], head[0]).transform(T), neck_mount=load("c_neck__1"),
                          rear_plate=load("rear__1"))
        self.battery = to_body(MU.load_stl(os.path.join(ROS, "battery_1.stl")).reshape(-1, 3)).reshape(-1, 3, 3)   # not closed: display only
        tail = MU.load_stl(os.path.join(HERE, "reference", "Bittle_tail.stl"))
        self.parts["tail"] = MU.mesh_to_manifold(tail[:, ::-1, :] * np.array([1, 1, -1]))   # Petoi file is mirrored in Z
        self.joints = dict(head=dict(p=self.neck[0].tolist(), axis=self.neck[1].tolist()))   # down the neck: + = right
        servos = None
        for k, (hj, kj, th, sh, hs) in LEGS.items():
            hp, kp = J[hj][0], J[kj][0]
            TH = sum((load(n) for n in th[1:]), load(th[0]))
            SH = sum((load(n) for n in sh[1:]), load(sh[0]))
            servos = load(hs) if servos is None else servos + load(hs)
            # hip: thigh (hip -> knee) to STAND["thigh"]
            a = STAND["thigh"] - angle_from_down(kp - hp)
            Th = rot((1, 0, 0), a, hp)           # rotation about +X raises the angle from down
            kp2 = Th[:, :3] @ kp + Th[:, 3]
            # knee: the far end of the shank (the foot) to STAND["shank"]
            v = np.asarray(SH.transform(Th).to_mesh().vert_properties)[:, :3]
            foot = v[np.argmax(np.linalg.norm(v[:, 1:] - kp2[1:], axis=1))]
            b = STAND["shank"] - angle_from_down(foot - kp2)
            Tk = compose(rot((1, 0, 0), b, kp2), Th)
            self.parts[f"thigh_{k}"] = TH.transform(Th)
            self.parts[f"shank_{k}"] = SH.transform(Tk)
            self.joints[f"hip_{k}"] = dict(p=hp.tolist(), axis=[1.0, 0, 0])
            self.joints[f"knee_{k}"] = dict(p=kp2.tolist(), axis=[1.0, 0, 0], parent=f"hip_{k}")
        self.parts["hip_servos"] = servos
        self.chain = {"head": ["head"]}
        for k in LEGS:
            self.chain[f"thigh_{k}"] = [f"hip_{k}"]
            self.chain[f"shank_{k}"] = [f"hip_{k}", f"knee_{k}"]

    def matrix(self, name, angles):
        """3x4 pose of a part for joint angles {joint: deg} (missing joints: 0)."""
        M = np.hstack([np.eye(3), np.zeros((3, 1))])
        for j in self.chain.get(name, []):
            J = self.joints[j]
            M = compose(M, rot(J["axis"], angles.get(j, 0.0), J["p"]))
        return M

    def posed(self, angles):
        return {n: P.transform(self.matrix(n, angles)) for n, P in self.parts.items()}

    def ground(self):
        return min(self.parts[f"shank_{k}"].bounding_box()[1] for k in LEGS)


def main():
    os.makedirs(OUT, exist_ok=True)
    R = Robot()
    for n, P in R.parts.items():
        MU.save_stl(P.simplify(0.08), os.path.join(OUT, f"{n}.stl"))   # display meshes: 0.08 mm
        print(f"{n:12s} {P.num_tri():7d} tris  bbox {np.round(P.bounding_box(), 1)}")
    MU.save_tris(R.battery, os.path.join(OUT, "battery.stl"))
    json.dump(dict(joints=R.joints, chain=R.chain, ground=round(R.ground(), 1), stand=STAND),
              open(os.path.join(OUT, "robot.json"), "w"), indent=1)
    print("ground Y", round(R.ground(), 1))


if __name__ == "__main__":
    main()
