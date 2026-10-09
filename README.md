# Pi 7" Touchscreen Wall Panel

3D-printable wall-mount enclosure for the **official Raspberry Pi 7" touchscreen**
+ **Raspberry Pi 3B+**, built as a Home Assistant kiosk panel.

## Parts

| File | Description | Print orientation |
|---|---|---|
| `panel-bezel.stl` | Front bezel, 214 x 130 x 8 mm, window + display pocket + 4x M3 insert bosses | Front-face-down |
| `panel-backbox.stl` | Back box, 214 x 130 x 40 mm, 3 mm walls, open front | Back-face-down (open side up) |

Assembled outer dimensions: **214 x 130 x 48 mm**.

## Verified dimensions (mm)

| Item | Size |
|---|---|
| Display PCB (official 7") | 194 x 110, viewable 155 x 86 (centred) |
| Display depth incl. standoffs | ~20 |
| Pi 3B+ | 85 x 56 (mounts on the display's own 4x M2.5 standoffs) |
| Bezel outer | 214 x 130 x 8, corner r8 |
| Bezel pocket (back) | 195 x 111 x 4 deep (0.5 mm/side clearance) |
| Bezel window (front) | 160 x 91 (2.5 mm margin/side around viewable) |
| Insert bosses | 8 dia x 10 tall, corners inset 12; 4.1 dia blind hole, 7 deep, lead-in |
| Backbox outer | 214 x 130 x 40, 3 mm walls, corner r8 |
| Backbox screw holes | 3.2 clearance + 5.6 dia x 3.2 deep counterbore (outer face) |
| Keyholes (back) | 7 dia circle + 4 wide slot x 8 toward centre; mid-edges, inset 20 |
| Vent slots | 3 x 12, two rows, top and bottom walls |
| Power notch | 8 x 6, bottom wall, centred, at front edge |

## Print settings

- Material: **PETG** recommended (heat resistance near a wall / sun).
- Layer height: 0.2 mm. Walls: 3+ perimeters. Infill: 20% gyroid.
- **No supports needed.** Bezel prints front-face-down (flat first layer);
  backbox prints back-face-down with the open side up (straight walls).
- Both STLs sit on z=0 in their print orientation — drop straight onto the
  build plate.

## Assembly

1. Press 4x **M3 brass heat-set inserts** into the bezel bosses (soldering iron,
   4.1 mm holes with lead-in chamfer).
2. Seat the 7" display PCB into the bezel pocket (front of the display against
   the pocket floor, screen visible through the window).
3. Mount the Pi 3B+ to the display's own 4x M2.5 standoffs (official kit);
   connect the DSI ribbon and the GPIO jumper wires (5 V + GND) per the
   official display guide.
4. Feed a **5 V micro-USB cable** through the bottom-wall notch and plug it
   into the display's micro-USB port — this powers both boards.
5. Close the backbox over the assembly and fasten with 4x **M3x35** screws
   through the back-wall clearance holes into the bezel inserts. The
   socket-head counterbores leave the screw heads flush.
6. Wall mount: drive 4 screws into the wall (heads ~5 mm dia max) at the
   keyhole positions, offer the panel up, and let it seat. Keyholes are at
   mid-top, mid-bottom, mid-left and mid-right.

## Power wiring note

Single 5 V supply into the display's micro-USB powers both boards via the
official GPIO jumper wires (5 V and GND from display to Pi). Use a quality
5 V / 2.5 A+ supply — the Pi 3B+ plus display plus Wi-Fi can brown out on
weak chargers.

## Regenerating

```sh
~/workspace/doorbell-cam/.venv/bin/python generate_panel.py   # STLs
~/workspace/doorbell-cam/.venv/bin/python render_preview.py   # PNGs
```

Built with `manifold3d` CSG booleans (watertight solids).

## Fit notes / verify before printing

- The M3 insert bosses sit 2 mm inside the display PCB footprint at the
  corners and protrude 10 mm into the box. The display's own M2.5 corner
  standoffs live in the same region — test-fit the printed bezel against
  your physical display before printing the backbox. If a standoff collides
  with a boss, the boss positions can be moved outward in `generate_panel.py`
  (`BOSS_XY`).
- The 5.6 x 3.2 counterbore is deeper than the 3 mm back wall, so each screw
  hole has a 12 dia x 2 mm interior pad (local 5 mm thickness). This is
  intentional.
- Boss height (10 mm) is a design choice: it holds the 7 mm insert with
  3 mm of material below. Screws are M3x35 to span the 40 mm box depth.
