from build123d import *
import math, os

STL_FILE = os.path.expanduser("~/Desktop/adapter_v2_bottom_pmw_3389.stl")

R_OUTER  = 447 / 2
R_INNER  = 304 / 2
HEIGHT   = 47
PCD_R    = 335 / 2
BOSS_R   = 73  / 2
HOLE_R   = 38  / 2
ANGLES   = [4, 51, 171.5, 271.3]
CSINK_D  = (BOSS_R - HOLE_R)
PCD_R2   = 374 / 2
HOLE_R2  = 45  / 2
ANGLES2  = [113.4, 292.1]
REV_ANG  = 12

profile_pts = [
    (147.4411,  17.1255), (154.6125,   2.1747),  (161.2123,  -11.5748),
    (167.5521,  -34.0596),(213.4322,  -33.3877),  (218.7502,  -32.0893),
    (221.3547,  -29.4849),(223.3929,  -25.1819),  (223.3929,  110.0305),
    (147.4411,  110.4214),(147.4411,   17.1255),
]

def rotate_pts(pts, deg):
    r = math.radians(deg)
    return [(x*math.cos(r) - y*math.sin(r),
             x*math.sin(r) + y*math.cos(r)) for x, y in pts]

def rotate_pt(x, y, deg):
    r = math.radians(deg)
    return (x*math.cos(r) - y*math.sin(r),
            x*math.sin(r) + y*math.cos(r))

# ── Step 1: Base ring ──
outer  = Solid.make_cylinder(R_OUTER, HEIGHT)
inner  = Solid.make_cylinder(R_INNER, HEIGHT)
result = outer.cut(inner)
try:    result = result.solids()[0]
except: pass
print("✅ Base ring done")

# ── Step 2: Boss fuse ──
for ang in ANGLES:
    rad  = math.radians(ang)
    cx   = PCD_R * math.cos(rad)
    cy   = PCD_R * math.sin(rad)
    boss = Solid.make_cylinder(BOSS_R, HEIGHT)
    boss = boss.moved(Location(Vector(cx, cy, 0)))
    result = result.fuse(boss)
    try:    result = result.solids()[0]
    except: pass

# ── Step 3: Countersink + thru hole ──
for ang in ANGLES:
    rad  = math.radians(ang)
    cx   = PCD_R * math.cos(rad)
    cy   = PCD_R * math.sin(rad)
    cone = Solid.make_cone(HOLE_R, BOSS_R, CSINK_D)
    cone = cone.moved(Location(Vector(cx, cy, HEIGHT - CSINK_D)))
    cyl  = Solid.make_cylinder(HOLE_R, HEIGHT - CSINK_D + 1)
    cyl  = cyl.moved(Location(Vector(cx, cy, -1)))
    cutter = cone.fuse(cyl)
    try:    cutter = cutter.solids()[0]
    except: pass
    result = result.cut(cutter)
    try:    result = result.solids()[0]
    except: pass

# ── Step 4: dia45 holes ──
for ang in ANGLES2:
    rad  = math.radians(ang)
    cx   = PCD_R2 * math.cos(rad)
    cy   = PCD_R2 * math.sin(rad)
    hole = Solid.make_cylinder(HOLE_R2, HEIGHT + 2)
    hole = hole.moved(Location(Vector(cx, cy, -1)))
    result = result.cut(hole)
    try:    result = result.solids()[0]
    except: pass

# ── Step 5: Profile revolve ±12° ──
with BuildPart() as rev_part:
    with BuildSketch(Plane.YZ):
        with BuildLine():
            for i in range(len(profile_pts) - 1):
                Line((profile_pts[i][0], profile_pts[i][1]),
                     (profile_pts[i+1][0], profile_pts[i+1][1]))
        make_face()
    revolve(axis=Axis.Z, revolution_arc=REV_ANG * 2)

rev_solid = rev_part.part
rev_solid = rev_solid.rotate(Axis.Z, -REV_ANG)
rev_solid = rev_solid.moved(Location(Vector(0, 0, HEIGHT - 156.5)))

clip_outer = Solid.make_cylinder(R_OUTER, 500)
clip_outer = clip_outer.moved(Location(Vector(0, 0, -300)))
clip_inner = Solid.make_cylinder(R_INNER, 500)
clip_inner = clip_inner.moved(Location(Vector(0, 0, -300)))
clip_ring  = clip_outer.cut(clip_inner)
rev_solid  = rev_solid.intersect(clip_ring)
try:    rev_solid = rev_solid.solids()[0]
except: pass
result = result.fuse(rev_solid)
try:    result = result.solids()[0]
except: pass

# ── Step 6: Revolve cut dia35 ──
CUT_R  = 183.116
CUT_Z  = -109
CUT_HR = 35 / 2

with BuildPart() as cut_part:
    with BuildSketch(Plane.YZ):
        with Locations((CUT_R, CUT_Z)):
            Circle(CUT_HR)
    revolve(axis=Axis.Z, revolution_arc=360)
result = result.cut(cut_part.part)
try:    result = result.solids()[0]
except: pass
# ── Step 7: Rectangle thru cut both directions ──
slot_pts = [
    (-13.2724, 150.5165), ( 13.4881, 150.5165),
    ( 10.3482, 198.5788), (-13.2724, 198.2575),
    (-13.2724, 150.5165),
]
wire    = Wire.make_polygon([Vector(x, y, 0) for x, y in slot_pts], close=True)
cutter1 = Solid.extrude(Face(wire), Vector(0, 0, -1000))  # -Z
cutter2 = Solid.extrude(Face(wire), Vector(0, 0,  1000))  # +Z
cutter  = cutter1.fuse(cutter2)
try:    cutter = cutter.solids()[0]
except: pass
result = result.cut(cutter)
try:    result = result.solids()[0]
except: pass

# ── Step 8: Profile revolve ±5° ──
REV_ANG2 = 5
profile_pts2 = [
    (222.773,  -2.4837), (222.773,  109.4898),
    (210.1359, 109.4898),(210.1359,   9.9632),
    (217.5553,   2.8186),(222.773,   -2.4837),
]
with BuildPart() as rev_part2:
    with BuildSketch(Plane.YZ):
        with BuildLine():
            for i in range(len(profile_pts2) - 1):
                Line((profile_pts2[i][0], profile_pts2[i][1]),
                     (profile_pts2[i+1][0], profile_pts2[i+1][1]))
        make_face()
    revolve(axis=Axis.Z, revolution_arc=REV_ANG2 * 2)
rev_solid2 = rev_part2.part
rev_solid2 = rev_solid2.rotate(Axis.Z, -REV_ANG2)
rev_solid2 = rev_solid2.moved(Location(Vector(0, 0, HEIGHT - 156.5)))
rev_solid2 = rev_solid2.intersect(clip_ring)
try:    rev_solid2 = rev_solid2.solids()[0]
except: pass
result = result.fuse(rev_solid2)
try:    result = result.solids()[0]
except: pass

# ── Step 9: Pattern ×3 ──
for pa in [120, 240]:
    with BuildPart() as rev_p:
        with BuildSketch(Plane.YZ):
            with BuildLine():
                for i in range(len(profile_pts) - 1):
                    Line((profile_pts[i][0], profile_pts[i][1]),
                         (profile_pts[i+1][0], profile_pts[i+1][1]))
            make_face()
        revolve(axis=Axis.Z, revolution_arc=REV_ANG * 2)
    rs = rev_p.part
    rs = rs.rotate(Axis.Z, -REV_ANG)
    rs = rs.moved(Location(Vector(0, 0, HEIGHT - 156.5)))
    rs = rs.intersect(clip_ring)
    try:    rs = rs.solids()[0]
    except: pass
    rs = rs.rotate(Axis.Z, pa)
    result = result.fuse(rs)
    try:    result = result.solids()[0]
    except: pass

    with BuildPart() as cut_p:
        with BuildSketch(Plane.YZ):
            with Locations((CUT_R, CUT_Z)):
                Circle(CUT_HR)
        revolve(axis=Axis.Z, revolution_arc=360)
    cs = cut_p.part.rotate(Axis.Z, pa)
    result = result.cut(cs)
    try:    result = result.solids()[0]
    except: pass

    # ── Slot cut both directions ──
    wire    = Wire.make_polygon([Vector(x, y, 0) for x, y in slot_pts], close=True)
    cutter1 = Solid.extrude(Face(wire), Vector(0, 0, -1000))
    cutter2 = Solid.extrude(Face(wire), Vector(0, 0,  1000))
    cutter  = cutter1.fuse(cutter2)
    try:    cutter = cutter.solids()[0]
    except: pass
    cutter  = cutter.rotate(Axis.Z, pa)
    result  = result.cut(cutter)
    try:    result = result.solids()[0]
    except: pass

    print(f"✅ Pattern at {pa}°")

# ── Step 10: extrude -15mm + mirror ──
step10_pts = [
    (171.8442, -143.0987), (84.5694,  -41.5245),  (75.0571,  -37.561),
    (63.6952,  -39.1464),  (53.9186,  -48.3945),  (51.7743,  -60.0913),
    (55.4824,  -69.6634),  (143.9431, -171.1375),  (150.5179, -165.3845),
    (157.0602, -159.1847), (165.569,  -150.3149),  (171.8442, -143.0987),
]
step10_rot = rotate_pts(step10_pts, -15)
wire10  = Wire.make_polygon([Vector(x, y, 0) for x, y in step10_rot], close=True)
solid10 = Solid.extrude(Face(wire10), Vector(0, 0, -15))
solid10_mirror = solid10.rotate(Axis.Z, 200)
result = result.fuse(solid10)
try:    result = result.solids()[0]
except: pass
result = result.fuse(solid10_mirror)
try:    result = result.solids()[0]
except: pass

# ── Step 11: extrude 15mm + mirror ──
step11_pts = [
    (32.6268, -150.7715), (16.6839, -111.6354),
    (69.5981,  -88.7398), (86.0258, -126.6283),
    (32.6268, -150.7715),
]
step11_rot = rotate_pts(step11_pts, 15)
wire11  = Wire.make_polygon([Vector(x, y, 0) for x, y in step11_rot], close=True)
solid11 = Solid.extrude(Face(wire11), Vector(0, 0, 15))
solid11_mirror = solid11.rotate(Axis.Z, 180)
result = result.fuse(solid11)
try:    result = result.solids()[0]
except: pass
result = result.fuse(solid11_mirror)
try:    result = result.solids()[0]
except: pass

# ── Step 12: Hole at Step 11 center + mirror ──
cx11 = (32.6268 + 16.6839 + 69.5981 + 86.0258) / 4
cy11 = (-150.7715 + -111.6354 + -88.7398 + -126.6283) / 4
hx, hy = rotate_pt(cx11, cy11, 15)
cyl12 = Solid.make_cylinder(15/2, 400)
cyl12 = cyl12.moved(Location(Vector(hx, hy, -200)))
result = result.cut(cyl12)
try:    result = result.solids()[0]
except: pass
result = result.cut(cyl12.rotate(Axis.Z, 180))
try:    result = result.solids()[0]
except: pass

# ── Step 13: Top face cut -15mm ──
step13_pts = [
    (-41.2606,  174.7526), (152.8725,   89.1305),
    ( 41.8182, -173.6697), (-157.4013,  -87.2),
    (-41.2606,  174.7526),
]
wire13   = Wire.make_polygon([Vector(x, y, 0) for x, y in step13_pts], close=True)
cutter13 = Solid.extrude(Face(wire13), Vector(0, 0, -22))
cutter13 = cutter13.moved(Location(Vector(0, 0, HEIGHT)))
result   = result.cut(cutter13)
try:    result = result.solids()[0]
except: pass

# ── Step 14: Top face cut -10mm ──
step14_pts = [
    ( -59.316,  216.5504), (-201.6159, -107.197),
    (-224.19,   -47.6783), (-225.1374,  11.6906),
    (-218.3162,  95.9017), (-170,       200.1129),
    (-121.2838, 200.7763), ( -59.316,   216.5504),
]
wire14   = Wire.make_polygon([Vector(x, y, 0) for x, y in step14_pts], close=True)
cutter14 = Solid.extrude(Face(wire14), Vector(0, 0, -13))
cutter14 = cutter14.moved(Location(Vector(0, 0, HEIGHT)))
result   = result.cut(cutter14)
try:    result = result.solids()[0]
except: pass

print(f"\nVolume   : {result.volume:.4e} mm³")

result = result.scale(0.1)
export_stl(result, STL_FILE)
print("✅ STL saved:", STL_FILE)

try:
    from ocp_vscode import show, Camera
    show(result, reset_camera=Camera.RESET)
    print("✅ Preview opened")
except ImportError:
    pass