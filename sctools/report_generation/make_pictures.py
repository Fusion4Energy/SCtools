# Python Script, API Version = V17
import csv
import os
import re


class Comp(object):
    """
    This superclass defines the attributes and
    methods that will be applicable to the
    components, they can be from SC or from
    a csv.
    """

    def __init__(self):
        """
        This is a dummy init. It will be
        overwritten by the subclasses inits.
        """
        # The tree attribute is a list where
        # each element is the name of a component.
        # The first element is the root and the
        # last one is the comp name.
        self.tree = None
        # bodies is an instance of the class Bodies.
        # It contains all the useful information of
        # the bodies located at that level.
        self.bodies = None
        # simplified_comp calls to the comp instance
        # of the simplified version
        self.simplified_comp = None
        self.comment = ""
        self.comps = []  # All the comp's subcomps

    def get_enovia(self):
        """
        Returns the # +6digits enovia code from the name
        """
        enovia_list = re.findall("#.{6}", self.tree[-1])
        if len(enovia_list) == 1:
            return enovia_list[0]
        else:
            return False

    def get_tree_length(self, t=0):
        """
        Returns the maximum lenght of the tree.
        """
        if len(self.tree) > t:
            t = len(self.tree)
        return max([t] + [c.get_tree_length(t) for c in self.comps])

    def populate_simplified_comp(self, simp_comp):
        """
        It populates the self.simplified_comp with
        the analogous comp instance of simp_comp
        """
        self.simplified_comp = simp_comp
        simplified_subcomps = simp_comp.comps + []
        for subcomp in self.comps:
            name = subcomp.tree[-1]
            for i in range(len(simplified_subcomps)):
                sim_name = simplified_subcomps[i].tree[-1]
                if name in sim_name:
                    subcomp.populate_simplified_comp(simplified_subcomps.pop(i))
                    break

    def write_csv(self, csv_filename, is_original):
        tree_length = self.get_tree_length()
        columns = ["Level " + str(i + 1) for i in range(tree_length)]
        columns += [
            "MATERIAL",
            "MASS [g]",
            "DENSITY [g/cm3]",
            "CELL IDs",
            "ORIGINAL VOLUME [cm3]",
            "%dif (ORG-SIM)/ORG*100",
            "SIMPLIFIED VOLUME",
            "STOCHASTIC VOLUME",
            "DCF=ORG/STOCH",
            "COMMENT",
        ]
        with open(csv_filename, "wb") as infile:
            writer = csv.DictWriter(infile, fieldnames=columns)
            writer.writeheader()
            self.write_row(writer, is_original, tree_length)

    def write_row(self, writer, is_original, tree_length):
        tree = self.tree + []
        while len(tree) < tree_length:
            tree.append("-")
        row = {"Level " + str(i + 1): tree.pop(0) for i in range(len(tree))}
        row["COMMENT"] = self.comment
        if self.bodies != None:
            vol = float(self.bodies.vol)
            row["ORIGINAL VOLUME [cm3]"] = vol
            row["CELL IDs"] = str(self.bodies.cellID)
            row["MATERIAL"] = (
                self.bodies.mat_name if self.bodies.mat_name != None else "N/A"
            )
            row["DENSITY [g/cm3]"] = (
                float(self.bodies.dens) if self.bodies.dens != None else "N/A"
            )
            row["MASS [g]"] = (
                round(vol * float(self.bodies.dens), 2)
                if self.bodies.dens != None
                else "N/A"
            )
            if not is_original:
                if self.simplified_comp == None:
                    row["SIMPLIFIED VOLUME"] = "DELETED"
                    row["CELL IDs"] = "DELETED"
                    row["%dif (ORG-SIM)/ORG*100"] = "DELETED"
                elif self.simplified_comp.bodies == None:
                    row["SIMPLIFIED VOLUME"] = "DELETED"
                    row["CELL IDs"] = "DELETED"
                    row["%dif (ORG-SIM)/ORG*100"] = "DELETED"
                else:
                    row["SIMPLIFIED VOLUME"] = self.simplified_comp.bodies.vol
                    row["CELL IDs"] = str(self.simplified_comp.bodies.cellID)
                    diff = (
                        (
                            float(self.bodies.vol)
                            - float(self.simplified_comp.bodies.vol)
                        )
                        / float(self.bodies.vol)
                        * 100
                    )
                    row["%dif (ORG-SIM)/ORG*100"] = diff if abs(diff) > 1e-3 else 0.0
        else:
            if self.simplified_comp != None:
                if self.simplified_comp.bodies != None:
                    # Its a merging, look for the new original volume vol
                    vol = self.merged_volume()
                    row["ORIGINAL VOLUME [cm3]"] = vol
                    row["CELL IDs"] = str(self.simplified_comp.bodies.cellID)
                    row["MATERIAL"] = "N/A"
                    row["DENSITY [g/cm3]"] = "N/A"
                    row["MASS [g]"] = "N/A"
                    row["SIMPLIFIED VOLUME"] = self.simplified_comp.bodies.vol
                    diff = (
                        (float(vol) - float(self.simplified_comp.bodies.vol))
                        / float(vol)
                        * 100
                    )
                    row["%dif (ORG-SIM)/ORG*100"] = diff if diff > 1e-3 else 0.0
        writer.writerow(row)
        [c.write_row(writer, is_original, tree_length) for c in self.comps]

    def merged_volume(self):
        """
        For a component that has no bodies but its
        .simplified_comp has bodies.
        Finds which of the subcomps that had bodies and now
        dont or the subcomps that have been removed and return
        the sum of their volumes (we can assume that they
        have been removed because they have been merged a the
        higher level)
        """
        vol = 0.0
        for subcomp in self.comps:
            if subcomp.bodies != None:
                if subcomp.simplified_comp == None:
                    vol += float(subcomp.bodies.vol)
                elif subcomp.simplified_comp.bodies == None:
                    vol += float(subcomp.bodies.vol)
        return vol


class Comp_from_SC(Comp):
    """
    Subclass of Comp. It has an init function able
    to iterate over the SC file.
    """

    def __init__(self, sc_comp, tree):
        """
        sc_comp is a SpaceClaim component
        """
        Comp.__init__(self)
        self.sc_comp = sc_comp  # Added for MakePictures
        self.tree = tree + [sc_comp.GetName()]
        if len(sc_comp.GetBodies()) > 0:
            self.bodies = Bodies_from_SC(sc_comp)
            if self.bodies.count == 0:  # In case only surfaces
                self.bodies = None
        else:
            self.bodies = None
        self.new_bodies = None
        self.comps = [
            Comp_from_SC(c, self.tree) for c in sc_comp.Components
        ]  # Modified for Make_pictures


class Comp_from_csv(Comp):
    """
    Subclass of Comp. I has an init able to read
    a csv comp file.
    """

    def __init__(self, csv_filename):
        """
        Reads a csv and generates a Comp instance
        of the same features as a Comp_from_SC
        previous_comp is the comp that was read in
        the previous line.
        """
        Comp.__init__(self)
        row_comps = []
        with open(csv_filename, "r") as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                c = Comp()
                keys = row.keys()
                tree_length = 0
                for key in keys:
                    if "Level " in key:
                        n = int(re.findall("\d+", key)[0])
                        if n > tree_length:
                            tree_length = n
                c.tree = [
                    row["Level " + str(i + 1)]
                    for i in range(tree_length)
                    if row["Level " + str(i + 1)] != "-"
                ]
                c.comment = row["COMMENT"]
                if row["ORIGINAL VOLUME [cm3]"] != "":
                    c.bodies = Bodies()
                    c.bodies.vol = row["ORIGINAL VOLUME [cm3]"]
                    c.bodies.cellID = row["CELL IDs"]
                    if row["MATERIAL"] == "N/A":
                        c.bodies.mat_name = None
                        c.bodies.dens = None
                    else:
                        c.bodies.mat_name = row["MATERIAL"]
                        c.bodies.dens = row["DENSITY [g/cm3]"]
                row_comps.append(c)
        self.row_comps = row_comps
        super_comps = [row_comps.pop(0)]
        for c in row_comps:
            for i in range(len(super_comps)):
                i = -1 - i  # Reverse sorting of list
                if c.tree[:-1] == super_comps[i].tree:
                    super_comps[i].comps.append(c)
                    super_comps.append(c)
                    break
        self.__dict__ = super_comps[0].__dict__


class Bodies(object):
    """
    This superclass contains the information of
    a set of bodies like volume, material and
    density.
    """

    def __init__(self):
        self.volume = None
        self.mat_name = None
        self.dens = None
        self.count = None
        self.cellID = None


class Bodies_from_SC(Bodies):
    """
    Sub class of Bodies.
    Reads the bodies info from a SpaceClaim
    component.
    """

    globalID = 1  # Shared with all other instances

    def __init__(self, sc_comp):
        bods = sc_comp.GetBodies()
        bods = [b for b in bods if b.Shape.Volume > 0.0]
        self.count = len(bods)
        if self.count == 0:
            return None
        self.cellID = [
            Bodies_from_SC.globalID,
            Bodies_from_SC.globalID + self.count - 1,
        ]
        Bodies_from_SC.globalID += self.count
        self.vol = sum([b.MassProperties.Mass for b in bods])
        self.vol *= 1000000  # To make it cm3
        # Try to take the material from the component
        # If there is None then try it with the first
        # body of the component.
        material = bods[0].GetMaster().Parent.Material
        if material == None:
            material = bods[0].GetMaster().Material
        if material != None:
            self.mat_name = material.Name.replace(",", ";")
            self.dens = material.Properties["General.Density.Mass"].Value / 1000
        else:
            self.mat_name, self.dens = None, None


######################################################


def recursive_pictures(csv_comp):
    global row
    global path
    row += 1
    if csv_comp.simplified_comp != None:
        c = csv_comp.simplified_comp.sc_comp
        sel = Selection.Create(c.GetAllBodies())
        ViewHelper.SetObjectVisibility(sel, VisibilityType.Show)
        ViewHelper.ZoomToEntity(sel)
        ViewHelper.ActivateNamedView("Isometric", True)
        DocumentSave.Execute(path + "\\" + str(row) + ".jpg")
        ViewHelper.SetObjectVisibility(sel, VisibilityType.Hide)
    for comp in csv_comp.comps:
        recursive_pictures(comp)


try:
    GetRootPart().Document.Path[1]
    path = GetRootPart().Document.Path
    path = "\\".join(path.split("\\")[0:-1])
except:
    path = "D:\\"
path_original = path + "\\Original_Pictures\\"
try:
    os.mkdir(path_original)
    path = path_original
except:
    path = path + "\\Simplified_Pictures\\"
try:
    os.mkdir(path)
except:
    pass

csv_filename = GetRootPart().Document.Path[0:-6] + ".csv"
part = GetRootPart()
SC_comp = Comp_from_SC(part, [])
sel = Selection.Create(part.GetAllBodies())
ViewHelper.SetObjectVisibility(sel, VisibilityType.Show)
ColorHelper.SetFillStyle(sel, FillStyle.Opaque)

csv_comp = Comp_from_csv(csv_filename)
csv_comp.populate_simplified_comp(SC_comp)

# row will be the name of the picture, it corresponds to
# the component found in that row in the csv
row = 1
recursive_pictures(csv_comp)
