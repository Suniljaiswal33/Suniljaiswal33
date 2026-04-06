import os
import ezdxf
from build123d import *

# =========================
# PATH
# =========================
desktop = os.path.join(os.path.expanduser("~"), "Desktop")

DXF_FILE = os.path.join(desktop, "alien_v2_185.dxf")
STL_FILE = os.path.join(desktop, "alien_v2_185.stl")

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
show(part)