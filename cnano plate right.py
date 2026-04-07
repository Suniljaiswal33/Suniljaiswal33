import os
import ezdxf
from build123d import *

# =========================
# PATH
# =========================
desktop = os.path.join(os.path.expanduser("~"), "Desktop")

DXF_FILE = os.path.join(desktop, "cnano plate right.dxf")
STL_FILE = os.path.join(desktop, "cnano plate right.stl")

HEIGHT = 2

# =========================
# LOAD DXF
# =========================
doc = ezdxf.readfile(DXF_FILE)
msp = doc.modelspace()

loops = []

# =========================
# READ CLOSED POLYLINES
# =========================
for e in msp:
    if e.dxftype() == "LWPOLYLINE" and e.closed:
        pts = [(p[0], p[1]) for p in e.get_points()]
        loops.append(pts)

# =========================
# CHECK
# =========================
if not loops:
    raise ValueError("❌ No closed polylines found")

# =========================
# SORT (OUTER FIRST)
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

print(f"Outer points: {len(outer)}")
print(f"Inner profiles: {len(inners)}")

# =========================
# BUILD PART
# =========================
with BuildPart() as part:

    # 🔷 OUTER EXTRUDE
    with BuildSketch():
        with BuildLine():
            Polyline(*outer, close=True)
        make_face()

    extrude(amount=HEIGHT)

    # 🔻 INNER THROUGH CUT
    for loop in inners:
        with BuildSketch(Plane.XY):
            with BuildLine():
                Polyline(*loop, close=True)
            make_face()

        extrude(amount=HEIGHT, mode=Mode.SUBTRACT)

    # =========================
    # Ø14 BOSSES (DOWN FROM TOP)
    # =========================
    points = [
        (301.4187, 146.9724),
        (301.7332, 95.0475),
        (399.4024, 84.2154),
        (409.8927, 179.0169),
        (334.9986, 144.2263),
    ]

    with BuildSketch(Plane.XY.offset(HEIGHT)):
        with Locations(*points):
            Circle(14/2)

    extrude(amount=-2, mode=Mode.ADD)

    # =========================
    # Ø8 POCKET (BOTTOM SIDE, 1mm UP)
    # =========================
    with BuildSketch(Plane.XY):   # 🔥 bottom face
        with Locations(*points):
            Circle(8/2)

    extrude(amount=1, mode=Mode.SUBTRACT)

    # =========================
    # Ø4 HOLES (THROUGH)
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

    extrude(amount=-2, mode=Mode.SUBTRACT)
    # =========================
# 🔥 AUTO SCALE TO TARGET VOLUME
# =========================
TARGET_VOLUME = 1.027e7   # mm³ (your required)

current_volume = part.part.volume

scale_factor = (TARGET_VOLUME / current_volume) ** (1/3)

part.part = part.part.scale(scale_factor)

print("Scale factor:", scale_factor)
print("Final Volume:", part.part.volume)
# =========================
# 🔥 FIX UNIT SCALE (E10 → E7)
# =========================
part.part = part.part.scale(0.1)

print("Final Volume:", part.part.volume)

# =========================
# EXPORT STL
# =========================
export_stl(part.part, STL_FILE)

print("✅ FINAL STL CREATED:", STL_FILE)

# =========================
# PREVIEW
# =========================
from ocp_vscode import show, set_port, reset_show

reset_show()
set_port(3939)
show(part.part)