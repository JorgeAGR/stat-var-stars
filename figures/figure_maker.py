#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 21 00:19:25 2018

@author: jorgeagr
"""

import os
from lightkurve import KeplerTargetPixelFile, KeplerLightCurveFile
from lightkurve import log
log.setLevel('ERROR')
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.animation as animation
from matplotlib.backends.backend_pdf import PdfPages
from astropy.io import fits
import numpy as np
import PyPDF2 as pypdf2
from astropy.io import fits
import subprocess
from scipy.signal import lombscargle
import matplotlib.colors as colors
from scipy import interpolate

golden_ratio = (np.sqrt(5) + 1) / 2
width = 12
height = width / golden_ratio

mpl.rcParams['font.size'] = 12
mpl.rcParams['figure.titlesize'] = 'large'
mpl.rcParams['legend.fontsize'] = 'small'
mpl.rcParams['figure.figsize'] = (width, height)

def getMetaData(fields):
    TWOMASS = fields[4]
    KP = fields[45]
    TEFF = fields[46]
    E_TEFF = fields[47]
    LOGG = fields[49]
    E_LOGG = fields[50]
    FEH = fields[52]
    E_FEH = fields[53]
    RAD = fields[55]
    E_RAD = fields[56]
    MASS = fields[58]
    E_MASS = fields[59]
    RHO = fields[61]
    E_RHO = fields[62]
    LUM = fields[64]
    E_LUM = fields[65]
    D = fields[67]
    E_D = fields[68]
    return {'TWOMASS': TWOMASS, 'KP': KP, 'TEFF': TEFF, 'LOGG': LOGG, 
            'FEH': FEH, 'RAD': RAD, 'MASS': MASS, 'RHO': RHO, 'LUM': LUM,
            'D': D}


pathdir = '../candidates/target_lists/'
epicdir = '../epic-catalog/'
dsct_dir = '../deltasct/'

delta_scutis = 'deltasct_targetlist.txt'
binaries = 'binaries_targetlist.txt'


def save_metadata():
    
    target_list = []
    temperature = []
    logg = []
    
    with open(pathdir + delta_scutis) as file:
        for line in file:
            target = int(line[5:14])
    
            if 210000000 >= target >= 201000001:
                filename = 'epic_1_06July2018.txt'
            elif 220000000 >= target >= 210000001:
                filename = 'epic_2_06July2018.txt'
            elif 230000000 >= target >= 220000001:
                filename = 'epic_3_06July2018.txt'
            elif 240000000 >= target >= 230000001:
                filename = 'epic_4_06July2018.txt'
            elif 250000000 >= target >= 240000001:
                filename = 'epic_5_06July2018.txt'
            elif 251809654 >= target >= 250000001:
                filename = 'epic_6_06July2018.txt'
            
            with open(epicdir + filename) as file:
                    for line in file:
                        if str(target) in line:
                            try:
                                fields = line.split('|')
                                metadata = getMetaData(fields)
                                break
                            except:
                                fields = line.split(' ')
                                fields = fields[0].split('\t')
                                metadata = getMetaData(fields)
                                break
            
            print(target, metadata['TEFF'], metadata['LOGG'])
            target_list.append(target)
            temperature.append(float(metadata['TEFF']))
        logg.append(float(metadata['LOGG']))
    
    with open(dsct_dir + 'deltasct_teff.txt', 'w+') as file:
        for t in temperature:
            print(t, file=file)
    
    with open(dsct_dir + 'deltasct_logg.txt', 'w+') as file:
        for l in logg:
            print(l, file=file)
            
#target = 211044267 # Delta Sct
#campaign = 4

#target = 217163685 # Gamma Dor
#campaign = 7

target = 214675496 # Binary
campaign =  7

target = 212628518 #210425611 # Hybrid
campaign = 6


lcf = KeplerLightCurveFile.from_archive(target, campaign=campaign).PDCSAP_FLUX
lcf = lcf.remove_nans().remove_outliers(sigma=8).fill_gaps()
lcf.flux = (lcf.flux / np.mean(lcf.flux) - 1) * 10**6
lcf.time = lcf.time - lcf.time[0]

fig, ax = plt.subplots()
lcf.plot(ax=ax, color='black', xlabel='Time [d]', ylabel='Normalized Flux [ppm]' , normalize=False)
ax.set_xlim(lcf.time[0], lcf.time[-1])
ax.set_xlim(lcf.time[0] + 30, lcf.time[0] + 32)
ax.ticklabel_format(style = 'sci', scilimits = (0,0), axis = 'y', useMathText = True)
#ax.legend(loc='lower right')
plt.tight_layout()