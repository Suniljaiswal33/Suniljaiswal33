from build123d import *
import os

STL_FILE = os.path.expanduser("~/Desktop/sensor_cover.stl")

R_OUTER  = 470 / 2
HEIGHT   = 220
FILLET_R = 20
SHELL_T  = 10
PCD_R    = 370 / 2
HOLE_R   = 30 / 2

# Step 1: Cylinder
cyl = Solid.make_cylinder(R_OUTER, HEIGHT)
cyl = cyl.moved(Location(Vector(0, 0, -HEIGHT)))
print("✅ Cylinder done")

# Step 2: Fillet bottom edge
bottom_edges = cyl.edges().group_by(Axis.Z)[0]
cyl = cyl.fillet(FILLET_R, bottom_edges)
print("✅ Fillet done")

# Step 3: Shell 10mm
inner  = Solid.make_cylinder(R_OUTER - SHELL_T, HEIGHT - SHELL_T)
inner  = inner.moved(Location(Vector(0, 0, -(HEIGHT - SHELL_T))))
result = cyl.cut(inner)
try:    result = result.solids()[0]
except: pass
print("✅ Shell done")

# Step 4: 2x holes
hole_pts = [( PCD_R, 0), (-PCD_R, 0)]
for i, (hx, hy) in enumerate(hole_pts, 1):
    hole   = Solid.make_cylinder(HOLE_R, HEIGHT + 10)
    hole   = hole.moved(Location(Vector(hx, hy, -HEIGHT - 5)))
    result = result.cut(hole)
    try:    result = result.solids()[0]
    except: pass
    print(f"✅ Hole {i} at ({hx:.1f}, {hy:.1f})")

print(f"Volume   : {result.volume:.4e} mm³")

# ── Cut 1 ──
cut_pts1 = [
    (391.1333,  83.3387),
    (-133.5596, 380.6332),
    (-108.0234, 208.9505),
    (228.5577,  -54.3772),
    (391.1333,  83.3387),
]
wire   = Wire.make_polygon([Vector(x, y, 0) for x, y in cut_pts1], close=True)
cutter = Solid.extrude(Face(wire), Vector(0, 0, -200))
result = result.cut(cutter)
try:    result = result.solids()[0]
except: pass
print(f"✅ Cut 1 done | Volume: {result.volume:.4e}")

# ── Cut 2: updated points ──
cut_pts2 = [
    ( 99.4159,  155.0042),
    (-100.5936, 155.0042),
    (-100.5936, 198.4491),
    (-100.8842, 202.6828),
    (-100.8842, 206.0449),
    (-103.7067, 208.9505),
    (-105.865,  209.324),
    (-108.0234, 208.9505),
    (-133.5596, 380.6332),
    ( -100,  450.8777),
    (-113.4931, 300.8646),
    ( 108.6457, 208.5938),
    ( 101.6389, 208.8615),
    (  99.6316, 206.0961),
    (  99.4159, 155.0042),
]
wire   = Wire.make_polygon([Vector(x, y, 0) for x, y in cut_pts2], close=True)
cutter = Solid.extrude(Face(wire), Vector(0, 0, -240))
result = result.cut(cutter)
try:    result = result.solids()[0]
except: pass
print(f"✅ Cut 2 done | Volume: {result.volume:.4e}")
result = result.scale(0.1)
export_stl(result, STL_FILE)
print("✅ STL saved:", STL_FILE)

try:
    from ocp_vscode import show, Camera
    show(result, reset_camera=Camera.RESET)
    print("✅ Preview opened")
except ImportError:
    pass