from build123d import *
import os

STL_FILE = os.path.expanduser("~/Desktop/printable_btu_2.5mm_ball.stl")

pts = [
    (-10.1264,   0.1023), (-41.731,    0.1023),  (-41.731,  -39.9932),
    (-40.9207,  -39.9932),(-19.8464,  -50.019),  (-12.7289,  -50.019),
    (-13.3127,  -47.9276),(-13.5673,  -45.5403), (-13.3127,  -42.8665),
    (-12.7289,  -40.7339),(-11.6893,  -38.665),  (-10.8936,  -37.4236),
    (-15.2225,  -37.4236),(-12.7289,  -33.0157), (-9.9462,   -30.3825),
    (-10.1264,    0.1023),
]

# ── Revolve around Z axis (360°) ──
with BuildPart() as part:
    with BuildSketch(Plane.YZ):
        with BuildLine():
            for i in range(len(pts) - 1):
                Line(
                    (pts[i][0],   pts[i][1]),
                    (pts[i+1][0], pts[i+1][1])
                )
        make_face()
    revolve(axis=Axis.Z, revolution_arc=360)

result = part.part
print(f"Volume before scale: {result.volume:.4e} mm³")

# ── Scale 0.1 ──
result = result.scale(0.1)
print(f"Volume after scale : {result.volume:.4e} mm³")

export_stl(result, STL_FILE)
print("✅ STL saved:", STL_FILE)

try:
    from ocp_vscode import show, Camera
    show(result, reset_camera=Camera.RESET)
    print("✅ Preview opened")
except ImportError:
    pass