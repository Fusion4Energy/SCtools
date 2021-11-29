# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 11:10:14 2020

This script takes a csv and calculates the proportion of materials by volume
present in the model.

WARNING: This script will sum all the volumes of the cells, this includes the
empty components like the envelope.

@author: cubial
"""


import pandas as pd

csv = pd.read_csv('PFC4.csv')


volumes = []
materials = []

for i, row in csv.iterrows():
  if str(row['CELL IDs']) != 'nan':
    volumes.append(row['ORIGINAL VOLUME [cm3]'])
    materials.append(row['MATERIAL'])

matByVolume = {}
for i in range(len(volumes)):
  mat = materials[i]
  vol = volumes[i]
  if mat in matByVolume.keys():
    matByVolume[mat] += vol
  else:
    matByVolume[mat] = vol
  
totalVol = sum([x for x in matByVolume.values()])
matByPercent = {}
for key in matByVolume.keys():
  matByPercent[key] = matByVolume[key]/totalVol*100










