import csv
import os
import math
from build123d import *

# =========================
# PATH
# =========================
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
csv_path = os.path.join(desktop, "hex_v1_150.csv")
stl_path = os.path.join(desktop, "hex_v1_150.stl")

# =========================
# LOAD POINTS
# =========================
points = []
with open(csv_path, "r") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        points.append((float(row[0]), float(row[1])))

points = list(dict.fromkeys(points))
print(f"Loaded points: {len(points)}")

# =========================
# POINT INSIDE CHECK
# =========================
def inside(x, y, poly):
    c = False
    j = len(poly) - 1
    for i in range(len(poly)):
        if ((poly[i][1] > y) != (poly[j][1] > y)) and \
           (x < (poly[j][0] - poly[i][0]) * (y - poly[i][1]) /
            (poly[j][1] - poly[i][1] + 1e-9) + poly[i][0]):
            c = not c
        j = i
    return c

# =========================
# HEX FUNCTION
# =========================
def create_hex(cx, cy, side):
    pts = []
    for i in range(6):
        ang = math.radians(60 * i + 30)
        pts.append((cx + side * math.cos(ang),
                    cy + side * math.sin(ang)))
    return pts

# =========================
# BUILD
# =========================
with BuildPart() as part:

    # =========================
    # BASE PLATE
    # =========================
    with BuildSketch():
        with BuildLine():
            for i in range(len(points) - 1):
                Line(points[i], points[i + 1])
            Line(points[-1], points[0])
        make_face()

    extrude(amount=20)
    print("✅ Plate created")

    # =========================
    # HONEYCOMB (PERFECT GRID)
    # =========================
    side = 58

    spacing_x = 3 * side
    spacing_y = math.sqrt(3) * side

    xs = [p[0] for p in points]
    ys = [p[1] for p in points]

    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    with BuildSketch(Plane.XY):

        y = ymin
        row = 0

        while y < ymax:
            x_offset = 0 if row % 2 == 0 else 1.5 * side
            x = xmin + x_offset

            while x < xmax:

                hex_pts = create_hex(x, y, side)

                # 🔥 FULL HEX INSIDE CHECK
                valid = all(inside(px, py, points) for px, py in hex_pts)

                if valid:
                    Polygon(hex_pts)

                x += spacing_x

            y += spacing_y
            row += 1

    # =========================
    # CUT (SAFE & CLEAN)
    # =========================
    extrude(amount=25, mode=Mode.SUBTRACT)

    print("✅ Honeycomb cut applied")

# =========================
# EXPORT
# =========================
export_stl(part.part, stl_path)
print("✅ STL Generated:", stl_path)

# =========================
# VIEW
# =========================
try:
    from ocp_vscode import show
    show(part.part)
except Exception as e:
    print("Viewer issue:", e)
    print("👉 Open STL in Fusion/FreeCAD")