# Attribution

## Petoi Bittle X parts

Source: Petoi, https://github.com/PetoiCamp/NonCodeFiles, folder
`stl/Bittle & BittleX`, last changed in commit d467ed3a23 (2025-06-18).
The files here are byte-identical copies of the files at that commit.

Petoi publishes these files without a stated license. They are not covered
by the licenses of this repository. All rights stay with Petoi.

| File in this repository | Petoi file |
|---|---|
| `bittle_platform/reference/Bittle_Cover_with_hole_for_Pi.stl` | `BittleCover/Bittle_Cover_with_hole_for_Pi.stl` |
| `bittle_platform/reference/Bittle_Cover.stl` | `BittleCover/Bittle_Cover.stl` |
| `bittle_platform/reference/Bittle_SideShoulder.stl` | `Bittle_SideShoulder.stl` |
| `bittle_platform/reference/Bittle_FrontPlate.stl` | `Bittle_FrontPlate.stl` |
| `bittle_platform/reference/Bittle_tail.stl` | `Bittle_tail.stl` |

Files made from the Petoi parts:

- `cover_pegs.stl` (in `bittle_platform/stl/print/`, `bittle_platform/stl/installed/`
  and `bittle_pi_addon/stl/installed/`): Bittle_Cover_with_hole_for_Pi.stl
  with 4 pegs added. The print version is rotated to the print orientation.
- `bittle_platform/stl/installed/keepout.stl`: a clearance volume above the
  cover, the side shoulders and the front plate.
- `bittle_pi_addon/stl/models/cover_slot.stl`: the free space in the Pi slot
  of the cover.
- The 3D viewer on the site loads the side shoulder and the front plate
  (also mirrored as the rear plate).

Image from the Petoi documentation, also without a stated license:

- `bittle_platform/doc/petoi_touch_areas.png`: the touch area layout from
  https://docs.petoi.com/extensible-modules/back-touch-sensor/bittle-x-v2-bittle-x+arm,
  unchanged.

`bittle_platform/stl/robot/tail.stl` is Bittle_tail.stl mirrored in Z into
the robot frame by `bittle_platform/robot.py`.

## Petoi ROS model of Bittle

Source: Petoi, https://github.com/PetoiCamp/ros_opencat, folder
`petoi_ROS_model_docs/bittle_ros/bittle_description`, branch `ros1`, commit
85962928970 (2025-03-13). License: MIT, in that folder and copied to
`bittle_platform/reference/petoi_ros/LICENSE`. The files in
`bittle_platform/reference/petoi_ros/` are byte-identical copies of 38 of its
meshes and of `urdf/bittle.xacro`.

Files made from them, also under MIT: `bittle_platform/stl/robot/*.stl`
(except `tail.stl`) and `robot.json`. `bittle_platform/robot.py` moves the
meshes into the robot frame, turns the legs to a standing pose, and
simplifies the meshes to 0.08 mm. The 3D viewer on the site loads them.

## Raspberry Pi Zero model

Source: PiSugar, https://github.com/PiSugar/PiSugar, commit 61a5e2083f
(2022-01-18). License: GPL-3.0 (`LICENSES/GPL-3.0.txt`). The file here is
a byte-identical copy of the file at that commit.

| File in this repository | PiSugar file |
|---|---|
| `bittle_pi_addon/reference/RaspberryPiZeroW-1.STL` | `model3/RaspberryPiZeroW-1.STL` |

Made from it, also under GPL-3.0: `bittle_pi_addon/stl/models/pizero.stl`.
This is the same mesh moved and rotated into the robot frame by
`bittle_pi_addon/pod.py`. It is a fit reference. The printed parts do not
contain it.

## Other component models

The models of the NS4168 amp, the speaker, the SPH0645 mic, the battery,
the BiBoard header and the Dupont plugs in `bittle_pi_addon/stl/models/`
are boxes drawn by `pod.py` from measurements. They are CC BY 4.0 with the
other designs.

PiSugar publishes no 3D model of the PiSugar S. `pod.py` draws its fit
model (`bittle_pi_addon/stl/models/pisugar_s.stl`) from the PCB drawing
and the photos in the PiSugar documentation
(https://github.com/PiSugar/pisugar-doc, `docs/product-wiki/battery/pisugar-s-series.md`,
and https://cdn.pisugar.com/img/PiSugarS240705.jpg). The repository holds
no copy of the drawing or the photos. The model is CC BY 4.0 with the other
designs.

## Font

`bittle_pi_addon/reference/fonts/LiberationSans-Bold.ttf` is Liberation Sans
Bold 2.1.5 (Red Hat), under the SIL Open Font License 1.1
(`LICENSES/OFL-1.1-Liberation.txt`). `pod.py` cuts the labels inside the
body with it.

## Logo

`bittle_pi_addon/reference/logo/linechef.jpg` is the avatar of the GitHub
account LineChef (github.com/LineChef). The repository licenses do not
cover it. Since add-on rev 0.25, no part uses it.

## Trademarks

This is an independent community project. It is not affiliated with or
endorsed by Petoi. Bittle and Petoi are trademarks of Petoi LLC.
