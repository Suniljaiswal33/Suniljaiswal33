from build123d import *
import os

STL_FILE = os.path.join(os.path.expanduser("~/Desktop"), "sensor_cover_v51.stl")

P1 = (-615.343 * 0.1,  1737.675 * 0.1)
P2 = ( 615.343 * 0.1, -1737.675 * 0.1)

OUTER_R = 100 / 2
INNER_R = 30  / 2
BOSS_H  = 35
TOTAL_H = 10 + BOSS_H

# Cut profile points — divide by 10
cut_pts = [
    (-1111.8106 / 10, -1347.0972 / 10),
    (-1061.5078 / 10, -1326.3108 / 10),
    (-1029.1061 / 10, -1302.3781 / 10),
    (-1006.7761 / 10, -1273.3697 / 10),
    (-992.9349  / 10, -1238.3209 / 10),
    (-989.5173  / 10, -1214.9837 / 10),
    (-990.8137  / 10, -1187.4399 / 10),
    (-1500.5365 / 10,   56.1627  / 10),
    (-1524.3244 / 10,  113.7291  / 10),
    (-1552.3551 / 10,  156.1441  / 10),
    (-1592.2189 / 10,  184.0586  / 10),
    (-1639.9614 / 10,  195.8108  / 10),
    (-1692.0308 / 10,  188.3002  / 10),
    (-2019.3183 / 10,   53.2346  / 10),
    (-2051.4842 / 10,   39.9429  / 10),
    (-2092.5715 / 10,   31.3842  / 10),
    (-2141.1579 / 10,   36.9938  / 10),
    (-2177.649  / 10,   53.7726  / 10),
    (-2213.195  / 10,   86.5587  / 10),
    (-2231.3622 / 10,  117.8605  / 10),
    (-2241.9305 / 10,  184.2634  / 10),
    (-2712.6317 / 10,   85.611   / 10),
    (-1836.1033 / 10, -2290.6973 / 10),
    (-1437.3625 / 10, -1731.037  / 10),
    (-1490.1844 / 10, -1673.5147 / 10),
    (-1501.9989 / 10, -1645.0607 / 10),
    (-1507.6846 / 10, -1606.291  / 10),
    (-1501.9989 / 10, -1565.6142 / 10),
    (-1485.4777 / 10, -1529.2225 / 10),
    (-1464.278  / 10, -1503.3416 / 10),
    (-1427.1478 / 10, -1477.6231 / 10),
]

with BuildPart() as part:

    # BASE — dia 450mm, extrude 10mm
    with BuildSketch(Plane.XY):
        Circle(radius=450 / 2)
    extrude(amount=10)

    # BOSS 1 — dia 100mm, extrude 35mm at P1
    with BuildSketch(Plane.XY.offset(10)):
        with Locations(P1):
            Circle(radius=OUTER_R)
    extrude(amount=BOSS_H)

    # BOSS 2 — dia 100mm, extrude 35mm at P2
    with BuildSketch(Plane.XY.offset(10)):
        with Locations(P2):
            Circle(radius=OUTER_R)
    extrude(amount=BOSS_H)

    # THROUGH HOLE 1 — dia 30mm full height
    with BuildSketch(Plane.XY):
        with Locations(P1):
            Circle(radius=INNER_R)
    extrude(amount=TOTAL_H + 2, mode=Mode.SUBTRACT)

    # THROUGH HOLE 2 — dia 30mm full height
    with BuildSketch(Plane.XY):
        with Locations(P2):
            Circle(radius=INNER_R)
    extrude(amount=TOTAL_H + 2, mode=Mode.SUBTRACT)

    # TRIM — remove everything outside dia 450mm
    with BuildSketch(Plane.XY):
        Circle(radius=700 / 2)
        Circle(radius=450 / 2, mode=Mode.SUBTRACT)
    extrude(amount=TOTAL_H + 2, mode=Mode.SUBTRACT)

    # FILLET — bottom edge of bosses at z=10, r=50
    try:
        boss_edges = (
            part.edges()
            .filter_by(GeomType.CIRCLE)
            .filter_by_position(Axis.Z, 10, 10, inclusive=(True, True))
            .filter_by(lambda e: abs(e.radius - 50.0) < 0.5)
        )
        print(f"Boss edges found: {len(boss_edges)}")
        fillet(boss_edges, radius=10)
        print("Fillet OK")
    except Exception as e:
        print(f"Fillet failed: {e}")

result = part.part

# PROFILE CUT — close boundary extrude subtract
try:
    wire      = Wire.make_polygon([Vector(x, y, -1) for x, y in cut_pts], close=True)
    face      = Face(wire)
    cut_solid = Solid.extrude(face, Vector(0, 0, TOTAL_H + 2))
    result    = result - cut_solid
    print("Profile cut OK")
except Exception as e:
    print(f"Profile cut failed: {e}")
    result = result.scale(0.1)
    result = result.scale(1.0118)

print(f"Volume: {result.volume:.4e} mm³")
export_stl(result, STL_FILE)
print("✅ STL saved:", STL_FILE)

try:
    from ocp_vscode import show
    show(result, reset_camera=True)
    print("✅ 3D preview opened")
except ImportError:
    print("⚠️  pip install ocp-vscode")
    print("    then run: ocp_vscode")