import os
import ezdxf
from build123d import *

# =========================
# PATH
# =========================
desktop = os.path.join(os.path.expanduser("~"), "Desktop")
DXF_FILE = os.path.join(desktop, "mcu_holder.dxf")
STL_FILE = os.path.join(desktop, "mcu_holder.stl")
HEIGHT = 35

# =========================
# HOLES

HOLE1_RADIUS = 22.65 / 2
HOLE1_POINTS = [
    (-1190.0863, 637.5365),
    (-1190.0863, 585.3211),
    (-1116.3060, 637.5365),
    (-1116.3060, 585.3211),
]

HOLE2_RADIUS = 40 / 2
HOLE2_POINTS = [
    (-857.5598, 472.3736),
    (-1209.1598, 755.0436),
]

# =========================
# RECTANGLE CUT
RECT_POINTS = [
    (-1187.8030, 646.0361),
    (-1117.8030, 646.0361),
    (-1117.8030, 576.0361),
    (-1187.8030, 576.0361),
]
CUT_DEPTH = 20

# =========================
# ✅ NEW FEATURE (FROM 3D POINTS)

FEATURE_POINTS = [
    (-1101.7748, 434.7471),
    (-1101.7748, 533.6408),
    (-1103.3263, 541.2825),
    (-1105.4893, 545.1961),
    (-1109.3050, 549.2775),
    (-1115.1693, 552.5185),
    (-1118.4300, 553.3273),
    (-1177.8944, 553.5780),
    (-1183.3804, 552.5185),
    (-1189.0223, 549.4522),
    (-1192.4115, 546.1107),
    (-1196.4917, 536.9940),
    (-1196.7748, 526.3978),
    (-1196.7748, 517.4829),
    (-1196.7748, 498.6980),
    (-1196.7748, 490.4199),
    (-1196.7748, 479.2763),
    (-1196.8831, 438.2042),
    (-1190.5122, 436.6123),
    (-1181.7748, 435.9783),
    (-1181.7748, 538.6408),
    (-1116.7748, 538.6408),
    (-1116.7748, 434.3736),
    (-1101.7748, 434.3736),
]

FEATURE_HEIGHT = 70
FEATURE_Z_START = -69.9  # from your 3D data

# =========================
# READ DXF
# =========================
doc = ezdxf.readfile(DXF_FILE)
msp = doc.modelspace()
loops = []

for e in msp:
    if e.dxftype() == "LWPOLYLINE" and e.closed:
        pts = [(round(float(p[0]), 6), round(float(p[1]), 6)) for p in e.get_points()]
        cleaned = [pts[0]]
        for pt in pts[1:]:
            if pt != cleaned[-1]:
                cleaned.append(pt)
        if cleaned[0] != cleaned[-1]:
            cleaned.append(cleaned[0])
        loops.append(cleaned)

def polygon_area(poly):
    return abs(sum(
        poly[i][0] * poly[(i+1) % len(poly)][1] - poly[(i+1) % len(poly)][0] * poly[i][1]
        for i in range(len(poly))
    ) / 2)

loops.sort(key=polygon_area, reverse=True)
outer  = loops[0]
inners = loops[1:]

# =========================
# BUILD BASE PART
# =========================
with BuildPart() as part:

    outer_wire = Wire.make_polygon([Vector(x, y) for x, y in outer])
    outer_face = Face(outer_wire)
    extrude(outer_face, amount=HEIGHT)

    for loop in inners:
        inner_wire = Wire.make_polygon([Vector(x, y) for x, y in loop])
        inner_face = Face(inner_wire)
        extrude(inner_face, amount=HEIGHT, mode=Mode.SUBTRACT)

# =========================
# HOLES
# =========================
for x, y in HOLE1_POINTS:
    cyl = Cylinder(HOLE1_RADIUS, HEIGHT + 10, align=(Align.CENTER,)*3)
    cyl = cyl.located(Location((x, y, HEIGHT / 2)))
    part.part -= cyl

for x, y in HOLE2_POINTS:
    cyl = Cylinder(HOLE2_RADIUS, HEIGHT + 10, align=(Align.CENTER,)*3)
    cyl = cyl.located(Location((x, y, HEIGHT / 2)))
    part.part -= cyl

# =========================
# RECTANGLE CUT
# =========================
xs = [p[0] for p in RECT_POINTS]
ys = [p[1] for p in RECT_POINTS]

cut_box = Box(
    max(xs) - min(xs),
    max(ys) - min(ys),
    CUT_DEPTH,
    align=(Align.CENTER, Align.CENTER, Align.MIN)
)

cut_box = cut_box.located(Location(
    ((min(xs)+max(xs))/2, (min(ys)+max(ys))/2, HEIGHT - CUT_DEPTH)
))

part.part -= cut_box

# =========================
# ✅ FINAL FEATURE ADD (CORRECT 3D POSITION)
# =========================

feature_wire = Wire.make_polygon([Vector(x, y) for x, y in FEATURE_POINTS])
feature_face = Face(feature_wire)

feature_solid = extrude(feature_face, amount=FEATURE_HEIGHT)

# Place at correct Z from your data
feature_solid = feature_solid.located(Location((0, 0, FEATURE_Z_START)))

# Fuse
part.part = part.part.fuse(feature_solid)
# =========================
# ✅ FINAL FEATURE (CLEAN PROFILE + COPY 120 mm)
# =========================

NEW_FEATURE_POINTS = [
    (-906.6962, 744.8626),
    (-907.1976, 749.3130),
    (-908.6768, 753.5403),
    (-911.0595, 757.3324),
    (-914.2264, 760.4992),
    (-919.0546, 763.3111),
    (-924.4569, 764.7368),
    (-947.8355, 764.7368),
    (-953.2378, 763.3111),
    (-956.2368, 761.7971),
    (-959.7383, 759.0047),
    (-962.5307, 755.5032),
    (-964.4738, 751.4682),
    (-965.2826, 748.2074),
    (-965.5333, 745.9822),
    (-965.5962, 744.8626),
]

NEW_FEATURE_HEIGHT = 72.8
NEW_FEATURE_Z = -72

# ---- Feature 1 ----
wire1 = Wire.make_polygon([Vector(x, y) for x, y in NEW_FEATURE_POINTS])
face1 = Face(wire1)

solid1 = extrude(face1, amount=NEW_FEATURE_HEIGHT)
solid1 = solid1.located(Location((0, 0, NEW_FEATURE_Z)))

# ---- Feature 2 (LEFT copy -120 mm) ----
SHIFTED_POINTS = [(x - 113, y) for x, y in NEW_FEATURE_POINTS]

wire2 = Wire.make_polygon([Vector(x, y) for x, y in SHIFTED_POINTS])
face2 = Face(wire2)

solid2 = extrude(face2, amount=NEW_FEATURE_HEIGHT)
solid2 = solid2.located(Location((0, 0, NEW_FEATURE_Z)))

# ---- ADD (UNION) ----
part.part = part.part.fuse(solid1)
part.part = part.part.fuse(solid2)
# =========================
# ✅ NEW FEATURE (Z = -112.8, EXTRUDE 25 mm)
# =========================

NEW_FEATURE2_POINTS = [
    (-962.5159, 717.6237),
    (-960.7505, 724.3792),
    (-958.5168, 729.4382),
    (-953.5266, 736.0462),
    (-948.1290, 740.3622),
    (-943.1733, 742.8298),
    (-935.1041, 744.7277),
    (-1049.5681, 744.7277),
    (-1041.4988, 742.8298),
    (-1037.7535, 741.0364),
    (-1032.1252, 737.0260),
    (-1028.3956, 732.9347),
    (-1025.4811, 728.2278),
    (-1023.4813, 723.0656),
    (-1022.4640, 717.6237),
    (-962.2081, 717.6237),
]

NEW_FEATURE2_HEIGHT = 25
NEW_FEATURE2_Z = -72.0


# ---- Create feature ----
wire = Wire.make_polygon([Vector(x, y) for x, y in NEW_FEATURE2_POINTS])
face = Face(wire)

solid = extrude(face, amount=NEW_FEATURE2_HEIGHT)

# ---- Place at correct Z ----
solid = solid.located(Location((0, 0, NEW_FEATURE2_Z)))

# ---- ADD (UNION) ----
part.part = part.part.fuse(solid)
# =========================
# ✅ TWO CIRCULAR HOLES (UPDATED POSITION)
# =========================

HOLE_RADIUS = 25 / 2
HOLE_DEPTH = 20

HOLE_CENTERS = [
    (-912.8237, 454.0096),
    (-1066.2577, 454.0096),
]

for (x, y) in HOLE_CENTERS:
    hole = Cylinder(
        HOLE_RADIUS,
        HOLE_DEPTH + 50,   # ensures full intersection
        align=(Align.CENTER, Align.CENTER, Align.CENTER)
    )
    
    # place through the part
    hole = hole.located(Location((x, y, 0)))
    
    # CUT
    part.part -= hole
# =========================
# ✅ RECTANGULAR CUT (UPDATED POINTS, 50 mm DEPTH)
# =========================

RECT_POINTS = [
    (-1123.1195, 434.3736),
    (-1092.8378, 434.3736),
    (-1092.8378, 537.6198),
    (-1123.1195, 537.6198),
]

CUT_DEPTH = 90
CUT_Z = -110  # from your points

# ---- Create rectangle profile ----
wire = Wire.make_polygon([Vector(x, y) for x, y in RECT_POINTS])
face = Face(wire)

# ---- Create cutting solid ----
cut_solid = extrude(face, amount=CUT_DEPTH)

# ---- Place at correct Z ----
cut_solid = cut_solid.located(Location((0, 0, CUT_Z)))

# ---- SUBTRACT ----
part.part -= cut_solid
# =========================
# ✅ NEW FEATURE (ADD 20 mm FROM Z = -110)
# =========================

NEW_FEATURE_POINTS = [
    (-1131.2585, 537.6198),
    (-1167.2910, 537.6198),
    (-1165.8926, 537.1508),
    (-1164.7370, 536.6219),
    (-1163.9203, 536.2067),
    (-1163.1731, 535.6765),
    (-1161.1025, 533.8789),
    (-1159.5285, 531.6335),
    (-1158.4213, 529.1250),
    (-1157.8869, 525.5093),
    (-1157.8869, 492.9914),
    (-1140.6459, 492.9914),
    (-1140.6626, 525.5093),
    (-1140.3283, 528.2309),
    (-1139.4711, 530.8355),
    (-1138.0090, 533.1552),
    (-1135.3764, 535.6765),
    (-1131.2585, 537.6198),
]

FEATURE_HEIGHT = 20
FEATURE_Z = -70

# =========================
# ✅ Ø25 THROUGH HOLE (FORCED ALONG Y AXIS)
# =========================

HOLE_RADIUS = 25 / 2

cx, cy, cz = -1148.9000, 553.1092, -35

# ---- Create cylinder ----
hole = Cylinder(HOLE_RADIUS, 400)

# ---- Apply rotation CORRECTLY ----
hole = hole.located(
    Location((cx, cy, cz)) * Rotation(Axis.X, 90)
)

# ---- CUT ----
part.part -= hole
# =========================
# AUTO SCALE
# =========================
TARGET_VOLUME = 4.397e6

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
# ✅ FINAL EXPORT (UPDATED)
# =========================

import os

if os.path.exists(STL_FILE):
    os.remove(STL_FILE)

export_stl(part.part, STL_FILE)

print("✅ STL UPDATED:", STL_FILE)