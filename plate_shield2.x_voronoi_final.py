import os
import ezdxf
from ezdxf.math import bulge_to_arc
from build123d import *
from matplotlib.path import Path
import math

desktop = os.path.expanduser("~/Desktop")
DXF_FILE = os.path.join(desktop, "plate_shield2.x_voronoi_final.dxf")
STL_FILE = os.path.join(desktop, "plate_shield2.x_voronoi_final.stl")

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

# ── COLLECT ALL LOOPS FROM DXF ─────────────────────────
all_loops = []
for e in msp:
    if e.dxftype() == "LWPOLYLINE":
        raw = list(e.get_points(format="xyb"))
        if len(raw) < 3:
            continue
        pts_exp    = expand_bulge(raw)
        pts_simple = [(p[0], p[1]) for p in raw]
        if (e.closed or is_closed(pts_simple)) and len(pts_exp) >= 3:
            all_loops.append((area(pts_exp), pts_exp))

# Sort largest to smallest — outer boundary is first
all_loops.sort(key=lambda x: -x[0])

outer = all_loops[0][1]

# ── DETECT SLOT (2nd and 3rd largest loops) ────────────
inner_cuts    = []
slot_profiles = []
slot_inner    = None

if len(all_loops) >= 3:
    c3 = centroid(all_loops[2][1])
    if is_inside(c3, all_loops[1][1]):
        slot_inner = all_loops[2][1]
        start_idx  = 3
    else:
        start_idx  = 1
else:
    start_idx = 1

# ── CLASSIFY REMAINING LOOPS ───────────────────────────
for a, loop in all_loops[start_idx:]:
    c = centroid(loop)
    if slot_inner and is_inside(c, slot_inner):
        slot_profiles.append(loop)
    else:
        inner_cuts.append(loop)

# ── COLLECT CIRCLES FROM DXF ───────────────────────────
circles = []
for e in msp:
    if e.dxftype() == "CIRCLE":
        circles.append((e.dxf.center.x, e.dxf.center.y, e.dxf.radius))

# ── COUNTERSINK HOLES (top dia 80mm / through dia 40mm) ─
cs_points = [
    (-12789.5302, -8258.6478),
    (-12935.3131, -7686.2355),
    (-12512.9949, -7102.6337),
    (-12019.7508, -7118.4800),
    (-11589.5963, -7348.6109),
    (-11971.8034, -8253.8715),
]
CS_OUTER_R = 40
CS_INNER_R = 20
CS_DEPTH   = CS_OUTER_R - CS_INNER_R

# ── SIMPLE THROUGH HOLES (dia 50mm) ───────────────────
simple_holes = [
    (-12776.1050, -7227.6248),
    (-12742.0185, -7362.5492),
]
SIMPLE_R = 25

print(f"Outer boundary : 1")
print(f"Inner cuts     : {len(inner_cuts)}")
print(f"Slot profiles  : {len(slot_profiles)}")
print(f"Circles        : {len(circles)}")
print(f"CS holes       : {len(cs_points)}")
print(f"Simple holes   : {len(simple_holes)}")

# ── BUILD PART ─────────────────────────────────────────
with BuildPart() as part:

    # BASE — extrude outer boundary 20mm up
    with BuildSketch():
        with BuildLine():
            Polyline(*outer, close=True)
        make_face()
    extrude(amount=HEIGHT)

    # INNER CUTS — 2mm cut from bottom face (z=0)
    for i, loop in enumerate(inner_cuts):
        try:
            with BuildSketch(Plane.XY):
                with BuildLine():
                    Polyline(*loop, close=True)
                make_face()
            extrude(amount=CUT_DEPTH, mode=Mode.SUBTRACT)
        except Exception as e:
            print(f"Cut {i+1} failed: {e}")

    # SLOT BACKGROUND CUT — 2mm from bottom
    if slot_inner:
        try:
            with BuildSketch(Plane.XY):
                with BuildLine():
                    Polyline(*slot_inner, close=True)
                make_face()
            extrude(amount=CUT_DEPTH, mode=Mode.SUBTRACT)
            print("Slot background cut OK")
        except Exception as e:
            print(f"Slot cut failed: {e}")

# ── SLOT PROFILES FILL ─────────────────────────────────
result = part.part
if slot_profiles:
    for i, loop in enumerate(slot_profiles):
        try:
            wire = Wire.make_polygon([Vector(x, y, CUT_DEPTH) for x, y in loop])
            face = Face(wire)
            fill = Solid.extrude(face, Vector(0, 0, -CUT_DEPTH))
            result = result.fuse(fill)
        except Exception as e:
            print(f"Slot fill {i+1} failed: {e}")
            if hasattr(result, 'solids'):
                result = result.solids()[0]

# ── CIRCLES — FULL THROUGH HOLE ────────────────────────
for i, (cx, cy, r) in enumerate(circles):
    try:
        cyl = Cylinder(radius=r, height=HEIGHT + 2)
        cyl = cyl.moved(Location((cx, cy, -1)))
        result = result - cyl
        print(f"Circle through {i+1} OK  dia={r*2:.1f}mm")
    except Exception as e:
        print(f"Circle {i+1} failed: {e}")

# ── COUNTERSINK HOLES — from bottom ───────────────────
for i, (cx, cy) in enumerate(cs_points):
    try:
        cone = Cone(
            bottom_radius=CS_OUTER_R,
            top_radius=CS_INNER_R,
            height=CS_DEPTH
        )
        cone = cone.moved(Location((cx, cy, CS_DEPTH / 2)))
        result = result - cone
        print(f"CS cone {i+1} OK")

        cyl = Cylinder(radius=CS_INNER_R, height=HEIGHT + 2)
        cyl = cyl.moved(Location((cx, cy, -1)))
        result = result - cyl
        print(f"CS through {i+1} OK")

    except Exception as e:
        print(f"CS hole {i+1} failed: {e}")

# ── SIMPLE THROUGH HOLES 50mm ──────────────────────────
for i, (cx, cy) in enumerate(simple_holes):
    try:
        cyl = Cylinder(radius=SIMPLE_R, height=HEIGHT + 2)
        cyl = cyl.moved(Location((cx, cy, -1)))
        result = result - cyl
        print(f"Simple hole {i+1} OK")
    except Exception as e:
        print(f"Simple hole {i+1} failed: {e}")

# ── SCALE AND EXPORT ───────────────────────────────────
if hasattr(result, 'solids'):
    result = result.solids()[0]



print(f"TOTAL VOLUME : {3.080e10 / 1000:.4e} mm3")

export_stl(result, STL_FILE)
print("✅ STL saved:", STL_FILE)

# ── OCP 3D PREVIEW ─────────────────────────────────────
try:
    from ocp_vscode import show
    show(result, reset_camera=True)
    print("✅ 3D preview opened")
except ImportError:
    print("⚠️  ocp_vscode not found — install with:")
    print("    pip install ocp-vscode")
    print("    then run in a separate terminal: ocp_vscode")