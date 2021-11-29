import pandas as pd
import re


class Cell:
    def __init__(self, _material, _volume):
        self.volume = _volume
        material_ids = {'316LN': 940001, '304': 940002, 'Aluminium-Bronze': 940003, '316L': 940004,
                        'Nitronic 60': 940005, 'Inconel 718': 940006, 'Inconel 600': 940007, 'void': 0,
                        '304L': 940009, 'AL2O3': 940010, 'Fused Silica': 940011, 'Aluminum Nitride (AlN)': 940012,
                        'Kapton + Copper': 940013, 'B4C': 940014, 'SS660': 940015, 'CableLoomMix': 940016,
                        'Tungsten': 940017, 'PEEK': 940018}
        self.material = material_ids[_material]


def get_cells_from_csv(csv_filename, id_number_correction=0):
    df = pd.read_csv(csv_filename)
    cells = dict()
    for _index, row in df.iterrows():
        id_range = re.findall(r'\d+', str(row['CELL IDs']))
        if len(id_range) == 2:
            id_range = [int(x) + id_number_correction for x in id_range]
            i = id_range[0]
            while i <= id_range[1]:
                cells[i] = Cell(row['MATERIAL'], float(row['ORIGINAL VOLUME [cm3]']))
                i += 1
    return cells


def obtain_all_material_ids_from_cells(cells):
    """
    Parameters
    ----------
    cells: Dict[cell_id: Cell]

    Returns
    -------
    list[int]
    """
    materials_of_all_cells = [cells[key].material for key in cells.keys()]
    material_ids = list(set(materials_of_all_cells))  # to remove duplicates
    return material_ids


def write_tallies_in_chunks_by_material(infile, cells, tally_id=1, chunk_size=300, particle='n', envelopes='',
                                        multiplier='', comment=''):
    """
    Writes as many tallies as necessary to tally all cells. The cells of a given tally must all contain the same
    material as all of them will share the same tally multiplier. The multiplier can include the word "implicit",
    it will be substituted by the material number corresponding to the cell.
    """
    if envelopes == '':
        raise NotImplementedError
    if comment == '':
        print('A unique comment is required to be able to do the post-processing...')
        raise NotImplementedError
    material_ids = obtain_all_material_ids_from_cells(cells)
    for current_material in material_ids:
        current_multiplier = multiplier.replace('implicit', str(current_material))
        current_comment = comment + f' with material {str(current_material)}'
        infile.write(f'F{tally_id}4:{particle}')
        cells_in_chunk = 0
        volumes = []
        for cell_id in cells.keys():
            if cells[cell_id].material == current_material:
                cells_in_chunk += 1
                if cells_in_chunk > chunk_size:
                    infile.write(f'SD{tally_id}4: ')
                    for volume in volumes:
                        infile.write(f'     {volume} \n')
                    volumes = []
                    if current_multiplier != '':
                        infile.write(f'FM{tally_id}4 {current_multiplier}\n')
                    infile.write(f'FC{tally_id}4 {current_comment}\n')
                    tally_id += 1
                    infile.write(f'F{tally_id}4:{particle}')
                    cells_in_chunk = 1
                volumes.append(cells[cell_id].volume)
                infile.write(f'     ({cell_id}<({envelopes}))\n')
        infile.write(f'SD{tally_id}4: ')
        for volume in volumes:
            infile.write(f'     {volume} \n')
        if current_multiplier != '':
            infile.write(f'FM{tally_id}4 {current_multiplier}\n')
        infile.write(f'FC{tally_id}4 {current_comment}\n')
        tally_id += 1
    return tally_id


def main():
    csv_filename = 'TOKAMAK_COMPLEX_with_MATERIALS.csv'
    cells = get_cells_from_csv(csv_filename, id_number_correction=940000 - 1)  # cellID: Cell()
    envelopes_port_5 = '448575 435575 444582 435719\n     435720 435721 435722 444282 444682'
    envelopes_port_17 = '491684 483094 491641'
    with open('cell_tallies.txt', 'w') as infile:
        tally_id = 1
        tally_id = write_tallies_in_chunks_by_material(infile, cells, tally_id=tally_id, particle='n',
                                                       envelopes=envelopes_port_5,
                                                       multiplier='1.7757e20',
                                                       comment='Neutron flux in port 5')
        tally_id = write_tallies_in_chunks_by_material(infile, cells, tally_id=tally_id, particle='n',
                                                       envelopes=envelopes_port_17,
                                                       multiplier='1.7757e20',
                                                       comment='Neutron flux in port 17')
        tally_id = write_tallies_in_chunks_by_material(infile, cells, tally_id=tally_id, particle='p',
                                                       envelopes=envelopes_port_5,
                                                       multiplier='1.7757e20',
                                                       comment='Photon flux in port 5')
        tally_id = write_tallies_in_chunks_by_material(infile, cells, tally_id=tally_id, particle='p',
                                                       envelopes=envelopes_port_17,
                                                       multiplier='1.7757e20',
                                                       comment='Photon flux in port 17')
        tally_id = write_tallies_in_chunks_by_material(infile, cells, tally_id=tally_id, particle='n',
                                                       envelopes=envelopes_port_5,
                                                       multiplier='-2.845e7 implicit 1 -4',
                                                       comment='Neutron heating in port 5')
        tally_id = write_tallies_in_chunks_by_material(infile, cells, tally_id=tally_id, particle='n',
                                                       envelopes=envelopes_port_17,
                                                       multiplier='-2.845e7 implicit 1 -4',
                                                       comment='Neutron heating in port 17')
        tally_id = write_tallies_in_chunks_by_material(infile, cells, tally_id=tally_id, particle='p',
                                                       envelopes=envelopes_port_5,
                                                       multiplier='-2.845e7 implicit -5 -6',
                                                       comment='Photon heating in port 5')
        tally_id = write_tallies_in_chunks_by_material(infile, cells, tally_id=tally_id, particle='p',
                                                       envelopes=envelopes_port_17,
                                                       multiplier='-2.845e7 implicit -5 -6',
                                                       comment='Photon heating in port 17')
        tally_id = write_tallies_in_chunks_by_material(infile, cells, tally_id=tally_id, particle='n',
                                                       envelopes=envelopes_port_5,
                                                       multiplier='3.004e7 implicit 444',
                                                       comment='DPA implicit material in port 5')
        tally_id = write_tallies_in_chunks_by_material(infile, cells, tally_id=tally_id, particle='n',
                                                       envelopes=envelopes_port_17,
                                                       multiplier='3.004e7 implicit 444',
                                                       comment='DPA implicit material in port 17')
    return


if __name__ == '__main__':
    main()
