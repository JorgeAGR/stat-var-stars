ce
from astropy.io import fits
import os
import numpy as np

campaigns = []
for d in os.listdir():
    if 'k2c' in d:
        campaigns.append(d)

del campaigns[0]
del campaigns[0]

for c in campaigns:
    for obj in os.listdir(c + '/data'):
        if '-b' not in obj:
            with fits.open(c + '/data/' + obj, mode = 'update') as star:
                
                if star[0].header['EPIC'] >= 201000001:
                
                    if 210000000 >= star[0].header['EPIC'] >= 201000001:
                        filename = 'epic_1_27Feb2018.txt'
                    elif 220000000 >= star[0].header['EPIC'] >= 210000001:
                        filename = 'epic_2_27Feb2018.txt'
                    elif 230000000 >= star[0].header['EPIC'] >= 220000001:
                        filename = 'epic_3_27Feb2018.txt'
                    elif 240000000 >= star[0].header['EPIC'] >= 230000001:
                        filename = 'epic_4_27Feb2018.txt'
                    elif 250000000 >= star[0].header['EPIC'] >= 240000001:
                        filename = 'epic_5_27Feb2018.txt'
                    elif 251809654 >= star[0].header['EPIC'] >= 250000001:
                        filename = 'epic_6_27Feb2018.txt'
                    
                    try:
                        with open('epic-catalog/' + filename) as file:
                            for line in file:
                                if str(star[0].header['EPIC']) in line:
                                    try:
                                        fields = line.split('|')
                                        star[0].header['2MASS'] = fields[4]
                                        break
                                    except:
                                        fields = line.split(' ')
                                        fields = fields[0].split('\t')
                                        star[0].header['2MASS'] = fields[4]
                                        break
                    except:
                        star[0].header['2MASS'] = ''
                    
                    star[0].header.comments['2MASS'] = "['2MASS ID']"
                    print('EPIC ' + str(star[0].header['EPIC']) + '--> 2MASS J' + star[0].header['2MASS'])
                    star.flush()
                    
                else:
                    
                    star[0].header['2MASS'] = ''
                    star[0].header.comments['2MASS'] = "['2MASS ID']"
                    print('EPIC ' + str(star[0].header['EPIC']) + '--> 2MASS J' + star[0].header['2MASS'])
                    star.flush()