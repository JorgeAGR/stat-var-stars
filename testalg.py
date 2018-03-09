# Testing algorithsm

from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
from astroML.time_series import lomb_scargle, lomb_scargle_bootstrap
from scipy.signal import lombscargle

def sin(t):
    f = 5*np.cos(2*np.pi*0.5*t)
    return f

#test1 = fits.open('k2c4/k2fits/210359769.fits')

def frequency_grid(time, oversampling):
    period = time[-1] - time[0]
    dt = period / len(time)
    df = 1/period/oversampling
    fmax = 1/(2*dt)
    fmin = df
    freqs = np.arange(fmin, fmax, df)
    omegas = 2*np.pi*freqs
    return freqs, omegas

days_to_seconds = 60 * 60 * 24
seconds_to_days = 1.0 / days_to_seconds

A = 2. # amplitude
period = 3 * days_to_seconds # seconds
frequency = 1.0 / period # Hertz
omega = 2. * np.pi * frequency # radians per second
phi = 0.5 * np.pi # radians
N = 1000 # number of samples we're dealing with
dt = 30 * 60 / 1.0 # 30 minutes each sample, ~5e-4 samples / sec

timesteps = np.linspace(0.0, N*dt, N)
signal = A * np.sin(omega * timesteps + phi)

freqs, omegas = frequency_grid(timesteps, 1)


#dy = dy = 0.5 + 0.5 * np.random.random(N)
    
#freqs, omegas = frequency_grid(timesteps, 1)
#P_LS = lomb_scargle(timesteps, signal, dy, omegas)#/ len(self.lc)
#A_LS = np.sqrt(4*P_LS / len(y))# * 10 ** 6

fig, ax = plt.subplots()
ax.plot(freqs, P_LS)
ax.grid()
