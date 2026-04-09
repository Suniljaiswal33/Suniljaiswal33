import os
import ezdxf
from build123d import *

# =========================
# PATH
# =========================
desktop = os.path.join(os.path.expanduser("~"), "Desktop")

DXF_FILE = os.path.join(desktop, "charybdisnano_ChairMountPlate_v13.dxf")
STL_FILE = os.path.join(desktop, "charybdisnano_ChairMountPlate_v13.stl")

HEIGHT = 40
BOSS_HEIGHT = 200

# =========================
# LOAD DXF
# =========================
doc = ezdxf.readfile(DXF_FILE)
msp = doc.modelspace()

loops = []

for e in msp:
    if e.dxftype() == "LWPOLYLINE" and e.closed:
        pts = [(p[0], p[1]) for p in e.get_points()]
        loops.append(pts)

if not loops:
    raise ValueError("❌ No closed polylines found")

# =========================
# SORT (Outer first)
# =========================
def area(poly):
    return abs(sum(
        poly[i][0]*poly[(i+1)%len(poly)][1] -
        poly[(i+1)%len(poly)][0]*poly[i][1]
        for i in range(len(poly))
    ) / 2)

loops.sort(key=area, reverse=True)

outer = loops[0]
inners = loops[1:]

print(f"Outer points: {len(outer)}")
print(f"Inner profiles: {len(inners)}")

# =========================
# RECTANGULAR BOSS POINTS
# =========================
boss_pts = [
    (-2623.2588, 3037.3934),
    (-2631.9031, 3042.0140),
    (-2639.4799, 3048.2321),
    (-2645.6981, 3055.8089),
    (-2650.3186, 3064.4533),
    (-2653.1639, 3073.8329),
    (-2654.1246, 3083.5874),
    (-2653.6442, 3288.4647),
    (-2648.0083, 3307.0438),
    (-2635.6915, 3322.0518),
    (-2623.2588, 3329.7814),
    (-2613.8791, 3332.6267),
    (-2404.1246, 3333.5874),
    (-2384.9904, 3329.7814),
    (-2376.3461, 3325.1609),
    (-2365.6602, 3315.1544),
    (-2362.5511, 3311.3659),
    (-2357.9306, 3302.7216),
    (-2354.1246, 3287.6954),
    (-2355.0853, 3073.8329),
    (-2357.9306, 3064.4533),
    (-2362.5511, 3055.8089),
    (-2368.7693, 3048.2321),
    (-2376.3461, 3042.0140),
    (-2384.9904, 3037.3934),
    (-2394.3701, 3034.5482),
    (-2404.1246, 3033.5874),
    (-2604.1246, 3033.5874),
]

# =========================
# BUILD PART (MAIN)
# =========================
with BuildPart() as part:

    # -------------------------
    # BASE PLATE (DXF)
    # -------------------------
    with BuildSketch(Plane.XY):
        with BuildLine():
            Polyline(*outer, close=True)
        make_face()

    extrude(amount=HEIGHT)

    # -------------------------
    # INNER CUTS
    # -------------------------
    for loop in inners:
        with BuildSketch(Plane.XY):
            with BuildLine():
                Polyline(*loop, close=True)
            make_face()

        extrude(amount=HEIGHT, mode=Mode.SUBTRACT)

    # -------------------------
    # RECTANGULAR BOSS (TOP)
    # -------------------------
    with BuildSketch(Plane(origin=(0, 0, HEIGHT))):  # top surface
        with BuildLine():
            Polyline(boss_pts, close=True)
        make_face()

    extrude(amount=BOSS_HEIGHT, mode=Mode.ADD)

# =========================
# EXPORT STL
# =========================
export_stl(part.part, STL_FILE)
print("✅ FINAL STL CREATED:", STL_FILE)

# =========================
# PREVIEW
# =========================
from ocp_vscode import show, set_port, reset_show

reset_show()
set_port(3939)
show(part.part)