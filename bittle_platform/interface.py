"""Bittle X platform interface. All numbers for add-on design are here.

The platform is the stock Petoi Bittle X back cover (Bittle_Cover_with_hole_for_Pi.stl)
with 4 teardrop pegs on its flat top. On the robot, the cover is turned 180 deg about Y from
the STL: the Pi slot is at the front left (v3.2; build.py turns the cover meshes).
Add-ons drop onto the pegs, slide forward, and click.
To remove an add-on, slide it rearward (away from the head) and lift it.
v3.0 is not compatible with v1.x or v2.0: reprint the cover and the add-on plate.

This file is the single source of numbers. build.py makes the parts, the checks,
interface.json, SPEC.md and the PDF from it. ../pod.py reads it too.

Frame (the Petoi reference STL frame), units mm:
  X = lateral, +X = robot right side.
  Y = up.
  Z = length, -Z = head end (front), +Z = rear.
  Origin: on the robot center line, at the middle of the cover length.
"""

VERSION = "3.4"

# --------------------------------------------------------------------------
# Stock cover (measured from the Petoi STL)
# --------------------------------------------------------------------------
COVER_STL = "Bittle_Cover_with_hole_for_Pi.stl"
COVER_TOP = 25.29               # Y of the flat top surface
COVER_INNER_AT_PEGS = 23.89     # Y of the inner surface under the pegs
COVER_FLAT = dict(x=(-15.37, 15.37), z=(-21.37, 21.37))   # flat area of the top
COVER_END_Z = (-36.95, 36.95)
LOGO = dict(x=(-9.14, 9.14), z=(-7.80, 7.85), top=25.59)  # raised Petoi logo, 0.3 high
COVER_TURN = [[-1, 0, 0], [0, 1, 0], [0, 0, -1]]             # cover STL -> robot frame (180 deg about Y)
SLOT = dict(x0=-27.75, x1=-24.25, y0=19.5, z0=-25.75, z1=-11.75)   # Pi slot in the cover top (front left)
# v3.3: the slot is cut wider toward the center, to x1 of SLOT_WIDE (the user: the BiBoard Dupont plugs did not fit).
# It is 7.0 wide, the same as the BiBoard notch in the floor of the Pi add-on.
SLOT_WIDE = dict(SLOT, x1=-20.75)
# BiBoard 5-pin female header in the slot (GND, +5V, TX2, RX2, ..). Height is a photo estimate.
HDR = dict(x0=-27.27, x1=-24.73, z0=-25.1, z1=-12.4, top=29.1)
PLUG_TOP = 48.0                 # Y of free space for straight Dupont plugs and wires on the header
# v3.1: notch in the front edge of the cover, left side, for the Grove plug on the BiBoard (the head camera
# cable) and its cable. The plug is a little inside the front edge (user photo, not measured): GROVE_PLUG is
# an estimate of its space above the cover. Add-ons keep out of it (keepout.stl has it, swept over the slide).
GROVE_NOTCH = dict(x=(-25.5, -12.5), z=(-38.0, -26.45))
GROVE_PLUG = dict(x=(-25.0, -13.0), y_top=30.0, z=(-37.0, -27.0))

# --------------------------------------------------------------------------
# Pegs (part of the platform)
# --------------------------------------------------------------------------
# v3.0: the add-on slides forward to lock and rearward to come off. A closed add-on cannot slide
# toward the head (the head is 1.35 mm in front of the lid), but 7 mm to the rear is clear.
# Teardrop pegs (v2.0): the head, the shaft and the collar are teardrops with the point to the rear (+Z).
# The drop-in holes have the head shape with the point toward the slot, so an add-on goes on in one
# direction only: turned 180 deg, the round side of each hole is where the point of the head is.
# The cover prints standing on its rear end: all the points are down, so the pegs print without overhangs.
PEGS = [(12.0, -5.5), (12.0, 14.5), (-12.0, -5.5), (-12.0, 14.5)]   # (X, Z) centers: 24 x 20, 4.5 mm behind the cover center
# (the front drop-in holes stay 0.45 behind the speaker wall of the Pi add-on)
TIP_DEG = 45.0                  # half angle of the teardrop point
HEAD_TIP = 1.0                  # all the points are toward +Z
HEAD_TIP_DEG = 30.0             # a long head point: turned 180 deg, about 3 mm of it is over the plate
PEG_SHAFT_D = 4.0               # round part of the shaft teardrop
PEG_HEAD_D = 7.0                # round part of the head teardrop
PEG_HEAD_Y0, PEG_HEAD_Y1 = 27.8, 29.0      # head underside, head top
PEG_HEAD_CHAMFER = 0.5                      # 45 deg on the head top edge
PEG_ROOT_Y = 24.3                           # the shaft starts inside the 1.4 mm cover wall
PEG_COLLAR_D = 5.6                          # root collar, Y COVER_TOP-0.3 .. COVER_TOP+0.4
PEG_COLLAR_Y1 = COVER_TOP + 0.4


def tip_len(d, deg=TIP_DEG):
    """Distance from the center of a teardrop (round part d, half angle deg) to its point."""
    import math
    return d / 2 / math.sin(math.radians(deg))


# --------------------------------------------------------------------------
# Mount plate of an add-on (the part of the add-on that touches the pegs)
# --------------------------------------------------------------------------
MOUNT_Y0 = 26.0                 # bottom face of the mount plate (0.31 over the collar, 0.41 over the logo)
MOUNT_Y1 = 27.5                 # top face of the plate where the peg heads pass (0.3 under the heads)
MOUNT_T = MOUNT_Y1 - MOUNT_Y0   # 1.5
HEAD_CLEAR_Y = PEG_HEAD_Y1 + 0.5   # keep add-on material above this Y over the head sweep (29.5)

# Keyhole, one for each peg, in the plate. The add-on drops on SLIDE rearward (+Z)
# of its locked place, then slides SLIDE forward (-Z) to lock.
SLIDE = 7.0
KEY_HOLE_GAP = 0.45             # drop-in hole = the head teardrop + this gap, center at (px, pz - SLIDE)
KEY_SLOT_GAP = 0.35             # slot = the shaft + this gap each side, from (px, pz - SLIDE) to (px, pz)
KEY_SLOT_W = PEG_SHAFT_D + 2 * KEY_SLOT_GAP      # 4.7
KEY_LEAD = 0.4                  # 45 deg chamfer on the top and bottom edges of the slot and the hole
# The rear end of the slot is a V: the shaft teardrop + KEY_SLOT_GAP, moved forward so that a peg
# at (px, pz) touches both flanks. This is the stop of the locked place, and it centers the peg in X.
# Click (detent): two cantilever beams, one on each side of the slot, made by U slits
# (fixed only at the root, behind the peg). Each beam has a round bump at its free end, in front of the peg.
# The bumps push the shaft into the V stop: the add-on does not rattle.
# Shaft between the bumps: beam travel = travel. With a 1.2 x 1.5 beam, arm 7.0, PLA (E 2400):
# build.py detent_force() gives the slide force and the strain.
# v3.3: travel 0.28 -> 0.20 (the user found the add-on hard to slide on and off).
DET = dict(beam_w=1.2, slit_w=0.8, arm=7.5, bump_r=1.5, travel=0.20, preload=0.05, free_end=1.2, pad=0.0)   # pad > 0: build.py clamp_pads()
# Screw mount (v3.4): an alternative to the pegs, for a heavy add-on. The cover for screws (bittle_pi_addon pod.py
# build_cover_screw) has no pegs. At each peg place it has a ring from the cover top up to MOUNT_Y0, a clr_d hole and a
# pocket (head_d) for the screw head, web under MOUNT_Y0. An M2.5 x 4 screw goes up from inside the cover: its head is
# at Y MOUNT_Y0 - web, and its tip at Y MOUNT_Y0 - web + 4. The add-on plate has a thread (an insert or a nut) there.
SCREW_MOUNT = dict(screw="M2.5 x 4", clr_d=2.9, head_d=5.4, web=0.8, ring_d=7.6)
E_PLA = 2400.0                  # MPa, for the detent force estimate
MU_PLA = 0.3                    # PLA on PLA friction, for the detent force estimate

# --------------------------------------------------------------------------
# Envelope (checked with the pod; outside this, check the robot yourself)
# --------------------------------------------------------------------------
ENVELOPE = dict(
    z=(-37.8, 56.2),            # front and rear faces of the Pi add-on body
    half_w_low=29.6,            # max |X| of the add-on body (flat floor at Y 26.0, over the cover and the shoulders)
    half_w_high=35.6,           # max |X| above Y 36 (a 45 deg chamfer from Y 30): the rear legs swing back past the floor edge
    top=67.2,                   # add-on top; no robot limit, but a high mass makes the robot less stable
    com_z_max=10.0,             # keep the add-on center of mass within this distance of Z 0 (robot center)
    hug_gap=0.4,                # gap to the cover and the shoulder plates
)
