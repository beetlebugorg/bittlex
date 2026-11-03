"""The peg cover and the peg interface: build the parts, the keep-out volumes, the checks and the CAD files.

Run:  python build.py          (then: python docs.py for interface.json, SPEC.md and the PDF)
Needs: build123d, manifold3d, numpy. Frame and numbers: interface.py.

Outputs (this folder):
  cad/*.step              pegs, keyhole cutter, detent bumps, starter plate (exact B-rep)
  stl/print/*.stl         print orientation, on the bed (Z = 0)
  stl/installed/*.stl     robot frame (interface.py): the parts and the keep-out
  checks.json             fit, slide path, loose pieces, overhang area
"""
import json
import math
import os
import sys

import numpy as np
import manifold3d as m3
from build123d import (Axis, Box, Circle, Cylinder, Polygon, Pos, Rot, Rectangle, RectangleRounded, Plane, chamfer, extrude,
                       export_step, loft)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import interface as I            # noqa: E402
import meshutil as MU            # noqa: E402

REF = os.path.join(HERE, "reference")
CAD = os.path.join(HERE, "cad")
STL = os.path.join(HERE, "stl")


# --------------------------------------------------------------------------
# build123d helpers (robot frame)
# --------------------------------------------------------------------------
def box(x0, x1, y0, y1, z0, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


def cyl_y(x, z, y0, y1, r):
    return Pos(x, (y0 + y1) / 2, z) * Rot(90, 0, 0) * Cylinder(r, y1 - y0)


def union(shapes):
    out = None
    for s in shapes:
        out = s if out is None else out + s
    return out


# --------------------------------------------------------------------------
# Peg cover parts
# --------------------------------------------------------------------------
def tear_outline(r, n=720, tip=1.0, deg=None):
    """Teardrop outline in plan (X, Z), round part r at (0, 0), point toward Z sign tip (half angle I.TIP_DEG)."""
    a = math.radians(deg or I.TIP_DEG)
    th = np.linspace(a, -math.pi - a, n)          # right tangent point, around the front (z = -r), left tangent point
    arc = np.c_[r * np.cos(th), r * np.sin(th)]
    return np.vstack([arc, [[0.0, r / math.sin(a)]]]) * [1.0, tip]


def tear_prism(x, z, r, y0, y1, top_chamfer=0.0, tip=1.0, deg=None):
    """Teardrop prism along +Y from y0 to y1: round part r at (x, z), point toward Z sign tip."""
    a = math.radians(deg or I.TIP_DEG)
    c, s_ = r * math.cos(a), r * math.sin(a)
    # local sketch (u, v) = (X, -Z): Pos(..) * Rot(-90, 0, 0) maps local (u, v, w) to (x + u, y0 + w, z - v)
    f = Circle(r) + Polygon((0, 0), (-c, -s_), (0, -r / math.sin(a)), (c, -s_), align=None)   # counterclockwise: normal +w
    p = extrude(f, amount=y1 - y0)
    if top_chamfer:
        p = chamfer(p.faces().sort_by(Axis.Z)[-1].edges(), top_chamfer)
    p = Pos(x, y0, z) * Rot(-90, 0, 0) * p
    return p if tip > 0 else Pos(0, 0, 2 * z) * p.mirror(Plane.XY)


def tear_face(x, z, r, y, deg=None):
    """Teardrop face in the plane at height y (point toward +Z)."""
    a = math.radians(deg or I.TIP_DEG)
    c, s_ = r * math.cos(a), r * math.sin(a)
    f = Circle(r) + Polygon((0, 0), (-c, -s_), (0, -r / math.sin(a)), (c, -s_), align=None)
    return Pos(x, y, z) * Rot(-90, 0, 0) * f


def rect_face(x0, x1, z0, z1, y):
    return Pos((x0 + x1) / 2, y, (z0 + z1) / 2) * Rot(-90, 0, 0) * Rectangle(x1 - x0, z1 - z0)


def lead_ins(face_at, l=None):
    """45 deg lead-in chamfers at the top and bottom edges of a cut through the mount plate.
    face_at(grow, y) gives the cut section grown by grow at height y."""
    l = I.KEY_LEAD if l is None else l
    y0, y1 = I.MOUNT_Y0, I.MOUNT_Y1
    return (loft([face_at(0.0, y1 - l), face_at(l, y1)]) + loft([face_at(l, y0), face_at(0.0, y0 + l)])
            + extrude(face_at(l, y1 - 0.01), amount=1.0) + extrude(face_at(l, y0 - 1.0), amount=1.01))


def peg(x, z):
    p = tear_prism(x, z, I.PEG_SHAFT_D / 2, I.PEG_ROOT_Y, I.PEG_HEAD_Y0 + 0.01)
    p += tear_prism(x, z, I.PEG_HEAD_D / 2, I.PEG_HEAD_Y0, I.PEG_HEAD_Y1, I.PEG_HEAD_CHAMFER, I.HEAD_TIP, I.HEAD_TIP_DEG)
    p += tear_prism(x, z, I.PEG_COLLAR_D / 2, I.COVER_TOP - 0.3, I.PEG_COLLAR_Y1)
    return p


def pegs():
    return union(peg(x, z) for x, z in I.PEGS)


def detent_geometry():
    """Bump center (dx, dz) relative to the peg, and the slide curve.

    2D model in plan: the shaft teardrop moves along Z between the two bumps. Each beam moves out
    in X until its bump (radius bump_r) is clear of the shaft. dz puts the bump on the shaft with
    the preload when the shaft is at the V stop (s = 0).
    Model frame: +z = forward from the peg (toward the bumps), s = the peg moves toward the bumps
    (the add-on slides rearward: unlock). The shaft point is toward -z in this frame."""
    D = I.DET
    rs, rb = I.PEG_SHAFT_D / 2, D["bump_r"]
    S = tear_outline(rs, 1440, tip=-1.0)
    dx = rs - D["travel"] + rb

    def defl(s, dz):
        P = S + [0.0, s]
        lo, hi = 0.0, 2.0
        for _ in range(30):
            m = (lo + hi) / 2
            lo, hi = (lo, m) if np.hypot(P[:, 0] - (dx + m), P[:, 1] - dz).min() >= rb else (m, hi)
        return hi

    lo, hi = 0.0, 6.0
    for _ in range(30):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if defl(0.0, m) > D["preload"] else (lo, m)
    dz = hi
    ss = np.linspace(-0.2, I.SLIDE, 300)
    d = np.array([defl(s, dz) for s in ss])
    return dx, dz, ss, d


def detent_force():
    """Peak slide force (N) of all the beams, to lock and to unlock, and the beam strain."""
    D = I.DET
    _, _, ss, d = detent_geometry()
    b, t, L = D["beam_w"], I.MOUNT_T, D["arm"]
    k = 3 * I.E_PLA * (t * b ** 3 / 12) / L ** 3          # N/mm at the free end
    n = 2 * len(I.PEGS)
    g = np.gradient(d, ss)
    F = k * d
    unlock = n * (F * g + I.MU_PLA * F * np.sqrt(1 + g ** 2))     # the add-on moves rearward: the peg moves +s
    lock = n * (-F * g + I.MU_PLA * F * np.sqrt(1 + g ** 2))
    return dict(lock_N=round(float(lock.max()), 1), unlock_N=round(float(unlock.max()), 1),
                hold_N=round(float(n * k * D["preload"]), 2), beam_travel=round(float(d.max()), 2),
                strain_pct=round(100 * 1.5 * float(d.max()) * b / L ** 2, 2), k_N_per_mm=round(k, 2))


DET_DX, DET_DZ = detent_geometry()[:2]


def keyhole_cutter(px, pz):
    """Tool body: subtract it from the add-on mount plate (add-on frame = robot frame, locked position).
    Drop-in hole in front of the peg, slot back to a V stop, lead-in chamfers, and the U slits of the
    two detent beams (free ends in front of the peg, roots behind it)."""
    D = I.DET
    y0, y1 = I.MOUNT_Y0 - 1, I.MOUNT_Y1 + 1
    hw = I.KEY_SLOT_W / 2
    g = I.KEY_SLOT_GAP
    zb = pz - I.SLIDE                                      # drop-in hole center
    zv = pz - g * math.sqrt(2)                             # V stop: the shaft at pz touches both flanks
    rh, rv = I.PEG_HEAD_D / 2 + I.KEY_HOLE_GAP, I.PEG_SHAFT_D / 2 + g
    c = tear_prism(px, zb, rh, y0, I.HEAD_CLEAR_Y, deg=I.HEAD_TIP_DEG)   # the head passes through it
    c += box(px - hw, px + hw, y0, y1, zb, zv)
    c += tear_prism(px, zv, rv, y0, y1)
    c += lead_ins(lambda e, y: tear_face(px, zb, rh + e, y, I.HEAD_TIP_DEG))
    c += lead_ins(lambda e, y: rect_face(px - hw - e, px + hw + e, zb, zv, y))
    c += lead_ins(lambda e, y: tear_face(px, zv, rv + e, y))
    zt = pz - DET_DZ - D["free_end"]                       # free end of the beams (front)
    zr = zt + D["arm"]                                     # beam root (behind the peg)
    for sx in (1, -1):
        xa, xb = sorted((px + sx * (hw + D["beam_w"]), px + sx * (hw + D["beam_w"] + D["slit_w"])))
        c += box(xa, xb, y0, y1, zt - D["slit_w"], zr)                                 # outer slit
        xa, xb = sorted((px + sx * (hw - 0.2), px + sx * (hw + D["beam_w"] + D["slit_w"])))
        c += box(xa, xb, y0, y1, zt - D["slit_w"], zt)                                 # end slit
        xa, xb = sorted((px + sx * (hw - D["slit_w"]), px + sx * hw))
        c += box(xa, xb, y0, y1, zv, zr)                                               # inner slit, from the slot
    return c


def detent_bump(px, pz):
    """Add it to the plate after the cut: the two bumps on the free ends of the beams."""
    D = I.DET
    hw = I.KEY_SLOT_W / 2
    out = None
    for sx in (1, -1):
        b = cyl_y(px + sx * DET_DX, pz - DET_DZ, I.MOUNT_Y0, I.MOUNT_Y1, D["bump_r"])
        xa, xb = sorted((px + sx * (hw - 2.0), px + sx * (hw + D["beam_w"])))
        b &= box(xa, xb, I.MOUNT_Y0, I.MOUNT_Y1, pz - DET_DZ - D["free_end"], pz - DET_DZ + D["bump_r"])
        out = b if out is None else out + b
    if D.get("pad", 0.0) > 0:
        out += clamp_pads(px, pz)
    return out


def clamp_pads(px, pz):
    """A pad with a ramp on the top of each detent beam, under the peg head at the locked place.
    The pad is DET["pad"] higher than the head underside: the head climbs the ramp at the end of the slide
    and pushes the beams down. This clamps the plate in Y (no lift or tilt on the 0.3 mm head gap)."""
    D = I.DET
    hw = I.KEY_SLOT_W / 2
    top, y1 = I.PEG_HEAD_Y0 + D["pad"], I.MOUNT_Y1 - 0.01
    prof = [(y1, pz - 2.6), (top, pz - 1.3), (top, pz + 1.8), (y1, pz + 1.8)]    # (Y, Z): the head comes from -Z
    out = None
    for sx in (1, -1):
        xa, xb = sorted((px + sx * (hw + 0.05), px + sx * (hw + D["beam_w"] - 0.05)))
        p = extrude(Plane.YZ.offset(xa) * Polygon(*prof, align=None), amount=xb - xa)
        p &= cyl_y(px, pz, y1 - 0.1, top + 0.1, I.PEG_HEAD_D / 2 - 0.1)
        out = p if out is None else out + p
    return out


STARTER = dict(x=18.5, z=(-20.0, 25.5), r=3.0, rim_w=1.6, rim_top=31.5,
               holes=[(x, z) for x in (-5.0, 5.0) for z in (-10.0, 0.0, 10.0)], hole_d=3.2)


def starter_base():
    """The starter plate with no mount: the plate, a stiffening rim and an M3 grid."""
    S = STARTER
    w, (z0, z1) = 2 * S["x"], S["z"]
    zc = (z0 + z1) / 2

    def plate(inset, y0, y1):
        f = RectangleRounded(w - 2 * inset, z1 - z0 - 2 * inset, max(S["r"] - inset, 0.5))
        return Pos(0, y0, zc) * Rot(-90, 0, 0) * extrude(f, amount=y1 - y0)    # plan in XZ, up along +Y

    p = plate(0, I.MOUNT_Y0, I.MOUNT_Y1)
    p += plate(0, I.MOUNT_Y1 - 0.01, S["rim_top"]) - plate(S["rim_w"], I.MOUNT_Y1 - 1, S["rim_top"] + 1)
    for x, z in S["holes"]:
        p -= cyl_y(x, z, I.MOUNT_Y0 - 1, I.MOUNT_Y1 + 1, S["hole_d"] / 2)
    return p


def starter_plate():
    """Minimal add-on: the starter base with 4 keyholes and the click beams."""
    p = starter_base()
    for px, pz in I.PEGS:
        p -= keyhole_cutter(px, pz)
    for px, pz in I.PEGS:
        p += detent_bump(px, pz)
    return p


def grove_notch():
    """Cut through the cover shell at the front-left edge (v3.1): room for the BiBoard Grove plug and its cable."""
    N = I.GROVE_NOTCH
    (x0, x1), (z0, z1), r = N["x"], N["z"], 2.0           # round inside corners
    return (box(x0, x1, 0.0, 40.0, z0, z1 - r) + box(x0 + r, x1 - r, 0.0, 40.0, z1 - r - 0.01, z1)
            + cyl_y(x0 + r, z1 - r, 0.0, 40.0, r) + cyl_y(x1 - r, z1 - r, 0.0, 40.0, r))


def grove_plug():
    """Estimated space of the Grove plug and the cable bend, from the cover surface up to GROVE_PLUG y_top."""
    G = I.GROVE_PLUG
    return box(*G["x"], 10.0, G["y_top"], *G["z"])


def cover_with_notch():
    """The stock Petoi cover with the Grove notch and the Pi slot cut wider (SLOT_WIDE)."""
    S = I.SLOT_WIDE
    slot = box(S["x0"], S["x1"], S["y0"], S["y0"] + 12.0, S["z0"], S["z1"])
    return MU.mesh_to_manifold(ref_tris(I.COVER_STL)) - to_m(grove_notch()) - to_m(slot)


def header_keepout():
    """BiBoard header + 0.4, swept SLIDE to the front (add-on frame), and the Dupont plug space."""
    H, S = I.HDR, I.SLOT
    k = box(H["x0"] - 0.4, H["x1"] + 0.4, S["y0"], H["top"] + 0.5, H["z0"] - I.SLIDE - 0.4, H["z1"] + 0.4)
    plugs = box(S["x0"], S["x1"], H["top"], I.PLUG_TOP, S["z0"], S["z1"])
    return k, plugs


# --------------------------------------------------------------------------
# Meshes of the robot
# --------------------------------------------------------------------------
def ref_tris(name):
    t = MU.load_stl(os.path.join(REF, name))
    if name.startswith("Bittle_Cover"):                   # the cover is turned on the robot (interface.py)
        t = t @ np.array(I.COVER_TURN, float).T
    return t


def mirror_tris(t, axis):
    m = t.copy()
    m[:, :, axis] *= -1
    return m[:, ::-1, :]


def robot_meshes():
    sh = ref_tris("Bittle_SideShoulder.stl")
    fp = ref_tris("Bittle_FrontPlate.stl")
    return dict(shoulder_r=sh, shoulder_l=mirror_tris(sh, 0), front_plate=fp, rear_plate_mirror=mirror_tris(fp, 2))


def support_tris(with_cover=True):
    R = robot_meshes()
    t = list(R.values())
    if with_cover:
        t.append(ref_tris("Bittle_Cover.stl"))      # cover without the slot: a closed top surface
    return np.concatenate(t)


def to_m(shape):
    return MU.b3d_to_manifold(shape)


def swept(M, dz, step=0.5):
    """Union of M moved 0..dz along +Z."""
    out = M
    for t in np.arange(step, dz + 1e-9, step):
        out = out + M.translate([0, 0, float(t)])
    return out


def hull_sweep(M, dz):
    return m3.Manifold.batch_hull([M, M.translate([0, 0, dz])])


# --------------------------------------------------------------------------
# Print orientation and checks
# --------------------------------------------------------------------------
PRINT_R = {
    # cover: stand on the rear end (as Petoi prints it); the pegs are horizontal, their layers run along the axis
    "cover_pegs": [[1, 0, 0], [0, -1, 0], [0, 0, -1]],
    "cover_stock": [[1, 0, 0], [0, -1, 0], [0, 0, -1]],
    # starter plate: mount face (Y = MOUNT_Y0) on the bed
    "starter_plate": [[1, 0, 0], [0, 0, -1], [0, 1, 0]],
}


def print_orient(name, M):
    R = np.array(PRINT_R[name], float)
    if abs(np.linalg.det(R) - 1) > 1e-6:
        raise ValueError(name)
    M = M.transform(np.hstack([R, np.zeros((3, 1))]))
    b = M.bounding_box()
    return M.translate([-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, -b[2]])


def overhang_area(M, limit_deg=45.5, bed=0.3):
    """Area (mm^2) of down-facing surface steeper than limit_deg from vertical, not on the bed."""
    m = M.to_mesh()
    v = np.asarray(m.vert_properties)[:, :3]
    t = v[np.asarray(m.tri_verts)]
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    a = np.linalg.norm(n, axis=1) / 2
    nz = n[:, 2] / (2 * a + 1e-12)
    sel = (nz < -math.sin(math.radians(limit_deg))) & (t[:, :, 2].min(1) > bed)
    return float(a[sel].sum())


def overhang_regions(M, limit_deg=45.5, bed=0.3, min_area=0.5):
    """Connected regions of down-facing surface steeper than limit_deg from vertical, off the bed.
    Returns [{area, flat, x, y, z}] (print frame), largest first. 'flat' = area of flat ceilings."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    m = M.to_mesh()
    v = np.asarray(m.vert_properties)[:, :3]
    tv = np.asarray(m.tri_verts)
    t = v[tv]
    n = np.cross(t[:, 1] - t[:, 0], t[:, 2] - t[:, 0])
    a = np.linalg.norm(n, axis=1) / 2
    nz = n[:, 2] / (2 * a + 1e-12)
    idx = np.where((nz < -math.sin(math.radians(limit_deg))) & (t[:, :, 2].min(1) > bed) & (a > 1e-9))[0]
    if not len(idx):
        return []
    owner = {}
    rows, cols = [], []
    for k, i in enumerate(idx):
        for vv in tv[i]:
            if vv in owner:
                rows.append(owner[vv]); cols.append(k)
            else:
                owner[vv] = k
    G = coo_matrix((np.ones(len(rows)), (rows, cols)), shape=(len(idx), len(idx)))
    _, lab = connected_components(G, directed=False)
    out = []
    for c in np.unique(lab):
        ii = idx[lab == c]
        A = float(a[ii].sum())
        if A < min_area:
            continue
        P = t[ii].reshape(-1, 3)
        lo, hi = P.min(0), P.max(0)
        out.append(dict(area=round(A, 1), flat=round(float(a[ii][nz[ii] < -0.98].sum()), 1),
                        x=[round(float(lo[0]), 1), round(float(hi[0]), 1)], y=[round(float(lo[1]), 1), round(float(hi[1]), 1)],
                        z=[round(float(lo[2]), 1), round(float(hi[2]), 1)]))
    return sorted(out, key=lambda r: -r["area"])


# Break-off foot for the standing cover print. The cover stands on a thin curved strip
# (about 56 x 1.6 mm) and its center of mass is 2 mm past that strip, over the leaning
# top face. The foot is a 3-layer plate with fins under that face. The fins stand
# FOOT["gap"] off the cover and touch it only at small teeth, so they snap off.
# Each tooth is 0.6 wide and 0.25 tall: 21 teeth, about 3 mm2 of contact in total. Only the teeth hold,
# so the foot breaks off clean. With the "Bittle X" Cura profile (0.25 first layer, then 0.20) the layer
# mid-planes are at 0.125, then 0.35 + 0.2 k: the plate (0.70) is 3 layers, each tooth exactly 1 layer.
FOOT = dict(t=0.70, y=(-14.0, 4.0), x=30.0, fins_x=(-24.0, -16.0, -8.0, 0.0, 8.0, 16.0, 24.0),
            fin_t=0.8, fin_h=14.0, gap=0.45, teeth_z=(1.0, 6.0, 11.0), tooth=0.6, tooth_h=0.25)


def dilate(M, d):
    """Approximate offset of a mesh: union of copies moved by d along the six axis directions."""
    out = M
    for v in ((d, 0, 0), (-d, 0, 0), (0, d, 0), (0, -d, 0), (0, 0, d), (0, 0, -d)):
        out = out + M.translate(list(v))
    return out


def cover_foot(P):
    """Foot for the print-oriented cover P (bed at Z = 0, top face of the cover toward -Y)."""
    F = FOOT
    y0, y1 = F["y"]
    near = dilate(P, F["gap"])
    foot = to_m(box(-F["x"], F["x"], y0, y1, 0.0, F["t"]))
    for xf in F["fins_x"]:
        # right triangle: 45 deg top edge from the plate edge up toward the cover
        fin = m3.Manifold.extrude(m3.CrossSection([[(y0, 0.0), (y1, 0.0), (y1, F["fin_h"]), (y0 + F["fin_h"], F["fin_h"])]]),
                                  F["fin_t"])
        fin = fin.transform(np.array([[0.0, 0, 1, xf - F["fin_t"] / 2], [1, 0, 0, 0], [0, 1, 0, 0]]))
        foot += fin
    foot -= near
    reach = dilate(P, F["gap"] + 0.15)
    teeth = None
    for xf in F["fins_x"]:
        for zt in F["teeth_z"]:
            tb = to_m(box(xf - F["tooth"] / 2, xf + F["tooth"] / 2, y0, y1, zt, zt + F["tooth_h"]))
            tb = tb ^ reach
            teeth = tb if teeth is None else teeth + tb
    return (foot + teeth) - P


def loose(M):
    v = sorted(c.volume() for c in M.decompose())
    return sum(v[:-1])


def main():
    for d in ("cad", "stl/print", "stl/installed"):
        os.makedirs(os.path.join(HERE, d), exist_ok=True)

    # ---- exact parts
    P = pegs()
    cutter = union(keyhole_cutter(x, z) for x, z in I.PEGS)
    bumps = union(detent_bump(x, z) for x, z in I.PEGS)
    plate = starter_plate()
    hdr_k, plug_k = header_keepout()
    export_step(P, os.path.join(CAD, "pegs.step"))
    export_step(cutter, os.path.join(CAD, "keyhole_cutter.step"))
    export_step(bumps, os.path.join(CAD, "detent_bumps.step"))
    export_step(plate, os.path.join(CAD, "starter_plate.step"))

    # ---- mesh parts
    cover_pegs = cover_with_notch() + to_m(P)
    plate_m = to_m(plate)

    # keep-out for add-on bodies, add-on frame at the locked position, swept over the slide
    robot = MU.heightfield_solid(support_tris(True), -45, 45, -66, 66, lift=0.3).simplify(0.05)
    robot_sw = MU.heightfield_solid(support_tris(True), -45, 45, -66 - I.SLIDE, 66, lift=0.3,
                                    sweep_z=-I.SLIDE).simplify(0.05)    # 0.05 mm of the 0.3 mm gap
    heads = None
    for x, z in I.PEGS:
        h = to_m(tear_prism(x, z, I.PEG_HEAD_D / 2 + 0.4, I.MOUNT_Y1, I.HEAD_CLEAR_Y, tip=I.HEAD_TIP, deg=I.HEAD_TIP_DEG))
        h = hull_sweep(h, -I.SLIDE)
        heads = h if heads is None else heads + h
    hdr_m, plug_m = to_m(hdr_k), to_m(plug_k)
    keepout = robot_sw + heads + hdr_m + hull_sweep(to_m(grove_plug()), -I.SLIDE)

    parts = dict(cover_pegs=cover_pegs, starter_plate=plate_m)
    installed = dict(parts, keepout=keepout)
    for k, M in installed.items():
        MU.save_stl(M, os.path.join(STL, "installed", f"{k}.stl"))
    for k, M in parts.items():
        MU.save_stl(print_orient(k, M), os.path.join(STL, "print", f"{k}.stl"))
    Pc = print_orient("cover_pegs", cover_pegs)
    footed = Pc + cover_foot(Pc)
    MU.save_stl(footed, os.path.join(STL, "print", "cover_pegs_foot.stl"))

    # ---- faceted STEP files (mesh-based parts)

    # ---- checks
    R = {k: MU.mesh_to_manifold(t) for k, t in robot_meshes().items()}
    hdr_real = to_m(box(I.HDR["x0"], I.HDR["x1"], 0.0, I.HDR["top"], I.HDR["z0"], I.HDR["z1"]))
    rows = []
    vol = lambda a, b: (a ^ b).volume()
    for name, dz in (("locked", 0.0), ("at detent bump", DET_DZ), ("drop-on", I.SLIDE)):
        T = plate_m.translate([0, 0, dz])        # the add-on goes on behind its place
        rows.append((f"starter_plate {name}", "cover_pegs", vol(T, cover_pegs)))
        rows.append((f"starter_plate {name}", "biboard_header", vol(T, hdr_real)))
        for rn, M in R.items():
            rows.append((f"starter_plate {name}", rn, vol(T, M)))
    rows.append(("starter_plate (body)", "keepout", vol(plate_m - to_m(cutter), keepout)))
    # one direction only: the plate turned 180 deg (about Y) does not go down over the heads
    heads_fp = to_m(union(tear_prism(x, z, I.PEG_HEAD_D / 2, I.MOUNT_Y0 - 1, I.HEAD_CLEAR_Y, tip=I.HEAD_TIP, deg=I.HEAD_TIP_DEG) for x, z in I.PEGS))
    turned = plate_m.transform(np.array([[-1.0, 0, 0, 0], [0, 1, 0, 0], [0, 0, -1, 0]]))
    # Z shifts up to 12 mm: a larger shift puts the plate off the cover top
    keyed = min(vol(turned.translate([0, 0, float(dz)]), heads_fp) for dz in np.arange(-12.0, 12.01, 0.25))
    rows.append(("starter_plate turned 180 (min, Z +-12)", "peg heads", keyed))
    rows.append(("starter_plate drop-on (lowered)", "peg heads", vol(plate_m.translate([0, 0, I.SLIDE]), heads_fp)))
    for k, M in parts.items():
        rows.append((k, "loose_pieces", loose(M)))
    rows.append(("cover_pegs_foot (print)", "loose_pieces", loose(footed)))
    ovh = {k: overhang_area(print_orient(k, M)) for k, M in parts.items()}
    ovh["cover_pegs_foot"] = overhang_area(footed)
    ovh["cover_stock"] = overhang_area(print_orient("cover_stock", MU.mesh_to_manifold(ref_tris(I.COVER_STL))))
    mass = {k: round(M.volume() * 1.24e-3, 1) for k, M in parts.items()}    # PLA, solid
    clear = dict(
        plate_to_collar=round(I.MOUNT_Y0 - I.PEG_COLLAR_Y1, 2),
        plate_to_logo=round(I.MOUNT_Y0 - I.LOGO["top"], 2),
        plate_top_to_head=round(I.PEG_HEAD_Y0 - I.MOUNT_Y1, 2),
        slot_to_shaft_each_side=round((I.KEY_SLOT_W - I.PEG_SHAFT_D) / 2, 2),
        big_hole_to_head_each_side=I.KEY_HOLE_GAP,
        collar_to_logo=round(float(min(np.hypot(*((tear_outline(I.PEG_COLLAR_D / 2) + p)[:, None] - logo_pts()[None]).transpose(2, 0, 1)).min()
                                       for p in I.PEGS)), 2),
        collar_to_flat_edge=round(I.COVER_FLAT["x"][1] - max(abs(x) for x, _ in I.PEGS) - I.PEG_COLLAR_D / 2, 2),
    )
    det = detent_force()
    json.dump(dict(rows=rows, overhang_mm2=ovh, mass_g_pla_solid=mass, clearances=clear, detent=det),
              open(os.path.join(HERE, "checks.json"), "w"), indent=1)
    print("checks (mm^3, > 0.05 shown):")
    for r in rows:
        if r[2] > 0.05:
            print(f"  {r[0]:32s} x {r[1]:22s} {r[2]:8.2f}")
    print("overhang mm^2 (> 45 deg, off the bed):", {k: round(v, 1) for k, v in ovh.items()})
    print("mass g (PLA, solid):", mass)
    print("clearances:", clear)
    print("detent:", det)


def logo_pts():
    v = ref_tris(I.COVER_STL).reshape(-1, 3)
    r = v[v[:, 1] > I.COVER_TOP + 0.01]
    return r[:, [0, 2]]


def step_from_mesh(M, path):
    """Faceted STEP solid from a manifold mesh (one planar face per triangle)."""
    from OCP.StlAPI import StlAPI_Reader
    from OCP.TopoDS import TopoDS_Shape, TopoDS
    from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeSolid, BRepBuilderAPI_Sewing
    from build123d import Solid
    tmp = path + ".tmp.stl"
    MU.save_stl(M, tmp)
    sh = TopoDS_Shape()
    StlAPI_Reader().Read(sh, tmp)
    os.unlink(tmp)
    sw = BRepBuilderAPI_Sewing(1e-4)
    sw.Add(sh)
    sw.Perform()
    S = Solid(BRepBuilderAPI_MakeSolid(TopoDS.Shell(sw.SewedShape())).Solid())
    export_step(S, path)


if __name__ == "__main__":
    main()
