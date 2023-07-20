# -*- coding: utf-8 -*-
"""
Created on Tue Jun  2 14:05:46 2020

@author: cubial
"""

from numjuggler import parser as mp
import re
import pandas as pd


def read_csv_cellIDs(csv_filename, first_cellID = 1):
    '''
    Returns a dictionary with all the cellIDs
    '''
    first_cellID -= 1  # If the first cell was 100 the cellID will be 1 + 99

    csv = pd.read_csv(csv_filename)
    csv = csv[pd.notnull(csv['CELL IDs'])]  # remove the rows with cellID==nan
    # This dictionary will have as key the cellID and as value the csv row
    cellIDs = {}  
    for i, row in csv.iterrows():
        cellID = row['CELL IDs']
        if re.match('\[\d+, \d+\]', cellID):
            span = re.findall('\d+', cellID)
            span = [int(j) + first_cellID for j in span]
            for j in range(span[0], span[1] + 1):
                cellIDs[j] = row

    return cellIDs


def write_MCNP_with_materials(MCNP_input, cellsIDs, material_ID):
    '''
    Writes a new MCNP input file with the cells that had material in the csv
    filled with materialID and density.
    '''
    cards = mp.get_cards(MCNP_input)
    with open(MCNP_input+'[materials_added]','w') as infile:
        for card in cards:
            if card.ctype == mp.CID.cell:
                card.get_values()
                cellID = card.values[0][0]
                if cellID in cellIDs:
                    row = cellIDs[cellID]
                    
                    name = [row['Level '+str(i+1)] for i in range(len(row))
                            if 'Level '+str(i+1) in row.keys() 
                            and row['Level '+str(i+1)] != '-'][-1]
                    
                    DCF  = row['DCF=ORG/STOCH']
                    if str(DCF) != 'nan':
                        name = 'DCF='+ DCF +' '+ name
                    else:
                        DCF = 1.
                    
                    material_name = str(row['MATERIAL'])
                    # if no material is found in the csv the cell will be void
                    if material_name == 'nan':
                        matID = '0'
                    else:
                        if material_name not in material_ID.keys():
                            material_ID[material_name] = max(material_ID.values()) + 1
                        matID = material_ID[material_name]
                   
                        
                    density = str(row['DENSITY [g/cm3]'])
                    if density == 'nan' or density == 'N/A':
                        density = ' '
                    else:
                        density = float(density)*float(DCF)
                        density = f'-{density:.3f}'
                    
                     
                    header = (str(cellID) + ' ' + str(matID) + ' ' + density 
                              + '  $' + name)
                    
                    split = [header] + card.card().split('\n')
                    
                    if split[1].split()[1] == '0':  # void cell
                        split[1] = '          ' + ' '.join(split[1].split()[2:])
                    else:  # card that previously had a material and density
                        split[1] = '          ' + ' '.join(split[1].split()[3:])
                    card_def = '\n'.join(split)
                    
                    infile.write(card_def)
                    continue  # To avoid reading the line infile.write(card.card())
                    
            infile.write(card.card())

MCNP_input = 'MCNP_TOKAMAK.i'
csv_filename = 'TOKAMAK_COMPLEX.csv'
cellIDs = read_csv_cellIDs(csv_filename, first_cellID = 950000)

# key=material_name value=mID. Can be custom prepared. If a material_name
# is missing a new ID will be automaticaly assigned 
material_ID = {'dummy_mat': 0}                   
                    
write_MCNP_with_materials(MCNP_input, cellIDs, material_ID)
