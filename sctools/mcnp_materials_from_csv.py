import pandas as pd
import re
from numjuggler import parser as mp

MCNP_INPUT = "JT60_v0.5_without_materials.i"
CSV_FILE = "JT60_v0.5.csv"
FIRST_CELL_ID = 1
# key=material_name value=mID. Can be custom prepared. If a material_name is
# missing a new ID will be automatically assigned
MATERIAL_IDS = {
    "void": 0,
    "plasma": 1,
    "316L": 2,
    "316LN": 3,
    "insulator": 4,
    "304": 5,
    "graphite": 7,
    "upper divertor base": 8,
    "VVTS": 9,
    "CTS": 10,
    "TFC SCM": 11,
    "CS Coil": 12,
    "VV inner coil": 13,
    "EFC 1, 2, 5, 6": 15,
    "EFC 3, 4": "16",
    "lower divertor base": 17,
    "divertor heatsink": 18,
    "STB base": 19,
    "STB heatsink": 20,
    "air": 21,
    "concrete": 23,
    "VV inner section": 25,
}


def read_csv_cell_ids(csv_file, first_cell_id):
    """Returns a dictionary with all the cell ids"""
    first_cell_id -= 1  # If the first cell was 100 the cellID will be 1 + 99
    csv = pd.read_csv(csv_file)
    # remove the rows with cellID==nan
    csv = csv[pd.notnull(csv["CELL IDs"])]
    # This dictionary will have as key the cellID and as value the csv row
    cell_ids = {}
    for i, row in csv.iterrows():
        cell_id_range = row["CELL IDs"]
        if re.match(r"\[\d+, \d+\]", cell_id_range):
            span = re.findall(r"\d+", cell_id_range)
            span = [int(j) + first_cell_id for j in span]
            for j in range(span[0], span[1] + 1):
                cell_ids[j] = row
    return cell_ids


def process_cell_card(card: mp.Card, cell_ids, material_ids):
    card.get_values()
    cell_id = card.values[0][0]
    if cell_id not in cell_ids:
        return card.card()
    row = cell_ids[cell_id]
    cell_comment = row["COMMENT"]
    density_correction_factor = row["DCF=ORG/STOCH"]
    if str(density_correction_factor) != "nan":
        cell_comment = "DCF=" + density_correction_factor + " " + cell_comment
        density_correction_factor = float(density_correction_factor)
    else:
        density_correction_factor = 1.0
    # if no material is found in the csv the cell will be void
    material_name = str(row["MATERIAL"])
    if material_name == "nan" or material_name == "void":
        material_id = "0"
    else:
        if material_name not in material_ids.keys():
            material_ids[material_name] = max(material_ids.values()) + 1
        material_id = material_ids[material_name]
    density = str(row["DENSITY [g/cm3]"])
    if density == "nan" or density == "N/A":
        density = ""
    else:
        density = float(density) * float(density_correction_factor)
        density = f"-{density:.5e}"
    header = f"{cell_id} {material_id} {density} ${cell_comment}"
    split = [header] + card.card().split("\n")
    if split[1].split()[1] == "0":  # void cell
        split[1] = "          " + " ".join(split[1].split()[2:])
    else:  # card that previously had a material and density
        split[1] = "          " + " ".join(split[1].split()[3:])
    card_def = "\n".join(split)
    return card_def


def write_mcnp_with_materials(mcnp_input, cell_ids, material_ids):
    """Writes a new MCNP input file with the cells that had material in the csv filled
    with materialID and density."""
    cards = mp.get_cards(mcnp_input)
    with open(mcnp_input + "[materials_added]", "w") as infile:
        for card in cards:
            if card.ctype == mp.CID.cell:
                card_definition = process_cell_card(card, cell_ids, material_ids)
            else:
                card_definition = card.card()
            infile.write(card_definition)
    return


def main():
    cell_ids = read_csv_cell_ids(CSV_FILE, FIRST_CELL_ID)
    write_mcnp_with_materials(MCNP_INPUT, cell_ids, MATERIAL_IDS)
    return


if __name__ == "__main__":
    main()
