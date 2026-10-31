# Bittle X Pi Add-on v0.25 - Build Guide

Version 0.25, 2026-10-26. A sample add-on for the Bittle X platform v3.3 (../bittle_platform). It holds a Raspberry Pi Zero 2 W with a PiSugar S (1200 mAh), an NS4168 I2S amp with a 3 W speaker, and an SPH0645 I2S mic. The case is one rounded box (the body) and a slide-on top panel. The body clicks onto the platform pegs, and every part goes in from the top. No tools are necessary. A dab of glue sets the amp. On FDM, the add-on parts print without supports.

![The add-on on the platform: the port windows in the panel. The mic holes are in the right side, near the front.](doc/iso/hero-light.png)


## 1. Parts to print

| File (stl/print/) | Material | Orientation | Mass |
|---|---|---|---|
| pod_body.3mf (or .stl) | PLA | floor on the bed | 39 g |
| pod_body_fine.3mf (or .stl), for 0.10 mm layers | PLA | floor on the bed | 39 g |
| pod_panel.stl | PLA, second color | upside down: top on the bed | 20 g |
| pod_door.stl | PLA, white | flat on its outer face | 1 g |
| cover_pegs.stl (../bittle_platform), recommended | PLA | stand on the rear end, tree supports, 14-line brim | 11 g |
| cover_pegs_foot.stl (../bittle_platform), alternative | PLA | stand on the rear end, foot on the bed | 11 g |

Print every part with the Cura profile "Bittle X" (../cura/Bittle_X.curaprofile; 0.20 mm layers, no supports, 6-line brim). ../cura/install_profiles.py installs it, and a copy with the size compensation of each spool that the tolerance app measured ("Bittle X - <spool>"). The add-on parts need no supports. Print the cover without the foot: the foot teeth leave a spot on the cover where they break off.

At 0.10 mm layers, print pod_body_fine in place of pod_body. At fine layers the keyholes print near their true size, and the standard body is loose on the pegs. The fine body has a smaller slot gap (0.10 mm a side, standard 0.35) and more click travel (0.375 mm, standard 0.20). A 0.1 mm pad with a ramp on each click beam clamps the body down on the peg heads, so the body does not lift or tilt. The slide force is about 8 N. The fit test plates are in ../bittle_platform/stl/fit_fine/ (test 14). Only the floor keyholes change; the cover and its pegs stay the same.

The 3MF files (pod_body.3mf, pod_body_fine.3mf) have support blockers on the two amp nubs and on the latch rib of the rear wall. These print without support, and the tall, narrow support under them fails. Open the 3MF in Cura and turn on support as usual.

Screw version (rev 0.26, for 0.10 mm layers; viewer: --stl bittle_pi_addon/stl/screw). The pod screws to a cover with no pegs, and the pod and the cover clip onto the robot as one unit. The panel slides on as before, with smaller hook gaps, and two screws hold it in place of the latch.

| File (stl/print/) | Inserts and screws |
|---|---|
| cover_screw.stl: stand on the rear end, tree supports, 14-line brim | 4 x M2.5 x 4 or x 5 button or pan head screws, up from inside the cover |
| pod_body_screw.3mf (or .stl): floor on the bed | 4 x M2.5 x 4 inserts in the floor bosses, 2 x M2.5 x 4 inserts in the speaker post bosses (3.6 mm holes) |
| pod_panel_screw.stl: top on the bed | 2 x M2.5 x 12 screws down through the panel top, over the speaker posts |
| starter_plate_screw.stl: plate bottom on the bed | the starter plate for the screw mount: 4 x M2.5 x 4 inserts in the bosses, for an add-on of your own |

1. Press the 6 inserts in flush with a soldering iron.
2. Screw the body to the cover from inside the cover. Then put in the electronics.
3. Put the panel down 5 mm behind its place, slide it forward, and put in the two panel screws.
4. Clip the cover onto the robot.

Print quality. The body and panel walls are 2.0 mm: with the offsets of the body profile, Cura slices 4 full lines of 0.5 mm. The body walls are vertical and its floor is on the bed. The only overhangs (50 mm² in total) are the flat undersides of the two amp nubs (1.5 x 4 mm). The front-left cable notch is a 45 deg chamfer. The grille holes and the mic holes are teardrops (round, with a 45 deg point on top), so they print without bridges. The panel top edge round ends in a 45 deg chamfer at the bed, the port openings have 45 deg chamfers, and the lid hooks and the lugs in the body have 45 deg faces. The latch tongue bends along the layers of the panel. Its overhangs (7 mm²) are short bridges at the lid hooks. The door prints flat on its outer face.


## Print plates

stl/plates/ has every part and the platform cover on one bed, in its print orientation. Each 3MF has one object for each part. Each plate folder has one STL for each part.

| Printer | File | Orientation |
|---|---|---|
| FDM: LulzBot TAZ Workhorse (280 x 280 x 300), 0.5 mm nozzle | fdm_taz.3mf or fdm_taz_plate.stl | The parts as in stl/print/. Use the "Bittle X" Cura profile. The cover stands on its rear end: turn on tree supports and a 14-line brim. |
| Resin: Peopoly Phenom, first model (276 x 155 x 400) | resin_phenom.3mf or resin_phenom_plate.stl | The body, the panel, the door and the two fit coupons are tipped 45 deg, and the cover stands on its rear end. The lowest point is at Z 0. Lift the parts 5 mm in the slicer and add supports. |

1. Body (resin): the floor is toward the plate. Put the supports on the floor underside. Keep them out of the keyhole slots and off the click beams. Sand the marks flat: the floor slides on the cover.
2. Panel (resin): the open side is toward the plate. The top face has no support marks.
3. Cover (resin): it stands on its rear end, the points of the peg heads down. Put the supports on the rear edge only.
4. Door (resin): the outer face is up, tipped 45 deg. The supports go on the inner face and the ears.
5. The resin check found no cups (trapped resin) in these orientations.
6. The resin plate has the resin fit (pod.py RESIN_FIT, a best guess; stl/installed/resin/). Keyholes: slot gap 0.08 mm a side, click travel 0.25 mm (about 2.8 N), and a 0.05 mm clamp pad. Door gap 0.12 mm, door post gap 0.15 mm, amp slot gap 0.15 mm. The lid hooks and the latch do not change.
7. The two fit coupons are a step tighter (1 notch in the front rim: gap 0.05, click 0.30) and a step looser (2 notches: gap 0.12, click 0.20) than the body. Try them on the cover with the body. If the body is loose or tight, the coupon that fits shows the next fit.
8. Use a tough resin (ABS-like) for the click beams and the latch tongue.
9. Wash the parts in IPA and post-cure them before the fit test.


## 2. Electronics

| Part | Place |
|---|---|
| Raspberry Pi Zero 2 W + PiSugar S, 1200 mAh | On the long edge over the robot center, 4.9 mm left of the center line so the battery is near it: ports and PiSugar controls up, GPIO header down to the left (toward the BiBoard), SD card to the rear. Two end posts hold the boards in one groove, the same depth for both boards; the M2.5 screw heads go down channels in the posts. The pin-fin heatsink on the SoC points into the left well (14 x 14 x 6.5 mm, estimated). |
| Dupont jumpers | 3 female-to-male jumpers to the BiBoard (female on the Pi pin, male into the BiBoard socket). 6 female-female jumpers to the mic (2 of them through the splices): 10 cm, but 15 cm for GND and 3V. |
| NULLLAB NS4168 I2S amp | 38.4 x 22.4 mm board, on edge along the right wall, parts to the inside, in a slot bar on the floor, upright with its screw terminal at the top. Two nubs and two forks under the panel hold its top edge. Its PH2.0 connectors are side entry: the I2S cable plugs in at the front end, the speaker at the rear end. |
| NULLLAB 3 W 4 ohm speaker | At the rear, sound to the grille in the rear face. Body 27.9 wide, 15.2 deep. Two tapered wings (44 across, 3 thick) at the middle of the body depth stand in two side grooves. |
| HiLetgo SPH0645 I2S mic | 12.45 x 16.12 board, high on the right wall near the front, port to the wall (holes in the right side). Its straight 6-pin header is along its front edge: the plugs point inward, and the wires go straight across behind the front wall. 3V is the lowest pin, SEL the highest. It drops into a slot in a post (rear edge) and a ledge (bottom edge). No tools. |

Balance. The add-on weighs 114 g (weighed parts; printed parts at 50 % fill). Its center of mass is 8.8 mm behind the robot center and 0.2 mm right of the center line, 19 mm above the cover top. With the add-on, the center of mass of the robot is about 4 mm behind the midpoint of the front and rear paws (110 mm apart), and on the center line. The side is the limit when the robot tips: keep heavy parts low. Put your own masses in MASS_G in pod.py and run pod.py again.


## 3. Assembly

The 3D viewer shows each step with animation: [https://beetlebugorg.github.io/bittlex/viewer/#step=1](https://beetlebugorg.github.io/bittlex/viewer/#step=1). Labels are cut into the inside of the body: MIC, AMP and SPEAKER where each part goes, PIN 1 at the end of the Pi header, and grooves in the floor under the amp cable and the mic wire run. BIBOARD and PIN 40 are on the inner face of the door. The door is a piece of the left wall over the BiBoard plugs. With the panel off, lift the door out: a finger reaches the plugs from the side.

1. Fit the platform cover in place of the stock cover. ([viewer step 2](https://beetlebugorg.github.io/bittlex/viewer/#step=2))
2. Put the empty body on the pegs 7 mm behind its place, grille to the rear. Slide it 7 mm forward until it clicks (about 2.2 N). The BiBoard header is now in the notch at the front of the left well. ([viewer step 3](https://beetlebugorg.github.io/bittlex/viewer/#step=3)) ([viewer step 4](https://beetlebugorg.github.io/bittlex/viewer/#step=4))
3. Push the speaker down into the two side grooves at the rear, body to the rear. ([viewer step 5](https://beetlebugorg.github.io/bittlex/viewer/#step=5))
4. Plug the six mic jumpers onto the mic header: 15 cm jumpers on GND and 3V. Drop the mic into the slots in the post and the ledge on the right wall near the front, port to the wall, header at the front. ([viewer step 6](https://beetlebugorg.github.io/bittlex/viewer/#step=6))
5. Plug the flat amp cable into the I2S connector at the front end of the amp and the speaker into its rear end. Put the bottom edge of the amp into the slot along the right wall, parts to the inside, tilt its top edge under the two nubs, and set it with a dab of glue. Let the amp cable hang out of the top. ([viewer step 7](https://beetlebugorg.github.io/bittlex/viewer/#step=7))
6. Set the PiSugar AUTO switch before the cell goes on the board: it is under the cell. Push the Pi + PiSugar S stack down into the end grooves. ([viewer step 8](https://beetlebugorg.github.io/bittlex/viewer/#step=8))
7. Plug the wires one at a time, in the order of section 5: the splices, the Pi ends of the BiBoard jumpers, the amp cable, the mic jumpers, then the BiBoard ends. The viewer has one step for each wire. ([viewer step 9](https://beetlebugorg.github.io/bittlex/viewer/#step=9)) ([viewer step 19](https://beetlebugorg.github.io/bittlex/viewer/#step=19))
8. Slide the door down into the two grooves of the opening in the left wall, labels to the inside. The panel holds it down. ([viewer step 20](https://beetlebugorg.github.io/bittlex/viewer/#step=20))
9. Put the panel down 5 mm behind its place, then slide it forward until the latch clicks (about 9.2 N). The hooks under the panel go under the lugs in the walls. ([viewer step 21](https://beetlebugorg.github.io/bittlex/viewer/#step=21))
10. Open: lift the rear edge of the panel at the finger notch (about 5 N), slide the panel 5 mm rearward and lift it. Remove: open the panel, lift the door out, pull the BiBoard plugs off from the side, slide the body 7 mm rearward and lift it.

![Step 1 of the build guide: Fit the platform cover. The parts of the step are green.](doc/iso/step01-light.png)

![Step 2 of the build guide: Click the body on. The parts of the step are green.](doc/iso/step02-light.png)

![Step 3 of the build guide: Speaker. The parts of the step are green.](doc/iso/step03-light.png)

![Step 4 of the build guide: Mic. The parts of the step are green.](doc/iso/step04-light.png)

![Step 5 of the build guide: Amp and speaker lead. The parts of the step are green.](doc/iso/step05-light.png)

![Step 6 of the build guide: Pi + PiSugar S stack. The parts of the step are green.](doc/iso/step06-light.png)

![Step 7 of the build guide: Splices (BCLK and LRCLK). The parts of the step are green.](doc/iso/step07-light.png)

![Step 8 of the build guide: BiBoard jumpers: Pi ends. The parts of the step are green.](doc/iso/step08-light.png)

![Step 9 of the build guide: Amp cable. The parts of the step are green.](doc/iso/step09-light.png)

![Step 10 of the build guide: Mic jumpers. The parts of the step are green.](doc/iso/step10-light.png)

![Step 11 of the build guide: BiBoard ends. The parts of the step are green.](doc/iso/step11-light.png)

![Step 12 of the build guide: Door. The parts of the step are green.](doc/iso/step12-light.png)

![Step 13 of the build guide: Panel. The parts of the step are green.](doc/iso/step13-light.png)

On the top: the port openings are shaped to the plug bodies of common cables (plug + 1 mm). The Pi power, the Pi data and the PiSugar charge ports share one plain rounded rectangle. The HDMI opening also shows the PiSugar power switch, beside the plug. The lever is 5.7 mm under the panel: move it with a pen tip or a toothpick. The PiSugar button is in that rectangle too: press it with a fingertip or a pen tip.

![The top: one opening for HDMI and the power switch, and one for the Pi power, data USB, PiSugar charge and the PiSugar button.](doc/iso/top-light.png)


## 4. Wiring

| Board pin | Pi pin | Signal |
|---|---|---|
| BiBoard TX2 / RX2 / GND | 10 / 8 / 6 | RXD / TXD / GND (TX and RX cross). BiBoard +5V: not wired |
| Amp V / G | 2 / 14 | 5V / GND |
| Mic 3V / GND / SEL | 1 / 9 / 39 | 3V3 / GND / GND (left channel) |
| Amp BCLK + mic BCLK | 12 (splice) | GPIO18: one wire from the pin to a soldered splice, then one wire to each board |
| Amp LRC + mic LRCL | 35 (splice) | GPIO19: the same, a second splice |
| Amp DIN / mic DOUT | 40 / 38 | GPIO21 / GPIO20 |
| Speaker | - | amp 2-pin PH2.0 at the rear end of the amp |

Pin map from the wiring blueprint (reference/g2-wiring-blueprint.html; that blueprint wins if they differ). PiSugar S touches pins 2, 4, 5, 6 and 9 from below with its pogo pins. It uses pin 5 (SCL) for its button and auto start: with its AUTO switch ON, I2C cannot be used. Pins 11, 17-20 and 22-24 are kept free for a screen.


## 5. Cable routing

The BiBoard wires are female-to-male jumpers (the male end goes into the BiBoard socket), the mic wires female-female; 10 cm, but the mic GND and 3V jumpers are 15 cm. The amp keeps its own cable, and the two splices are cut from pack jumpers. pod.py models every wire (1.4 mm) at its real length and checks it: no wire touches a printed part or a board, no two wires pass through each other (0 found), and no bend is smaller than 2 mm radius (1.35 mm in the slack). A pack jumper is longer than its route, so its excess is an arch or a coil (a service loop) in free space. The pages below show each module: its pins, then its wires in the case.

![](doc/15_wiring_0.png)

![](doc/15_wiring_1.png)

![](doc/15_wiring_2.png)

![](doc/15_wiring_3.png)

| # | From | To (excess) | mm | # | From | To (excess) | mm |
|---|---|---|---|---|---|---|---|
| 1 | BiBoard TX2 | pin 10 (2-turn loop) | 100 | 10 | mic LRCL | LRCLK splice | 62 |
| 2 | BiBoard RX2 | pin 8 (arch) | 98 | 11 | mic DOUT | pin 38 (1-turn loop on a 5 mm stem) | 97 |
| 3 | BiBoard GND | pin 6 (arch) | 98 | 12 | mic BCLK | BCLK splice | 76 |
| 4 | amp G | pin 14 | 116 | 13 | mic GND | pin 9 (2-turn loop) | 149 |
| 5 | amp V | pin 2 | 130 | 14 | mic 3V | pin 1 (1-turn loop on a 5 mm stem) | 148 |
| 6 | amp BCLK | BCLK splice | 109 | 15 | BCLK splice | pin 12 | 16 |
| 7 | amp LRC | LRCLK splice | 95 | 16 | LRCLK splice | pin 35 | 7 |
| 8 | amp DIN | pin 40 | 81 | 17 | amp speaker + | speaker + | 43 |
| 9 | mic SEL | pin 39 (1-turn loop) | 99 | 18 | amp speaker - | speaker - | 44 |

Plug the jumpers one at a time, in this order. Each wire goes to its place before the next one, so the later wires lie over the earlier ones:

1. #1: BiBoard TX2 to pin 10. Put its excess in a 2-turn loop as in the drawing.
2. #2: BiBoard RX2 to pin 8. Put its excess in a arch as in the drawing.
3. #3: BiBoard GND to pin 6. Put its excess in a arch as in the drawing.
4. #14: mic 3V to pin 1. Put its excess in a 1-turn loop on a 5 mm stem as in the drawing.
5. #13: mic GND to pin 9. Put its excess in a 2-turn loop as in the drawing.
6. #12: mic BCLK to BCLK splice. Cut to length.
7. #11: mic DOUT to pin 38. Put its excess in a 1-turn loop on a 5 mm stem as in the drawing.
8. #10: mic LRCL to LRCLK splice. Cut to length.
9. #9: mic SEL to pin 39. Put its excess in a 1-turn loop as in the drawing.
10. Last, push the BiBoard ends of #1, #2 and #3 onto the BiBoard header.

1. The mic has a straight header along its front edge. Plug the six mic jumpers onto it before the mic goes in. Mic wires: straight inward out of the mic plugs, across behind the front wall in front of the stack, then rearward as a flat stack in the left well beside the BiBoard plugs; each wire stays at the height of its pin.
2. Amp cable: a flat cable on edge (G on top), with no twist: out of the plug, down a step, forward to the front wall, across behind it under the mic plugs, rearward along the left well; each wire turns in at its own height into its pin or splice (DIN first, V last). Lay it after the BiBoard jumpers: its V wire runs over their Pi ends.
3. Splices: the LRCLK splice stands beside the BiBoard plugs, the BCLK splice at the middle of the left well.
4. The BiBoard wires go in first, from the lowest: TX2, RX2, then GND. Their BiBoard ends go on last: a Pi housing for the mic slides off its pin past them.
5. The mic wires go in from the lowest of the stack: 3V, GND, BCLK, DOUT, LRCL, then SEL.

![From the left, panel off, the body see-through: the wires in 3D.](doc/iso/wires-light.png)


## 6. Checks

1. Slide: the empty body is clear of the robot at the click point, half way and at the drop-on place. The clicks are about 2.2 N to lock and 2.2 N to unlock (beam strain 0.64 %).
2. Panel: it goes down 5 mm behind its place and slides forward without contact. The latch tongue lifts 1 mm over the rib: about 9.2 N to slide on, 5 N to lift, strain 0.89 %. Lifted 0.3 mm, the hooks touch the lugs. Turned 180 deg, the panel does not go down.
3. Install: the speaker and the stack each go straight down 40 mm without contact. The mic drops into its slots; the post, the ledge and a stop hold it. The amp tilts in under its nubs. Each wire, in its order, goes in from 40 mm above without contact with the parts and wires already in place (small contacts of 2 to 3 mm³ stay where a wire slides under a loose service loop). Each Dupont housing slides off its pin without contact.
4. Door: it slides down its grooves from 45 mm up without contact. Pushed 0.3 mm in any direction, it touches the body. Lifted 0.3 mm, it touches the panel. With the door out, a finger tip has space over the BiBoard plug.
5. Switch and button: the switch lever is under the HDMI opening over its full travel. The PiSugar button is under the large opening.
6. Robot: the head turns from -85 to 85 deg without contact. 18 front and 36 rear leg poses (of 504) touch the add-on, only when a thigh swings up over the back. The Petoi tail is 3.2 mm under the add-on, and 0.05 mm at the drop-on place.

Open items: the BiBoard header height is an estimate (measure it). The speaker size is a ruler measurement. The mic port is assumed at the board center; the 7 holes cover ±2.2 mm. The SD card is assumed 2.5 mm out of its holder. The heatsink and the screw heads (4.6 x 1.8 mm) are estimates. PiSugar has no 3D model of the PiSugar S: its fit model is drawn from the PCB drawing in the PiSugar docs. The part heights, the cell gap (3.3 mm) and the cell size (taken from the PiSugar 2 cell) are estimates. To change the SD card, lift the stack out. The Pi power port and the PiSugar charge port are side by side: use one of them at a time.


## 7. Files and license

| File | Content |
|---|---|
| stl/print/ | the parts in print orientation |
| stl/plates/ | print plates for the FDM and the resin printer (3MF, STL), plates.json, resin_check.json |
| cad/*.step | the parts as STEP (from the mesh) |
| cad/assembly_step.zip | one STEP file with the robot, the platform and the add-on in place, with named and colored parts |
| stl/installed/, stl/models/ | the parts and the electronics in the robot frame |
| pod.py, motion.py, plates.py, render.py, docs.py | dimensions, build and checks; robot motion; print plates; pictures; this guide |

The printed parts, the drawings and this guide are CC BY 4.0, and the code is MIT (Jeremy Collins). The Pi Zero fit model is from github.com/PiSugar/PiSugar (GPL-3.0). The Petoi parts are from github.com/PetoiCamp/NonCodeFiles, without a stated license. LICENSE.md and ATTRIBUTION.md in the repository give the details.

