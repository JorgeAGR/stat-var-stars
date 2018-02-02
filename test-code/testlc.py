from astropy.io import fits
from astropy.table import Table
import numpy as np
import numpy.fft as fft
import matplotlib.pyplot as plt

# Seperate into two classes Object and LightCurve
# H, J and K magnitudes Derived properties.
# grep to search text
#for every object: txt with metadata and fits for data

class LightCurve(object):
    
    def __init__(self,hdul):
        
        self.lc = hdul[1].data['PDCSAP_FLUX'] # Lightcurve
        self.time = hdul[1].data['TIME'] # Time
        
        self.lc = self.lc[~np.isnan(self.lc)]
        self.ps = np.abs(fft.rfft(self.lc))**2
    
    def standarize(self):
        mean = np.mean(self.lc)
        self.lc = self.lc - mean
    
    

class Object(object):
    
    def __init__(self, file):
        self.file = file  #String of name of the file
        
        with fits.open(self.file) as hdul:
            self.id = hdul[0].header['KEPLERID'] #  Kepler ID
            self.epic = hdul[0].header['OBJECT'] # EPIC ID
            self.campaign = hdul[0].header['CAMPAIGN'] # Campaign Number
            self.ccdModule = hdul[0].header['MODULE']
            #self.ccdChannel = hdul[0].header['CHANNEL']
            #self.ccdOutput = hdul[0],header['OUTPUT'] #Do we need these two?
            
            self.ra = hdul[0].header['RA_OBJ'] # RA
            self.dec = hdul[0].header['DEC_OBJ'] # Declination
            self.parallax = hdul[0].header['PARALLAX'] # Parallax
            self.data = LightCurve(hdul)
            
            self.cadence = hdul[0].header['OBSMODE'] #Long/short cadence observation
            
            #Flag determines interest in data. 0 - Unprocessed.
            #0 - Unprocessed. 1 - Priority. 2 - Good. 3 -Trash
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

test1 = Object('testlc1.fits')
test2 = Object('testlc2.fits')