import os
import ezdxf
from build123d import *

# =========================
# PATH
# =========================
desktop = os.path.join(os.path.expanduser("~"), "Desktop")

DXF_FILE = os.path.join(desktop, "plate _flush.dxf")
STL_FILE = os.path.join(desktop, "plate_flush.stl")

HEIGHT = 20
WALL = 10.0

# 🔥 FIXED SCALE
SCALE_FACTOR = 0.09749

# =========================
# LOAD DXF
# =========================
doc = ezdxf.readfile(DXF_FILE)
msp = doc.modelspace()

loops = []

for e in msp:
    if e.dxftype() == "LWPOLYLINE":
        pts = [(p[0], p[1]) for p in e.get_points()]
        if len(pts) > 3:
            if pts[0] != pts[-1]:
                pts.append(pts[0])
            loops.append(pts)

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

print("Outer:", len(outer))
print("Inner:", len(inners))

# =========================
# BUILD PLATE
# =========================
edges = [Line(outer[i], outer[i+1]) for i in range(len(outer)-1)]
outer_wire = Wire.combine(edges)[0]
outer_face = Face(outer_wire)

plate = extrude(outer_face, amount=HEIGHT)

# CUTS
for loop in inners:
    try:
        edges = [Line(loop[i], loop[i+1]) for i in range(len(loop)-1)]
        wire = Wire.combine(edges)[0]

        face = Face(wire)
        cut = extrude(face, amount=HEIGHT + 5)

        plate = plate - cut

    except:
        print("Skip bad loop")

# =========================
# WALL
# =========================
offset_result = outer_wire.offset_2d(WALL)

if isinstance(offset_result, list):
    offset_wire = offset_result[0]
else:
    offset_wire = offset_result

outer_offset_face = Face(offset_wire)

wall_face = outer_offset_face - outer_face
wall_solid = extrude(wall_face, amount=HEIGHT)

final_part = plate + wall_solid

# =========================
# 🔥 FIXED SCALE (CENTER BASED)
# =========================
bbox = final_part.bounding_box()

center = Vector(
    (bbox.min.X + bbox.max.X)/2,
    (bbox.min.Y + bbox.max.Y)/2,
    (bbox.min.Z + bbox.max.Z)/2
)

final_part = final_part.translate(-center)
final_part = scale(final_part, SCALE_FACTOR)
final_part = final_part.translate(center)

# =========================
# EXPORT
# =========================
if os.path.exists(STL_FILE):
    os.remove(STL_FILE)

export_stl(final_part, STL_FILE)

print("✅ FINAL PART READY")

# =========================
# VIEW
# =========================
from ocp_vscode import show
show(final_part)