# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 09:38:12 2020

@author: cubial
"""
import pandas as pd
import re
import numpy as np

file = 'Volume_tally.txt'
cellID = []
volume = []
relerr = []
with open(file, 'r') as infile:
    for line in infile:
        if 'cell' in line:
            # Be carful to adjust the 940000 to the first cellID preset in the
            # model
            cellID.append(int(re.findall('\d+', line)[0])-940000+1)
        elif len(line.split()) == 2:
            v, e = line.split()
            volume.append(float(v))
            relerr.append(float(e))
df = pd.DataFrame({'cellID':cellID, 'volume':volume, 'relerr':relerr})
df.set_index('cellID', inplace=True)

csv = pd.read_csv('TOKAMAK_COMPLEX_with_MATERIALS.csv')
for i, row in csv.iterrows():
    cellID = csv.at[i, 'CELL IDs']
    cellIDs = re.findall('\d+', str(cellID))
    if len(cellIDs) == 2:
        i0 = int(cellIDs[0])
        i1 = int(cellIDs[1])
        for j in range(i0, i1 + 1):
            if str(csv.at[i, 'STOCHASTIC VOLUME']) == 'nan':
                csv.at[i, 'STOCHASTIC VOLUME'] = df.at[j, 'volume']
            else:
                csv.at[i, 'STOCHASTIC VOLUME'] = (float(csv.at[i, 'STOCHASTIC VOLUME'])
                                                  + float(df.at[j, 'volume'])) 
csv.to_csv('stochastic.csv')
import matplotlib.pyplot as plt     

# relative error over volume of MCNP cells
ax = plt.gca()
ax.set_xscale('log')
plt.scatter(volume, relerr)
plt.title('MCNP statistical error')
plt.xlabel('Stochastic MCNP cell volume [cm3]')
plt.ylabel('Relative error')
plt.show()

simplified = csv['SIMPLIFIED VOLUME']
stochastic = csv['STOCHASTIC VOLUME']
simplified = [float(i) for i in simplified if str(i) != 'nan' and str(i) != 'DELETED']
stochastic = [float(i) for i in stochastic if str(i) != 'nan']

# Volume difference between CAD and MCNP
dif = np.array(stochastic)/np.array(simplified) 
plt.scatter(simplified, dif)
ax = plt.gca()
ax.set_xscale('log')
plt.title('Volume difference between CAD and MCNP') 
plt.xlabel('Stochastic MCNP cell volume [cm3]')
plt.ylabel('CAD/STOCHASTIC volume')
plt.show()

# Cumulative MCNP - CAD volume difference
dif = np.array(stochastic) - np.array(simplified) 
a = list(zip(simplified, dif))
a.sort()
dif = [j for i, j in a]
simplified = [i for i, j in a]
new = [0]
for i in dif:
    new.append(new[-1]+i)
dif = new[1:]

ax = plt.gca()
ax.set_xscale('log')
plt.title('Cumulative MCNP - CAD volume difference') 
plt.xlabel('Stochastic MCNP cell volume [cm3]')
plt.ylabel('STOCHASTIC - CAD volume [cm3]')
plt.plot(simplified, dif)
plt.show()









