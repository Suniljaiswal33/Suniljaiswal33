from build123d import *
import os

STL_FILE = os.path.expanduser("~/Desktop/battery_holder_cover.stl")
HEIGHT   = 615

R_OUTER  = 259.989 / 2
R_INNER  = 159.995 / 2
R_MID    = (R_OUTER + R_INNER) / 2
HOLE_R   = 41.422 / 2
HOLE_D   = 18

# ── Semi-circle ring (outer - inner) ──
with BuildPart() as part:
    with BuildSketch() as sk:
        with BuildLine():
            RadiusArc((R_OUTER, 0), (-R_OUTER, 0), R_OUTER)
            Line((-R_OUTER, 0), (R_OUTER, 0))
        make_face()

        with BuildLine():
            RadiusArc((R_INNER, 0), (-R_INNER, 0), R_INNER)
            Line((-R_INNER, 0), (R_INNER, 0))
        make_face(mode=Mode.SUBTRACT)

    extrude(amount=HEIGHT)

result = part.part
print(f"✅ Semi-circle ring extruded ({HEIGHT}mm)")

# ── Holes on flat face, 18mm deep ──
hole_centers = [
    ( R_MID, HEIGHT / 2),
    (-R_MID, HEIGHT / 2),
]

for i, (hx, hz) in enumerate(hole_centers, 1):
    cyl    = Solid.make_cylinder(HOLE_R, HOLE_D + 10)  # 28mm total
    cyl    = cyl.rotate(Axis.X, -90)                    # +Y direction (confirmed working)
    cyl    = cyl.moved(Location(Vector(hx, -18, hz)))   # Y=-10 to Y=+18
    result = result.cut(cyl)
    try:    result = result.solids()[0]
    except: pass
    print(f"✅ Hole {i} at X={hx:.3f}, Z={hz:.1f}, depth={HOLE_D}mm")

print(f"\nOuter radius : {R_OUTER:.4f} mm  (dia {R_OUTER*2:.3f})")
print(f"Inner radius : {R_INNER:.4f} mm  (dia {R_INNER*2:.3f})")
print(f"Mid radius   : {R_MID:.4f} mm")
print(f"Hole dia     : {HOLE_R*2:.3f} mm  depth: {HOLE_D}mm")
print(f"Volume       : {result.volume:.4e} mm³")

export_stl(result, STL_FILE)
print("✅ STL saved:", STL_FILE)

try:
    from ocp_vscode import show, Camera
    show(result, reset_camera=Camera.RESET)
    print("✅ Preview opened")
except ImportError:
    pass