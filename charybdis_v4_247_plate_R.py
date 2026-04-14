import os
import ezdxf
from ezdxf.math import bulge_to_arc
from build123d import *
from matplotlib.path import Path
import math

desktop = os.path.expanduser("~/Desktop")
DXF_FILE = os.path.join(desktop, "charybdis_v4_247_plate_R.dxf")
STL_FILE = os.path.join(desktop, "charybdis_v4_247_plate_R.stl")

HEIGHT    = 20
CUT_DEPTH = 2

doc = ezdxf.readfile(DXF_FILE)
msp = doc.modelspace()

def area(poly):
    return abs(sum(
        poly[i][0]*poly[(i+1)%len(poly)][1] -
        poly[(i+1)%len(poly)][0]*poly[i][1]
        for i in range(len(poly))
    ) / 2)

def centroid(poly):
    return (sum(p[0] for p in poly)/len(poly), sum(p[1] for p in poly)/len(poly))

def is_inside(pt, poly):
    p = Path(poly)
    if p.contains_point(pt):
        return True
    for dx, dy in [(50,0),(-50,0),(0,50),(0,-50)]:
        if p.contains_point((pt[0]+dx, pt[1]+dy)):
            return True
    return False

def is_closed(pts, tol=500.0):
    if len(pts) < 3:
        return False
    dx = pts[0][0] - pts[-1][0]
    dy = pts[0][1] - pts[-1][1]
    return (dx*dx + dy*dy) ** 0.5 < tol

def expand_bulge(raw):
    result = []
    n = len(raw)
    for i in range(n):
        x0, y0, bulge = raw[i]
        x1, y1, _ = raw[(i+1) % n]
        result.append((x0, y0))
        if abs(bulge) > 1e-6:
            try:
                cx, cy, r, start_a, end_a = bulge_to_arc((x0,y0),(x1,y1), bulge)
                if bulge < 0:
                    start_a, end_a = end_a, start_a
                steps = max(16, int(abs(end_a-start_a)/math.radians(3)))
                for t in range(1, steps):
                    a = start_a + (end_a-start_a)*t/steps
                    result.append((cx + r*math.cos(a), cy + r*math.sin(a)))
            except:
                pass
    return result

all_loops = []
for e in msp:
    if e.dxftype() == "LWPOLYLINE":
        raw = list(e.get_points(format="xyb"))
        if len(raw) < 3:
            continue
        pts_exp = expand_bulge(raw)
        pts_simple = [(p[0], p[1]) for p in raw]
        if (e.closed or is_closed(pts_simple)) and len(pts_exp) >= 3:
            all_loops.append((area(pts_exp), pts_exp))

all_loops.sort(key=lambda x: -x[0])

outer      = all_loops[0][1]
slot_outer = all_loops[1][1]
slot_inner = all_loops[2][1]

slot_profiles = []
voronoi       = []

for a, loop in all_loops[3:]:
    c = centroid(loop)
    if is_inside(c, slot_inner) or a < 4500:
        slot_profiles.append(loop)
    else:
        voronoi.append(loop)

circles = []
for e in msp:
    if e.dxftype() == "CIRCLE":
        circles.append((e.dxf.center.x, e.dxf.center.y, e.dxf.radius))

# COUNTERSINK HOLES
cs_points = [
    (3726.3855, 2102.7971),
    (3872.1887, 2675.5927),
    (4689.8745, 2670.8777),
    (5072.1887, 1765.5927),
    (4642.1887, 1535.5927),
    (4148.7252, 1519.7660),
]
CS_INNER_R = 20
CS_OUTER_R = 40
CS_DEPTH   = CS_OUTER_R - CS_INNER_R

# ── MIRROR FIX ──────────────────────────────────────────
min_x    = min(p[0] for p in outer)
max_x    = max(p[0] for p in outer)
center_x = (min_x + max_x) / 2

def mirror_loop(loop):
    return [(2*center_x - x, y) for x, y in loop]
# ────────────────────────────────────────────────────────

print(f"Voronoi cuts  : {len(voronoi)}")
print(f"Slot profiles : {len(slot_profiles)}")
print(f"Circles       : {len(circles)}")
print(f"CS holes      : {len(cs_points)}")

with BuildPart() as part:

    # BASE
    with BuildSketch():
        with BuildLine():
            Polyline(*outer, close=True)
        make_face()
    extrude(amount=HEIGHT)

    # VORONOI CUTS — bottom se (mirrored)
    for i, loop in enumerate(voronoi):
        try:
            mirrored = mirror_loop(loop)
            with BuildSketch(Plane.XY):
                with BuildLine():
                    Polyline(*mirrored, close=True)
                make_face()
            extrude(amount=CUT_DEPTH, mode=Mode.SUBTRACT)
        except Exception as e:
            print(f"Voronoi {i+1} failed: {e}")

    # SLOT BACKGROUND CUT — bottom se (mirrored)
    try:
        mirrored_slot = mirror_loop(slot_inner)
        with BuildSketch(Plane.XY):
            with BuildLine():
                Polyline(*mirrored_slot, close=True)
            make_face()
        extrude(amount=CUT_DEPTH, mode=Mode.SUBTRACT)
        print("Slot background cut OK")
    except Exception as e:
        print(f"Slot cut failed: {e}")

    # CIRCLES — bottom se (mirrored)
    for i, (cx, cy, r) in enumerate(circles):
        try:
            mcx = 2*center_x - cx
            with BuildSketch(Plane.XY):
                with Locations((mcx, cy)):
                    Circle(r)
            extrude(amount=CUT_DEPTH, mode=Mode.SUBTRACT)
        except Exception as e:
            print(f"Circle {i+1} failed: {e}")

# SLOT PROFILES FILL — bottom se (mirrored)
result = part.part
for i, loop in enumerate(slot_profiles):
    try:
        mirrored = mirror_loop(loop)
        wire = Wire.make_polygon([Vector(x, y, CUT_DEPTH) for x, y in mirrored])
        face = Face(wire)
        fill = Solid.extrude(face, Vector(0, 0, -CUT_DEPTH))
        result = result.fuse(fill)
    except Exception as e:
        print(f"Slot fill {i+1} failed: {e}")
        if hasattr(result, 'solids'):
            result = result.solids()[0]

# COUNTERSINK HOLES — bottom se (mirrored)
for i, (cx, cy) in enumerate(cs_points):
    try:
        mcx = 2*center_x - cx
        cone = Cone(
            bottom_radius=CS_OUTER_R,
            top_radius=CS_INNER_R,
            height=CS_DEPTH
        )
        cone = cone.moved(Location((mcx, cy, CS_DEPTH / 2)))
        result = result - cone
        print(f"CS cone {i+1} OK")

        cyl = Cylinder(radius=CS_INNER_R, height=HEIGHT + 2)
        cyl = cyl.moved(Location((mcx, cy, -1)))
        result = result - cyl
        print(f"CS through {i+1} OK")

    except Exception as e:
        print(f"CS hole {i+1} failed: {e}")

if hasattr(result, 'solids'):
    result = result.solids()[0]
    result = result.scale(0.1)

print(f"\nVolume: {result.volume:.4e} mm³")
export_stl(result, STL_FILE)
print("✅ STL saved:", STL_FILE)