from build123d import *
import os
import math

STL_FILE = os.path.join(os.path.expanduser("~/Desktop"), "adapter_v4_bottom_v17.stl")

HEIGHT      = 47
PCD_35      = 335 / 2
PCD_50      = 371 / 2
CS_OUTER_R  = 75 / 2
CS_INNER_R  = 35 / 2
CS_DEPTH    = CS_OUTER_R - CS_INNER_R
HOLE_50_R   = 50 / 2

ANGLE_35_1 = 58.6
ANGLE_35_2 = ANGLE_35_1 + 120
ANGLE_35_3 = ANGLE_35_2 + 100

ANGLE_50_1 = ANGLE_35_1 + 64
ANGLE_50_2 = ANGLE_50_1 + 180

raw_pts = [
    (1270.5658,    0.0),
    (2222.883,     0.0),
    (2222.883,  -1434.5),
    (1679.563,  -1434.5),
    (1580.6121, -1124.3076),
    (1480.3932,  -933.8006),
    (1389.4995,  -802.5871),
    (1270.5658,  -665.962),
]
scaled = [(x * 0.1, y * 0.1) for x, y in raw_pts]

TAB_OUTER_R  = 222.2883
TAB_INNER_R  = 127.0566
TAB_BOTTOM_Z = -1434.5 * 0.1
SLOT_W       = 27
SLOT_D       = 100
SLOT_L       = (TAB_OUTER_R - TAB_INNER_R) + 20

HOLE_30_R  = 30 / 2
HOLE_30_Y  = 1872.883 * 0.1
HOLE_30_Z  = -1034.5  * 0.1

cut_pts_1 = [
    (-389.1923 * 0.1,  2241.9024 * 0.1),
    ( 686.1469 * 0.1,  3195.7411 * 0.1),
    (3265.4669 * 0.1,  1392.3142 * 0.1),
    (2270.1606 * 0.1,   154.8153 * 0.1),
]

cut_pts_2 = [
    (-487.1169 * 0.1, -1171.0789 * 0.1),
    (1273.6866 * 0.1,   -28.704  * 0.1),
    (1266.0968 * 0.1,  -131.2523 * 0.1),
    (1246.7653 * 0.1,  -269.3344 * 0.1),
    (1213.7334 * 0.1,  -391.3436 * 0.1),
    (1319.9908 * 0.1,  -430.1711 * 0.1),
    (1252.0196 * 0.1,  -599.8914 * 0.1),
    (1158.5222 * 0.1,  -765.0158 * 0.1),
    (1040.1417 * 0.1,  -919.526  * 0.1),
    ( 845.9566 * 0.1,  -893.0759 * 0.1),
    ( 714.8056 * 0.1,  -919.526  * 0.1),
    ( 580.9567 * 0.1,  -990.5485 * 0.1),
    ( 457.0053 * 0.1, -1125.2781 * 0.1),
    ( 384.7466 * 0.1, -1333.9389 * 0.1),
    ( 127.6612 * 0.1, -1378.6708 * 0.1),
    (-121.692  * 0.1, -1382.9728 * 0.1),
    (-288.1023 * 0.1, -1358.0942 * 0.1),
    (-266.6149 * 0.1, -1235.9093 * 0.1),
    (-393.6504 * 0.1, -1202.7696 * 0.1),
]

cut_pts_3 = [
    ( -876.241  * 0.1,  1186.5188 * 0.1),
    ( -364.5012 * 0.1,   638.2283 * 0.1),
    (-1357.9122 * 0.1,  -288.9589 * 0.1),
    (-1411.7883 * 0.1,  -288.9589 * 0.1),
    (-1441.6835 * 0.1,  -263.4353 * 0.1),
    (-1458.6407 * 0.1,  -219.0716 * 0.1),
    (-1473.1846 * 0.1,    73.1591 * 0.1),
    (-1458.6407 * 0.1,   308.6141 * 0.1),
    (-1355.8334 * 0.1,   580.8105 * 0.1),
    (-1214.8088 * 0.1,   836.5792 * 0.1),
    (-1098.1965 * 0.1,   984.6773 * 0.1),
    ( -987.2278 * 0.1,  1095.9043 * 0.1),
]

with BuildPart() as part:

    with BuildSketch(Plane.XY):
        Circle(radius=445.467 / 2)
        Circle(radius=254.411 / 2, mode=Mode.SUBTRACT)
    extrude(amount=HEIGHT)

    for angle in [ANGLE_50_1, ANGLE_50_2]:
        rad = math.radians(angle)
        cx  = PCD_50 * math.cos(rad)
        cy  = PCD_50 * math.sin(rad)
        with BuildSketch(Plane.XY):
            with Locations((cx, cy)):
                Circle(radius=HOLE_50_R)
        extrude(amount=HEIGHT + 2, mode=Mode.SUBTRACT)
        print(f"50mm hole at {angle:.1f}°")

result = part.part

for angle in [ANGLE_35_1, ANGLE_35_2, ANGLE_35_3]:
    rad = math.radians(angle)
    cx  = PCD_35 * math.cos(rad)
    cy  = PCD_35 * math.sin(rad)
    try:
        cone = Cone(bottom_radius=CS_INNER_R, top_radius=CS_OUTER_R, height=CS_DEPTH)
        cone = cone.moved(Location((cx, cy, HEIGHT - CS_DEPTH / 2)))
        result = result - cone
        cyl = Cylinder(radius=CS_INNER_R, height=HEIGHT + 2)
        cyl = cyl.moved(Location((cx, cy, -1)))
        result = result - cyl
        print(f"CS hole at {angle:.1f}°")
    except Exception as e:
        print(f"CS hole failed: {e}")

try:
    with BuildPart() as rev_part:
        with BuildSketch(Plane.XZ):
            with BuildLine():
                Polyline(*scaled, close=True)
            make_face()
        revolve(axis=Axis.Z, revolution_arc=35.4)
    rev_solid = rev_part.part
    rev_solid = rev_solid.rotate(Axis.Z, -17.7)

    slot_cx   = (TAB_OUTER_R + TAB_INNER_R) / 2
    box       = Box(SLOT_L, SLOT_W, SLOT_D)
    box       = box.moved(Location((slot_cx, 0, TAB_BOTTOM_Z + SLOT_D / 2)))
    rev_solid = rev_solid - box
    print("Slot cut OK")

    cyl_hole  = Cylinder(radius=HOLE_30_R, height=400)
    cyl_hole  = cyl_hole.rotate(Axis.X, 90)
    cyl_hole  = cyl_hole.moved(Location((HOLE_30_Y, 0, HOLE_30_Z)))
    rev_solid = rev_solid - cyl_hole
    print("30mm hole OK")

    try:
        all_edges = rev_solid.edges()
        min_z = min(e.center().Z for e in all_edges)
        bottom_edges = (
            rev_solid.edges()
            .filter_by_position(Axis.Z, min_z - 0.1, min_z + 0.1, inclusive=(True, True))
        )
        print(f"Bottom edges: {len(bottom_edges)}")
        fillet(bottom_edges, radius=10)
        print("Fillet OK")
    except Exception as e:
        print(f"Fillet failed: {e}")

    for angle in [0, 120, 240]:
        instance = rev_solid.rotate(Axis.Z, angle)
        result   = result.fuse(instance)
        print(f"Tab {angle}° OK")

except Exception as e:
    print(f"Tab failed: {e}")

# PROFILE CUT 1 — depth 12mm (badha ke extra material hatao)
try:
    wire      = Wire.make_polygon([Vector(x, y, HEIGHT) for x, y in cut_pts_1], close=True)
    face      = Face(wire)
    cut_solid = Solid.extrude(face, Vector(0, 0, -12))
    result    = result - cut_solid
    print("Profile cut 1 OK")
except Exception as e:
    print(f"Profile cut 1 failed: {e}")

# PROFILE EXTRUDE 2 — depth 5mm (kam karo)
try:
    wire      = Wire.make_polygon([Vector(x, y, 0) for x, y in cut_pts_2], close=True)
    face      = Face(wire)
    add_solid = Solid.extrude(face, Vector(0, 0, -5))
    result    = result.fuse(add_solid)
    print("Profile extrude 2 OK")
except Exception as e:
    print(f"Profile extrude 2 failed: {e}")

# PROFILE EXTRUDE 3 — depth 5mm (kam karo)
try:
    wire      = Wire.make_polygon([Vector(x, y, 0) for x, y in cut_pts_3], close=True)
    face      = Face(wire)
    add_solid = Solid.extrude(face, Vector(0, 0, -5))
    result    = result.fuse(add_solid)
    print("Profile extrude 3 OK")
except Exception as e:
    print(f"Profile extrude 3 failed: {e}")

print(f"\nVolume        : {result.volume:.4e} mm³")
print(f"Target        : 6.798e6")
print(f"Diff          : {((result.volume - 6.798e6) / 6.798e6 * 100):.2f}%")

export_stl(result, STL_FILE)
print("✅ STL saved:", STL_FILE)

try:
    from ocp_vscode import show
    show(result, reset_camera=True)
    print("✅ 3D preview opened")
except ImportError:
    print("⚠️  pip install ocp-vscode")
    print("    then run: ocp_vscode")