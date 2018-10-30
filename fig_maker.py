#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 28 16:46:16 2018

@author: jorgeagr
"""
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.animation as animation
import matplotlib.colors as colors

def frequency_grid(oversampling):
    df = 0.01 #1/period/oversampling
    fmax = 25 #1/(2*dt)
    fmin = df
    freqs = np.linspace(fmin, fmax, num=10000)
    omegas = 2*np.pi*freqs
    return freqs, omegas

golden_ratio = (np.sqrt(5) + 1) / 2
width = 12
height = width / golden_ratio

mpl.rcParams['font.size'] = 12
mpl.rcParams['figure.titlesize'] = 'large'
mpl.rcParams['legend.fontsize'] = 'small'
mpl.rcParams['figure.figsize'] = (width, height)

dsct_dir = 'deltasct/'
epic_ids = 'deltasct_epic.txt'
twomass_ids = 'deltasct_2mass.txt'

targets = np.load(dsct_dir + 'dsct_targets.npy')
campaigns = np.arange(0, 14, 1)
teff = np.load(dsct_dir + 'dsct_teff.npy')
logg = np.load(dsct_dir + 'dsct_logg.npy')

freqs, _ = frequency_grid(1)

dsct_start = np.where(np.isclose(freqs, 5, atol=1e-3))[0][0]

ps_image = np.load(dsct_dir + 'ps_image3.npy')

#for i in range(len(ps_image)):
#    ps_image[i][:dsct_start] = ps_image[i][:dsct_start] - ps_image[i][:dsct_start]
'''
amp_image = np.ones(shape = ps_image.shape)

for i in range(len(ps_image)):
    amp_image[i] = np.sqrt(4*ps_image[i] / 10000)
'''

def sorting(param='none'):
    if param == 'none':
        return
    elif param == 'teff':
        return np.argsort(teff)
    elif param == 'logg':
        return np.argsort(logg)[::-1]

sort = 'logg'

ps_image = ps_image[sorting(sort)]

fig, ax = plt.subplots()
img = ax.imshow(ps_image, cmap = 'binary', vmin=0.2,)
ax.axvline(x = dsct_start, linestyle='--', linewidth=1, color='red')
cbar = fig.colorbar(img)
cbar.ax.set_ylabel('Normalized Amplitude')
ax.set_aspect('auto')
#ax.set_xticklabels(np.arange(-1, 26, 1))
#ax.xaxis.set_major_locator(mtick.MultipleLocator(400))
ax.set_xticklabels(np.arange(-5, 30, 5))
ax.xaxis.set_major_locator(mtick.MultipleLocator(ps_image.shape[1]/5))
ax.xaxis.set_minor_locator(mtick.MultipleLocator(ps_image.shape[1]/25))
ax.set_xlabel('Frequency [1/d]')
if not sort:
    ax.set_yticklabels([])
    ax.set_ylabel('Targets')
elif sort == 'logg':
    logg = logg[sorting(sort)]
    multiple = 4
    dim = ps_image.shape[0]
    #ticks = np.hstack([0, logg[np.arange(0, dim, dim/multiple, dtype=np.int)]])
    #ax.set_yticklabels(ticks)
    ax.set_ylabel(r'$\log(g)$')
    #ax.yaxis.set_major_locator(mtick.MultipleLocator(dim/multiple))
    ax.yaxis.set_major_locator(mtick.FixedLocator([1, 19, 45, 65, 72, 101, 106, 111]))
   # ax.yaxis.set_minor_locator(mtick.FixedLocator([106, 101, 72, 45, 19, 1]))
    ax.set_yticklabels([4.3, 4.2, 4.1, 4, 3.9, 3.8, 3.7, 3.6, 3.5,])
plt.tight_layout()