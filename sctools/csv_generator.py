# Python Script, API Version = V22
import os
import csv
from copy import deepcopy


class Component:
    def __init__(self):
        self.tree = []  # e.g. ["Assembly1", "ComponentXYZ"]
        self.material = None
        self.mass = None
        self.density = None
        self.cell_ids = None
        self.volume_original = None
        self.volume_difference = None
        self.volume_simplified = None
        self.volume_stochastic = None
        self.density_correction_factor = None
        self.comment = None
        self.subcomponents = []
        self.simplified_comp = None
        return

    def write_csv(self):
        tree_length = self.get_tree_length()
        columns = ["Level {}".format(i + 1) for i in range(tree_length)]
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
            csv_writer = csv.DictWriter(infile, fieldnames=columns)
            csv_writer.writeheader()
            self.write_row(csv_writer, tree_length)
        return

    def write_row(self, csv_writer, tree_length):
        csv_tree = deepcopy(self.tree)
        while len(csv_tree) < tree_length:
            csv_tree.append("-")
        row = {"Level {}".format(i + 1): csv_tree[i] for i in range(tree_length)}
        row["MATERIAL"] = str(self.material)
        row["MASS [g]"] = str(self.mass)
        row["DENSITY [g/cm3]"] = str(self.density)
        row["CELL IDs"] = str(self.cell_ids)
        row["ORIGINAL VOLUME [cm3]"] = str(self.volume_original)
        row["%dif (ORG-SIM)/ORG*100"] = str(self.volume_difference)
        row["SIMPLIFIED VOLUME"] = str(self.volume_simplified)
        row["STOCHASTIC VOLUME"] = str(self.volume_stochastic)
        row["DCF=ORG/STOCH"] = str(self.density_correction_factor)
        row["COMMENT"] = str(self.comment)
        for key in row.keys():
            if row[key] == "None":
                row[key] = ""
        csv_writer.writerow(row)
        [c.write_row(csv_writer, tree_length) for c in self.subcomponents]
        return

    def get_tree_length(self, length=0):
        """
        Returns the maximum length of the tree.
        """
        if len(self.tree) > length:
            length = len(self.tree)
        return max([length] + [c.get_tree_length(length) for c in self.subcomponents])

    def compare_with_simplified_component(self, simplified_component):
        self.populate_simplified_component(simplified_component)
        self.populate_simplified_volume_values()
        return

    def populate_simplified_component(self, simplified_component):
        self.simplified_comp = simplified_component
        simplified_component.original_component = self
        simplified_subcomponents = deepcopy(simplified_component.subcomponents)
        for original_subcomponent in self.subcomponents:
            original_name = original_subcomponent.tree[-1]
            for index_simplified_subcomp in range(len(simplified_subcomponents)):
                simplified_name = simplified_subcomponents[
                    index_simplified_subcomp
                ].tree[-1]
                if original_name == simplified_name:
                    original_subcomponent.populate_simplified_component(
                        simplified_subcomponents.pop(index_simplified_subcomp)
                    )
                    break
        return

    def populate_simplified_volume_values(self):
        if not is_positive_float(self.volume_original):
            if is_positive_float(self.simplified_comp.volume_original):
                self.populate_simplified_merged_components_volume_values()
        elif self.simplified_comp is None:
            self.volume_simplified = "DELETED"
            self.cell_ids = "DELETED"
        elif self.simplified_comp.cell_ids is None:
            self.volume_simplified = "DELETED"
            self.cell_ids = "DELETED"
        else:
            self.volume_simplified = self.simplified_comp.volume_original
            self.cell_ids = self.simplified_comp.cell_ids
            diff = (
                (self.volume_original - self.simplified_comp.volume_original)
                / self.volume_original
                * 100
            )
            self.volume_difference = diff if abs(diff) > 1e-3 else 0.0
        for subcomponent in self.subcomponents:
            subcomponent.populate_simplified_volume_values()
        return

    def populate_simplified_merged_components_volume_values(self):
        """
        If a merging happened in the simplified component the original volume now is
        that of the original merged components.
        """
        self.volume_original = self.merged_volume()
        self.cell_ids = self.simplified_comp.cell_ids
        self.volume_simplified = self.simplified_comp.volume_original
        diff = (
            (self.volume_original - self.simplified_comp.volume_original)
            / self.volume_original
            * 100
        )
        self.volume_difference = diff if abs(diff) > 1e-3 else 0.0
        return

    def merged_volume(self):
        """
        For a component that has no volume (no bodies) but its simplified counterpart
        has volume. This means that the subcomponents were merged into the higher
        component level. This function finds which of the subcomponents had volume and
        now don't or the subcomponents that have been removed and return the sum of
        their volumes (we can assume that they have been removed because they have been
        merged a the higher level).
        """
        merged_volume = 0.0
        for subcomponent in self.subcomponents:
            if subcomponent.volume_original is not None:
                # the subcomponent was removed, we assume its bodies were moved to a
                # higher level and the component deleted
                if subcomponent.simplified_comp is None:
                    merged_volume += subcomponent.volume_original
                    continue
                # the subcomponent now has no volume, we assume its bodies were moved to
                # a higher level and the component was left there without bodies
                if not is_positive_float(subcomponent.simplified_comp.volume_original):
                    merged_volume += subcomponent.volume_original
        return merged_volume


class ComponentFromSC(Component):
    def __init__(self, sc_part, parent_component=None):
        Component.__init__(self)
        if parent_component:
            self.tree = deepcopy(parent_component.tree)
        self.tree.append(sc_part.GetName())
        bodies = [b for b in sc_part.GetBodies() if b.Shape.Volume > 0.0]
        if len(bodies) > 0:
            self.cell_ids = [BodyCounter.global_counter]
            BodyCounter.add_to_counter(len(bodies))
            self.cell_ids.append(BodyCounter.global_counter - 1)
            self.volume_original = sum([b.MassProperties.Mass for b in bodies])
            self.volume_original *= 1000000  # To make it cm3
        self.subcomponents = [
            ComponentFromSC(sub_part, parent_component=self)
            for sub_part in sc_part.GetComponents()
        ]
        return


class ComponentFromCSV(Component):
    def __init__(self, csv_filename, row=None, levels=None):
        Component.__init__(self)
        if row is not None:
            self.read_row(row, levels)
            return
        # first component
        levels = read_tree_levels_from_csv(csv_filename)
        components = []
        with open(csv_filename, "r") as infile:
            reader = csv.DictReader(infile)
            current_row = reader.next()
            self.read_row(current_row, levels)
            for row in reader:
                components.append(ComponentFromCSV(csv_filename, row, levels))
        # populate the self.subcomponents of all instances
        super_components = [self]
        for component in components:
            for index_super_comp in reversed(range(len(super_components))):
                if component.tree[:-1] == super_components[index_super_comp].tree:
                    super_components[index_super_comp].subcomponents.append(component)
                    super_components.append(component)
                    break
        return

    def read_row(self, row, levels):
        self.tree = [row[level] for level in levels]
        self.tree = [level for level in self.tree if level != "-"]
        self.material = row["MATERIAL"]
        self.mass = float_or_none(row["MASS [g]"])
        self.density = float_or_none(row["DENSITY [g/cm3]"])
        self.cell_ids = list_or_none(row["CELL IDs"])
        self.volume_original = float_or_none(row["ORIGINAL VOLUME [cm3]"])
        self.volume_difference = float_or_none(row["%dif (ORG-SIM)/ORG*100"])
        self.volume_simplified = float_or_none(row["SIMPLIFIED VOLUME"])
        self.volume_stochastic = float_or_none(row["STOCHASTIC VOLUME"])
        self.density_correction_factor = float_or_none(row["DCF=ORG/STOCH"])
        self.comment = row["COMMENT"]
        self.subcomponents = []
        return


class BodyCounter:
    global_counter = 1

    @classmethod
    def add_to_counter(cls, amount):
        cls.global_counter += amount
        return


def read_tree_levels_from_csv(csv_filename):
    with open(csv_filename, "r") as infile:
        reader = csv.DictReader(infile)
        row = reader.next()
        level_titles = [k for k in row.keys() if "Level" in k]
        tree_length = max([int(words.split()[-1]) for words in level_titles])
        return ["Level {}".format(i + 1) for i in range(tree_length)]


def float_or_none(value):
    try:
        return float(value)
    except ValueError:
        return None


def list_or_none(value):
    try:
        id_0 = value.split()[0][1:-1]
        id_1 = value.split()[-1][:-1]
        return [int(id_0), int(id_1)]
    except (ValueError, IndexError):
        return None


def is_positive_float(value):
    if type(value) == float:
        if value > 1e-10:
            return True
    return False


################################################

root_part = GetRootPart()
csv_filename = root_part.Document.Path[0:-6] + ".csv"
csv_exists = os.path.exists(csv_filename)
sc_comp = ComponentFromSC(root_part)
if csv_exists:
    csv_comp = ComponentFromCSV(csv_filename)
    csv_comp.compare_with_simplified_component(sc_comp)
    csv_comp.write_csv()
else:
    sc_comp.write_csv()
