# Testing algorithsm

from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from astroML.time_series import lomb_scargle, lomb_scargle_bootstrap

'''hdul = fits.open('k2c4/k2fits/ktwo210517342-c04_llc.fits')
lc = hdul[1].data['PDCSAP_FLUX'] # Lightcurve
dlc = hdul[1].data['PDCSAP_FLUX_ERR'] # Lightcurve Error
time = hdul[1].data['TIME'] # Time
bjdrefi = hdul[1].header['BJDREFI']
bjdreff = hdul[1].header['BJDREFF']

time = time[~np.isnan(lc)]
dlc = lc[~np.isnan(lc)]
lc = lc[~np.isnan(lc)]

mean = np.mean(lc)
lc = (lc/mean - 1) * 10**6
time = time + bjdrefi + bjdreff
#time = time[::-1]
def frequency_grid(time):
    freq_min = 2*np.pi / (time[-1] - time[0])
    freq_max = np.pi / np.median(time[1:] - time[:-1])
    n_bins = np.round(5 * (freq_max - freq_min)/freq_min)
    return np.linspace(freq_min, freq_max, int(n_bins))

fgrid = frequency_grid(time)

P_LS = lomb_scargle(time, lc, dlc, fgrid)

A_LS = np.sqrt(4*P_LS / len(lc)) * 10 ** 6
'''
test1 = fits.open('k2c4/data/210359769.fits')

fig, ax = plt.subplots()
ax.plot(fgrid, A_LS)
ax.grid()
