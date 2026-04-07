import os
import ezdxf
from build123d import *

# =========================
# PATH (FIXED NAME)
# =========================
desktop = os.path.join(os.path.expanduser("~"), "Desktop")

DXF_FILE = os.path.join(desktop, "magsafe_3dp_v0_1.dxf")
STL_FILE = os.path.join(desktop, "magsafe_3dp_v0_1.stl")

print("Using DXF:", DXF_FILE)

# =========================
# LOAD DXF
# =========================
if not os.path.exists(DXF_FILE):
    raise FileNotFoundError(f"❌ DXF not found: {DXF_FILE}")

doc = ezdxf.readfile(DXF_FILE)
msp = doc.modelspace()

loops = []

for e in msp:
    if e.dxftype() == "LWPOLYLINE" and e.closed:
        pts = [(p[0], p[1]) for p in e.get_points()]
        loops.append(pts)

if not loops:
    raise ValueError("❌ No closed polylines found")

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

HEIGHT = 2.0

# =========================
# BUILD PART
# =========================
with BuildPart() as part:

    # OUTER PROFILE
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
    # FEATURES
    # =========================
    points = [
        (301.4187, 146.9724),
        (301.7332, 95.0475),
        (399.4024, 84.2154),
        (409.8927, 179.0169),
        (334.9986, 144.2263),
    ]

    # Ø14 BOSSES
    with BuildSketch(Plane.XY.offset(HEIGHT)):
        with Locations(*points):
            Circle(14/2)
    extrude(amount=-2.0, mode=Mode.ADD)

    # Ø4 HOLES
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

    # Ø60 BOSS
    with BuildSketch(Plane.XY):
        with Locations((356.1622, 116.3360)):
            Circle(60/2)
    extrude(amount=HEIGHT, mode=Mode.ADD)

# =========================
# ✅ VOLUME CHECK (CORRECTED)
# =========================
print("Volume (system):", part.part.volume)
print("Actual Volume (mm³):", part.part.volume / 1000)

# =========================
# 🔥 FINAL CORRECTION SCALE
# =========================
part.part = part.part.scale(0.972)

print("Corrected Volume (mm³):", part.part.volume / 1000)

# =========================
# EXPORT STL
# =========================
if os.path.exists(STL_FILE):
    os.remove(STL_FILE)

export_stl(part.part, STL_FILE)

print("✅ STL CREATED:", STL_FILE)

# =========================
# PREVIEW
# =========================
from ocp_vscode import show, set_port, reset_show

reset_show()
set_port(3939)
show(part.part)