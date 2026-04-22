from build123d import *
import math, os

STL_FILE = os.path.expanduser("~/Desktop/NewPlate.stl")

# ── Step 1: Base plate ──
pts_raw = [
    (-750.7797, 268.0762, 79.0735), (-744.5175, 240.0729, 79.0735),
    (-733.3825, 217.8029, 79.0735), (-718.3174, 204.0478, 79.0735),
    (-700.6324, 193.5678, 79.0735), (-682.1679, 191.1378, 79.0735),
    (-516.1054, 191.1378, 79.0735), (-492.4127, 199.4511, 79.0735),
    (-478.7852, 215.0253, 79.0735), (-465.1578, 240.3335, 79.0735),
    (-453.4771, 261.7481, 79.0735), (-441.7964, 279.2691, 79.0735),
    (-417.4616, 289.9764, 79.0735), (-270.4797, 289.9764, 79.0735),
    (-245.5134, 289.9764, 79.0735), (-218.0126, 279.7331, 79.0735),
    (-200.3335, 270.5661, 79.0735), (-183.3092, 256.161,  79.0735),
    (-168.904,  237.8271, 79.0735), (-157.118,  214.9097, 79.0735),
    (-145.3319, 191.9924, 79.0735), (-134.8554, 169.7298, 79.0735),
    (-117.1763, 150.7412, 79.0735), (-87.7112,  138.9551, 79.0735),
    ( 142.8462,  93.432,  79.0735), ( 139.177,   81.943,  79.0735),
    ( 135.5904,  72.8279, 79.0735), ( 131.6014,  66.691,  79.0735),
    ( 125.4645,  61.1678, 79.0735), ( 116.2592,  53.4967, 79.0735),
    ( 106.1333,  46.4392, 79.0735), (  92.939,   38.7681, 79.0735),
    (  68.8283,  31.3894, 79.0735), (  55.8819,  27.0739, 79.0735),
    (  46.8194,  20.6006, 79.0735), (  36.8937,   7.2226, 79.0735),
    (  33.8729,  -8.7447, 79.0735), (  36.8937, -31.6167, 79.0735),
    (  44.1482, -44.3902, 79.0735), (  86.5787, -83.7681, 79.0735),
    ( 101.5266, -90.1896, 79.0735), ( 123.2552, -94.0896, 79.0735),
    ( 145.5409, -83.7681, 79.0735), ( 161.141,  -65.6753, 79.0735),
    ( 200.6982,  -2.1609, 79.0735), ( 210.1696,   5.6391, 79.0735),
    ( 222.4268,  11.7677, 79.0735), ( 286.4984,  19.5677, 79.0735),
    ( 367.3521, -35.6824, 79.0735), ( 395.345,  -49.4244, 79.0735),
    ( 417.2303, -56.5498, 79.0735), ( 438.0976, -54.0212, 79.0735),
    ( 450.453,  -47.0087, 79.0735), ( 461.2313, -35.0491, 79.0735),
    ( 550.6895,  81.6179, 79.0735), ( 558.0649,  95.4045, 79.0735),
    ( 561.814,  109.2762, 79.0735), ( 562.9387, 122.0231, 79.0735),
    ( 561.0431, 135.6639, 79.0735), ( 556.8964, 149.8656, 79.0735),
    ( 548.5197, 167.6252, 79.0735), ( 533.071,  189.304,  79.0735),
    ( 513.8092, 209.176,  79.0735), ( 491.6711, 227.3609, 79.0735),
    ( 410.4978, 290.6128, 79.0735), ( 396.0413, 306.1484, 79.0735),
    ( 388.7552, 322.0063, 79.0735), ( 386.1836, 339.5786, 79.0735),
    ( 386.1836, 362.7226, 79.0735), ( 409.914,  649.9496, 79.0735),
    ( 411.1693, 689.3593, 79.0735), ( 411.1693, 721.1912, 79.0735),
    ( 409.1272, 750.1095, 79.0735), ( 377.084,  1022.2867,79.0735),
    ( 374.0949, 1045.6202,79.0735), ( 365.4542, 1062.4468,79.0735),
    ( 349.9919, 1080.183, 79.0735), ( 324.0698, 1093.3714,79.0735),
    ( 283.5949, 1097.9192,79.0735), ( -31.0713, 1097.9192,79.0735),
    ( -56.3291, 1116.7914,79.0735), ( -84.2752, 1129.5225,79.0735),
    (-107.8742, 1131.3855,79.0735), (-473.2522, 1096.4251,79.0735),
    (-502.8661, 1090.2871,79.0735), (-526.8301, 1079.4741,79.0735),
    (-546.7026, 1064.5697,79.0735), (-566.5751, 1044.1127,79.0735),
    (-599.6966, 1000.12,  79.0735), (-608.522,   990.0688,79.0735),
    (-616.612,   983.94,  79.0735), (-627.8889,  978.7919,79.0735),
    (-638.9207,  977.5661,79.0735), (-667.1419,  969.0524,79.0735),
    (-700.6303,  955.0989,79.0735), (-721.7599,  940.7467,79.0735),
    (-737.3081,  925.5972,79.0735), (-746.0789,  908.4543,79.0735),
    (-748.8696,  896.0955,79.0735), (-750.7797,  882.8097,79.0735),
]

pts    = [(x*0.1, y*0.1, z*0.1) for x, y, z in pts_raw]
wire_p = Wire.make_polygon([Vector(x, y, 7.9) for x, y, z in pts], close=True)
result = Solid.extrude(Face(wire_p), Vector(0, 0, 2))
print(f"✅ Base plate | Volume: {result.volume:.4e}")

# ── Step 2: Hex pattern ──
hex_raw = [
    (232.5408, 698.6226), (203.7155, 748.477),
    (232.5408, 798.2639), (290.4683, 798.2639),
    (318.8207, 748.477),  (290.4683, 698.6226),
]
hex_pts = [(x*0.1, y*0.1) for x, y in hex_raw]
cx = sum(p[0] for p in hex_pts) / len(hex_pts)
cy = sum(p[1] for p in hex_pts) / len(hex_pts)
xs = [p[0] for p in hex_pts]
ys = [p[1] for p in hex_pts]
hex_w = max(xs) - min(xs)
hex_h = max(ys) - min(ys)

GAP    = 3.5
step_x = hex_w + GAP
step_y = hex_h + GAP

# Plate outline scaled 0.1 for point-in-polygon check
plate_pts = [(x*0.1, y*0.1) for x, y, z in pts_raw]

def point_in_polygon(px, py, polygon):
    n      = len(polygon)
    inside = False
    j      = n - 1
    for i in range(n):
        xi, yi = polygon[i]
        xj, yj = polygon[j]
        if ((yi > py) != (yj > py)) and (px < (xj-xi)*(py-yi)/(yj-yi+1e-10)+xi):
            inside = not inside
        j = i
    return inside

bb             = result.bounding_box()
x_min, x_max   = bb.min.X, bb.max.X
y_min, y_max   = bb.min.Y, bb.max.Y

count = 0
row   = 0
x     = x_min

while x < x_max + step_x:
    y_start = y_min + (step_y/2 * (row % 2))
    y       = y_start
    while y < y_max + step_y:
        offset_x = x - cx
        offset_y = y - cy
        verts    = [(px + offset_x, py + offset_y) for px, py in hex_pts]

        # All vertices must be inside plate outline
        if all(point_in_polygon(vx, vy, plate_pts) for vx, vy in verts):
            wire_h = Wire.make_polygon(
                [Vector(vx, vy, 0) for vx, vy in verts],
                close=True
            )
            cutter = Solid.extrude(Face(wire_h), Vector(0, 0, 500))
            cutter = cutter.moved(Location(Vector(0, 0, -250)))
            result = result.cut(cutter)
            try:    result = result.solids()[0]
            except: pass
            count += 1

        y += step_y
    x   += step_x
    row += 1

print(f"✅ {count} hex cuts | Volume: {result.volume:.4e}")
# Step 3: Annular ring boss 2mm down + dia97 cut 1mm deep
boss_pts_raw = [
    (-649.7547, 271.1265, 89.0735),
    (   0.0,    200.3289, 89.0735),
    ( 435.3279,  75.0496, 89.0735),
    ( 284.0759, 994.1552, 89.0735),
    (-648.8489, 857.5246, 89.0735),
]

boss_pts = [(x*0.1, y*0.1, z*0.1) for x, y, z in boss_pts_raw]

bb    = result.bounding_box()
z_top = bb.max.Z

for bx, by, bz in boss_pts:
    # dia14 — 2mm boss, top face aligned (z_top-2 to z_top)
    boss14 = Solid.make_cylinder(14.0/2, 2)
    boss14 = boss14.moved(Location(Vector(bx, by, z_top - 2)))
    result = result.fuse(boss14)
    try:    result = result.solids()[0]
    except: pass

    # dia9.7 — 1mm cut from top face
    cut97 = Solid.make_cylinder(9.7/2, 1)
    cut97 = cut97.moved(Location(Vector(bx, by, z_top - 1)))
    result = result.cut(cut97)
    try:    result = result.solids()[0]
    except: pass

    print(f"✅ Boss at ({bx:.1f}, {by:.1f})")

print(f"Volume: {result.volume:.4e}")
# ── Step 4: Countersink holes on actual part ─────────────────

SCALE    = 0.1
TOP_DIA  = 8.0
BOT_DIA  = 4.0
ANGLE    = 90

raw_points = [
    (-531.3222, 952.1196, 89.0735),
    (-471.8245, 342.4485, 89.0735),
    (-91.796, 217.904, 89.0735),
    (396.84, 253.658, 89.0735),
    (371.239, 582.758, 89.0735),
    (77.468, -10.3012, 89.0735),
]

pts = [(x*SCALE, y*SCALE, z*SCALE) for x,y,z in raw_points]

bb = result.bounding_box()
z_top = bb.max.Z

cs_depth = ((TOP_DIA - BOT_DIA)/2) / math.tan(math.radians(ANGLE/2))

print(f"Countersink depth: {cs_depth:.3f} mm")

for px, py, pz in pts:

    # --- Through hole (Ø4) ---
    hole = Solid.make_cylinder(BOT_DIA/2, 100)
    hole = hole.moved(Location(Vector(px, py, z_top - 100)))

    # ✅ FIXED CONE (direction corrected)
    cone = Solid.make_cone(
        BOT_DIA/2,   # 🔥 bottom = 4mm
        TOP_DIA/2,   # 🔥 top = 8mm
        cs_depth
    )
    cone = cone.moved(Location(Vector(px, py, z_top - cs_depth)))

    # --- Cut ---
    result = result.cut(hole)
    result = result.cut(cone)

    try:
        result = result.solids()[0]
    except:
        pass

    print(f"✅ Countersink at ({px:.1f}, {py:.1f})")

print(f"✅ Final Volume: {result.volume:.4e}")

export_stl(result, STL_FILE)
print("✅ STL saved:", STL_FILE)

try:
    from ocp_vscode import show, Camera
    show(result, reset_camera=Camera.RESET)
    print("✅ Preview opened")
except ImportError:
    pass