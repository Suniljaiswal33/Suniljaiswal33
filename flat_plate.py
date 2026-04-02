import csv
import os
from build123d import *

# =========================
# PATH
# =========================
script_path = os.path.abspath(__file__)
base_name = os.path.splitext(os.path.basename(script_path))[0]

CSV_FILE = "/Users/softage/Desktop/high_accuracy_points_with_id.csv"
OUTPUT_FILE = f"/Users/softage/Desktop/{base_name}.stl"

HEIGHT = 100
THICKNESS = 40

# =========================
# HEX SETTINGS
# =========================
HEX_SIDE = 57.74
WALL = 80

dx = 2*HEX_SIDE + WALL
dy = (3**0.5)*(HEX_SIDE + WALL/2)

# 🔥 FINAL FIX (NO WALL BREAK)
SAFE_OFFSET = HEX_SIDE + WALL

# =========================
# READ CSV
# =========================
raw_points = []

with open(CSV_FILE, "r") as f:
    reader = csv.DictReader(f)
    reader.fieldnames = [c.strip() for c in reader.fieldnames]

    sample = next(reader)
    keys = list(sample.keys())

    x_key = [k for k in keys if "x" in k.lower()][0]
    y_key = [k for k in keys if "y" in k.lower()][0]

    rows = [sample] + list(reader)

    for row in rows:
        try:
            raw_points.append((float(row[x_key]), float(row[y_key])))
        except:
            continue

# =========================
# CLEAN + ORDER
# =========================
unique = []
tol = 1e-4

for p in raw_points:
    if not any(abs(p[0]-q[0]) < tol and abs(p[1]-q[1]) < tol for q in unique):
        unique.append(p)

unused = unique.copy()
points = [unused.pop(0)]

while unused:
    last = points[-1]
    next_pt = min(unused, key=lambda p: (p[0]-last[0])**2 + (p[1]-last[1])**2)
    points.append(next_pt)
    unused.remove(next_pt)

# =========================
# BUILD
# =========================
with BuildPart() as part:

    # ---- OUTER SOLID ----
    with BuildSketch() as sk:
        with BuildLine():
            Polyline(*points, close=True)
        make_face()

    base_face = sk.face()
    extrude(amount=HEIGHT)

    # =========================
    # SHELL (UNCHANGED)
    # =========================
    outer_wire = base_face.outer_wire()
    outer_wire = Wire.combine(outer_wire.edges())[0]

    inner_wires = offset(outer_wire, amount=-THICKNESS)
    wires_list = inner_wires if isinstance(inner_wires, list) else [inner_wires]
    base_inner_wire = wires_list[0]

    # hollow
    for w in wires_list:
        with BuildSketch(Plane.XY):
            add(w)
            make_face()
        extrude(amount=HEIGHT, mode=Mode.SUBTRACT)

    # bottom fill
    for w in wires_list:
        with BuildSketch(Plane.XY):
            add(w)
            make_face()
        extrude(amount=THICKNESS)

    # =========================
    # 🔥 SAFE HEX PATTERN
    # =========================
    safe_inner = offset(base_inner_wire, amount=-SAFE_OFFSET)
    safe_list = safe_inner if isinstance(safe_inner, list) else [safe_inner]

    bb = safe_list[0].bounding_box()
    width = bb.max.X - bb.min.X
    height = bb.max.Y - bb.min.Y

    nx = max(1, int(width / dx))
    ny = max(1, int(height / dy))

    top_face = part.faces().sort_by(Axis.Z)[-1]

    with BuildSketch(top_face):

        # restrict area
        for w in safe_list:
            add(w)

        # main grid
        with GridLocations(dx, dy, nx, ny):
            RegularPolygon(radius=HEX_SIDE, side_count=6, rotation=30)

        # staggered grid
        with Locations((dx/2, dy/2)):
            with GridLocations(dx, dy, nx, ny):
                RegularPolygon(radius=HEX_SIDE, side_count=6, rotation=30)

    # =========================
    # CUT
    # =========================
    extrude(amount=-HEIGHT, mode=Mode.SUBTRACT)

# =========================
# EXPORT
# =========================
export_stl(part.part, OUTPUT_FILE)

print("✅ FINAL NO-BREAK STL CREATED:", OUTPUT_FILE)

# =========================
# PREVIEW
# =========================
from ocp_vscode import show, set_port, reset_show

reset_show()
set_port(3939)
show(part)