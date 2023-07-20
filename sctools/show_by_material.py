# Python Script, API Version = V22
import csv


def get_material_by_tree_from_csv(csv_filename):
    materials_by_tree = {}  # ("Assembly", "Comp1", "Subcomp34"): "316LN"
    with open(csv_filename, "r") as infile:
        reader = csv.DictReader(infile)
        row = reader.next()
        level_titles = [k for k in row.keys() if "Level" in k]
        tree_length = len(level_titles)
        levels = ["Level {}".format(i + 1) for i in range(tree_length)]
    with open(csv_filename, "r") as infile:
        reader = csv.DictReader(infile)
        for row in reader:
            material = row["MATERIAL"]
            if material == "":
                continue
            tree = [row[level] for level in levels]
            tree = [level for level in tree if level != "-"]
            tree = tuple(tree)  # list objects are not hashable
            materials_by_tree[tree] = material
        return materials_by_tree


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


def get_bodies_with_material(material, materials_by_tree):
    bodies_with_material = []
    bodies = GetRootPart().GetAllBodies()
    parts = [body.Parent for body in bodies]
    parts = list(set(parts))  # to remove duplicates
    for part in parts:
        tree = get_tree_from_part(part)
        part_material = materials_by_tree[tree]
        if part_material == material:
            bodies_with_material += part.GetBodies()
    return bodies_with_material


def get_chosen_material(materials_by_tree):
    material_names = set(materials_by_tree.values())
    for material in material_names:
        message = MessageBox.Show('Show only material ' + str(material),
                                  'Material selection',
                                  MessageBoxButtons.YesNo)
        if message == DialogResult.Yes:
            return material
    return None


try:
    materials_by_tree
except NameError:
    root_part = GetRootPart()
    csv_filename = root_part.Document.Path[0:-6] + ".csv"
    materials_by_tree = get_material_by_tree_from_csv(csv_filename)
material = get_chosen_material(materials_by_tree)
if material is not None:
    bodies_with_material = get_bodies_with_material(material, materials_by_tree)

    sel = Selection.Create(GetRootPart().GetAllBodies())
    visibility = VisibilityType.Hide
    inSelectedView = False
    ViewHelper.SetObjectVisibility(sel, visibility, inSelectedView)

    sel = Selection.Create(bodies_with_material)
    visibility = VisibilityType.Show
    inSelectedView = False
    ViewHelper.SetObjectVisibility(sel, visibility, inSelectedView)
