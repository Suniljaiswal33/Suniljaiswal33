from build123d import *
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepLib import BRepLib
from OCP.gp import gp_Pnt
from build123d import Solid as BSolid
import numpy as np
import os

SCALE     = 0.1
STL_FILE  = os.path.expanduser("~/Desktop/tent-connector.stl")
STEP_FILE = os.path.expanduser("~/Desktop/tent-connector.step")

# ══════════════════════════════════════════════
# STEP 1 — YZ Profile Symmetric Extrude
# ══════════════════════════════════════════════
OFFSET_X = -94.5
yz_pts = [
    (0.0,  389.2527,  -189.4292),
    (0.0,  401.5525,  -181.6016),
    (0.0,  417.7878,  -175.0198),
    (0.0,  434.9006,  -175.0198),
    (0.0,  455.085,   -179.4077),
    (0.0,  471.7591,  -190.3775),
    (0.0,  484.9228,  -205.2964),
    (0.0,  492.8211,  -224.1644),
    (0.0,  494.8116,  -245.4388),
    (0.0,  489.8887,  -265.9078),
    (0.0,  478.593,   -283.5659),
    (0.0,  467.2898,  -293.6666),
    (0.0,  457.8798,  -300.7558),
    (0.0,  130.3442,  -568.4126),
    (0.0,  120.4635,  -576.1406),
    (0.0,  111.8744,  -581.6064),
    (0.0,  101.984,   -584.99),
    (0.0,   86.1071,  -587.853),
    (0.0,   75.0628,  -587.2537),
    (0.0,   69.0732,  -586.1647),
    (0.0,   62.0415,  -583.9929),
    (0.0,   57.0046,  -582.1525),
    (0.0,   52.549,   -580.0215),
    (0.0,   52.549,   -463.6868),
]

wire1     = Wire.make_polygon([Vector(OFFSET_X, y*SCALE, z*SCALE) for x,y,z in yz_pts], close=True)
face1     = Face(wire1)
pos_solid = Solid.extrude(face1, Vector( 3.5, 0, 0))
neg_solid = Solid.extrude(face1, Vector(-3.5, 0, 0))
step1     = pos_solid.fuse(neg_solid)
try:    step1 = step1.solids()[0]
except: pass

bb1 = step1.bounding_box()
print(f"✅ Step 1 DONE | Volume: {step1.volume:.4e} mm³")
print(f"   X:{bb1.min.X:.1f}→{bb1.max.X:.1f}  Y:{bb1.min.Y:.1f}→{bb1.max.Y:.1f}  Z:{bb1.min.Z:.1f}→{bb1.max.Z:.1f}")

# ══════════════════════════════════════════════
# STEP 2 — Cylinder
# ══════════════════════════════════════════════
cx = -989.855 * SCALE
cy =  921.965 * SCALE
cz = -147.675 * SCALE

step2 = Solid.make_cylinder(
    43.0/2, 4.0,
    Plane(origin=(0,0,0), x_dir=(0,1,0), z_dir=(-1,0,0))
)
step2 = step2.rotate(Axis.X, 0)
step2 = step2.rotate(Axis.Z, 55)
step2 = step2.moved(Location(Vector(cx, cy, cz)))

bb2 = step2.bounding_box()
print(f"✅ Step 2 DONE | Volume: {step2.volume:.4e} mm³")
print(f"   X:{bb2.min.X:.1f}→{bb2.max.X:.1f}  Y:{bb2.min.Y:.1f}→{bb2.max.Y:.1f}  Z:{bb2.min.Z:.1f}→{bb2.max.Z:.1f}")

# ══════════════════════════════════════════════
# STEP 3 — Simple Loft (no guide curves)
# ══════════════════════════════════════════════
loft_pts1 = [
    (-980.0, 428.3322, -167.6176),
   
    (-980.0, 107.8359, -416.7163),
    (-980.0, 286.0387, -352.6991),
    (-980.0, 499.7299, -261.2279),
    (-980.0, 333.1353, -400.8501),
    (-980.0, 190.3399, -518.2596),
     (-980.0, 252.2179, -299.3067),

    
]

loft_pts2 = [
    (-984.1768,  869.1582,  -81.7066),
    (-950.9438,  845.8882, -149.4825),
    (-982.4079,  867.9196, -218.5051),
      (-1015.641, 891.19,  -150.729),
    (-1047.1051, 913.2209, -219.7519),
    (-1080.3382, 936.4909, -151.976),
    (-1048.8741, 914.4596,  -82.9534),

   
]

v1 = [Vector(x*SCALE, y*SCALE, z*SCALE) for x,y,z in loft_pts1]
v2 = [Vector(x*SCALE, y*SCALE, z*SCALE) for x,y,z in loft_pts2]

wire_l1 = Wire.make_polygon(v1, close=True)
wire_l2 = Wire.make_polygon(v2, close=True)

loft_builder = BRepOffsetAPI_ThruSections(True, False)
loft_builder.AddWire(wire_l1.wrapped)
loft_builder.AddWire(wire_l2.wrapped)
loft_builder.CheckCompatibility(False)
loft_builder.Build()

if loft_builder.IsDone():
    step3 = BSolid(loft_builder.Shape())
    print(f"✅ Step 3 Loft DONE | Volume: {step3.volume:.4e} mm³")
    bb3 = step3.bounding_box()
    print(f"   X:{bb3.min.X:.1f}→{bb3.max.X:.1f}  Y:{bb3.min.Y:.1f}→{bb3.max.Y:.1f}  Z:{bb3.min.Z:.1f}→{bb3.max.Z:.1f}")
else:
    print("❌ Loft Failed")
    step3 = None

# ══════════════════════════════════════════════
# CUT 3 — SVD plane + 3 instances 120° pattern on step2
# ══════════════════════════════════════════════
raw_cut3 = [
    (-992.5722,  992.5722,  -169.4103),
    (-984.5386,  984.5386,  -192.1328),
    (-982.4244,  982.4244,  -208.2777),
    (-982.4244,  982.4244,  -226.2165),
    (-987.4983,  987.4983,  -243.5573),
    (-994.2634,  994.2634,  -258.5063),
    (-1005.2568, 1005.2568, -275.8471),
    (-1012.8676, 1012.8676, -285.4144),
    (-1026.3978, 1026.3978, -290.1981),
    (-1036.9684, 1036.9684, -285.4144),
    (-1055.9953, 1055.9953, -255.5165),
    (-1065.2974, 1065.2974, -233.392),
    (-1071.2169, 1071.2169, -214.8552),
    (-1077.982,  1077.982,  -176.5858),
    (-1067.4115, 1067.4115, -152.6675),
    (-1049.2302, 1049.2302, -141.3062),
    (-1034.8543, 1034.8543, -137.7185),
    (-1019.6327, 1019.6327, -141.3062),
    (-1005.2568, 1005.2568, -152.0695),
]

pts      = np.array([[x*SCALE, y*SCALE, z*SCALE] for x,y,z in raw_cut3])
centroid = np.mean(pts, axis=0)
_, _, Vt = np.linalg.svd(pts - centroid)
normal   = Vt[-1] / np.linalg.norm(Vt[-1])

def project(pt, centroid, normal):
    return pt - np.dot(pt - centroid, normal) * normal

pts_proj = np.array([project(p, centroid, normal) for p in pts])

bb2        = step2.bounding_box()
cyl_center = np.array([
    (bb2.min.X + bb2.max.X) / 2,
    (bb2.min.Y + bb2.max.Y) / 2,
    (bb2.min.Z + bb2.max.Z) / 2,
])

local_x = np.cross(normal, np.array([0.0, 0.0, 1.0]))
local_x = local_x / np.linalg.norm(local_x)
local_y = np.cross(local_x, normal)
local_y = local_y / np.linalg.norm(local_y)

for i in range(3):
    rot_angle = np.radians(i * 120.0)
    pts_inst  = []
    for p in pts_proj:
        v      = p - cyl_center
        vx     = np.dot(v, local_x)
        vy     = np.dot(v, local_y)
        vn     = np.dot(v, normal)
        vx_rot = vx * np.cos(rot_angle) - vy * np.sin(rot_angle)
        vy_rot = vx * np.sin(rot_angle) + vy * np.cos(rot_angle)
        pts_inst.append(cyl_center + vx_rot*local_x + vy_rot*local_y + vn*normal)

    pts_inst  = np.array(pts_inst)
    vecs_inst = [Vector(float(p[0]), float(p[1]), float(p[2])) for p in pts_inst]
    wire_inst = Wire.make_polygon(vecs_inst, close=True)
    face_inst = Face.make_surface(wire_inst)

    thru     = 100.0
    off_v    = Vector(float(-normal[0]*thru/2), float(-normal[1]*thru/2), float(-normal[2]*thru/2))
    cut_tool = Solid.extrude(face_inst.moved(Location(off_v)),
                   Vector(float(normal[0]*thru), float(normal[1]*thru), float(normal[2]*thru)))

    step2 = step2.cut(cut_tool)
    try:    step2 = step2.solids()[0]
    except: pass
    print(f"✅ Cut 3 Instance {i+1} DONE | Volume: {step2.volume:.4e} mm³")

# ══════════════════════════════════════════════
# CUT 4 — 3 holes 4mm dia on same SVD plane on step2
# ══════════════════════════════════════════════
hole_pts = [
    (-899.2632,  858.5319, -85.7249),
    (-1081.2306, 985.9469, -85.7249),
    (-989.8535,  921.9639, -279.2283),
]

for i, (x, y, z) in enumerate(hole_pts):
    hx = x * SCALE
    hy = y * SCALE
    hz = z * SCALE

    hole_plane = Plane(
        origin=(hx, hy, hz),
        z_dir=Vector(float(normal[0]), float(normal[1]), float(normal[2]))
    )
    hole_face = Face(Wire(Edge.make_circle(2.0, hole_plane)))
    hole_tool = Solid.extrude(
        hole_face.moved(Location(Vector(
            float(-normal[0]*50), float(-normal[1]*50), float(-normal[2]*50)
        ))),
        Vector(float(normal[0]*100), float(normal[1]*100), float(normal[2]*100))
    )

    step2 = step2.cut(hole_tool)
    try:    step2 = step2.solids()[0]
    except: pass
    print(f"✅ Hole {i+1} DONE | Volume: {step2.volume:.4e} mm³")
    # ══════════════════════════════════════════════
# CUT 5 — 10mm dia circle thru cut on step3 + 1mm fillet
# ══════════════════════════════════════════════
hx = -980.0 * SCALE
hy =  428.7081 * SCALE
hz = -236.8034 * SCALE

# YZ plane pe circle (X normal)
hole_plane = Plane(
    origin=(hx, hy, hz),
    z_dir=Vector(1, 0, 0)  # X direction normal = YZ plane
)
hole_face = Face(Wire(Edge.make_circle(5.0, hole_plane)))  # r=5mm = 10mm dia

# Thru cut — step3 full X width
bb3_c     = step3.bounding_box()
start_x   = bb3_c.min.X - 1.0
cut_depth = (bb3_c.max.X - bb3_c.min.X) + 2.0

hole_tool = Solid.extrude(
    hole_face.moved(Location(Vector(start_x - hx, 0, 0))),
    Vector(cut_depth, 0, 0)
)

step3 = step3.cut(hole_tool)
try:    step3 = step3.solids()[0]
except: pass
print(f"✅ Cut 5 DONE | Volume: {step3.volume:.4e} mm³")

# 1mm fillet on top and bottom edges of hole
try:
    # Hole edges — circle edges filter karo (short edges)
    hole_edges = [e for e in step3.edges() if e.length < 35.0]
    step3 = step3.fillet(1.0, hole_edges)
    try:    step3 = step3.solids()[0]
    except: pass
    print(f"✅ Fillet DONE | Volume: {step3.volume:.4e} mm³")
except Exception as e:
    print(f"⚠️ Fillet failed: {e}")
# ══════════════════════════════════════════════
# CUT 6 — 2 holes 4mm dia on STEP1 (YZ plane)
# ══════════════════════════════════════════════
hole_pts6 = [
    (-980.0, 105.4751, -502.1541),
    (-980.0, 427.7178, -240.4342),
]

bb1_c = step1.bounding_box()
print(f"Step1: Y:{bb1_c.min.Y:.1f}→{bb1_c.max.Y:.1f}  Z:{bb1_c.min.Z:.1f}→{bb1_c.max.Z:.1f}")

for i, (x, y, z) in enumerate(hole_pts6):
    hy = y * SCALE
    hz = z * SCALE

    print(f"Hole {i+1}: Y:{hy:.1f} Z:{hz:.1f} — Y ok:{bb1_c.min.Y<=hy<=bb1_c.max.Y} Z ok:{bb1_c.min.Z<=hz<=bb1_c.max.Z}")

    hole_plane = Plane(
        origin=(bb1_c.min.X - 1.0, hy, hz),
        z_dir=Vector(1, 0, 0)
    )
    hole_face = Face(Wire(Edge.make_circle(2.0, hole_plane)))
    hole_tool = Solid.extrude(hole_face, Vector((bb1_c.max.X - bb1_c.min.X) + 2.0, 0, 0))

    step1 = step1.cut(hole_tool)
    try:    step1 = step1.solids()[0]
    except: pass
    print(f"✅ Cut 6 Hole {i+1} DONE | Volume: {step1.volume:.4e} mm³")
# COMBINE & EXPORT
# ══════════════════════════════════════════════
parts = [p for p in [step1, step2, step3] if p is not None]
final       = Compound(parts)
final.label = "tent-connector"

export_stl(final,  STL_FILE)
export_step(final, STEP_FILE)
print("✅ STL  saved:", STL_FILE)
print("✅ STEP saved:", STEP_FILE)

try:
    from ocp_vscode import show, Camera
    show(final, reset_camera=Camera.RESET)
    print("✅ Preview opened")
except ImportError:
    print("⚠️  ocp_vscode not found")