# Python Script, API Version = V22
# Python Script, API Version = V22
import csv


MAX_DIFF = 1  # maximum volume difference allowed in %
STEP = 1  # in mm


def get_volume_by_tree_from_csv(csv_filename):
    volume_by_tree = {}  # ("Assembly", "Comp1", "Subcomp34"): 1234.123 [cm3]
    with open(csv_filename, "r") as infile:
        reader = csv.DictReader(infile)
        row = reader.next()
        level_titles = [k for k in row.keys() if "Level" in k]
        tree_length = len(level_titles)
        levels = ["Level {}".format(i + 1) for i in range(tree_length)]
    with open(csv_filename, "r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            volume = row["ORIGINAL VOLUME [cm3]"]
            if volume == "":
                continue
            tree = [row[level] for level in levels]
            tree = [level for level in tree if level != "-"]
            tree = tuple(tree)  # list objects are not hashable
            volume_by_tree[tree] = float(volume)
        return volume_by_tree


def get_tree_from_part(part):
    tree = [part.GetName()]
    while part.Parent is not None:
        part = part.Parent
        name = part.GetName()
        if name != tree[-1]:
            tree.append(name)
    tree = tree[::-1]
    tree = tuple(tree)
    return tree


def total_volume(body):
    component = body.Parent
    vol = 0
    for b in component.Bodies:
        vol = vol + b.MassProperties.Mass * 1000000
    return vol


try:
    volumes_by_tree
except NameError:
    root_part = GetRootPart()
    csv_filename = root_part.Document.Path[0:-6] + ".csv"
    volumes_by_tree = get_volume_by_tree_from_csv(csv_filename)

volume_dif_exceeded_bodies = []

all_bodies = GetRootPart().GetAllBodies()
for body in all_bodies:
    current_volume = total_volume(body)
    tree = get_tree_from_part(body.Parent)
    original_volume = volumes_by_tree[tree]
    dif = abs(original_volume - current_volume) / original_volume * 100
    if dif > MAX_DIFF:
        volume_dif_exceeded_bodies.append(body)

sel = Selection.Create(all_bodies)
options = SetColorOptions()
options.FaceColorTarget = FaceColorTarget.Body
ColorHelper.SetColor(sel, options, Color.Blue)
ColorHelper.SetFillStyle(sel, FillStyle.Transparent)

sel = Selection.Create(volume_dif_exceeded_bodies)
options = SetColorOptions()
options.FaceColorTarget = FaceColorTarget.Body
ColorHelper.SetColor(sel, options, Color.Red)
ColorHelper.SetFillStyle(sel, FillStyle.Opaque)

