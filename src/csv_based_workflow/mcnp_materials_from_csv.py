import re
from dataclasses import dataclass
from math import isclose

import pandas as pd
from numjuggler import parser as mp

MCNP_INPUT_FILEPATH = "testing.mcnp"
CSV_FILEPATH = "testing.csv"
MATERIAL_IDS_FILEPATH = "material_ids.csv"
FIRST_CELL_ID = 1


@dataclass
class InputData:
    """
    Holds the input data for the processor taking the default values from the module
    """

    mcnp_input_filepath: str = MCNP_INPUT_FILEPATH
    csv_filepath: str = CSV_FILEPATH
    material_ids_filpath: str = MATERIAL_IDS_FILEPATH
    first_cell_id: int = FIRST_CELL_ID


class Processor:
    """
    Reads the input data, processes the MCNP input file and writes a new one with the
    necessary modifications.
    """

    def __init__(self, input_data: InputData):
        self.input_data = input_data
        self.material_ids = self.get_material_ids()
        self.cell_ids_dict = self.get_cell_id_info()
        self.employed_materials = {}

    def get_cell_id_info(self) -> dict[int, pd.Series]:
        """
        Returns a dictionary where the key is the cell id and the value is the row of
        the csv with the information.
        """
        # If the first cell was 100 the cellID will be 1 + 99
        cell_id_modifier = self.input_data.first_cell_id - 1

        csv = pd.read_csv(self.input_data.csv_filepath)
        csv = csv[csv["CELL IDs"].str.contains(r"\[\d+, \d+\]")]
        cell_ids_dict = {}
        for _, row in csv.iterrows():
            span = re.findall(r"\d+", row["CELL IDs"])
            span = [int(i) + cell_id_modifier for i in span]
            for cell_id in range(span[0], span[1] + 1):
                cell_ids_dict[cell_id] = row
        return cell_ids_dict

    def get_material_ids(self) -> dict[str, int]:
        """
        Returns a dictionary with the material name as the key and the material id as
        the value.
        """
        try:
            material_ids = pd.read_csv(self.input_data.material_ids_filpath)
            return dict(zip(material_ids["MATERIAL"], material_ids["ID"]))
        except FileNotFoundError:
            print("Material ids file not found! Creating all IDs automatically.")
            return {"Void": 0}
        except KeyError:
            print("Invalid material ids file! Creating all IDs automatically.")
            return {"Void": 0}

    def write_mcnp_with_materials(self) -> None:
        """
        Writes a new MCNP input file with the cells that had material in the csv filled
        with the material id, density (with the DCF applied) and a comment stating the
        component's name.
        """
        mcnp_input_filepath = self.input_data.mcnp_input_filepath
        cards = mp.get_cards(mcnp_input_filepath)
        with open(
            mcnp_input_filepath + "[materials_added]", "w", newline="", encoding="utf-8"
        ) as infile:
            for card in cards:
                if card.ctype == mp.CID.cell:
                    card_definition = self._process_cell_card(card)
                else:
                    card_definition = card.card()
                infile.write(card_definition)

        print(f"The employed materials were: {self.employed_materials}")

    def _process_cell_card(self, card: mp.Card) -> str:
        card.get_values()
        cell_id = card.values[0][0]
        if cell_id not in self.cell_ids_dict:
            return card.card()
        row = self.cell_ids_dict[cell_id]

        density_correction_factor = self._get_density_correction_factor(row)

        material_id, density = self._get_material_id_and_density(
            row, cell_id, density_correction_factor
        )

        cell_comment = self._get_comment(row, density_correction_factor)

        header = f"{cell_id} {material_id} {density} $ {cell_comment}"
        split = [header] + card.card().split("\n")
        if split[1].split()[1] == "0":  # void cell
            split[1] = "          " + " ".join(split[1].split()[2:])
        else:  # card that previously had a material and density
            split[1] = "          " + " ".join(split[1].split()[3:])
        card_definition = "\n".join(split)

        return card_definition

    def _get_density_correction_factor(self, row: pd.Series) -> float:
        try:
            density_correction_factor = float(row["DCF=ORG/STOCH"])
            assert pd.notna(density_correction_factor)
        except (ValueError, AssertionError):
            density_correction_factor = 1.0
        return density_correction_factor

    def _get_material_id_and_density(
        self, row: pd.Series, cell_id: int, density_correction_factor: float
    ):
        material_name = str(row["MATERIAL"])

        # Void material
        if material_name in ("nan", "Void"):
            return "0", ""

        # If the material is not in the dictionary, add it
        if material_name not in self.material_ids:
            self.material_ids[material_name] = max(self.material_ids.values()) + 1

        # Get the material id and density
        material_id = self.material_ids[material_name]
        try:
            density = float(row["DENSITY [g/cm3]"]) * density_correction_factor
            density = f"-{density:.4e}"
        except ValueError:
            raise ValueError(f"Invalid density value for cell {cell_id}!")

        # Update the employed materials for tracking
        if material_name not in self.employed_materials:
            self.employed_materials[material_name] = material_id

        return material_id, density

    def _get_comment(self, row: pd.Series, density_correction_factor: float) -> str:
        component_name = row["Component ID"]

        last_tree_name = ""
        level_keys = [key for key in row.keys() if "Level" in key]
        for key in level_keys:
            tree_name = row[key]
            if tree_name not in ["-", "nan"]:
                last_tree_name = tree_name

        comment = f"{component_name} - {last_tree_name}"

        if not isclose(density_correction_factor, 1.0):
            comment += f" - DCF={density_correction_factor:.3f}"

        return comment

    def remove_geouned_comments(self):
        """
        Removes the lines that contain only a $ comment, that is, the geouned automatic
        comments.
        """
        file_path = self.input_data.mcnp_input_filepath + "[materials_added]"
        with open(file_path, encoding="utf-8") as infile:
            lines = infile.readlines()

        with open(file_path, "w", encoding="utf-8") as infile:
            for line in lines:
                if not re.match(r"^\s*\$", line):
                    infile.write(line)


def main():
    processor = Processor(InputData())
    processor.write_mcnp_with_materials()
    processor.remove_geouned_comments()


if __name__ == "__main__":
    main()
