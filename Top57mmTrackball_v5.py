from build123d import *
import math, os

STL_FILE = os.path.expanduser("~/Desktop/Top57mmTrackball_v5.stl")

R_OUTER = 654 / 2  # 327mm
R_INNER = 584 / 2  # 292mm
ANG     = 45

ang_rad = math.radians(ANG)

# Profile: annular sector in YZ plane from -45° to +45°
# Y = R*cos(angle), Z = R*sin(angle)
p1 = (R_INNER * math.cos(-ang_rad), R_INNER * math.sin(-ang_rad))  # inner -45°
p2 = (R_OUTER * math.cos(-ang_rad), R_OUTER * math.sin(-ang_rad))  # outer -45°
p3 = (R_OUTER * math.cos( ang_rad), R_OUTER * math.sin( ang_rad))  # outer +45°
p4 = (R_INNER * math.cos( ang_rad), R_INNER * math.sin( ang_rad))  # inner +45°

# Build profile on YZ plane
verts = [
    Vector(0, p1[0], p1[1]),
    Vector(0, p2[0], p2[1]),
    Vector(0, p3[0], p3[1]),
    Vector(0, p4[0], p4[1]),
]

# Arcs in YZ plane
with BuildSketch(Plane.YZ) as sk:
    with BuildLine():
        Line((p1[0], p1[1]), (p2[0], p2[1]))          # -45° radial line
        RadiusArc((p2[0], p2[1]), (p3[0], p3[1]), -R_OUTER)  # outer arc
        Line((p3[0], p3[1]), (p4[0], p4[1]))          # +45° radial line
        RadiusArc((p4[0], p4[1]), (p1[0], p1[1]), R_INNER)   # inner arc
    make_face()

face  = sk.sketch.face()

# Revolve axis: -45° line in YZ plane through origin
rev_axis = Axis(
    origin    = Vector(0, 0, 0),
    direction = Vector(0, math.cos(-ang_rad), math.sin(-ang_rad))
)

result = Solid.revolve(face, 360, rev_axis)
# Step 2: Extrude from Z=-337 to Z=-231 (dome bottom)
step_pts = [
    (  0.0,    142.4051), (-206.9742, 142.4051), (-221.9645, 137.5301),
    (-225.92,  131.5969), (-227.5152, 123.1474), (-227.5152,-128.7216),
    (-226.1352,-135.7436), (-221.814, -142.4955), (-215.6023,-147.0868),
    (-207.2299,-149.2474), (  0.373,  -149.2474), (  0.0,    142.4051),
]

wire_s  = Wire.make_polygon([Vector(x, y, -337) for x, y in step_pts], close=True)
solid_s = Solid.extrude(Face(wire_s), Vector(0, 0, 110))  # Z=-337 to Z=-231

solid_s_mirror = solid_s.mirror(Plane.YZ)

result = result.fuse(solid_s)
try:    result = result.solids()[0]
except: pass
result = result.fuse(solid_s_mirror)
try:    result = result.solids()[0]
except: pass

print(f"✅ Step 2 | Volume: {result.volume:.4e}")
print(f"✅ Step 2 | Volume: {result.volume:.4e}")

print(f"Volume  : {result.volume:.4e} mm³")
bb = result.bounding_box()
print(f"X: {bb.min.X:.2f} to {bb.max.X:.2f}")
print(f"Y: {bb.min.Y:.2f} to {bb.max.Y:.2f}")
print(f"Z: {bb.min.Z:.2f} to {bb.max.Z:.2f}")
# Step 3: Close boundary on YZ plane offset X=227, extrude 40mm
step3_pts = [
    (-268.9459, -334.2047), ( 281.6327, -334.2047), ( 281.6327,  -30.2193),
    ( 232.2476,   17.0186), ( 232.2476,  -23.6812), ( 221.3615,  -69.7703),
    ( 204.8389, -107.1634), ( 173.5331, -155.8613), ( 136.14,   -189.776),
    (  97.8774, -208.9073), (  32.6569, -229.7779), ( -39.5205, -229.7779),
    ( -86.4792, -217.6034), (-116.9154, -202.8201), (-132.9468, -202.8201),
    (-143.5761, -208.8205), (-148.3898, -215.3504), (-268.9459, -215.3504),
    (-268.9459, -334.2047),
]

# Points on plane X=227 (YZ offset 227mm)
# First coord = Y, second = Z
wire3  = Wire.make_polygon([Vector(230, y, z) for y, z in step3_pts], close=True)
solid3 = Solid.extrude(Face(wire3), Vector(-40, 0, 0))  # extrude +X 40mm

result = result.fuse(solid3)
try:    result = result.solids()[0]
except: pass
# Step 3 + fillet before fuse
wire3  = Wire.make_polygon([Vector(230, y, z) for y, z in step3_pts], close=True)
solid3 = Solid.extrude(Face(wire3), Vector(-40, 0, 0))

# Check bounding box
bb3 = solid3.bounding_box()
print(f"Step3 X: {bb3.min.X:.2f} to {bb3.max.X:.2f}")
print(f"Step3 Y: {bb3.min.Y:.2f} to {bb3.max.Y:.2f}")
print(f"Step3 Z: {bb3.min.Z:.2f} to {bb3.max.Z:.2f}")
print(f"Total edges: {len(solid3.edges())}")

# Fillet all edges
try:
    solid3 = solid3.fillet(5, solid3.edges())
    print("✅ All edges fillet done")
except Exception as e:
    print(f"⚠️ All edges failed: {e}")
    # Try only sharp edges
    try:
        sharp = solid3.edges().filter_by(GeomType.LINE)
        solid3 = solid3.fillet(5, sharp)
        print("✅ Sharp edges fillet done")
    except Exception as e2:
        print(f"⚠️ Sharp also failed: {e2}")

result = result.fuse(solid3)
try:    result = result.solids()[0]
except: pass

# Cut inner sphere R=292mm
inner_sphere = Solid.make_sphere(R_INNER)
result = result.cut(inner_sphere)
try:    result = result.solids()[0]
except: pass
print(f"✅ Inner sphere cut | Volume: {result.volume:.4e}")
print(f"Volume after: {result.volume:.4e}")
print(f"✅ Step 5 | Volume: {result.volume:.4e}")
# Step 6: dia 40mm holes at two points on Z=-337 face
HOLE_R6 = 40 / 2  # 20mm

hole6_pts = [
    ( 185.772, -3.277, -337),
    (-185.772,  3.277, -337),
]

for hx, hy, hz in hole6_pts:
    cyl = Solid.make_cylinder(HOLE_R6, 95)
    cyl = cyl.moved(Location(Vector(hx, hy, hz)))
    result = result.cut(cyl)
    try:    result = result.solids()[0]
    except: pass
    print(f"✅ Hole at ({hx}, {hy}, {hz})")

print(f"Volume: {result.volume:.4e}")
# Step 7: Countersink — inner face, +X direction
THRU_R7  = 40 / 2
CSINK_R7 = 80 / 2
CSINK_D7 = 25

hole7_pts = [
    (240.814, -227.146, -287.833),
    (240.814,  227.146, -287.833),
]

for hx, hy, hz in hole7_pts:
    # Thru hole dia40 — full X thru
    thru = Solid.make_cylinder(THRU_R7, 400)
    thru = thru.rotate(Axis.Y, 90)
    thru = thru.moved(Location(Vector(hx - 220, hy, hz)))
    result = result.cut(thru)
    try:    result = result.solids()[0]
    except: pass

    # Countersink cone — small at inner face (hx), grows inward (-X)
    cone = Solid.make_cone(THRU_R7, CSINK_R7, CSINK_D7)
    cone = cone.rotate(Axis.Y, -90)   # -X direction (into part)
    cone = cone.moved(Location(Vector(hx, hy, hz)))
    result = result.cut(cone)
    try:    result = result.solids()[0]
    except: pass

    print(f"✅ Countersink at ({hx}, {hy}, {hz})")

print(f"Volume: {result.volume:.4e}")
# Step 8: Center rectangle 215x215 at Z=-337, extrude cut 35mm
rect_w = 215 / 2  # 107.5mm half width
rect_h = 215 / 2  # 107.5mm half height

# Rectangle centered at (0, 0, -337)
rect_pts = [
    (-rect_w, -rect_h, -337),
    ( rect_w, -rect_h, -337),
    ( rect_w,  rect_h, -337),
    (-rect_w,  rect_h, -337),
]

wire8   = Wire.make_polygon([Vector(x, y, z) for x, y, z in rect_pts], close=True)
cutter8 = Solid.extrude(Face(wire8), Vector(0, 0, 35))  # +Z 35mm deep

result = result.cut(cutter8)
try:    result = result.solids()[0]
except: pass
print(f"✅ Step 8 | Volume: {result.volume:.4e}")
# Step 9: dia180 thru hole at center Z=-337
cyl9 = Solid.make_cylinder(180/2, 400)
cyl9 = cyl9.moved(Location(Vector(0, 0, -337)))

result = result.cut(cyl9)
try:    result = result.solids()[0]
except: pass
print(f"✅ Step 9 dia180 thru | Volume: {result.volume:.4e}")
# Step 10: Cut opening following dome surface
# Use outer sphere to define the opening cut

# Cutting plane along revolve axis at +45° 
ang_cut = math.radians(45)

# Large box cutter rotated to match dome opening angle
box_cut = Solid.make_box(800, 800, 800)
box_cut = box_cut.moved(Location(Vector(-400, -400, 0)))

# Rotate to cut along +45° plane
box_cut = box_cut.rotate(
    Axis(origin=Vector(0,0,0), direction=Vector(1,0,0)),
    45
)

before = result.volume
result = result.cut(box_cut)
try:    result = result.solids()[0]
except: pass
print(f"Diff: {before - result.volume:.4e}")

export_stl(result, STL_FILE)
print("✅ STL saved:", STL_FILE)

try:
    from ocp_vscode import show, Camera
    show(result, reset_camera=Camera.RESET)
    print("✅ Preview opened")
except ImportError:
    pass