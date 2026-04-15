from build123d import *
import os
import math

STL_FILE = os.path.join(os.path.expanduser("~/Desktop"), "bot.stl")

raw_pts = [
    (2080.5935, -246.7057),
    (2095.0085,  -25.9303),
    (2095.0085,  255.0606),
    (2009.0224,  594.6109),
    (1889.3033,  905.6854),
    (1685.2792, 1244.8161),
    (1518.8295, 1443.2221),
    (1282.271,  1656.9593),
    (968.1198,  1858.0843),
    (652.7633,  1990.8876),
    (460.7339,  1985.3477),
    (329.6366,  1942.6648),
    (252.5024,  1768.5548),
    (252.5024,  1502.3666),
    (296.8857,  1186.741),
    (386.539,    886.9474),
    (473.6713,   690.1044),
    (658.6464,   389.9872),
    (854.3327,   161.5906),
    (1115.4715,  -62.1337),
    (1468.2531, -268.1625),
    (1702.8847, -359.3882),
    (1964.5255, -384.9825),
]

# Scale 0.1 only — no centering
scaled = [(x * 0.1, y * 0.1) for x, y in raw_pts]

with BuildPart() as part:

    # BASE CIRCLE — dia 480.869, extrude 30mm
    with BuildSketch(Plane.XY):
        Circle(radius=480.869 / 2)
    extrude(amount=30)

    # TOP CENTER BOSS — dia 119, extrude 30mm
    with BuildSketch(Plane.XY.offset(30)):
        Circle(radius=119 / 2)
    extrude(amount=30)

    # CENTER THROUGH HOLE — dia 50
    with BuildSketch(Plane.XY):
        Circle(radius=50 / 2)
    extrude(amount=62, mode=Mode.SUBTRACT)

    # FILLET — bottom edge of 119mm boss
    try:
        bottom_boss_edges = (
            part.edges()
            .filter_by(GeomType.CIRCLE)
            .filter_by_position(Axis.Z, 30, 30, inclusive=(True, True))
            .filter_by(lambda e: abs(e.radius - 119/2) < 1.0)
        )
        fillet(bottom_boss_edges, radius=27)
    except Exception as e:
        print(f"Fillet failed: {e}")

result = part.part

# SPOKE CUTS — 3 instances at 120 deg
for angle in [0, 120, 240]:
    rad     = math.radians(angle)
    rotated = [
        (
            x * math.cos(rad) - y * math.sin(rad),
            x * math.sin(rad) + y * math.cos(rad)
        )
        for x, y in scaled
    ]

    try:
        wire      = Wire.make_polygon([Vector(x, y, -1) for x, y in rotated], close=True)
        face      = Face(wire)
        cut_solid = Solid.extrude(face, Vector(0, 0, 32))
        result    = result - cut_solid
        print(f"Spoke cut {angle}° OK")
    except Exception as e:
        print(f"Spoke cut {angle}° failed: {e}")

if hasattr(result, 'solids'):
    result = result.solids()[0]

# Scale 0.1 then adjust to target volume 3.140e6
result = result.scale(0.1)
print(f"Volume after scale(0.1) : {result.volume:.4e} mm³")

result = result.scale(0.9893)
print(f"Volume after adjustment : {result.volume:.4e} mm³")

export_stl(result, STL_FILE)
print("✅ STL saved:", STL_FILE)

try:
    from ocp_vscode import show
    show(result, reset_camera=True)
    print("✅ 3D preview opened")
except ImportError:
    print("⚠️  pip install ocp-vscode")
    print("    then run: ocp_vscode")