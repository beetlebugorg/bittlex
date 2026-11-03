"""Write the "Bittle X" Cura profile: one profile for every printed part of the peg cover and the add-on.

It writes the base profile (no size compensation) and, for each spool that the tolerance app measured,
a copy with that spool's compensation ("Bittle X - <spool>"), the same way the tolerance app installs one.
It also writes cura/Bittle_X.curaprofile (the base profile) for import in Cura on another computer.
Close Cura first: Cura writes its configuration when it closes.
  python3 cura/install_profiles.py [CURA_DIR]
"""
import glob
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
CURA = sys.argv[1] if len(sys.argv) > 1 else max(glob.glob(os.path.expanduser("~/.local/share/cura/[0-9]*")))
SPOOLS = os.path.expanduser("~/.config/tolerance/spools")
NAME = "Bittle X"

# Global settings. 0.20 layers: the walls are 2.0 mm (4 lines of 0.5), and the break-off teeth of the cover foot
# are exactly one layer (see bittle_platform/build.py FOOT). No supports: every part is designed to print without.
GLOBAL = dict(layer_height=0.2, layer_height_0=0.25, adhesion_type="brim", support_enable=False, support_structure="tree",
              support_type="buildplate", acceleration_enabled=True, bridge_settings_enabled=True, speed_slowdown_layers=2,
              material_shrinkage_percentage_xy=100.0, material_shrinkage_percentage_z=100.0)
# Extruder settings: slow outer walls and low outer-wall acceleration for clean faces (from "Bittle Fine").
EXTRUDER = dict(
    acceleration_print=1500, acceleration_wall=1000, acceleration_wall_0=500, acceleration_wall_x=1000,
    acceleration_topbottom=1000, acceleration_roofing=1000, acceleration_travel=2500, acceleration_layer_0=500,
    acceleration_skirt_brim=1000, bridge_fan_speed=100, bridge_wall_speed=20, brim_line_count=6, brim_location="outside",
    cool_fan_full_layer=4, cool_fan_speed_min=100, cool_min_layer_time=10, cool_min_layer_time_fan_speed_max=0,
    infill_pattern="gyroid", infill_sparse_density=20, material_print_temperature=220, material_print_temperature_layer_0=220,
    retract_at_layer_change=True, retraction_amount=1.5, retraction_min_travel=3, retraction_speed=15, skin_angles="[45]",
    skin_monotonic=True, speed_infill=55, speed_layer_0=18, speed_print=50, speed_roofing=30, speed_topbottom=35,
    speed_travel=150, speed_travel_layer_0=100, speed_wall=35, speed_wall_0=25, speed_wall_x=40, support_angle=55,
    top_bottom_thickness=1.0, wall_0_wipe_dist=0.4, wall_line_count=3, xy_offset=0.0, hole_xy_offset=0.0,
    xy_offset_layer_0=-0.1, z_seam_corner="z_seam_corner_inner", z_seam_position="back", z_seam_type="back")


def fmt(v):
    return str(v) if not isinstance(v, float) else repr(round(v, 3) + 0.0)


def cfg(name, pos, values, spool):
    meta = [("quality_type", "draft"), ("setting_version", "27"), ("type", "quality_changes")]
    if spool:
        meta.insert(0, ("tolerance_spool", spool))
    if pos is not None:
        meta.insert(0, ("position", str(pos)))
    lines = ["[general]", "version = 4", f"name = {name}", "definition = fdmprinter", "", "[metadata]"]
    lines += [f"{k} = {v}" for k, v in meta] + ["", "[values]"] + [f"{k} = {fmt(v)}" for k, v in values.items()] + [""]
    return "\n".join(lines)


def write(name, spool=None, comp=None):
    g, e = dict(GLOBAL), dict(EXTRUDER)
    if comp:
        # the tolerance app rule: horizontal expansion makes pegs right; the hole expansion also cancels it in the holes
        g["material_shrinkage_percentage_xy"] = round(100 / comp["scale_xy"], 2)
        g["material_shrinkage_percentage_z"] = round(100 / comp.get("scale_z", 1) or 1, 2)
        e["xy_offset"] = round(-comp["peg_offset"] / 2, 3)
        e["hole_xy_offset"] = round(-comp["hole_offset"] / 2 + e["xy_offset"], 3)
    fid = name.replace(" ", "_")
    out = {}
    for pos, vals, f in ((None, g, f"{fid}.inst.cfg"), (0, e, f"{fid}_e0.inst.cfg")):
        out[f] = cfg(name, pos, vals, spool)
        open(os.path.join(CURA, "quality_changes", f), "w").write(out[f])
    print(f"{name}: xy_offset {e['xy_offset']}, hole_xy_offset {e['hole_xy_offset']}, shrinkage xy {g['material_shrinkage_percentage_xy']}")
    return out


if __name__ == "__main__":
    base = write(NAME)
    with zipfile.ZipFile(os.path.join(HERE, "Bittle_X.curaprofile"), "w") as z:
        for f, txt in base.items():
            z.writestr(f, txt)
    for p in sorted(glob.glob(os.path.join(SPOOLS, "*.json"))):
        d = json.load(open(p))
        if not d.get("measured") or "derived" not in d:
            print(f"{d['name']}: not measured, use the base profile until the tolerance app measures it")
            continue
        write(f"{NAME} - {d['name']}", d["name"], d["derived"])
