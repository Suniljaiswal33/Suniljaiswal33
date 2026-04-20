from build123d import *
import math, os

STL_FILE = os.path.expanduser("~/Desktop/adapter_btu_bottom_v32.stl")

R_OUTER  = 448.7 / 2
R_INNER  = 306 / 2
HEIGHT   = 47
PCD_R    = 335 / 2
BOSS_R   = 73  / 2
HOLE_R   = 38  / 2
ANGLES   = [4, 51, 171.5, 271.3]
CSINK_D  = (BOSS_R - HOLE_R)
PCD_R2   = 374 / 2
HOLE_R2  = 45  / 2
ANGLES2  = [220.4, 390.1]
REV_ANG  = 17.5

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
print("✅ Boss done")

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
print("✅ Countersink done")

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
print("✅ dia45 holes done")

# ── Step 5: Profile revolve ±17.5° ──
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
print("✅ Profile revolve done")

# ── Step 9: Pattern ×3 (120°, 240°) ──
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
    print(f"✅ Pattern revolve at {pa}°")

# ── Step 10: extrude -15mm + mirror ──
step10_pts = [
    (171.8442, -143.0987), (84.5694,  -41.5245),  (75.0571,  -37.561),
    (63.6952,  -39.1464),  (53.9186,  -48.3945),  (51.7743,  -60.0913),
    (55.4824,  -69.6634),  (143.9431, -171.1375),  (150.5179, -165.3845),
    (157.0602, -159.1847), (165.569,  -150.3149),  (171.8442, -143.0987),
]
step10_rot = rotate_pts(step10_pts, -82)  # rotate sketch -60°
wire10  = Wire.make_polygon([Vector(x, y, 0) for x, y in step10_rot], close=True)
solid10 = Solid.extrude(Face(wire10), Vector(0, 0, -20))
solid10_mirror = solid10.rotate(Axis.Z, 156)  # mirror 180°
result = result.fuse(solid10)
try:    result = result.solids()[0]
except: pass
result = result.fuse(solid10_mirror)
try:    result = result.solids()[0]
except: pass
print("✅ Step 10 done")

# ── Step 13: Top face cut -22mm ──
step13_pts = [
    (-41.2606,  174.7526), (152.8725,   89.1305),
    ( 41.8182, -173.6697), (-157.4013,  -87.2),
    (-41.2606,  174.7526),
]
wire13   = Wire.make_polygon([Vector(x, y, 0) for x, y in step13_pts], close=True)
cutter13 = Solid.extrude(Face(wire13), Vector(0, 0, -3))
cutter13 = cutter13.moved(Location(Vector(0, 0, HEIGHT)))
result   = result.cut(cutter13)
try:    result = result.solids()[0]
except: pass
print("✅ Step 13 done")

# ── Step 14: Top face cut -13mm ──
step14_pts = [
    ( -59.316,  216.5504), (-201.6159, -107.197),
    (-224.19,   -47.6783), (-225.1374,  11.6906),
    (-218.3162,  95.9017), (-170,       200.1129),
    (-121.2838, 200.7763), ( -59.316,   216.5504),
]
wire14   = Wire.make_polygon([Vector(x, y, 0) for x, y in step14_pts], close=True)
cutter14 = Solid.extrude(Face(wire14), Vector(0, 0, -3))
cutter14 = cutter14.moved(Location(Vector(0, 0, HEIGHT)))
result   = result.cut(cutter14)
try:    result = result.solids()[0]
except: pass
print("✅ Step 14 done")

# ── Step 15: Normal holes on inner wall of revolve plate ──
HOLE_LARGE_R = 90 / 2   # 45mm
HOLE_LARGE_D = 60
HOLE_SMALL_R = 22 / 2   # 11mm

plate_z_min    = -34.0596 + (HEIGHT - 156.5)
plate_z_max    = 110.4214 + (HEIGHT - 156.5)
plate_z_center = (plate_z_min + plate_z_max) / 2
print(f"Plate Z center: {plate_z_center:.2f}mm")

for pa in [0, 120, 240]:
    rad = math.radians(pa)
    cx  = -R_INNER * math.sin(rad)
    cy  =  R_INNER * math.cos(rad)
    cz  =  plate_z_center

    # ── Large pocket: 90mm dia, 60mm deep ──
    ox = cx + 10 * math.sin(rad)   # 10mm overlap bahar
    oy = cy - 10 * math.cos(rad)
    large = Solid.make_cylinder(HOLE_LARGE_R, HOLE_LARGE_D + 10)  # 70mm total
    large = large.rotate(Axis.X, -90)
    large = large.rotate(Axis.Z, pa)
    large = large.moved(Location(Vector(ox, oy, cz)))
    result = result.cut(large)
    try:    result = result.solids()[0]
    except: pass

    # ── Small thru hole: 22mm dia ──
    sx = cx + 150 * math.sin(rad)
    sy = cy - 150 * math.cos(rad)
    small = Solid.make_cylinder(HOLE_SMALL_R, 300)
    small = small.rotate(Axis.X, -90)
    small = small.rotate(Axis.Z, pa)
    small = small.moved(Location(Vector(sx, sy, cz)))
    result = result.cut(small)
    try:    result = result.solids()[0]
    except: pass

    print(f"✅ Holes at {pa}° done")
# ── Step 16: Revolve bottom face dia 310 cut 43mm ──
BOT_Z = -143.6  # revolve bottom face

# Dia 310 thru cylinder — origin centered
cyl16 = Solid.make_cylinder(375/2, 43)
cyl16 = cyl16.moved(Location(Vector(0, 0, BOT_Z)))  # Z=-143.6 to Z=-100.6

result = result.cut(cyl16)
try:    result = result.solids()[0]
except: pass
print(f"✅ Step 16 | dia310 cut from Z={BOT_Z} to Z={BOT_Z+43}")
print(f"Volume: {result.volume:.4e}")

# Scale 
result = result.scale(0.1)

export_stl(result, STL_FILE)
print("✅ STL saved:", STL_FILE)

try:
    from ocp_vscode import show, Camera
    show(result, reset_camera=Camera.RESET)
    print("✅ Preview opened")
except ImportError:
    pass