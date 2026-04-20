from build123d import *
import math, os

STL_FILE = os.path.expanduser("~/Desktop/TopEncoderMod_v6.stl")

R_OUTER  = 398 / 2
R_INNER  = 313 / 2
HEIGHT   = 180
FILLET_R = 10

profile_pts = [
    (69.427,  140.2574), (71.667,  137.9247), (73.595,  134.2614),
    (74.302,  130.341),  (74.302,  126.8063), (72.9523, 122.8216),
    (71.0243, 119.094),  (69.427,  115.2103), (68.6705, 110.8793),
    (69.427,  106.8678), (70.4806, 103.8725), (72.2051, 101.3433),
    (79.8091,  94.9001), (85.9791,  89.2745), (94.8712,  80.3824),
    (102.856,  70.7644), (106.6457, 68.2584), (111.4997, 66.964),
    (117.4055, 67.4494), (123.8775, 70.5237), (128.8934, 72.3035),
    (134.7991, 72.3035), (137.6635, 70.8899), (140.5079, 68.9186),
    (128.8934, 88.7623), (117.4055, 103.4804),(102.8451, 117.9624),
    (91.7489,  126.7848),(80.2753,  134.3433), (69.427,  140.2574),
]

step5_pts = [
    (277.1125, -315.5633), (277.1125, -234.9927), (268.6756, -219.0416),
    (253.7079, -204.6084), (232.8599, -195.5208), (177.2653, -195.5208),
    (159.7206, -191.7878), (139.3503, -177.7833), (129.1652, -161.2325),
    (126.1946, -133.2234), (127.5419,  -98.2255), (127.5419,  -57.303),
    (135.7264,  -12.6555), (-110.9061, -10.5649),(-128.9061, -19.5649), (-123.763,  -64.5781),
    (-123.763, -100.5941), (-123.763, -145.7175), (-131.4764, -171.5574),
    (-149.2172,-189.2982), (-173.8196, -195.693), (-227.8309, -195.693),
    (-243.5319,-200.0893), (-256.7207, -208.8818),(-268.9675, -224.8968),
    (-273.6296,-240.9947), (-273.6296, -315.5633), (277.1125, -315.5633),
]

# Step 1: Ring
outer  = Solid.make_cylinder(R_OUTER, HEIGHT)
inner  = Solid.make_cylinder(R_INNER, HEIGHT)
result = outer.cut(inner)
try:    result = result.solids()[0]
except: pass
print("✅ Ring done")

# Step 2 + Step 4: Pattern x3
for pa in [0, 120, 240]:
    wire2  = Wire.make_polygon([Vector(x, y, 0) for x, y in profile_pts], close=True)
    solid2 = Solid.extrude(Face(wire2), Vector(0, 0, 70))
    solid2 = solid2.rotate(Axis.Z, pa)
    result = result.fuse(solid2)
    try:    result = result.solids()[0]
    except: pass

    cyl4 = Solid.make_cylinder(40/2, 65)
    cyl4 = cyl4.moved(Location(Vector(118.553, 113.989, 0)))
    cyl4 = cyl4.rotate(Axis.Z, pa)
    result = result.cut(cyl4)
    try:    result = result.solids()[0]
    except: pass
    print(f"✅ Pattern at {pa}° done")

# Step 3: Top outer fillet R10
top_edges = (
    result.edges()
    .filter_by(GeomType.CIRCLE)
    .filter_by(lambda e: abs(e.center().Z - HEIGHT) < 0.01)
    .filter_by(lambda e: abs(e.radius - R_OUTER) < 0.1)
)
result = result.fillet(FILLET_R, top_edges)
print("✅ Top outer fillet done")

# Step 5: Profile on XY plane, extrude 40mm, rotate 42° + offset 75mm
import math

ANGLE  = 42
OFFSET = -133
angle  = math.radians(ANGLE)

wire5  = Wire.make_polygon([Vector(x, y, 0) for x, y in step5_pts], close=True)
solid5 = Solid.extrude(Face(wire5), Vector(0, 0, 40))

# Rotate 42° around Z
solid5 = solid5.rotate(Axis.X, ANGLE)
solid5 = solid5.moved(Location(Vector(0, 0, 60)))
solid5 = solid5.moved(Location(Vector(0, -47, 0)))
solid5 = solid5.moved(Location(Vector(-90, 0, 0)))
# Translate along plate face direction (after X rotation 42°)
MOVE   = 46  # adjust as needed
angle  = math.radians(42)
ny     = math.cos(angle)
nz     = math.sin(angle)

solid5 = solid5.moved(Location(Vector(0, ny * MOVE, nz * MOVE)))

# Offset 75mm along rotated normal
solid5 = solid5.moved(Location(Vector(
    OFFSET * (-math.sin(angle)),
    OFFSET *   math.cos(angle),
    0
)))
# Remove only plate part inside inner cylinder
inner_wall = Solid.make_cylinder(R_INNER, 500)
inner_wall = inner_wall.moved(Location(Vector(0, 0, -250)))

solid5 = solid5.cut(inner_wall)
try:    solid5 = solid5.solids()[0]
except: pass
result = result.fuse(solid5)
try:    result = result.solids()[0]
except: pass
print(f"✅ Step 5 done | Volume: {result.volume:.4e}")
# Step 6: Countersink holes on plate face
THRU_R  = 43 / 2
CSINK_R = 80 / 2
TAPER_D = 30
ang     = math.radians(42)

hole_pts_3d = [
    ( 226.779, -290.33, -70.101),
    (-224.521, -290.33, -70.101),
]

for hx, hy, hz in hole_pts_3d:
    # Thru hole
    thru = Solid.make_cylinder(THRU_R, 200)
    thru = thru.rotate(Axis.X, 42)
    thru = thru.moved(Location(Vector(
        hx,
        hy + 100 * math.sin(ang),
        hz - 100 * math.cos(ang)
    )))
    result = result.cut(thru)
    try:    result = result.solids()[0]
    except: pass

    # Countersink
    cone = Solid.make_cone(THRU_R, CSINK_R, TAPER_D)
    cone = cone.rotate(Axis.X, 222)
    cone = cone.moved(Location(Vector(
        hx,
        hy - 20 * math.sin(ang),
        hz + 20 * math.cos(ang)
    )))
    result = result.cut(cone)
    try:    result = result.solids()[0]
    except: pass
    print(f"✅ Countersink at ({hx:.0f}, {hy:.0f}, {hz:.0f})")

print(f"Volume: {result.volume:.4e}")
   # Step 7: Close boundary extrude cut 8mm
# Step 7: Close boundary cut aligned with plate
step7_pts = [
    (-64.0837, -202.3682), ( 61.1979, -202.8634),
    ( 60.7027, -129.081),  ( 30.6104, -134.6815),
    ( -1.8786, -137.4892), (-35.1699, -135.4837),
    (-64.5789, -130.5665),
]

pts_closed = step7_pts + [step7_pts[0]]
ang5 = math.radians(42)

# Points are in local plate coords — apply plate transform
def plate_transform(solid):
    solid = solid.rotate(Axis.X, 42)
    solid = solid.moved(Location(Vector(0, 0, 60)))
    solid = solid.moved(Location(Vector(0, -47, 0)))
    solid = solid.moved(Location(Vector(-90, 0, 0)))
    solid = solid.moved(Location(Vector(
        -133 * (-math.sin(math.radians(-75))),
        -133 *   math.cos(math.radians(-75)),
        0
    )))
    solid = solid.moved(Location(Vector(
        0,
        math.cos(ang5) * 30,
        math.sin(ang5) * 30
    )))
    return solid

# Build on XY plane then transform
vecs    = [Vector(x, y, 0) for x, y in pts_closed]
wire7   = Wire.make_polygon(vecs, close=False)
face7   = Face(wire7)
cutter7 = Solid.extrude(face7, Vector(0, 0, 8))
cutter7 = plate_transform(cutter7)

b = result.volume
result = result.cut(cutter7)
try:    result = result.solids()[0]
except: pass
print(f"Step 7 diff: {b - result.volume:.4e}")
print(f"✅ Step 7 | Volume: {result.volume:.4e}")
print(f"✅ Step 7 done | Volume: {result.volume:.4e}")
print(f"Volume: {result.volume:.4e}")
export_stl(result, STL_FILE)
print("✅ STL saved:", STL_FILE)

try:
    from ocp_vscode import show, Camera
    show(result, reset_camera=Camera.RESET)
    print("✅ Preview opened")
except ImportError:
    pass