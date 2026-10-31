"""Print plates: every part of the add-on and the platform cover on one bed, in its print orientation.

  fdm_taz       LulzBot TAZ Workhorse (280 x 280 x 300), 0.5 mm nozzle, the "Bittle X" Cura profile. The parts are
                the print STLs of pod.py and the platform. The cover stands on its rear end without the foot (the user
                printed it best this way).
  resin_phenom  Peopoly Phenom, first model (276 x 155 x 400). Each part is tilted, the cosmetic face away from the
                supports, and its lowest point is at Z 0. Lift the parts 5 mm in the slicer and add supports there.

Outputs (stl/plates/): one STL per part and one STL of the full plate in each plate folder, a 3MF of each plate
(one object for each part), plates.json (the desktop viewer reads it) and resin_check.json.

The resin check slices each resin part at RESIN_LAYER and reports, for each layer:
  cup: a void that is closed all around in the layer, over solid or over a closed void in the layer below. In a
       bottom-up resin printer the vat film closes it from above: it pulls on the part at each peel.
  island: a region of the layer with no solid under it in the layer below. It needs a support.
  peel area: the area of the layer (the peel force goes up with it).
"""
import json
import math
import os
import sys
import zipfile

import numpy as np
import manifold3d as m3

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(ROOT))
sys.path.insert(0, ROOT)
import pod as P                                        # noqa: E402

OUT = os.path.join(P.OUT, "plates")
PLATFORM_PRINT = os.path.join(os.path.dirname(ROOT), "bittle_platform", "stl", "print")
GAP = 8.0                                              # between parts on a plate
RESIN_LAYER = 0.25                                     # check layer (the print uses 0.05)
CUP_MIN = 1.0                                          # mm2: smaller closed voids are not counted
COLORS = dict(pod_door="#e9e9e6", pod_body="#e9e9e6", pod_panel="#e8641b", cover_pegs="#26272b",
              coupon_tight="#9aa0a6", coupon_loose="#9aa0a6")

PLATES = {
    "fdm_taz": dict(label="FDM: LulzBot TAZ Workhorse, 0.5 mm nozzle", bed=(280.0, 280.0, 300.0)),
    "resin_phenom": dict(label="Resin: Peopoly Phenom (first model)", bed=(276.0, 155.0, 400.0)),
}

# Resin orientations, from the installed part (robot frame: Y up, -Z to the head). tip = deg about X (the front edge
# goes up), roll = deg about Y (a side goes up), flip = upside down first. The choice of each one and the reason:
RESIN = {
    # Floor toward the plate, tipped 45 deg and 15 deg to the side. At 30 deg, or with no side tilt, the floor and the
    # walls close a cup (resin_check). The outer faces of the walls and the seam under the panel have no supports.
    # Supports go on the flat floor underside: keep them out of the keyhole slots and off the click beams, and sand
    # the marks flat (the floor slides on the cover).
    "pod_body": dict(flip=False, tip=45.0, roll=15.0),
    # Open side toward the plate (as installed), tipped 45 deg and 15 deg to the side: the top face is the last face,
    # with no support marks.
    "pod_panel": dict(flip=False, tip=45.0, roll=15.0),
    # The door: outer face up (R0: robot -X to plate +Z), tipped 45 deg: supports on the inner face and the ears.
    "pod_door": dict(R0=[[0, 0, 1], [0, 1, 0], [-1, 0, 0]], tip=45.0, roll=0.0),
    # The stock cover with the pegs: on its rear end, the points of the peg heads down (R0: robot +Z to plate -Z), as
    # in the FDM print (user choice). The pegs print along their length; the supports go on the rear edge only, clear
    # of the fit faces of the pegs.
    "cover_pegs": dict(R0=[[1, 0, 0], [0, -1, 0], [0, 0, -1]], tip=0.0, roll=0.0),
}


def rot(axis, deg):
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return dict(x=np.array([[1, 0, 0], [0, c, -s], [0, s, c]]), y=np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]),
                z=np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]]))[axis]


def affine(R):
    return np.hstack([R, np.zeros((3, 1))])


def on_bed(M):
    """Centered in X and Y, the lowest point at Z 0."""
    b = M.bounding_box()
    return M.translate([-(b[0] + b[3]) / 2, -(b[1] + b[4]) / 2, -b[2]])


def resin_orient(name, M):
    """The installed part (robot frame, Y up) -> Z up, then the RESIN turns."""
    o = RESIN[name]
    R = np.array(o.get("R0", [[1, 0, 0], [0, 0, -1], [0, 1, 0]]), float)   # default: robot Y (up) -> plate Z, robot -Z -> plate +Y
    if o.get("flip"):
        R = rot("x", 180.0) @ R
    R = rot("y", o["roll"]) @ rot("x", o["tip"]) @ R
    return on_bed(M.transform(affine(R)))


def load(path):
    return P.mesh_to_manifold(P.load_stl(path))


def fdm_parts():
    return dict(pod_body=load(os.path.join(P.OUT, "print", "pod_body.stl")),
                pod_panel=load(os.path.join(P.OUT, "print", "pod_panel.stl")),
                pod_door=load(os.path.join(P.OUT, "print", "pod_door.stl")),
                cover_pegs=load(os.path.join(PLATFORM_PRINT, "cover_pegs.stl")))     # no foot: it printed best (user)


# Resin fit coupons: starter plates (platform build.py) a step tighter and a step looser than pod.py RESIN_FIT.
# Front rim notches: 1 = tight, 2 = loose. Try them on the cover with the body: they show the next step.
RESIN_COUPONS = {"coupon_tight": dict(gap=0.05, travel=0.30, pad=0.05, notches=1),
                 "coupon_loose": dict(gap=0.12, travel=0.20, pad=0.05, notches=2)}


def coupon(fit):
    from bittle_platform import build as BP
    with P.fit_set(fit):
        p = BP.starter_plate()
    S, k = BP.STARTER, fit["notches"]
    for j in range(k):
        x = 3.0 * j - 1.5 * (k - 1)
        p -= BP.box(x - 0.5, x + 0.5, S["rim_top"] - 1.0, S["rim_top"] + 1, S["z"][0] - 1, S["z"][0] + S["rim_w"] + 1)
    return BP.to_m(p)


def resin_parts():
    """The installed parts with the resin fit (pod.py RESIN_FIT: stl/installed/resin/), the cover and the fit
    coupons."""
    def inst(n):
        r = os.path.join(P.OUT, "installed", "resin", f"{n}.stl")
        return load(r if os.path.exists(r) else os.path.join(P.OUT, "installed", f"{n}.stl"))
    out = {n: resin_orient(n, inst(n)) for n in RESIN}
    for n, f in RESIN_COUPONS.items():
        o = RESIN["pod_body"]
        R = rot("y", o["roll"]) @ rot("x", o["tip"]) @ np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]], float)
        out[n] = on_bed(coupon(f).transform(affine(R)))
    return out


# Resin plate: two columns, each part list from the back (+Y) to the front. A row is a list of parts side by side.
RESIN_COLUMNS = [[["pod_body"], ["cover_pegs"]],
                 [["pod_panel"], ["coupon_tight", "coupon_loose"], ["pod_door"]]]


def column_layout(parts, bed, columns, gap=6.0):
    """Place the parts in columns (see RESIN_COLUMNS), centered on the bed. Parts that are not here go nowhere."""
    size = lambda n: (lambda b: (b[3] - b[0], b[4] - b[1]))(parts[n].bounding_box())
    cols = [[r for r in c if all(n in parts for n in r)] for c in columns]
    cols = [c for c in cols if c]
    cw = [max(sum(size(n)[0] for n in r) + gap * (len(r) - 1) for r in c) for c in cols]
    ch = [sum(max(size(n)[1] for n in r) for r in c) + gap * (len(c) - 1) for c in cols]
    W = sum(cw) + gap * (len(cols) - 1)
    if W > bed[0] or max(ch) > bed[1]:
        raise RuntimeError(f"the resin plate is {W:.1f} x {max(ch):.1f}, the bed is {bed[0]} x {bed[1]}")
    out, x = {}, -W / 2
    for c, w, h in zip(cols, cw, ch):
        y = h / 2
        for r in c:
            rd = max(size(n)[1] for n in r)
            rw = sum(size(n)[0] for n in r) + gap * (len(r) - 1)
            xr = x + (w - rw) / 2
            for n in r:
                b = parts[n].bounding_box()
                out[n] = parts[n].translate([xr - b[0], y - (rd + size(n)[1]) / 2 - b[1], 0.0])
                xr += size(n)[0] + gap
            y -= rd + gap
        x += w + gap
    return out


def pack(parts, bed):
    """Shelf packing of the footprints, largest first, centered on the bed. Returns {name: moved part}."""
    names = sorted(parts, key=lambda n: -(lambda b: (b[3] - b[0]) * (b[4] - b[1]))(parts[n].bounding_box()))
    W, D = bed[0], bed[1]
    rows, row, x, depth = [], [], 0.0, 0.0
    for n in names:
        b = parts[n].bounding_box()
        w, d = b[3] - b[0], b[4] - b[1]
        if row and x + w > W:
            rows.append((row, depth))
            row, x, depth = [], 0.0, 0.0
        row.append((n, x, w, d))
        x += w + GAP
        depth = max(depth, d)
    rows.append((row, depth))
    total_d = sum(d for _, d in rows) + GAP * (len(rows) - 1)
    out, y = {}, -total_d / 2
    for row, depth in rows:
        row_w = row[-1][1] + row[-1][2]
        for n, x0, w, d in row:
            b = parts[n].bounding_box()
            out[n] = parts[n].translate([x0 - row_w / 2 - b[0], y + (depth - d) / 2 - b[1], 0.0])
        y += depth + GAP
    for n, M in out.items():
        b = M.bounding_box()
        if b[0] < -W / 2 or b[3] > W / 2 or b[1] < -D / 2 or b[4] > D / 2 or b[5] > bed[2]:
            raise RuntimeError(f"{n} is off the bed: {np.round(b, 1)} on {bed}")
    return out


def write_3mf(parts, path, bed):
    """One object for each part, at its place on the bed. The parts are centered on 0, 0; the 3MF origin
    is the front-left corner of the bed."""
    objs, items = [], []
    for i, (n, M) in enumerate(parts.items(), start=1):
        m = M.translate([bed[0] / 2, bed[1] / 2, 0.0]).to_mesh()
        v = np.asarray(m.vert_properties)[:, :3]
        t = np.asarray(m.tri_verts)
        vs = "\n".join(f'     <vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}" />' for a, b, c in v)
        ts = "\n".join(f'     <triangle v1="{a}" v2="{b}" v3="{c}" />' for a, b, c in t)
        objs.append(f'  <object id="{i}" name="{n}" type="model">\n   <mesh>\n    <vertices>\n{vs}\n    </vertices>\n'
                    f'    <triangles>\n{ts}\n    </triangles>\n   </mesh>\n  </object>')
        items.append(f'  <item objectid="{i}" />')
    model = ('<?xml version="1.0" encoding="UTF-8"?>\n'
             '<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02">\n'
             ' <resources>\n' + "\n".join(objs) + '\n </resources>\n <build>\n' + "\n".join(items) + '\n </build>\n</model>')
    types = ('<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" />'
             '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml" /></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel" />'
            '</Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", types)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", model)


def _outer(cs):
    """The section with its holes filled: only the counterclockwise (outer) contours."""
    polys = cs.to_polygons()
    outer = [p for p in polys if len(p) > 2 and _area(p) > 0]
    return m3.CrossSection(outer, m3.FillRule.NonZero) if outer else m3.CrossSection()


def _area(p):
    p = np.asarray(p)
    return 0.5 * float(np.sum(p[:, 0] * np.roll(p[:, 1], -1) - np.roll(p[:, 0], -1) * p[:, 1]))


def resin_check(M, layer=RESIN_LAYER):
    """Cups, islands and peel area of a part in its plate orientation (see the module notes)."""
    zmax = M.bounding_box()[5]
    prev = m3.CrossSection()
    sealed_prev = m3.CrossSection()
    cup_vol, cup_layers, cup_max, islands, peel_max, peel_z = 0.0, 0, 0.0, [], 0.0, 0.0
    z = layer / 2
    while z < zmax:
        cs = M.slice(float(z))
        a = cs.area()
        if a > peel_max:
            peel_max, peel_z = a, z
        holes = _outer(cs) - cs
        sealed = m3.CrossSection()
        below = prev + sealed_prev
        for h in holes.decompose():
            ha = h.area()
            if ha < CUP_MIN:
                continue
            if (h - below).area() < 0.01 * ha:          # closed all around and closed under it
                sealed = sealed + h
        if sealed.area() > 0:
            cup_vol += sealed.area() * layer
            cup_layers += 1
            cup_max = max(cup_max, sealed.area())
        if not prev.is_empty():
            grow = prev.offset(layer * 1.0, m3.JoinType.Round)       # 45 deg: the layer below, grown by one layer
            for c in cs.decompose():
                if (c ^ grow).area() < 0.02:
                    b = c.bounds()
                    islands.append(dict(z=round(z, 2), area=round(c.area(), 2), x=round((b[0] + b[2]) / 2, 1), y=round((b[1] + b[3]) / 2, 1)))
        prev, sealed_prev = cs, sealed
        z += layer
    return dict(height=round(zmax, 1), peel_max_mm2=round(peel_max, 1), peel_max_z=round(peel_z, 1),
                cup_volume_mm3=round(cup_vol, 1), cup_layers=cup_layers, cup_max_mm2=round(cup_max, 1),
                islands=len(islands), island_list=islands[:20], volume_ml=round(M.volume() / 1000, 1))


def main():
    os.makedirs(OUT, exist_ok=True)
    meta = {"plates": []}
    report = {}
    for pid, parts in (("fdm_taz", fdm_parts()), ("resin_phenom", resin_parts())):
        bed = PLATES[pid]["bed"]
        placed = column_layout(parts, bed, RESIN_COLUMNS) if pid == "resin_phenom" else pack(parts, bed)
        d = os.path.join(OUT, pid)
        os.makedirs(d, exist_ok=True)
        for f in os.listdir(d):
            os.unlink(os.path.join(d, f))
        entry = dict(id=pid, label=PLATES[pid]["label"], bed=list(bed), parts=[])
        for n, M in placed.items():
            P.save_stl(M, os.path.join(d, f"{n}.stl"))
            entry["parts"].append(dict(name=n, file=f"{pid}/{n}.stl", color=COLORS[n]))
        P.save_stl(P.union(list(placed.values())), os.path.join(OUT, f"{pid}_plate.stl"))
        write_3mf(placed, os.path.join(OUT, f"{pid}.3mf"), bed)
        meta["plates"].append(entry)
        print(f"{pid}: {', '.join(placed)} on {bed[0]:g} x {bed[1]:g}")
        if pid == "resin_phenom":
            for n, M in parts.items():
                r = resin_check(M)
                report[n] = dict(r, orient=RESIN.get(n, "see plates.py"))
                print(f"  {n:11s} h {r['height']:5.1f}  {r['volume_ml']:4.1f} ml  peel max {r['peel_max_mm2']:6.1f} mm2"
                      f"  cups {r['cup_volume_mm3']:6.1f} mm3 ({r['cup_layers']} layers, max {r['cup_max_mm2']} mm2)  islands {r['islands']}")
    json.dump(meta, open(os.path.join(OUT, "plates.json"), "w"), indent=1)
    json.dump(report, open(os.path.join(OUT, "resin_check.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
