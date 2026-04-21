from build123d import *
import math, os

STL_FILE = os.path.expanduser("~/Desktop/LargeKnobLowProBlank_v3.stl")

profile_pts = [
    (  0.0,      97.5996), (-30.2601,  97.4901), (-30.2601, -33.0764),
    (-54.9275,  -33.0282), (-55.1174,  67.987),  (-58.1368,  73.7896),
    (-62.8492,   80.1984), (-68.881,   85.2878),  (-75.1013,  88.4922),
    (-84.903,    90.0002), (-149.6016, 89.926),   (-158.9174, 86.5564),
    (-165.2601,  82.1958), (-170.4135, 75.8532),  (-173.7831, 68.7177),
    (-174.6994,  60.9943), (-175.2103, -0.3982),  (-224.5878, -0.3982),
    (-224.974,    9.6628), (-195.1516, 26.7981),  (-224.974,  44.7318),
    (-224.974,   56.3889), (-195.1516, 73.6256),  (-211.3116, 83.5218),
    (-174.7623, 120.0842), (  0.0,    120.0349),  (  0.0,     97.5996),
]

# Revolve axis: last two points
# (0.0, 120.0349) → (0.0, 97.5996) in YZ plane
# Both X=0, so axis is along Y direction (Z axis in YZ plane)
# Direction: (0, 120.0349) to (0, 97.5996) = (0, -22.4) = -Y direction
# Revolve around Y axis

with BuildSketch(Plane.YZ) as sk:
    with BuildLine():
        for i in range(len(profile_pts) - 1):
            Line(
                (profile_pts[i][0],   profile_pts[i][1]),
                (profile_pts[i+1][0], profile_pts[i+1][1])
            )
    make_face()

face = sk.sketch.face()

# Revolve axis: from (0,0,0) along last two points direction
# Both points have Y=0 in YZ coords, so axis is Z axis
rev_axis = Axis(
    origin    = Vector(0, 0, 0),
    direction = Vector(0, profile_pts[-1][0] - profile_pts[-2][0],
                          profile_pts[-1][1] - profile_pts[-2][1])
)

result = Solid.revolve(face, 360, rev_axis)

print(f"Volume  : {result.volume:.4e} mm³")
# Close boundary thru cut in Z direction
cut_pts = [
    (-179.847, -111.302),
    (-180.157,  -74.623),
    (-205.874,  -48.468),
    (-179.847, -111.302),
]

wire_c  = Wire.make_polygon([Vector(x, y, 0) for x, y in cut_pts], close=True)
cutter  = Solid.extrude(Face(wire_c), Vector(0, 0, 500))  # +Z thru
cutter2 = Solid.extrude(Face(wire_c), Vector(0, 0, -500)) # -Z thru

result = result.cut(cutter)
try:    result = result.solids()[0]
except: pass
result = result.cut(cutter2)
try:    result = result.solids()[0]
except: pass
print(f"✅ Thru cut Z | Volume: {result.volume:.4e}")
print(f"✅ Thru cut | Volume: {result.volume:.4e}")
# 16x pattern thru cut around Z axis
cut_pts = [
    (-179.847, -111.302),
    (-180.157,  -74.623),
    (-205.874,  -48.468),
    (-179.847, -111.302),
]

for i in range(20):
    angle = 360 / 20 * i

    wire_c = Wire.make_polygon([Vector(x, y, 0) for x, y in cut_pts], close=True)
    cutter = Solid.extrude(Face(wire_c), Vector(0, 0, 1000))
    cutter = cutter.moved(Location(Vector(0, 0, -500)))  # center Z
    cutter = cutter.rotate(Axis.Z, angle)

    result = result.cut(cutter)
    try:    result = result.solids()[0]
    except: pass
    print(f"✅ Cut {i+1}/16 at {angle:.1f}°")

print(f"Volume: {result.volume:.4e}")
import math

raw_pts = [
    (1950.0,  143.2126, 135.7019),
    (1950.0,  -87.191,  267.3611),
    (1950.0,  145.5636, 406.0734),
    (1950.0,  340.7013, 267.3611),
]

pts    = [(x*0.1, y*0.1, z*0.1) for x, y, z in raw_pts]
yz_pts = [(y, z) for x, y, z in pts]

cy = sum(p[0] for p in yz_pts) / len(yz_pts)
cz = sum(p[1] for p in yz_pts) / len(yz_pts)

DEPTH  = -25
TAPER  = -12
shrink = math.tan(math.radians(TAPER)) * DEPTH

bot = [Vector(195, y, z) for y, z in yz_pts]
top = [Vector(195 - DEPTH,
              cy + (y-cy) * max(0, 1 - shrink/abs(y-cy+1e-6)),
              cz + (z-cz) * max(0, 1 - shrink/abs(z-cz+1e-6)))
       for y, z in yz_pts]

wire_bot  = Wire.make_polygon(bot, close=True)
wire_top  = Wire.make_polygon(top, close=True)
boss_base = Solid.make_loft([wire_bot, wire_top])

# Z spacing
z_height = max(z for y, z in yz_pts) - min(z for y, z in yz_pts)

# Pattern x20 around Z, x3 in Z
for zi in range(3):
    z_move = z_height * zi
    for i in range(20):
        angle = 360 / 20 * i
        boss  = boss_base.rotate(Axis.Z, angle)
        boss  = boss.moved(Location(Vector(0, 0, z_move)))
        result = result.fuse(boss)
        try:    result = result.solids()[0]
        except: pass
    print(f"✅ Z row {zi+1}/3 done")

print(f"Volume: {result.volume:.4e}")
# Revolve profile around last two points axis
rev_raw = [
    (0.0, 674.7239,  1200.0672),
    (0.0, 674.7239,  1422.8818),
    (0.0, 729.9114,  1412.2316),
    (0.0, 781.226,   1388.0266),
    (0.0, 814.1448,  1357.0441),
    (0.0, 851.9047,  1308.6341),
    (0.0, 896.4419,  1254.4148),
    (0.0, 955.5022,  1217.6232),
    (0.0, 1020.1639, 1200.842),
    (0.0, 674.7239,  1200.0672),
]

rev_pts = [(x*0.1, y*0.1, z*0.1) for x, y, z in rev_raw]

p_last = rev_pts[-1]
p_prev = rev_pts[-9]

ax       = Vector(p_last[0]-p_prev[0], p_last[1]-p_prev[1], p_last[2]-p_prev[2])
rev_axis = Axis(origin=Vector(*p_last), direction=ax)

with BuildSketch(Plane.YZ) as sk2:
    with BuildLine():
        for i in range(len(rev_pts) - 1):
            Line(
                (rev_pts[i][1],   rev_pts[i][2]),
                (rev_pts[i+1][1], rev_pts[i+1][2])
            )
    make_face()

face2       = sk2.sketch.face()
dimple_base = Solid.revolve(face2, 360, rev_axis)
dimple_base = dimple_base.scale(1.0)
dimple_base = dimple_base.moved(Location(Vector(-113.85, 0, 0)))

# Pattern 3 instances around Z axis
for i in range(3):
    angle  = 360 / 3 * i
    dimple = dimple_base.rotate(Axis.Z, angle)
    result = result.fuse(dimple)
    try:    result = result.solids()[0]
    except: pass
    print(f"✅ Dimple {i+1}/3 at {angle:.1f}°")

print(f"Volume: {result.volume:.4e}")

print("✅ STL saved:", STL_FILE)
print(f"Volume: {result.volume:.4e}")

export_stl(result, STL_FILE)  
print("✅ STL saved:", STL_FILE)

try:
    from ocp_vscode import show, Camera
    show(result, reset_camera=Camera.RESET)
    print("✅ Preview opened")
except ImportError:
    pass