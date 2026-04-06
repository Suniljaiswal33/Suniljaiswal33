import os
import ezdxf
from build123d import *

# =========================
# PATH
# =========================
desktop = os.path.join(os.path.expanduser("~"), "Desktop")

DXF_FILE = os.path.join(desktop, "alien_flush_v1_2.dxf")
STL_FILE = os.path.join(desktop, "alien_flush_v1_2.stl")

HEIGHT = 5

# =========================
# LOAD DXF
# =========================
doc = ezdxf.readfile(DXF_FILE)
msp = doc.modelspace()

loops = []

for e in msp:
    if e.dxftype() == "LWPOLYLINE" and e.closed:
        pts = [(p[0], p[1]) for p in e.get_points()]
        loops.append(pts)

if not loops:
    raise ValueError("No closed polylines found")

# =========================
# SORT
# =========================
def area(poly):
    return abs(sum(
        poly[i][0]*poly[(i+1)%len(poly)][1] -
        poly[(i+1)%len(poly)][0]*poly[i][1]
        for i in range(len(poly))
    ) / 2)

loops.sort(key=area, reverse=True)

outer = loops[0]
inners = loops[1:]

# =========================
# BUILD
# =========================
with BuildPart() as part:

    # OUTER
    with BuildSketch():
        with BuildLine():
            Polyline(*outer, close=True)
        make_face()

    extrude(amount=HEIGHT)

    # INNER CUTS
    for loop in inners:
        with BuildSketch(Plane.XY):
            with BuildLine():
                Polyline(*loop, close=True)
            make_face()

        extrude(amount=HEIGHT + 5, mode=Mode.SUBTRACT)

    # =========================
    # FEATURE LOCATIONS
    # =========================
    points = [
        (301.4187, 146.9724),
        (301.7332, 95.0475),
        (399.4024, 84.2154),
        (409.8927, 179.0169),
        (334.9986, 144.2263),
    ]

    # =========================
    # Ø14 BOSSES (5mm DOWN)
    # =========================
    with BuildSketch(Plane.XY.offset(HEIGHT)):
        with Locations(*points):
            Circle(14/2)

    extrude(amount=-5, mode=Mode.ADD)

    # =========================
    # Ø8 POCKET (3mm DOWN)
    # =========================
    with BuildSketch(Plane.XY.offset(HEIGHT)):
        with Locations(*points):
            Circle(8/2)

    extrude(amount=-3, mode=Mode.SUBTRACT)

    # =========================
    # Ø4 HOLES
    # =========================
    hole_points = [
        (300.9860, 157.9938),
        (315.9870, 89.0187),
        (400.9870, 134.0187),
        (372.9870, 188.0187),
    ]

    with BuildSketch(Plane.XY.offset(HEIGHT)):
        with Locations(*hole_points):
            Circle(4/2)

    extrude(amount=-5, mode=Mode.SUBTRACT)

# =========================
# 🔥 SCALE (FINAL STEP)
# =========================
SCALE_FACTOR = 0.694
part.part = part.part.scale(SCALE_FACTOR)

# =========================
# EXPORT
# =========================
export_stl(part.part, STL_FILE)

print("✅ FINAL STL CREATED (SCALED):", STL_FILE)

# =========================
# PREVIEW
# =========================
from ocp_vscode import show, set_port, reset_show

reset_show()
set_port(3939)
show(part.part)