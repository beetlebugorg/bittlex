# Bittle X Pi Add-on v0.26 - Build Guide

Version 0.26, 2026-10-31. A sample add-on for the Bittle X platform v3.4 (../bittle_platform). It holds a Raspberry Pi Zero 2 W with a PiSugar S (1200 mAh), an NS4168 I2S amp with a 3 W speaker, and an SPH0645 I2S mic. The case is one rounded box (the body) and a slide-on top panel. The body screws to a cover for screws, and the cover and the body clip onto the robot as one unit, in place of the stock cover. Every part goes in from the top. Two screws hold the panel. A dab of glue sets the amp.

![The add-on on the robot: the port windows in the panel. The mic holes are in the right side, near the front.](doc/iso/hero-light.png)


## 1. Parts to print

| File (stl/print/) | Material | Orientation | Mass |
|---|---|---|---|
| pod_body_screw.3mf (or .stl) | PLA | floor on the bed | 40 g |
| pod_panel_screw.stl | PLA, second color | upside down: top on the bed | 21 g |
| pod_door.stl | PLA | flat on its outer face | 1 g |
| cover_screw.stl | PLA | stand on the rear end, tree supports, 14-line brim | 10 g |
| starter_plate_screw.stl (optional) | PLA | plate bottom on the bed | 5 g |

Each part has a file for 0.20 mm layers and a *_fine file for 0.10 mm layers, for example pod_panel_screw.stl and pod_panel_screw_fine.stl. The fine panel has smaller hook gaps (0.05 mm). The other fine files are the same as the 0.20 mm files now. Slice them with the profiles in ../profiles/taz-workhorse-se (pla-0.20-standard and pla-0.10-fine) and a brim. printdeck.yml in the repository root has the profile and the settings of each part. The old Cura profile "Bittle X" (../cura/Bittle_X.curaprofile; 0.20 mm layers) also works for the 0.20 mm files.

pod_body_screw.3mf has support blockers on the two amp nubs and at the middle of the rear wall. The nubs print without support, and the tall, narrow support under them fails. Open the 3MF in Cura and turn on support as usual. starter_plate_screw.stl is the starter plate of the platform with the same 4 bosses: use it to start an add-on of your own, or to test the inserts or nuts on the cover.


## Inserts or nuts

Each of the 6 bosses holds a threaded part for an M2.5 screw: 4 in the floor (the cover screws) and 2 on the speaker posts (the panel screws). The FDM parts use heat-set inserts. The resin parts use M2.5 nuts with superglue in place of the inserts. The screws are the same for both.

|  | FDM print (PLA): heat-set inserts | Resin print: glued nuts |
|---|---|---|
| Files | stl/print/: pod_body_screw, pod_panel_screw, cover_screw | stl/print/resin/, or the resin plate (stl/plates/resin_phenom) |
| In the bosses | 6 x M2.5 heat-set insert, 4 mm long (3.6 mm holes, 3.9 mm deep; bosses 7 mm) | 6 x M2.5 hex nut (5 mm across the flats, 2 mm thick) in hex pockets; bosses 8 mm |
| Screws | 4 x M2.5 x 4 button or pan head (cover), 2 x M2.5 x 12 (panel) | the same |
| Tools | soldering iron (an insert tip helps), screwdriver | superglue, screwdriver |

1. FDM: heat each insert with the soldering iron and press it in straight, flush with the top of the boss. Let it cool before you put in a screw.
2. Resin: put a nut flat into the hex pocket at the top of each boss and push it to the bottom. Put a drop of superglue on its edge. Keep the glue off the thread. Let the glue set.
3. Floor: the nut is at the bottom of its pocket. The M2.5 x 4 cover screw goes fully through the nut (the screw tip is at Y 29.2, the nut top at Y 29.0).
4. Speaker posts: the panel column is over the nut and holds it in its pocket. The M2.5 x 12 panel screw goes through the nut.


## Click-on version

The click-on version has no screws: pod_body.3mf, pod_body_fine.3mf and pod_panel.stl click onto cover_pegs.stl (../bittle_platform). Put the body on the pegs 7 mm behind its place and slide it forward until it clicks; a latch at the rear holds the panel. At 0.10 mm layers, print pod_body_fine in place of pod_body: it has a smaller slot gap (0.10 mm a side) and more click travel (0.375 mm). The fit test plates are in ../bittle_platform/stl/fit_fine/ (test 14). With the full pod on it, the click-on body is loose: the screw version replaces it.

Print quality. The body and panel walls are 2.0 mm: with the offsets of the body profile, Cura slices 4 full lines of 0.5 mm. The body walls are vertical and its floor is on the bed. The only overhangs are the flat undersides of the two amp nubs (1.5 x 4 mm). The front-left cable notch is a 45 deg chamfer. The grille holes and the mic holes are teardrops (round, with a 45 deg point on top), so they print without bridges. The panel top edge round ends in a 45 deg chamfer at the bed, the port openings have 45 deg chamfers, and the lid hooks and the lugs in the body have 45 deg faces. The holes in the cover are teardrops, because the cover prints on its rear end. The door prints flat on its outer face.


## Print plates

stl/plates/ has every part on one bed, in its print orientation. Each 3MF has one object for each part. Each plate folder has one STL for each part.

| Printer | File | Orientation |
|---|---|---|
| FDM: LulzBot TAZ Workhorse (280 x 280 x 300), 0.5 mm nozzle | fdm_taz.3mf or fdm_taz_plate.stl | The screw parts as in stl/print/ (0.20 mm files). The cover stands on its rear end: turn on tree supports and a 14-line brim. |
| Resin: Peopoly Phenom, first model (276 x 155 x 400) | resin_phenom.3mf or resin_phenom_plate.stl | The screw version with nuts: the body, the panel, the door and the starter plate are tipped 45 deg, and the cover stands on its rear end. The lowest point is at Z 0. Lift the parts 5 mm in the slicer and add supports. stl/print/resin/ has each part alone. |

1. Body (resin): the floor is toward the plate. Put the supports on the floor underside, off the screw holes. Sand the marks flat: the floor is on the cover rings.
2. Panel (resin): the open side is toward the plate. The top face has no support marks.
3. Cover (resin): it stands on its rear end. Put the supports on the rear edge only.
4. Door (resin): the outer face is up, tipped 45 deg. The supports go on the inner face and the ears.
5. The resin check found no cups (trapped resin) in these orientations.
6. The resin fit (pod.py RESIN_FIT, a best guess; stl/installed/resin/): door gap 0.12 mm, door post gap 0.15 mm, amp slot gap 0.15 mm. The panel has the hook gaps for 0.10 mm layers (0.05 mm).
7. The starter plate (resin) has the same nut bosses. Print it first to test the nut pockets on the cover.
8. Wash the parts in IPA and post-cure them before the fit test.


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

The 3D viewer shows each step with animation: [https://beetlebugorg.github.io/bittlex/viewer/#step=1](https://beetlebugorg.github.io/bittlex/viewer/#step=1). Grooves in the floor are under the amp cable and the mic wire run. The door is a piece of the left wall over the BiBoard plugs. With the panel off, lift the door out: a finger reaches the plugs from the side.

1. Put the 6 inserts or nuts into the bosses: 4 in the floor and 2 on the speaker posts (see Inserts or nuts). ([viewer step 2](https://beetlebugorg.github.io/bittlex/viewer/#step=2))
2. Put the empty body on the cover for screws, grille to the rear. Put an M2.5 x 4 screw up through each of the 4 rings from inside the cover, into the insert or the nut, and tighten it. ([viewer step 3](https://beetlebugorg.github.io/bittlex/viewer/#step=3))
3. Remove the stock back cover. Clip the cover and the body onto the robot as one unit. The BiBoard header comes up through the opening in the cover and the notch at the front of the left well. ([viewer step 4](https://beetlebugorg.github.io/bittlex/viewer/#step=4))
4. Push the speaker down into the two side grooves at the rear, body to the rear. ([viewer step 5](https://beetlebugorg.github.io/bittlex/viewer/#step=5))
5. Plug the six mic jumpers onto the mic header: 15 cm jumpers on GND and 3V. Drop the mic into the slots in the post and the ledge on the right wall near the front, port to the wall, header at the front. ([viewer step 6](https://beetlebugorg.github.io/bittlex/viewer/#step=6))
6. Plug the flat amp cable into the I2S connector at the front end of the amp and the speaker into its rear end. Put the bottom edge of the amp into the slot along the right wall, parts to the inside, tilt its top edge under the two nubs, and set it with a dab of glue. Let the amp cable hang out of the top. ([viewer step 7](https://beetlebugorg.github.io/bittlex/viewer/#step=7))
7. Set the PiSugar AUTO switch before the cell goes on the board: it is under the cell. Push the Pi + PiSugar S stack down into the end grooves. ([viewer step 8](https://beetlebugorg.github.io/bittlex/viewer/#step=8))
8. Plug the wires one at a time, in the order of section 5: the splices, the Pi ends of the BiBoard jumpers, the amp cable, the mic jumpers, then the BiBoard ends. The viewer has one step for each wire. ([viewer step 9](https://beetlebugorg.github.io/bittlex/viewer/#step=9)) ([viewer step 19](https://beetlebugorg.github.io/bittlex/viewer/#step=19))
9. Slide the door down into the two grooves of the opening in the left wall. The panel holds it down. ([viewer step 20](https://beetlebugorg.github.io/bittlex/viewer/#step=20))
10. Put the panel down 5 mm behind its place, then slide it forward. The hooks under the panel go under the lugs in the walls. Put the two M2.5 x 12 screws down through the panel into the speaker posts. ([viewer step 21](https://beetlebugorg.github.io/bittlex/viewer/#step=21))
11. Open: take out the two panel screws, slide the panel 5 mm rearward and lift it. Remove: open the panel, lift the door out, pull the BiBoard plugs off from the side, and unclip the cover from the robot. To take the body off the cover, take out the 4 screws from inside the cover.

![Step 1 of the build guide: Inserts or nuts. The parts of the step are green.](doc/iso/step01-light.png)

![Step 2 of the build guide: Screw the body to the cover. The parts of the step are green.](doc/iso/step02-light.png)

![Step 3 of the build guide: Clip onto the robot. The parts of the step are green.](doc/iso/step03-light.png)

![Step 4 of the build guide: Speaker. The parts of the step are green.](doc/iso/step04-light.png)

![Step 5 of the build guide: Mic. The parts of the step are green.](doc/iso/step05-light.png)

![Step 6 of the build guide: Amp and speaker lead. The parts of the step are green.](doc/iso/step06-light.png)

![Step 7 of the build guide: Pi + PiSugar S stack. The parts of the step are green.](doc/iso/step07-light.png)

![Step 8 of the build guide: Splices (BCLK and LRCLK). The parts of the step are green.](doc/iso/step08-light.png)

![Step 9 of the build guide: BiBoard jumpers: Pi ends. The parts of the step are green.](doc/iso/step09-light.png)

![Step 10 of the build guide: Amp cable. The parts of the step are green.](doc/iso/step10-light.png)

![Step 11 of the build guide: Mic jumpers. The parts of the step are green.](doc/iso/step11-light.png)

![Step 12 of the build guide: BiBoard ends. The parts of the step are green.](doc/iso/step12-light.png)

![Step 13 of the build guide: Door. The parts of the step are green.](doc/iso/step13-light.png)

![Step 14 of the build guide: Panel. The parts of the step are green.](doc/iso/step14-light.png)

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

1. Mount: the cover and the body go straight down onto the robot together. The body has no contact on the way. The cover touches the shoulders only at its clips, the same as the cover with the pegs. Each cover screw goes through the cover and the floor into its insert or nut, clear of the boards. The floor is on the 4 cover rings.
2. Panel: it goes down 5 mm behind its place and slides forward without contact. Each panel screw goes down through the panel column and the post boss, clear of the boards.
3. Install: the speaker and the stack each go straight down 40 mm without contact. The mic drops into its slots; the post, the ledge and a stop hold it. The amp tilts in under its nubs. Each wire, in its order, goes in from 40 mm above without contact with the parts and wires already in place (small contacts of 2 to 3 mm³ stay where a wire slides under a loose service loop). Each Dupont housing slides off its pin without contact.
4. Door: it slides down its grooves from 45 mm up without contact. Pushed 0.3 mm in any direction, it touches the body. Lifted 0.3 mm, it touches the panel. With the door out, a finger tip has space over the BiBoard plug.
5. Switch and button: the switch lever is under the HDMI opening over its full travel. The PiSugar button is under the large opening.
6. Robot: the head turns from -85 to 85 deg without contact. 18 front and 36 rear leg poses (of 504) touch the add-on, only when a thigh swings up over the back. The Petoi tail is 3.2 mm under the add-on.

Open items: the BiBoard header height is an estimate (measure it). The speaker size is a ruler measurement. The mic port is assumed at the board center; the 7 holes cover ±2.2 mm. The SD card is assumed 2.5 mm out of its holder. The heatsink and the screw heads (4.6 x 1.8 mm) are estimates. PiSugar has no 3D model of the PiSugar S: its fit model is drawn from the PCB drawing in the PiSugar docs. The part heights, the cell gap (3.3 mm) and the cell size (taken from the PiSugar 2 cell) are estimates. To change the SD card, lift the stack out. The Pi power port and the PiSugar charge port are side by side: use one of them at a time.


## 7. Files and license

| File | Content |
|---|---|
| stl/print/ | the parts in print orientation (the screw version, and the click-on version) |
| stl/print/resin/ | the resin parts (glued nuts), each one alone in its resin orientation |
| stl/screw/ | the screw version in the robot frame, with the screws and the inserts (desktop viewer: --stl stl/screw) |
| stl/plates/ | print plates for the FDM and the resin printer (3MF, STL), plates.json, resin_check.json |
| cad/*.step | the parts as STEP (from the mesh) |
| cad/assembly_step.zip | one STEP file with the robot, the platform and the add-on in place, with named and colored parts |
| stl/installed/, stl/models/ | the parts and the electronics in the robot frame |
| pod.py, motion.py, plates.py, render.py, docs.py | dimensions, build and checks; robot motion; print plates; pictures; this guide |

The printed parts, the drawings and this guide are CC BY 4.0, and the code is MIT (Jeremy Collins). The Pi Zero fit model is from github.com/PiSugar/PiSugar (GPL-3.0). The Petoi parts are from github.com/PetoiCamp/NonCodeFiles, without a stated license. LICENSE.md and ATTRIBUTION.md in the repository give the details.

