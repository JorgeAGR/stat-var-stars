#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 00:32:16 2018

@author: jorgeagr
"""

from lightkurve import KeplerLightCurveFile, Periodogram
from lightkurve import log
log.setLevel('ERROR')
from astropy import units
import numpy as np
from scipy.signal import lombscargle
from scipy import interpolate

def frequency_grid(oversampling):
    df = 0.01 #1/period/oversampling
    fmax = 25 #1/(2*dt)
    fmin = df
    freqs = np.linspace(fmin, fmax, num=10000)
    omegas = 2*np.pi*freqs
    return freqs, omegas

target = 211044267
c = 4

pathdir = 'deltasct/'
epic_ids = 'deltasct_epic.txt'
twomass_ids = 'deltasct_2mass.txt'

#targets = [211044267, 211018096, 211080847, 214404873]
targets = np.load(pathdir + 'dsct_targets.npy')
campaigns = np.arange(0, 14, 1)

powerspectrum = []
freqs, omegas = frequency_grid(1)
freqs = freqs * (1/units.day)
dsct_start = np.where(np.isclose(freqs.value, 5, atol=1e-3))[0][0]

time_grid = np.linspace(0, 1, num = len(freqs))

for i in range(len(targets)):
    c = 4
    while True:
        try:      
            lcf = KeplerLightCurveFile.from_archive(targets[i], campaign=c)
            if np.shape(np.shape(lcf)) == (1,):
                times = []
                for index, image in enumerate(lcf):
                    times.append(lcf[index].PDCSAP_FLUX.flux.shape[0])
                lcf = lcf[np.argmax(times)]
            break
        except:
            c += 1
    
    print(targets[i], c, (lcf.time - lcf.time[0])[-1])
    
    lcf = lcf.PDCSAP_FLUX.normalize().remove_nans().remove_outliers(sigma=8).fill_gaps()
    
    #f = interpolate.interp1d(lcf.time-lcf.time[0], lcf.flux, kind='cubic')
    norm_time = (lcf.time - lcf.time[0]) / (lcf.time[-1] - lcf.time[0])
    f = interpolate.interp1d(norm_time, lcf.flux, kind='cubic')
    
    t = 0
    while True:
        try:
            lcf.flux = f(time_grid)
            #lcf.time = time_grids[t]
            lcf.time = np.linspace(0, lcf.time[-1]-lcf.time[0], num=len(time_grid))
            break
        except:
            #t += 1
            pass
    
    ps = Periodogram.from_lightcurve(lcf, frequency=freqs).power.value
    #freqs, omegas = frequency_grid(1)
    #ps = lombscargle(lcf.time-lcf.time[0], lcf.flux, omegas)
    max_freq = np.max(ps[dsct_start:])
    max_noise = np.max(ps[:dsct_start])
    if max_freq > max_noise:
        ps = ps / max_freq
    else:
        ps[dsct_start:] = ps[dsct_start:] / max_freq
        ps[:dsct_start] = ps[:dsct_start] / max_noise
    
    powerspectrum.append(ps)

ps_image = np.array(powerspectrum)

np.save(pathdir + 'ps_image4.npy', ps_image)