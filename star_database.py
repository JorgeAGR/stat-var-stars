import pandas as pd
import numpy as np
import os

parameters = np.load('etc/tnldict.npz')
flags = np.load('etc/flagarray.npy')



starlist = pd.DataFrame({'T_Eff': parameters['teff'],
                         'log_g': parameters['logg'],
                         'Flag': flags
                         }, index = parameters['stars'])

twomass = []

for i in starlist.index:
    if ('-b' in i) | (starlist.loc[i]['T_Eff'] is 'N/A'):
        starlist = starlist.drop(i)

for i in starlist.index:
    
    if 210000000 >= int(i) >= 201000001:
        filename = 'epic_1_27Feb2018.txt'
    elif 220000000 >= int(i) >= 210000001:
        filename = 'epic_2_27Feb2018.txt'
    elif 230000000 >= int(i) >= 220000001:
        filename = 'epic_3_27Feb2018.txt'
    elif 240000000 >= int(i) >= 230000001:
        filename = 'epic_4_27Feb2018.txt'
    elif 250000000 >= int(i) >= 240000001:
        filename = 'epic_5_27Feb2018.txt'
    elif 251809654 >= int(i) >= 250000001:
        filename = 'epic_6_27Feb2018.txt'
    
    with open('epic-catalog/' + filename) as file:
        for line in file:
            if i in line:
                try:
                    fields = line.split('|')
                    twomass.append(fields[4])
                    break
                except:
                    fields = line.split(' ')
                    fields = fields[0].split('\t')
                    twomass.append(fields[4])
                    break
