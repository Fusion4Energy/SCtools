"""
An IronPython script to be used in SpaceClaim to load a csv of points as
spheres.

It assumes that the first three columns of the .csv are X, Y, Z coordinates
"""
import csv

# --- Input Parameters ---
INFILE = r"path/to/file.csv"  # path to the .csv file
RADIUS = MM(20)  # radius in mm of the spheres to be generated
LIMITER = 1000  # max spheres to generate. Use None to have no limits
SCALE = 1  # Scale the x,y,z coordinates by a factor


# --- Functions ---
def build_sphere(origin, radius, scale=1):
    x = float(origin[0]) * scale
    y = float(origin[1]) * scale
    z = float(origin[2]) * scale
    start_point = Point.Create(x, y, z)
    end_point = Point.Create(x, y, z + radius)
    SphereBody.Create(start_point, end_point, ExtrudeType.ForceIndependent)


# --- Code ---
# reads input file lines and iterate on them
with open(INFILE, "r") as infile:
    reader = csv.reader(infile, delimiter=",")
    for i, line in enumerate(reader):
        # skip the first line
        if i == 0:
            continue
        elif LIMITER is not None and i > LIMITER:
            break
        # Build a sphere
        build_sphere(line, RADIUS, scale=SCALE)
