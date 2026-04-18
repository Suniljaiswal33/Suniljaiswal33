from build123d import *
import os

STL_FILE = os.path.expanduser("~/Desktop/printable_btu_3.175mm_ball.stl")

pts = [
    (-41.7442,   0.0229), (-9.9912,    0.0229),  (-9.9912,  -30.3836),
    (-11.5538,  -31.6511),(-12.7403,  -32.897),  (-13.9269,  -34.4988),
    (-15.0244,  -36.516), (-16.0033,  -39.3933), (-16.346,   -40.8568),
    (-16.4938,  -42.8029),(-16.4938,  -44.9954), (-16.0721,  -47.6191),
    (-15.1867,  -50.0058),(-20.0372,  -50.0058), (-41.0033,  -39.9821),
    (-41.7537,  -39.9821),(-41.7442,    0.0229),
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