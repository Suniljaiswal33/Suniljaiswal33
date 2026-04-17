from build123d import *
import os

STL_FILE = os.path.expanduser("~/Desktop/Static-bearing-holder_v221117.stl")

pts = [
    (-9.2763,  -0.0042),  (-37.457,   -0.0042),  (-37.5044, -35.0018),
    (-37.0799, -35.0018), (-36.353,   -35.0645),  (-35.4549, -35.5135),
    (-34.7295, -36.3771), (-34.505,   -37.3961),  (-34.7295, -38.536),
    (-35.4204, -39.4514), (-36.3357,  -39.935),   (-37.457,  -40.0285),
    (-45.0278, -40.0285), (-45.0278,  -45.7197),  (-44.7278, -47.4378),
    (-44.046,  -48.6104), (-42.8734,  -49.7831),  (-40.9654, -50.5745),
    (-23.0095, -53.2772), (-14.7968,  -53.2772),  (-14.2135, -53.1242),
    (-13.9362, -52.8852), (-13.7449,  -52.4645),  (-13.7449, -52.0643),
    (-14.5517, -49.6906), (-14.9934,  -45.9156),  (-14.5517, -42.3337),
    (-13.3005, -39.0647), (-11.3634,  -36.1993),  (-9.2763,  -34.0734),
    (-9.2763,  -0.0042),
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

print(f"Points  : {len(pts)}")
print(f"Volume  : {result.volume:.4e} mm³")
result = result.scale(0.1)

export_stl(result, STL_FILE)
print("✅ STL saved:", STL_FILE)

try:
    from ocp_vscode import show, Camera
    show(result, reset_camera=Camera.RESET)
    print("✅ Preview opened")
except ImportError:
    pass