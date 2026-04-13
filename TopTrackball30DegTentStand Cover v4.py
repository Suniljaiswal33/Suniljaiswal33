from build123d import *
from ocp_vscode import show_object, Camera
import os

# =========================
FILE_NAME = "TopTrackball30DegTentStand Cover v4"
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
STL_FILE = os.path.join(desktop, FILE_NAME + ".stl")

# =========================
rect_points = [
    (1893.5759, 1263.2892),
    (2348.5759, 1263.2892),
    (2348.5759,  971.2892),
    (1893.5759,  971.2892)
]

with BuildPart() as part:
    with BuildSketch():
        with BuildLine():
            Polyline(rect_points, close=True)
        make_face()
    extrude(amount=60)
    fillet(part.edges().filter_by(Axis.Z), radius=20)

# =========================
# CUT FEATURE
# =========================
cut_points = [
    (2181.0759, 1263.2892),
    (2174.0049, 1260.3603),
    (2171.0759, 1253.2892),
    (2172.5442, 1244.0187),
    (2179.8627, 1232.0760),
    (2183.4424, 1229.0187),
    (2194.0942, 1224.2080),
    (2201.0759, 1223.2892),
    (2263.5759, 1223.2892),
    (2263.5759, 1011.2892),
    (1978.5759, 1011.2892),
    (1978.5759, 1223.2892),
    (2041.0759, 1223.2892),
    (2054.6956, 1226.5590),
    (2062.2891, 1232.0760),
    (2066.5763, 1237.6626),
    (2070.7066, 1248.5962),
    (2070.7352, 1255.8774),
    (2067.1115, 1261.1548),
    (2061.0759, 1263.2892)
]

with BuildLine() as ln:
    Polyline(cut_points, close=True)

cut_face = make_face(ln.wire())
top_z = part.part.bounding_box().max.Z
cut_face = cut_face.moved(Location((0, 0, top_z)))
cut_solid = extrude(cut_face, amount=-42)
part.part -= cut_solid

# =========================
# RECTANGULAR FEATURE 1
# =========================
RECT_W  = 36.0
RECT_L  = 40.0
RECT_H  = 26.5
RECT_CZ = 18.0 + RECT_H / 2

rect_box1 = Box(RECT_W, RECT_L, RECT_H)
rect_box1 = rect_box1.moved(Location((1996.5759, 1117.2892, RECT_CZ)))
part.part = part.part.fuse(rect_box1)

# =========================
# RECTANGULAR FEATURE 2
# =========================
rect_box2 = Box(RECT_W, RECT_L, RECT_H)
rect_box2 = rect_box2.moved(Location((2245.5759, 1117.2892, RECT_CZ)))
part.part = part.part.fuse(rect_box2)

# =========================
# COUNTERSINK HOLES
# 58mm dia bottom, 32mm dia top
# =========================
CS_OUTER_R = 58 / 2
CS_INNER_R = 32 / 2
CS_DEPTH   = CS_OUTER_R - CS_INNER_R

top_z = part.part.bounding_box().max.Z

cs_points = [
    (1936.2691, 1117.2892),
    (2305.8827, 1117.2892),
]

for cx, cy in cs_points:
    cs_cone = Cone(
        bottom_radius = CS_OUTER_R,
        top_radius    = CS_INNER_R,
        height        = CS_DEPTH
    )
    cs_cone = cs_cone.moved(Location((cx, cy, CS_DEPTH / 2)))
    part.part -= cs_cone

    cs_hole = Cylinder(
        radius = CS_INNER_R,
        height = top_z + 2
    )
    cs_hole = cs_hole.moved(Location((cx, cy, (top_z + 2) / 2 - 1)))
    part.part -= cs_hole

# =========================
# NEW RECTANGULAR FEATURE (200MM EXTRUDE)
# =========================
new_feat_pts = [
    (2348.5759,  971.2892),
    (2348.5759, 1263.2892),
    (2248.5759, 1263.2892),
    (2248.5759,  971.2892)
]

new_wire  = Wire.make_polygon([Vector(x, y, 0) for x, y in new_feat_pts])
new_face  = Face(new_wire)
new_solid = extrude(new_face, amount=-200)
part.part = part.part.fuse(new_solid)

# =========================
# TRIANGULAR CUT 1 - RIGHT SIDE FACE
# =========================
tri_v1 = Vector(2348.5759, 1145.2892, -200)
tri_v2 = Vector(2348.5759, 1263.2892, -200)
tri_v3 = Vector(2348.5759, 1263.2892,    0)

tri_wire  = Wire.make_polygon([tri_v1, tri_v2, tri_v3])
tri_face  = Face(tri_wire)
tri_solid = extrude(tri_face, amount=-500)
part.part -= tri_solid

# =========================
# TRIANGULAR CUT 2 - RIGHT SIDE FACE
# =========================
tri2_v1 = Vector(2348.5759,  971.2892, -100)
tri2_v2 = Vector(2348.5759,  971.2892, -200)
tri2_v3 = Vector(2348.5759, 1145.2892, -200)

tri2_wire  = Wire.make_polygon([tri2_v1, tri2_v2, tri2_v3])
tri2_face  = Face(tri2_wire)
tri2_solid = extrude(tri2_face, amount=-500)
part.part -= tri2_solid

# =========================
# TRIANGULAR ADD - RIGHT SIDE FACE
# =========================
tri3_v1 = Vector(2348.5759, 927.4872,  -76.364)
tri3_v2 = Vector(2348.5759, 971.2892,    0)
tri3_v3 = Vector(2348.5759, 971.2892, -100)

tri3_wire  = Wire.make_polygon([tri3_v1, tri3_v2, tri3_v3])
tri3_face  = Face(tri3_wire)
tri3_solid = extrude(tri3_face, amount=100)
part.part  = part.part.fuse(tri3_solid)

# =========================
# FILLET EDGE 17MM
# From (2348.5759, 1263.2892, 0) to (2348.5759, 1145.2892, -200)
# =========================
for edge in part.part.edges():
    verts = edge.vertices()
    pts = [(round(v.X, 1), round(v.Y, 1), round(v.Z, 1)) for v in verts]
    if (2348.6, 1263.3, 0.0) in pts and (2348.6, 1145.3, -200.0) in pts:
        try:
            part.part = part.part.fillet(17, [edge])
            print("Edge 1 filleted 17mm OK!")
        except Exception as e:
            print(f"Fillet 1 failed: {e}")
        break

# =========================
# FILLET EDGE 5MM
# From (2248.5759, 1145.2892, -200) to (2248.5759, 1263.2892, 0)
# =========================
for edge in part.part.edges():
    verts = edge.vertices()
    found = 0
    for v in verts:
        if abs(v.X - 2248.5759) < 1.0 and abs(v.Y - 1145.2892) < 1.0 and abs(v.Z - 200.0) < 1.0:
            found += 1
        if abs(v.X - 2248.5759) < 1.0 and abs(v.Y - 1263.2892) < 1.0 and abs(v.Z - 0.0) < 1.0:
            found += 1
    if found == 2:
        try:
            part.part = part.part.fillet(5, [edge])
            print("Edge 2 filleted 5mm OK!")
        except Exception as e:
            print(f"Fillet 2 failed: {e}")
        break

# =========================
# THROUGH HOLE - 58mm DIA DOWNWARD
# Start Z = -46.3344, cut downward
# =========================
cs_hole = Cylinder(
    radius = 58 / 2,
    height = 210
)
cs_hole = cs_hole.moved(Location((
    2305.8827,
    1117.2892,
    -46.3344 - 100 / 2
)))
part.part -= cs_hole

# =========================
# AUTO SCALE
# =========================
TARGET_VOLUME = 8.795e6

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
export_stl(part.part, STL_FILE)
print("STL saved:", STL_FILE)

show_object(part.part, reset_camera=Camera.RESET)