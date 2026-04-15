from build123d import *
import os
import math

STL_FILE = os.path.join(os.path.expanduser("~/Desktop"), "top.stl")

# Points divided by 10 — no centering
raw_pts = [
    (53.5495  / 10, -171.8501 / 10),
    (82.2457  / 10, -160.1114 / 10),
    (108.5655 / 10, -143.5741 / 10),
    (129.6311 / 10, -124.8831 / 10),
    (149.2149 / 10, -100.6724 / 10),
    (164.5017 / 10,  -73.0698 / 10),
    (173.5906 / 10,  -47.6057 / 10),
    (179.0525 / 10,  -18.4444 / 10),
    (179.8643 / 10,    6.9875 / 10),
    (177.111  / 10,   32.1202 / 10),
    (169.7317 / 10,   59.9263 / 10),
    (134.5473 / 10,   44.685  / 10),
    (106.0052 / 10,   24.6279 / 10),
    (80.0131  / 10,   -2.9547 / 10),
    (64.5649  / 10,  -27.017  / 10),
    (50.0578  / 10,  -62.9987 / 10),
    (43.6273  / 10, -100.7668 / 10),
    (43.6273  / 10, -128.8457 / 10),
]

with BuildPart() as part:

    # BASE — dia 45mm, extrude 4.5mm
    with BuildSketch(Plane.XY):
        Circle(radius=45 / 2)
    extrude(amount=4.5)

    # TOP BOSS — dia 42.0154mm, extrude 2mm
    with BuildSketch(Plane.XY.offset(4.5)):
        Circle(radius=42.0154 / 2)
    extrude(amount=2)

    # FILLET — bottom edge of 45mm dia at z=0
    try:
        bottom_edges = (
            part.edges()
            .filter_by(GeomType.CIRCLE)
            .filter_by_position(Axis.Z, 0, 0, inclusive=(True, True))
            .filter_by(lambda e: abs(e.radius - 45/2) < 1.0)
        )
        fillet(bottom_edges, radius=1.6)
    except Exception as e:
        print(f"Fillet failed: {e}")

    # CENTER THROUGH HOLE — dia 4mm
    with BuildSketch(Plane.XY):
        Circle(radius=4 / 2)
    extrude(amount=8, mode=Mode.SUBTRACT)

    # BOTTOM CUT 1 — dia 41mm, 1.5mm deep from bottom (z=0)
    with BuildSketch(Plane.XY):
        Circle(radius=41 / 2)
    extrude(amount=1.5, mode=Mode.SUBTRACT)

    # BOTTOM CUT 2 — dia 36mm, 3mm deep from bottom (z=0)
    with BuildSketch(Plane.XY):
        Circle(radius=36 / 2)
    extrude(amount=4.5, mode=Mode.SUBTRACT)

result = part.part

# THROUGH CUTS — 3 instances at 120 deg
for angle in [0, 120, 240]:
    rad     = math.radians(angle)
    rotated = [
        (
            x * math.cos(rad) - y * math.sin(rad),
            x * math.sin(rad) + y * math.cos(rad)
        )
        for x, y in raw_pts
    ]

    try:
        wire      = Wire.make_polygon([Vector(x, y, -1) for x, y in rotated], close=True)
        face      = Face(wire)
        cut_solid = Solid.extrude(face, Vector(0, 0, 10))
        result    = result - cut_solid
        print(f"Cut {angle}° OK")
    except Exception as e:
        print(f"Cut {angle}° failed: {e}")

if hasattr(result, 'solids'):
    result = result.solids()[0]

result = result.scale(10)
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