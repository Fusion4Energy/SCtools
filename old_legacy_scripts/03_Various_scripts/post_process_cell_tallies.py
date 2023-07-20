import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re


class CellTally:
    def __init__(self):
        self.id = None
        self.value = None
        self.error = None
        self.comment = None


def read_next_tally(infile):
    """
    Returns
    -------
    tuple[list[CellTally], bool]
    """
    new_cell_tallies = []
    cell_ids = []
    cell_values = []
    cell_errors = []
    end_of_file = False
    comment = ''
    inside_cell_id = False
    inside_values = False
    while True:
        line = infile.readline()
        if line == '':
            end_of_file = True
            break
        if not inside_cell_id and not inside_values:
            if re.match(r'tally', line):
                line = infile.readline()
                comment = line.strip()
                _ = infile.readline()
                inside_cell_id = True
        elif inside_cell_id:
            if re.match(r'd', line):
                inside_cell_id = False
                while not re.match('vals', line):
                    line = infile.readline()
                inside_values = True
            else:
                cell_ids += re.findall(r'\d+', line)
        elif inside_values:
            if 'tfc' in line:
                break
            else:
                cell_values += re.findall(r'\d\.\d+E[-+]\d+', line)
                cell_errors += re.findall(r'\d\.\d+[\s\n]', line)
    for i in range(len(cell_ids)):
        cell_tally = CellTally()
        cell_tally.id = int(cell_ids[i])
        cell_tally.value = float(cell_values[i])
        cell_tally.error = float(cell_errors[i])
        cell_tally.comment = comment
        new_cell_tallies.append(cell_tally)
    return new_cell_tallies, end_of_file


def read_all_cell_tallies(tally_filename):
    """
    Returns
    -------
    list[CellTally]
    """
    _all_cell_tallies = []
    with open(tally_filename, 'r') as infile:
        end_of_file = False
        while not end_of_file:
            new_cell_tallies, end_of_file = read_next_tally(infile)
            _all_cell_tallies += new_cell_tallies
    return _all_cell_tallies


def filter_tally_collection(_all_cell_tallies, included_in_comment):
    """
    Filter the tallies to include only those that have the included_in_comment string in the tally comment.
    """
    specific_cell_tallies = dict()
    for cell_tally in _all_cell_tallies:
        if included_in_comment in cell_tally.comment:
            specific_cell_tallies[cell_tally.id] = cell_tally
    return specific_cell_tallies


def plot_tally_collection(tallies_list, key='value', title=''):
    x = [tally.id for tally in tallies_list]
    if key == 'value':
        y = [tally.value for tally in tallies_list]
    elif key == 'error':
        y = [tally.error for tally in tallies_list]
    else:
        raise NotImplementedError
    fig, ax = plt.subplots()
    ax.plot(x, y, color='none')  # This is an invisible plot, used to avoid matplotlib bug with autoscale
    ax.scatter(x, y)
    plt.title(title)
    plt.show()
    return


def get_volumes_in_id_order(df: pd.DataFrame) -> np.ndarray:
    """
    The DataFrame has many rows without volume or cell id values that are of no interest. The cell id values are
    compressed in the format [id_1, id_n]. Return a np.array with the volume values for each cell id in order:
    [1, 2, ...]
    """
    cell_ids = df['CELL IDs'].values
    volumes = df['ORIGINAL VOLUME [cm3]'].values
    volumes_in_order = []
    for i in range(len(cell_ids)):
        ids = re.findall(r'\d+', str(cell_ids[i]))
        if len(ids) == 2:
            id_low, id_high = int(ids[0]), int(ids[1])
            current_id = id_low
            while current_id <= id_high:
                volumes_in_order.append(float(volumes[i]))
                current_id += 1
    return np.array(volumes_in_order)


def plot_relative_error_vs_volume(tallies_, csv_filename='TOKAMAK_COMPLEX_with_MATERIALS.csv'):
    df = pd.read_csv(csv_filename)
    x = get_volumes_in_id_order(df)
    ordered_ids = list(tallies_.keys())
    ordered_ids.sort()
    y = [tallies_[key].error for key in ordered_ids]
    fig, ax = plt.subplots()
    ax.scatter(x, y)
    ax.set_xscale('log')
    plt.show()
    return


def statistics_tally_collection(tallies_list, title=''):
    non_zero_tallies = [tally for tally in tallies_list if tally.value != 0]
    acceptable_error_tallies = [tally for tally in non_zero_tallies if tally.error <= 0.15]
    print(f'There are {len(tallies_list)} different cell tallies for {title}. {len(non_zero_tallies)} of which are '
          f'non-zero tallies. {len(acceptable_error_tallies)} of which have a relative error below 0.15.')
    return


def main():
    tally_filename = 'E-Lite_IVVS_v3.1_TCWS.m'
    all_cell_tallies_ = read_all_cell_tallies(tally_filename)
    tallies_ = {'neutron_flux_port_5': filter_tally_collection(all_cell_tallies_, 'Neutron flux in port 5'),
                'neutron_flux_port_17': filter_tally_collection(all_cell_tallies_, 'Neutron flux in port 17'),
                'neutron_heating_port_5': filter_tally_collection(all_cell_tallies_, 'Neutron heating in port 5'),
                'neutron_heating_port_17': filter_tally_collection(all_cell_tallies_, 'Neutron heating in port 17'),
                'photon_flux_port_5': filter_tally_collection(all_cell_tallies_, 'Photon flux in port 5'),
                'photon_flux_port_17': filter_tally_collection(all_cell_tallies_, 'Photon flux in port 17'),
                'photon_heating_port_5': filter_tally_collection(all_cell_tallies_, 'Photon heating in port 5'),
                'photon_heating_port_17': filter_tally_collection(all_cell_tallies_, 'Photon heating in port 17'),
                'dpa_implicit_port_5': filter_tally_collection(all_cell_tallies_, 'DPA implicit material in port 5'),
                'dpa_implicit_port_17': filter_tally_collection(all_cell_tallies_, 'DPA implicit material in port 17')}

    # This section produces lists with the results of every tally at the critical cells
    critical_ids = [30, 37, 106, 107, 113, 190, 203, 222, 303, 305, 306, 382, 384, 385, 386, 396, 398, 412, 413, 414,
                    419, 430, 440, 443, 447, 484, 486, 487, 597, 598, 599, 628, 638, 678, 687, 705, 770, 808, 810, 813,
                    854, 917, 918, 929, 990, 991, 1002, 1068, 1074, 1146, 1269, 1283, 1286, 1326]
    for key in tallies_.keys():
        statistics_tally_collection(tallies_[key].values(), key)
        critical_tallies_result = []
        critical_tallies_error = []
        for critical_id in critical_ids:
            critical_id += 940000 - 1
            print(tallies_[key][critical_id].error, end=' ')
            critical_tallies_result.append(tallies_[key][critical_id].value)
            critical_tallies_error.append(tallies_[key][critical_id].error)
        print('\n')  # A break in debug here allow to copy the values for each type of tally
        # plot_tally_collection(tallies[key].values(), key='value', title=key)
    return


if __name__ == '__main__':
    main()
    all_cell_tallies = read_all_cell_tallies('E-Lite_IVVS_v3.1_TCWS.m')
    tallies = filter_tally_collection(all_cell_tallies, 'Neutron flux in port 5')
    plot_relative_error_vs_volume(tallies, csv_filename='TOKAMAK_COMPLEX_with_MATERIALS.csv')
