from astropy.io import fits
from astropy.table import Table
import numpy as np
import numpy.fft as fft
import scipy.signal as signal
import matplotlib.pyplot as plt
#import pandas as pd
#import openpyxl
import csv
from astroML.time_series import lomb_scargle, lomb_scargle_bootstrap

# Seperate into two classes Object and LightCurve

# Look into Astropy LombScargle Periodogram (Astropy?)

#power spectra
# ppm
# amplitudes sqrt(4*ps / N)

class LightCurve(object):
    
    def __init__(self,hdul):
        
        self.lc = hdul[1].data['PDCSAP_FLUX'] # Lightcurve
        self.time = hdul[1].data['TIME'] # Time
        self.dlc = hdul[1].data['PDCSAP_FLUX_ERR'] # Lightcurve Error
        
        self.time = self.time[~np.isnan(self.lc)]
        self.dlc = self.dlc[~np.isnan(self.lc)]
        self.lc = self.lc[~np.isnan(self.lc)]
        
        bjdrefi = hdul[1].header['BJDREFI']
        bjdreff = hdul[1].header['BJDREFF']
        self.time = self.time + bjdrefi + bjdreff
        
        self.standarize()
        self.amplitudeSpectrum()
    
    def standarize(self):
        mean = np.mean(self.lc)
        #std = np.std(self.lc)
        self.lc = (self.lc/mean - 1) * 10**6#/std
    
    def amplitudeSpectrum(self):
        def frequency_grid(time):
            freq_min = 2*np.pi / (time[-1] - time[0])
            freq_max = np.pi / np.median(time[1:] - time[:-1])
            n_bins = int(np.round(5 * (freq_max - freq_min)/freq_min))
            return np.linspace(freq_min, freq_max, n_bins)
        
        self.freqs = frequency_grid(self.time)
        P_LS = lomb_scargle(self.time, self.lc, self.dlc, self.freqs)
        self.A_LS = np.sqrt(4*P_LS / len(self.lc)) * 10 ** 6

class Object(object):
    
    def __init__(self, file):
        self.file = file  #String of name of the file
        
        with fits.open(self.file) as hdul:
            self.id = int(hdul[0].header['KEPLERID']) #  Kepler ID
            self.epic = int(hdul[0].header['OBJECT'].strip('EPIC')) # EPIC ID.
                # Removes the 'EPIC' prefix from the ID.
            self.campaign = hdul[0].header['CAMPAIGN'] # Campaign Number
            self.ccdChannel = hdul[0].header['CHANNEL']
            self.ccdModule = hdul[0].header['MODULE']
            #self.ccdOutput = hdul[0],header['OUTPUT'] #Do we need these two?
            
            self.ra = hdul[0].header['RA_OBJ'] # RA
            self.dec = hdul[0].header['DEC_OBJ'] # Declination
            self.parallax = hdul[0].header['PARALLAX'] # Parallax
            self.data = LightCurve(hdul)
            
            self.cadence = hdul[0].header['OBSMODE'] # Long/short cadence observation
            
            # Flag determines interest in data. 0 - Unprocessed.
            # 0 - Unprocessed. 1 - Priority. 2 - Good. 3 -Trash
            self.flag = 0
            
            self.searchEpic()
    
    def setFlag(self,integer):
        self.flag = integer
    
    def plot(self):
        fig, ax = plt.subplots()
        ax.plot(self.data.time, self.data.lc)
        #ax.plot(self.data.ps)
        ax.set_title('Object ID: ' + str(self.id) + '   Campaign: ' + str(self.campaign))
        ax.grid()
    
    def plotAS(self):
        fig, ax = plt.subplots()
        ax.plot(self.data.freqs, self.data.A_LS)
        #ax.plot(self.data.ps)
        ax.set_title('Object ID: ' + str(self.id) + '   Campaign: ' + str(self.campaign))
        #ax.set_xlim()
        #ax.set_yscale('log')
        #ax.set_ylim(0,10**8)
        ax.grid()
    
    def searchEpic(self):
        if 210000000 >= self.epic >= 201000001:
            filename = 'epic-catalog/epic_1_19Dec2017.txt'
            print('uh oh')
        elif 220000000 >= self.epic >= 210000001:
            filename = 'epic-catalog/epic_2_19Dec2017.txt'
        elif 230000000 >= self.epic >= 220000001:
            filename = 'epic-catalog/epic_3_19Dec2017.txt'
        elif 240000000 >= self.epic >= 230000001:
            filename = 'epic-catalog/epic_4_19Dec2017.txt'
        elif 250000000 >= self.epic >= 240000001:
            filename = 'epic-catalog/epic_5_19Dec2017.txt'
        elif 251809654 >= self.epic >= 250000001:
            filename = 'epic-catalog/epic_6_19Dec2017.txt'
        
        with open(filename) as file:
            for line in file:
                if str(self.epic) in line:
                    fields = line.split('|')
                    self.jmag = fields[31]
                    self.e_jmag = fields[32] 
                    self.hmag = fields[33]
                    self.e_hmag = fields[34]
                    self.kMag = fields[35]
                    self.e_kmag = fields[36]
                    self.kp = fields[45]
                    self.tEff = fields[46]
                    self.e_tEff = fields[47]
                    self.logg = fields[49]
                    self.e_logg = fields[50]
                    self.feh = fields[52]
                    self.e_feh = fields[53]
                    self.rad = fields[55]
                    self.e_rad = fields[56]
                    self.mass = fields[58]
                    self.e_mass = fields[59]
                    self.rho = fields[61]
                    self.e_rho = fields[62]
                    self.lum = fields[64]
                    self.e_lum = fields[65]
                    self.d = fields[67]
                    self.e_d = fields[68]
                    self.ebv = fields[70]
                    self.e_ebv = fields[71]
                    break
    
    def writeOut(self):
        with open(str(self.epic)+'.csv', 'w') as file:
            atts = tuple(self.__dict__.items())
            write = csv.writer(file, delimiter='|', quoting = csv.QUOTE_MINIMAL)
            for i in range(len(atts)):
                if i != 8:
                    write.writerow([atts[i][0], atts[i][1]])
            del atts
    
    '''def saveBinTable(self):
        with fits.open(self.file) as hdul:
            self.lctable = Table(hdul[1].data)'''


test1 = Object('k2c4/k2fits/ktwo210359769-c04_llc.fits')
test2 = fits.open('k2c4/data/210359769.fits')
#test2 = Object('k2c4/k2fits/ktwo210384590-c04_llc.fits')
#test3 = Object('k2c4/k2fits/ktwo210517342-c04_llc.fits')

#test3.data.standarize()
#test2.data.standarize()

#test3.data.powerSpectrum()
#test2.data.powerSpectrum()

#test3.plotAS()