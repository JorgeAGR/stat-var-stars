from astropy.io import fits
from astropy.table import Table
import numpy as np
import numpy.fft as fft
import matplotlib.pyplot as plt
#import pandas as pd
#import openpyxl
import csv

# Seperate into two classes Object and LightCurve
# H, J and K magnitudes Derived properties.
#for every object: txt with metadata and fits for data

#

class LightCurve(object):
    
    def __init__(self,hdul):
        
        self.lc = hdul[1].data['PDCSAP_FLUX'] # Lightcurve
        self.time = hdul[1].data['TIME'] # Time
        
        self.lc = self.lc[~np.isnan(self.lc)]
    
    def standarize(self):
        mean = np.mean(self.lc)
        #std = clnp.std(self.lc)
        self.lc = (self.lc - mean)#/std
    
    def powerSpectrum(self):
        self.ps = np.abs(fft.rfft(self.lc))**2
        self.ps = fft.fftshift(self.ps)
    
    

class Object(object):
    
    def __init__(self, file):
        self.file = file  #String of name of the file
        
        with fits.open(self.file) as hdul:
            self.id = int(hdul[0].header['KEPLERID']) #  Kepler ID
            self.epic = int(hdul[0].header['OBJECT'].strip('EPIC')) # EPIC ID.
                # Removes the 'EPIC' prefix from the ID.
            self.campaign = hdul[0].header['CAMPAIGN'] # Campaign Number
            self.ccdModule = hdul[0].header['MODULE']
            #self.ccdChannel = hdul[0].header['CHANNEL']
            #self.ccdOutput = hdul[0],header['OUTPUT'] #Do we need these two?
            
            self.ra = hdul[0].header['RA_OBJ'] # RA
            self.dec = hdul[0].header['DEC_OBJ'] # Declination
            self.parallax = hdul[0].header['PARALLAX'] # Parallax
            self.data = LightCurve(hdul)
            
            self.cadence = hdul[0].header['OBSMODE'] # Long/short cadence observation
            
            # Flag determines interest in data. 0 - Unprocessed.
            # 0 - Unprocessed. 1 - Priority. 2 - Good. 3 -Trash
            self.flag = 0
    
    def saveBinTable(self):
        with fits.open(self.file) as hdul:
            self.lctable = Table(hdul[1].data)
    
    def setFlag(self,integer):
        self.flag = integer
    
    def plot(self):
        fig, ax = plt.subplots()
        ax.plot(self.data.lc)
        #ax.plot(self.data.ps)
        ax.set_title('Object ID: ' + str(self.id) + '   Campaign: ' + str(self.campaign))
        ax.grid()
    
    def plotPS(self):
        fig, ax = plt.subplots()
        ax.plot(self.data.ps)
        #ax.plot(self.data.ps)
        ax.set_title('Object ID: ' + str(self.id) + '   Campaign: ' + str(self.campaign))
        #ax.set_xlim(0,300)
        ax.set_yscale('log')
        #ax.set_ylim(0,10**8)
        ax.grid()
    
    def searchEpic(self):
        if 210000000 >= self.epic >= 201000001:
            filename = 'epic_1_19Dec2017.txt'
            print('uh oh')
        elif 220000000 >= self.epic >= 210000001:
            filename = 'epic_2_19Dec2017.txt'
        elif 230000000 >= self.epic >= 220000001:
            filename = 'epic_3_19Dec2017.txt'
        elif 240000000 >= self.epic >= 230000001:
            filename = 'epic_4_19Dec2017.txt'
        elif 250000000 >= self.epic >= 240000001:
            filename = 'epic_5_19Dec2017.txt'
        elif 251809654 >= self.epic >= 250000001:
            filename = 'epic_6_19Dec2017.txt'
        
        with open(filename) as file:
            for line in file:
                if str(self.epic) in line:
                    fields = line.split('|')
                    self.jMag = fields[31]
                    self.hMag = fields[33]
                    self.kMag = fields[35]
                    self.kp = fields[45]
                    self.tEff = fields[46]
                    self.e_tEff = fields[47]
                    self.logg = fields[48]
                    self.e_logg = fields[49]
                    self.metallicty = fields[50]
                    self.e_metallicity = fields[51]
                    self.rad = fields[52]
                    self.e_rad = fields[53]
                    self.mass = fields[54]
                    self.e_mass = fields[55]
                    self.rho = fields[56]
                    self.e_rho = fields[57]
                    self.lum = fields[58]
                    self.e_lum = fields[59]
                    self.d = fields[60]
                    self.e_d = fields[61]
                    self.ebv = fields[62]
                    break

    def writeOut(self):
        with open(str(self.epic)+'.csv', 'w') as file:
            atts = tuple(self.__dict__.items())
            write = csv.writer(file, delimiter='|', quoting = csv.QUOTE_MINIMAL)
            for i in range(len(atts)):
                if i != 8:
                    write.writerow([atts[i][0], atts[i][1]])
            del atts

test1 = Object('testlc1.fits')
test2 = Object('testlc2.fits')

test1.data.standarize()
#test2.data.standarize()

test1.data.powerSpectrum()
#test2.data.powerSpectrum()