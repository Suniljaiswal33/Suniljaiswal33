from build123d import *
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakePolygon
from OCP.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCP.BRepLib import BRepLib
from OCP.gp import gp_Pnt
from build123d import Solid as BSolid
import os

# ─────────────────────────────────────────────
SCALE     = 0.1
STL_FILE  = os.path.expanduser("~/Desktop/tent-connector.stl")
STEP_FILE = os.path.expanduser("~/Desktop/tent-connector.step")

# ══════════════════════════════════════════════
# STEP 1 — YZ Profile Symmetric Extrude (X-axis)
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
# STEP 2 — Cylinder on YZ Plane (X extrude)
# ══════════════════════════════════════════════
cx = -989.855 * SCALE   # -98.9855
cy =  921.965 * SCALE   #  92.1965
cz = -147.675 * SCALE   # -14.7675

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
# STEP 3 — Polygon Extrude 40mm
# ══════════════════════════════════════════════
raw_pts3 = [
    (-1114.5316, 854.468,  0.0),
    (-1133.341,  751.203,  0.0),
    (-1138.9769, 633.3496, 0.0),
    (-1133.341,  529.042,  0.0),
    (-1107.8647, 401.1198, 0.0),
    (-1075.6415, 294.4497, 0.0),
    (-1045.6405, 205.5579, 0.0),
    (-1014.5284, 126.6664, 0.0),
    (-998.9723,  110.5739, 0.0),
    (-979.9449,  110.5739, 0.0),
    (-979.9449,  493.6068, 0.0),
    (-1003.5491, 493.6068, 0.0),
    (-1019.643,  568.7112, 0.0),
    (-1019.643,  630.9407, 0.0),
    (-1012.1325, 698.5347, 0.0),
    (-986.3824,  783.2955, 0.0),
    (-953.1218,  842.3061, 0.0),
    (-1089.8249, 935.5737, 0.0),
]

# SCALE 0.1 apply + XY plane (Z=0) → Vector(x, y, 0)
vecs3 = [Vector(x * SCALE, y * SCALE, 0.0) for x, y, z in raw_pts3]

wire3  = Wire.make_polygon(vecs3, close=True)
face3  = Face(wire3)
step3  = Solid.extrude(face3, Vector(0, 0, -40.0))  # 40mm Z direction extrude

print(f"✅ Step 3 DONE | Volume: {step3.volume:.4e} mm³")
bb3 = step3.bounding_box()
print(f"   X:{bb3.min.X:.1f}→{bb3.max.X:.1f}  Y:{bb3.min.Y:.1f}→{bb3.max.Y:.1f}  Z:{bb3.min.Z:.1f}→{bb3.max.Z:.1f}")
# ══════════════════════════════════════════════
# CUT — Right Plane (YZ) Closed Profile → Thru Cut on Step3
# ══════════════════════════════════════════════
raw_cut = [
    (0.0, 1002.536, -511.9111),
    (0.0,  206.3825, -506.1834),
    (0.0,  295.735,  -454.6339),
    (0.0,  396.5429, -401.9388),
    (0.0,  491.6231, -352.6804),
    (0.0,  588.9944, -306.8586),
    (0.0,  697.8212, -269.0557),
    (0.0,  748.2251, -250.727),
    (0.0,  843.3053, -226.6705),
    (0.0,  910.8925, -212.924),
    (0.0,  953.2776, -203.7596),
    (0.0, 1002.536,  -194.5953),
]

# YZ plane profile → scale and fix X at step3 min boundary
bb3      = step3.bounding_box()
cut_x    = bb3.min.X - 1.0   # start slightly outside step3

vecs_cut = [Vector(cut_x, y * SCALE, z * SCALE) for x, y, z in raw_cut]
wire_cut = Wire.make_polygon(vecs_cut, close=True)
face_cut = Face(wire_cut)

# Extrude through full X width of step3 with margin
cut_depth   = (bb3.max.X - bb3.min.X) + 2.0
extrude_cut = Solid.extrude(face_cut, Vector(cut_depth, 0, 0))

# Subtract cut from step3
step3 = step3.cut(extrude_cut)
try:    step3 = step3.solids()[0]
except: pass

print(f"✅ Cut DONE | Step3 Volume after cut: {step3.volume:.4e} mm³")
bb3c = step3.bounding_box()
print(f"   X:{bb3c.min.X:.1f}→{bb3c.max.X:.1f}  Y:{bb3c.min.Y:.1f}→{bb3c.max.Y:.1f}  Z:{bb3c.min.Z:.1f}→{bb3c.max.Z:.1f}")
# ══════════════════════════════════════════════
# CUT 2 — Right Plane (YZ) Closed Profile → Thru Cut on Step3
# ══════════════════════════════════════════════
raw_cut2 = [
    (0.0,  99.5395, -424.6225),
    (0.0, 399.65,   -182.0331),
    (0.0, 485.9318, -150.7716),
    (0.0, 584.7182, -123.2615),
    (0.0, 673.5009, -104.5046),
    (0.0, 776.0386,  -85.7477),
    (0.0, 881.0773,  -70.7421),
    (0.0, 1002.372,  -70.7421),
    (0.0, 1002.372,  145.5876),
    (0.0,  99.5395,  145.5876),
]

# YZ plane profile → scale and fix X at step3 boundary
bb3      = step3.bounding_box()
cut_x    = bb3.min.X - 1.0   # start slightly outside step3

vecs_cut2 = [Vector(cut_x, y * SCALE, z * SCALE) for x, y, z in raw_cut2]
wire_cut2 = Wire.make_polygon(vecs_cut2, close=True)
face_cut2 = Face(wire_cut2)

# Extrude through full X width of step3 with margin
cut_depth2   = (bb3.max.X - bb3.min.X) + 2.0
extrude_cut2 = Solid.extrude(face_cut2, Vector(cut_depth2, 0, 0))

# Subtract cut from step3
step3 = step3.cut(extrude_cut2)
try:    step3 = step3.solids()[0]
except: pass

print(f"✅ Cut 2 DONE | Step3 Volume after cut: {step3.volume:.4e} mm³")
bb3c = step3.bounding_box()
print(f"   X:{bb3c.min.X:.1f}→{bb3c.max.X:.1f}  Y:{bb3c.min.Y:.1f}→{bb3c.max.Y:.1f}  Z:{bb3c.min.Z:.1f}→{bb3c.max.Z:.1f}")

        # ══════════════════════════════════════════════
# STEP 3 — Smooth Loft (ruled=False for organic curves)
# ══════════════════════════════════════════════
s1_face = sorted(step1.faces(), key=lambda f: f.center().X)[0]
s1_bb   = s1_face.bounding_box()
s1x     = s1_bb.min.X

# Step1 end — smooth spline wire instead of polygon
s1_corners = [
    Vector(s1x, s1_bb.min.Y, s1_bb.min.Z),
    Vector(s1x, s1_bb.max.Y, s1_bb.min.Z),
    Vector(s1x, s1_bb.max.Y, s1_bb.max.Z),
    Vector(s1x, s1_bb.min.Y, s1_bb.max.Z),
    Vector(s1x, s1_bb.min.Y, s1_bb.min.Z),  # close
]
w1 = Wire.make_spline(s1_corners, periodic=False)

# Step2 cylinder end — smooth spline wire
h = 9.0
s2_corners = [
    Vector(cx - h, cy - h, cz),
    Vector(cx + h, cy - h, cz),
    Vector(cx + h, cy + h, cz),
    Vector(cx - h, cy + h, cz),
    Vector(cx - h, cy - h, cz),  # close
]
w2 = Wire.make_spline(s2_corners, periodic=False)

# Smooth loft — ruled=False for curved organic surface
f1 = Face.make_surface(w1)
f2 = Face.make_surface(w2)

loft_builder = BRepOffsetAPI_ThruSections(True, False)  # ✅ ruled=False
loft_builder.AddWire(w1.wrapped)
loft_builder.AddWire(w2.wrapped)
loft_builder.CheckCompatibility(False)
loft_builder.Build()

if loft_builder.IsDone():
    step3 = BSolid(loft_builder.Shape())
    print(f"✅ Step 3 DONE | Volume: {step3.volume:.4e} mm³")
else:
    print("❌ Loft Failed")
    step3 = None
# ══════════════════════════════════════════════
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
    print("⚠️  ocp_vscode not found — open STL manually")