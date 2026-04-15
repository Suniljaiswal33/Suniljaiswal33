from build123d import *
import os
import math

STL_FILE = os.path.join(os.path.expanduser("~/Desktop"), "trackpad_holder.stl")

raw_pts = [
    (1811.5266, -221.351),
    (1824.9072,   18.4061),
    (1808.7579,  242.9397),
    (1766.1387,  459.76),
    (1701.9509,  658.7777),
    (1570.4801,  929.6329),
    (1431.7417, 1131.6981),
    (1270.0674, 1310.5548),
    (1090.2602, 1463.5429),
    (900.9049,  1587.1343),
    (714.0678,  1679.5036),
    (789.2983,  1601.6633),
    (798.4327,  1558.3385),
    (790.7042,  1505.5944),
    (577.7697,   901.042),
    (529.2708,   759.624),
    (520.8768,   572.8053),
    (590.6908,   354.1827),
    (707.028,    205.6718),
    (869.6273,    98.9227),
    (1059.5481,   49.8423),
    (1699.2351,  -68.0272),
    (1754.6899,  -91.7255),
    (1789.3224, -127.6256),
    (1807.6407, -167.9085),
]

scaled_pts = [(x * 0.1, y * 0.1) for x, y in raw_pts]

HOLE_CX = -(1108.513 * 0.1)
HOLE_CY = -(-640.0   * 0.1)
HOLE_R  = 593.53 / 2 * 0.1

# ── BASE CYLINDER WITH CUTS ─────────────────────────────
with BuildPart() as base_part:

    with BuildSketch(Plane.XY):
        Circle(radius=425 / 2)
    extrude(amount=90)

    with BuildSketch(Plane.XY.offset(90)):
        Circle(radius=407.556 / 2)
    extrude(amount=-15, mode=Mode.SUBTRACT)

    with BuildSketch(Plane.XY.offset(75)):
        Circle(radius=365 / 2)
    extrude(amount=-75, mode=Mode.SUBTRACT)

base_solid = base_part.part
print("Base OK")

# ── STEP 1 — PROFILE FUSE x3 ───────────────────────────
for angle in [0, 120, 240]:
    rad         = math.radians(angle)
    rotated_pts = [
        (
            x * math.cos(rad) - y * math.sin(rad),
            x * math.sin(rad) + y * math.cos(rad)
        )
        for x, y in scaled_pts
    ]
    try:
        wire          = Wire.make_polygon([Vector(x, y, 0) for x, y in rotated_pts], close=True)
        face          = Face(wire)
        profile_solid = Solid.extrude(face, Vector(0, 0, 60))
        base_solid    = base_solid.fuse(profile_solid)
        print(f"Profile fuse {angle}° OK")
    except Exception as e:
        print(f"Profile {angle}° failed: {e}")

# ── STEP 2 — HOLE CUT x3 ───────────────────────────────
for angle in [0, 120, 240]:
    rad = math.radians(angle)
    cx  = HOLE_CX * math.cos(rad) - HOLE_CY * math.sin(rad)
    cy  = HOLE_CX * math.sin(rad) + HOLE_CY * math.cos(rad)

    try:
        cyl        = Cylinder(radius=HOLE_R, height=200)
        cyl        = cyl.moved(Location((cx, cy, -1)))
        base_solid = base_solid - cyl
        print(f"Hole {angle}° OK  center=({cx:.2f}, {cy:.2f})")
    except Exception as e:
        print(f"Hole {angle}° failed: {e}")

result = base_solid
# After result is built, add these lines before export
result = result.scale(0.1)

TARGET_VOLUME = 5.339e6
current_volume = result.volume
adjust_scale = (TARGET_VOLUME / current_volume) ** (1/3)
result = result.scale(adjust_scale)
print(f"Adjust scale : {adjust_scale:.6f}")
print(f"Final volume : {result.volume:.4e} mm³")

print(f"\nVolume: {result.volume:.4e} mm³")
export_stl(result, STL_FILE)
print("✅ STL saved:", STL_FILE)

try:
    from ocp_vscode import show
    show(result, reset_camera=True)
    print("✅ 3D preview opened")
except ImportError:
    print("⚠️  pip install ocp-vscode")
    print("    then run: ocp_vscode")