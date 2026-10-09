#!/usr/bin/env python3
"""Generate STL files for the Pi 7" touchscreen wall-panel enclosure.

BEZEL (214 x 130 x 8, frame z=0 at FRONT outer face, prints front-face-down):
  - Front window 160 x 91, centred (viewable 155x86 + 2.5 mm/side), cut through.
  - Back pocket 195 x 111 x 4 deep (display PCB 194x110 + 0.5 mm/side).
  - 4x M3 brass heat-set insert bosses: 8 mm dia, 10 mm tall, on the back face
    at corners inset 12 mm from edges. 4.1 mm dia blind hole, 7 mm deep,
    with lead-in chamfer (doorbell-case pattern).

BACKBOX (214 x 130 x 40, frame z=0 at OUTER back face, prints back-face-down,
open side up):
  - 3 mm walls, open front mates to the bezel.
  - 4x M3 clearance holes (3.2 mm) through the back face, aligned with the
    bezel bosses; 5.6 mm dia x 3.2 deep socket-head counterbores on the outer
    back face (doorbell-lid v3.4 pattern). Because the wall is only 3 mm,
    each hole gets a 12 mm dia x 2 mm interior pad (local 5 mm thickness).
  - 4x keyhole wall-mount slots on the back face: 7 mm dia circle + 4 mm wide
    slot extending 8 mm toward the panel centre; at mid-top, mid-bottom,
    mid-left, mid-right, inset 20 mm from edges.
  - Ventilation: two rows of slots (3 wide x 12 long) on top and bottom walls.
  - Power cable notch: 8 wide x 6 deep on the bottom wall, centred, at the
    front (mating) edge.

Assembly: display PCB sits in the bezel pocket (front at pocket floor);
Pi mounts on the display's own M2.5 standoffs. M3x35 screws through the
backbox back wall into the bezel inserts. Single 5 V micro-USB into the
display powers both (official jumper-wire setup).

Run with the doorbell venv:  ~/workspace/doorbell-cam/.venv/bin/python generate_panel.py
Outputs: panel-bezel.stl, panel-backbox.stl (binary STL, mm).
"""
import os
import struct

import numpy as np
from manifold3d import CrossSection, Manifold, set_circular_segments

BASE = os.path.dirname(os.path.abspath(__file__))
set_circular_segments(96)

# ---------------------------------------------------------------- dims ---
W, H = 214.0, 130.0          # outer silhouette
CX, CY = W / 2.0, H / 2.0    # panel centre (107, 65)

# Bezel
BEZ_T = 8.0                  # bezel thickness
WIN = (160.0, 91.0)          # front window (viewable 155x86 + 2.5/side)
POCK = (195.0, 111.0, 4.0)   # back pocket (PCB 194x110 + 0.5/side), depth
BOSS_XY = [(12, 12), (202, 12), (12, 118), (202, 118)]  # inset 12 from edges
BOSS_R, BOSS_H = 4.0, 10.0   # 8 mm dia, 10 mm tall (holds 7 mm insert hole)
INS_R, INS_D = 2.05, 7.0     # 4.1 mm dia blind hole, 7 mm deep

# Backbox
BOX_D = 40.0                 # depth
WALL = 3.0                   # wall thickness
CLR_R = 1.6                  # M3 clearance 3.2 mm dia
CB_R, CB_D = 2.8, 3.2        # socket-head counterbore 5.6 dia x 3.2 deep
PAD_R, PAD_H = 6.0, 2.0      # interior pad under each screw hole
KEY_R = 3.5                  # keyhole circle 7 mm dia
KEY_INSET = 20.0             # keyhole centres inset 20 from edges
VENT = (12.0, 3.0)           # vent slots: 12 long (X) x 3 wide (Z)
NOTCH = (8.0, 6.0)           # power notch: 8 wide (X) x 6 deep (Z)


def rprism(w, h, r, cx, cy, z0, depth):
    """Rounded-rectangle prism centred on (cx, cy), from z0 up depth."""
    cs = CrossSection.square([w - 2 * r, h - 2 * r], center=True).offset(r)
    return cs.extrude(depth).translate([cx, cy, z0])


def cyl(r, x, y, z0, depth):
    return Manifold.cylinder(depth, r, circular_segments=96).translate([x, y, z0])


def cone(r0, r1, h, x, y, z0):
    """Truncated cone, radius r0 at bottom to r1 at top."""
    return Manifold.cylinder(h, r1, r0, circular_segments=96).translate([x, y, z0])


def box(x, y, z, sx, sy, sz):
    return Manifold.cube([sx, sy, sz]).translate([x, y, z])


def write_stl(solid, path):
    mesh = solid.to_mesh()
    verts = np.asarray(mesh.vert_properties, dtype=np.float64)[:, :3]
    tris = np.asarray(mesh.tri_verts, dtype=np.int64)
    assert solid.volume() > 0, "empty solid: %s" % path
    with open(path, "wb") as f:
        f.write(b"\x00" * 80)
        f.write(struct.pack("<I", len(tris)))
        for a, b, c in tris:
            p, q, s = verts[a], verts[b], verts[c]
            n = np.cross(q - p, s - p)
            ln = np.linalg.norm(n)
            n = n / ln if ln > 0 else n
            f.write(struct.pack(
                "<12f", n[0], n[1], n[2],
                p[0], p[1], p[2], q[0], q[1], q[2], s[0], s[1], s[2]))
            f.write(struct.pack("<H", 0))
    bb = solid.bounding_box()  # (minx, miny, minz, maxx, maxy, maxz)
    sx, sy, sz = bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2]
    print("wrote %s  %d tris  volume %.0f mm^3  bbox [%.1f x %.1f x %.1f]" % (
        os.path.basename(path), len(tris), solid.volume(), sx, sy, sz))
    return solid


# ================================================================ bezel ==
def build_bezel():
    bz = rprism(W, H, 8.0, CX, CY, 0.0, BEZ_T)          # outer shell
    # pocket on back face: 195x111, 4 deep -> z 4..8
    bz -= rprism(POCK[0], POCK[1], 2.0, CX, CY, BEZ_T - POCK[2], POCK[2] + 1.0)
    # window through the front: 160x91
    bz -= rprism(WIN[0], WIN[1], 2.0, CX, CY, -1.0, BEZ_T + 2.0)
    for bx, by in BOSS_XY:                             # insert bosses
        bz += cyl(BOSS_R, bx, by, BEZ_T, BOSS_H)
    for bx, by in BOSS_XY:                             # 4.1 blind holes, 7 deep
        top = BEZ_T + BOSS_H
        bz -= cyl(INS_R, bx, by, top - INS_D, INS_D + 1.0)
        bz -= cone(INS_R, INS_R + 0.55, 1.5, bx, by, top - 1.5)  # lead-in
    return bz


# ============================================================== backbox ==
def keyhole(x, y, dx, dy):
    """7 mm circle + 4 mm wide slot extending 8 mm toward (dx, dy) unit dir."""
    parts = [cyl(KEY_R, x, y, -1.0, WALL + 2.0)]
    if dx != 0:                                        # horizontal slot
        x0 = min(x, x + dx * 8.0)
        parts.append(box(x0, y - 2.0, -1.0, 8.0, 4.0, WALL + 2.0))
    else:                                              # vertical slot
        y0 = min(y, y + dy * 8.0)
        parts.append(box(x - 2.0, y0, -1.0, 4.0, 8.0, WALL + 2.0))
    s = parts[0]
    for p in parts[1:]:
        s += p
    return s


def build_backbox():
    bx = rprism(W, H, 8.0, CX, CY, 0.0, BOX_D)          # outer shell
    bx -= rprism(W - 2 * WALL, H - 2 * WALL, 5.0, CX, CY,
                 WALL, BOX_D)                          # hollow, open front
    for sx, sy in BOSS_XY:
        bx += cyl(PAD_R, sx, sy, WALL, PAD_H)           # interior screw pads
        bx -= cyl(CLR_R, sx, sy, -1.0, WALL + PAD_H + 1.0)   # M3 clearance
        bx -= cyl(CB_R, sx, sy, -1.0, CB_D + 1.0)       # socket-head c'bore
    # keyholes: mid-top/bottom/left/right, inset 20, slots toward centre
    bx -= keyhole(CX, H - KEY_INSET, 0, -1)             # top, slot down
    bx -= keyhole(CX, KEY_INSET, 0, +1)                # bottom, slot up
    bx -= keyhole(KEY_INSET, CY, +1, 0)                # left, slot right
    bx -= keyhole(W - KEY_INSET, CY, -1, 0)            # right, slot left
    # vent slots: two rows (z=12, 24) on top (y=127..130) and bottom (y=0..3)
    for zrow in (12.0, 24.0):
        for xc in (30, 50, 70, 90, 124, 144, 164, 184):
            bx -= box(xc - VENT[0] / 2, -1.0, zrow - VENT[1] / 2,
                      VENT[0], WALL + 2.0, VENT[1])            # bottom wall
            bx -= box(xc - VENT[0] / 2, H - WALL - 1.0, zrow - VENT[1] / 2,
                      VENT[0], WALL + 2.0, VENT[1])            # top wall
    # power notch: bottom wall, centred, at the front (mating) edge
    bx -= box(CX - NOTCH[0] / 2, -1.0, BOX_D - NOTCH[1],
              NOTCH[0], WALL + 2.0, NOTCH[1] + 1.0)
    return bx


# =========================================================== validation ==
def validate():
    # window fully clears the 155x86 viewable area (both centred)
    assert WIN[0] >= 155.0 + 2 * 2.5 - 1e-9 and WIN[1] >= 86.0 + 2 * 2.5 - 1e-9
    # pocket fully contains the 194x110 PCB with clearance
    assert POCK[0] - 194.0 >= 1.0 - 1e-9 and POCK[1] - 110.0 >= 1.0 - 1e-9
    # pocket depth holds the PCB (1.6 mm) with room
    assert POCK[2] >= 2.0
    # bosses clear the pocket? (flagged: 1.5 mm overlap at corners, see README)
    # keyholes clear of screw holes: min distance check
    keys = [(CX, H - KEY_INSET), (CX, KEY_INSET),
            (KEY_INSET, CY), (W - KEY_INSET, CY)]
    for kx, ky in keys:
        for sx, sy in BOSS_XY:
            d = ((kx - sx) ** 2 + (ky - sy) ** 2) ** 0.5
            assert d > KEY_R + 4.0 + PAD_R, (kx, ky, sx, sy)
    print("validation checks passed")


if __name__ == "__main__":
    validate()
    bezel = write_stl(build_bezel(), os.path.join(BASE, "panel-bezel.stl"))
    backbox = write_stl(build_backbox(), os.path.join(BASE, "panel-backbox.stl"))
    # bbox must match spec within 0.5 mm
    bb = bezel.bounding_box()
    assert abs((bb[3] - bb[0]) - W) < 0.5
    assert abs((bb[4] - bb[1]) - H) < 0.5
    assert abs((bb[5] - bb[2]) - (BEZ_T + BOSS_H)) < 0.5
    bb = backbox.bounding_box()
    assert abs((bb[3] - bb[0]) - W) < 0.5
    assert abs((bb[4] - bb[1]) - H) < 0.5
    assert abs((bb[5] - bb[2]) - BOX_D) < 0.5
    print("bbox checks passed: bezel 214x130x%.0f, backbox 214x130x%.0f"
          % (BEZ_T + BOSS_H, BOX_D))
