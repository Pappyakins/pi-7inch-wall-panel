#!/usr/bin/env python3
"""Preview renders for the Pi wall panel (matplotlib, no Blender needed).

  preview-front.png    - bezel (front-top) and backbox (back-top)
  preview-exploded.png - exploded stack: bezel / display PCB / Pi / backbox

Run with the doorbell venv.
"""
import os
import struct

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

BASE = os.path.dirname(os.path.abspath(__file__))
PETG = (0.16, 0.18, 0.23)
GREEN = (0.04, 0.32, 0.10)
BLUE = (0.07, 0.18, 0.52)
GRAY = (0.55, 0.55, 0.58)


def load_stl(path):
    with open(path, "rb") as f:
        data = f.read()
    n = struct.unpack("<I", data[80:84])[0]
    tris = np.empty((n, 3, 3))
    off = 84
    for i in range(n):
        v = struct.unpack("<12f", data[off:off + 48])
        off += 50
        tris[i] = [v[3:6], v[6:9], v[9:12]]
    return tris


def draw(ax, tris, color, alpha=1.0, zoff=0.0, flip_z=None):
    t = tris.copy()
    if flip_z is not None:                       # mirror about z=flip_z
        t[:, :, 2] = 2 * flip_z - t[:, :, 2]
        t = t[:, ::-1, :]                        # keep outward normals
    t[:, :, 2] += zoff
    # simple lambert shading from face normals
    e1 = t[:, 1] - t[:, 0]
    e2 = t[:, 2] - t[:, 0]
    n = np.cross(e1, e2)
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    n = n / np.maximum(ln, 1e-12)
    light = np.array([0.4, -0.5, 0.75])
    light /= np.linalg.norm(light)
    shade = 0.45 + 0.55 * np.abs(n @ light)
    cols = np.clip(np.array(color) * shade[:, None], 0, 1)
    pc = Poly3DCollection(t, facecolors=cols, edgecolors="none", alpha=alpha)
    ax.add_collection3d(pc)
    return t


def box_tris(x0, y0, z0, sx, sy, sz):
    c = np.array([[x0, y0, z0], [x0 + sx, y0, z0], [x0 + sx, y0 + sy, z0],
                  [x0, y0 + sy, z0], [x0, y0, z0 + sz], [x0 + sx, y0, z0 + sz],
                  [x0 + sx, y0 + sy, z0 + sz], [x0, y0 + sy, z0 + sz]])
    f = [(0, 1, 2), (0, 2, 3), (4, 6, 5), (4, 7, 6), (0, 4, 5), (0, 5, 1),
         (2, 6, 7), (2, 1, 6), (0, 3, 7), (0, 7, 4), (3, 2, 6), (3, 6, 7)]
    return np.array([[c[i], c[j], c[k]] for i, j, k in f])


def style(ax, title):
    ax.set_title(title, fontsize=11)
    ax.set_box_aspect((214, 130, 90))
    ax.set_xlim(0, 214)
    ax.set_ylim(0, 130)
    ax.set_zlim(0, 130)
    ax.set_xlabel("x mm")
    ax.set_ylabel("y mm")
    ax.view_init(elev=22, azim=-62)
    ax.grid(False)
    plt.setp(ax, xticks=[], yticks=[], zticks=[])


bezel = load_stl(os.path.join(BASE, "panel-bezel.stl"))
backbox = load_stl(os.path.join(BASE, "panel-backbox.stl"))

# ------------------------------------------------------- front views ---
fig = plt.figure(figsize=(16, 7))
ax = fig.add_subplot(121, projection="3d")
draw(ax, bezel, PETG)
style(ax, "bezel - front (prints face-down)")
ax = fig.add_subplot(122, projection="3d")
draw(ax, backbox, PETG)
style(ax, "backbox - outer back (prints face-down)")
fig.suptitle("Pi 7in wall panel - PETG, no supports", fontsize=13)
fig.tight_layout()
fig.savefig(os.path.join(BASE, "preview-front.png"), dpi=110)
print("wrote preview-front.png")

# -------------------------------------------------------- exploded ----
fig = plt.figure(figsize=(10, 12))
ax = fig.add_subplot(111, projection="3d")
draw(ax, bezel, PETG, zoff=0)                                   # bezel
draw(ax, box_tris(107 - 97, 65 - 55, 34, 194, 110, 1.6), GREEN)  # display PCB
draw(ax, box_tris(107 - 97, 65 - 55, 35.6, 150, 86, 10), GRAY,
     alpha=0.45)                                                # display guts
draw(ax, box_tris(107 - 42.5, 65 - 28, 52, 85, 56, 3), BLUE)     # Pi PCB
draw(ax, box_tris(107 - 42.5, 65 - 28, 55, 85, 56, 14), BLUE,
     alpha=0.45)                                                # Pi parts
draw(ax, backbox, PETG, zoff=78, flip_z=20)                     # backbox above
ax.set_title("exploded - bezel / display / Pi 3B+ / backbox", fontsize=11)
ax.set_box_aspect((214, 130, 170))
ax.set_xlim(0, 214)
ax.set_ylim(0, 130)
ax.set_zlim(0, 170)
ax.set_xlabel("x mm")
ax.set_ylabel("y mm")
ax.view_init(elev=18, azim=-62)
ax.grid(False)
plt.setp(ax, xticks=[], yticks=[], zticks=[])
fig.tight_layout()
fig.savefig(os.path.join(BASE, "preview-exploded.png"), dpi=110)
print("wrote preview-exploded.png")
