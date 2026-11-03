"""Mesh helpers (numpy + manifold3d + build123d) for the peg cover build."""
import math
import os
import tempfile

import numpy as np
import manifold3d as m3
from build123d import export_stl


def load_stl(path):
    d = open(path, "rb").read()
    n = np.frombuffer(d[80:84], np.uint32)[0]
    if 84 + n * 50 == len(d):
        a = np.frombuffer(d[84:84 + n * 50], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
        return a["v"].reshape(-1, 3, 3).astype(float)
    tris, cur = [], []
    for line in d.decode(errors="ignore").splitlines():
        s = line.split()
        if s and s[0] == "vertex":
            cur.append([float(t) for t in s[1:4]])
            if len(cur) == 3:
                tris.append(cur)
                cur = []
    return np.array(tris, dtype=float)


def mesh_to_manifold(tris):
    v = tris.reshape(-1, 3)
    uv, inv = np.unique(v.round(4), axis=0, return_inverse=True)
    mesh = m3.Mesh(vert_properties=uv.astype(np.float32), tri_verts=inv.reshape(-1, 3).astype(np.uint32))
    return m3.Manifold(mesh)


def b3d_to_manifold(shape, tol=0.02):
    with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as f:
        path = f.name
    export_stl(shape, path, tolerance=tol, angular_tolerance=0.1)
    M = mesh_to_manifold(load_stl(path))
    os.unlink(path)
    if M.status() != m3.Error.NoError:
        raise RuntimeError(f"tessellation not manifold: {M.status()}")
    return M


def save_stl(M, path):
    mesh = M.to_mesh()
    v = np.asarray(mesh.vert_properties)[:, :3]
    save_tris(v[np.asarray(mesh.tri_verts)], path)


def save_tris(tri, path):
    """Binary STL from an (n, 3, 3) triangle array."""
    nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
    rec = np.zeros(len(tri), dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    rec["n"] = nrm
    rec["v"] = tri.reshape(-1, 9)
    with open(path, "wb") as f:
        f.write(b"bittle-platform".ljust(80, b" "))
        f.write(np.uint32(len(tri)).tobytes())
        f.write(rec.tobytes())


def heightfield_solid(tris, x0, x1, z0, z1, step=0.4, lift=0.0, floor=0.0, sweep_z=0.0):
    """Closed solid under the top surface of a mesh (raised by `lift`).
    sweep_z: the surface is also swept that far along Z (+ or -; max over the grid shifts)."""
    xs = np.arange(x0, x1 + 1e-9, step)
    zs = np.arange(z0, z1 + 1e-9, step)
    H = np.full((len(xs), len(zs)), -1e9)
    nrm = np.cross(tris[:, 1] - tris[:, 0], tris[:, 2] - tris[:, 0])
    up = tris[nrm[:, 1] > 1e-9]
    for tri in up:
        (ax, ay, az), (bx, by, bz), (cx, cy, cz) = tri
        lo_x, hi_x = min(ax, bx, cx), max(ax, bx, cx)
        lo_z, hi_z = min(az, bz, cz), max(az, bz, cz)
        i0, i1 = np.searchsorted(xs, lo_x), np.searchsorted(xs, hi_x, "right")
        j0, j1 = np.searchsorted(zs, lo_z), np.searchsorted(zs, hi_z, "right")
        if i0 >= i1 or j0 >= j1:
            continue
        X, Z = np.meshgrid(xs[i0:i1], zs[j0:j1], indexing="ij")
        det = (bz - cz) * (ax - cx) + (cx - bx) * (az - cz)
        if abs(det) < 1e-12:
            continue
        l1 = ((bz - cz) * (X - cx) + (cx - bx) * (Z - cz)) / det
        l2 = ((cz - az) * (X - cx) + (ax - cx) * (Z - cz)) / det
        l3 = 1 - l1 - l2
        ok = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
        Y = l1 * ay + l2 * by + l3 * cy
        sub = H[i0:i1, j0:j1]
        sub[ok] = np.maximum(sub[ok], Y[ok])
    H[H < -1e8] = floor
    H = H + lift
    # dilate by one cell so the sampled surface stays above the true surface
    Hd = H.copy()
    for di in (-1, 0, 1):
        for dj in (-1, 0, 1):
            Hd = np.maximum(Hd, np.roll(np.roll(H, di, 0), dj, 1))
    H = Hd
    if sweep_z:
        Hs = H.copy()
        for k in range(1, int(math.ceil(abs(sweep_z) / step)) + 1):
            if sweep_z > 0:
                Hs[:, k:] = np.maximum(Hs[:, k:], H[:, :-k])
            else:
                Hs[:, :-k] = np.maximum(Hs[:, :-k], H[:, k:])
        H = Hs
    nx, nz = len(xs), len(zs)
    top = np.array([[x, H[i, j], z] for i, x in enumerate(xs) for j, z in enumerate(zs)])
    bot = np.array([[x, floor, z] for x in xs for z in zs])
    V = np.vstack([top, bot]).astype(np.float32)
    idx = lambda i, j, b=0: b * nx * nz + i * nz + j
    T = []
    for i in range(nx - 1):
        for j in range(nz - 1):
            a, b_, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j + 1), idx(i, j + 1)
            T += [(a, d, c), (a, c, b_)]                       # top (+Y)
            a, b_, c, d = idx(i, j, 1), idx(i + 1, j, 1), idx(i + 1, j + 1, 1), idx(i, j + 1, 1)
            T += [(a, c, d), (a, b_, c)]                       # bottom (-Y)
    for i in range(nx - 1):   # sides z = z0 and z = z1
        for j, flip in ((0, False), (nz - 1, True)):
            a, b_, c, d = idx(i, j), idx(i + 1, j), idx(i + 1, j, 1), idx(i, j, 1)
            T += [(a, b_, c), (a, c, d)] if not flip else [(a, c, b_), (a, d, c)]
    for j in range(nz - 1):   # sides x = x0 and x = x1
        for i, flip in ((0, False), (nx - 1, True)):
            a, b_, c, d = idx(i, j), idx(i, j + 1), idx(i, j + 1, 1), idx(i, j, 1)
            T += [(a, c, b_), (a, d, c)] if not flip else [(a, b_, c), (a, c, d)]
    M = m3.Manifold(m3.Mesh(vert_properties=V, tri_verts=np.array(T, dtype=np.uint32)))
    if M.status() != m3.Error.NoError or M.volume() <= 0:
        raise RuntimeError(f"heightfield solid failed: {M.status()} {M.volume()}")
    return M
