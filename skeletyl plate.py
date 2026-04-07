import os
import ezdxf
from build123d import *

# =========================
# PATH
# =========================
desktop = os.path.join(os.path.expanduser("~"), "Desktop")

DXF_FILE = os.path.join(desktop, "skeletyl plate.dxf")
STL_FILE = os.path.join(desktop, "skeletyl plate.stl")

HEIGHT = 20

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

print(f"Outer points: {len(outer)}")
print(f"Inner profiles: {len(inners)}")

# =========================
# BUILD PART
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

        extrude(amount=HEIGHT, mode=Mode.SUBTRACT)

    # =========================
    # Ø105 POCKET
    # =========================
    pocket_points = [
        (1693.7718, 1416.8435),
        (2339.9289, 1246.2798),
        (2327.5291, 740.4890),
        (1383.8464, 622.1634),
        (1239.9289, 1546.2798),
    ]

    with BuildSketch(Plane.XY.offset(HEIGHT)):
        with Locations(*pocket_points):
            Circle(105 / 2)

    extrude(amount=-10, mode=Mode.SUBTRACT)

   # =========================
# 🔥 TAPERED HOLE (Ø80 → Ø40) FINAL FIX
# =========================
taper_points = [
    (1349.9289, 1116.2798),
    (1773.9003, 1336.3225),
    (2199.9289, 666.2798),
    (2349.9386, 1356.0302),
]

DEPTH = 50

for pt in taper_points:

    # 🔷 CREATE CONE SOLID
    cone = Cone(
        bottom_radius=40/2,
        top_radius=80/2,
        height=DEPTH
    )

    # 🔷 POSITION CONE (TOP FACE ALIGN)
    cone = cone.move(Location((pt[0], pt[1], HEIGHT)))

    # 🔥 SUBTRACT FROM PART
    part.part = part.part.cut(cone)

# =========================
# AUTO SCALE
# =========================
TARGET_VOLUME = 1.128e7

current_volume = part.part.volume
scale_factor = (TARGET_VOLUME / current_volume) ** (1/3)

part.part = part.part.scale(scale_factor)

print("Scale factor:", scale_factor)
print("Volume after scale:", part.part.volume)

# =========================
# UNIT FIX
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