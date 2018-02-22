'''
== Object Identifier ==
+ Goes through FITS files, digs up some metadata
and lightcurves. Searches for more meta data
and writes a new FITS file with everything
'''
from astropy.io import fits
import numpy as np
from astroML.time_series import lomb_scargle
import csv
import os

class CampaignManager(object):
     
    def __init__(self):
        
        print('Developed by: Jorge A. Garcia @ New Mexico State University')
        
        self.main()
    
    def main(self):
        
        main = '=Menu=\n1) Process\n2) Exit\nSelect an option: '
        
        option = input(main)
        
        if option in ('1', 'process', 'Process'):
            self.process()
        else:
            print('Bye!')
    
    def process(self):
        while True:
            try:
                campaign = input('Enter campaign to process: ')
                int(campaign)
                break
            except:
                if campaign in ('q','Q','quit','QUIT','Quit'):
                    print('Bye!')
                    return
                else:
                    pass
        
        directory = 'k2c' + campaign + '/k2fits/'
        filelist = os.listdir(directory)
        
        for f in filelist:
            ObjectID(directory+f)
        print('Done!')
        repeat = input('Do another campaign?: ')
        if repeat in ('y','Y','yes','Yes','YES'):
            self.process(self)
        else:
            self.main()
        

class ObjectID(object):
    
    def __init__(self, file):
        self.file = file  #String of name of the file
        
        with fits.open(self.file) as hdul:
            self.KEPLERID = int(hdul[0].header['KEPLERID']) #  Kepler ID
            self.EPIC = int(hdul[0].header['OBJECT'].strip('EPIC')) # EPIC ID.
                # Removes the 'EPIC' prefix from the ID.
            self.CAMPAIGN = hdul[0].header['CAMPAIGN'] # Campaign Number
            
            self.LC = hdul[1].data['PDCSAP_FLUX'] # Lightcurve w/ NaNs
            self.E_LC = hdul[1].data['PDCSAP_FLUX_ERR'] # Lightcurve Error w/ NaNs
            self.TIME = hdul[1].data['TIME'] # Time w/ NaNs
            
            self.processData()
            
            # Flag determines interest in data. 0 - Unprocessed.
            # 0 - Unprocessed. 1 - Priority. 2 - Good. 3 -Trash
            self.FLAG = 0
            
            self.MODULE = hdul[0].header['MODULE'] # CCD Module Number
            self.CHANNEL = hdul[0].header['CHANNEL'] # CCD Channel Number
            #self.OUTPUT = hdul[0].header['OUTPUT'] # CCD Output - Do we need this?
            
            self.RA = hdul[0].header['RA_OBJ'] # RA
            self.DEC = hdul[0].header['DEC_OBJ'] # Declination
            self.PARALLAX = hdul[0].header['PARALLAX'] # Parallax
            
            self.CADENCE = hdul[0].header['OBSMODE'] # Long/short cadence observation
            
            self.searchEpic()
            self.writeCSV()
            self.writeData()
    
    def searchEpic(self):
        if 210000000 >= self.EPIC >= 201000001:
            filename = 'epic_1_19Dec2017.txt'
        elif 220000000 >= self.EPIC >= 210000001:
            filename = 'epic_2_19Dec2017.txt'
        elif 230000000 >= self.EPIC >= 220000001:
            filename = 'epic_3_19Dec2017.txt'
        elif 240000000 >= self.EPIC >= 230000001:
            filename = 'epic_4_19Dec2017.txt'
        elif 250000000 >= self.EPIC >= 240000001:
            filename = 'epic_5_19Dec2017.txt'
        elif 251809654 >= self.EPIC >= 250000001:
            filename = 'epic_6_19Dec2017.txt'
        
        with open('epic-catalog/' + filename) as file:
            for line in file:
                if str(self.EPIC) in line:
                    fields = line.split('|')
                    self.JMAG = fields[31]
                    self.E_JMAG = fields[32] 
                    self.HMAG = fields[33]
                    self.E_HMAG = fields[34]
                    self.KMAG = fields[35]
                    self.E_KMAG = fields[36]
                    self.KP = fields[45]
                    self.TEFF = fields[46]
                    self.E_TEFF = fields[47]
                    self.LOGG = fields[49]
                    self.E_LOGG = fields[50]
                    self.FEH = fields[52]
                    self.E_FEH = fields[53]
                    self.RAD = fields[55]
                    self.E_RAD = fields[56]
                    self.MASS = fields[58]
                    self.E_MASS = fields[59]
                    self.RHO = fields[61]
                    self.E_RHO = fields[62]
                    self.LUM = fields[64]
                    self.E_LUM = fields[65]
                    self.D = fields[67]
                    self.E_D = fields[68]
                    self.EBV = fields[70]
                    self.E_EBV = fields[71]
                    break
    
    def processData(self):
        def frequency_grid(time):
            freq_min = 2*np.pi / (time[-1] - time[0])
            freq_max = np.pi / np.median(time[1:] - time[:-1])
            n_bins = int(np.round(5 * (freq_max - freq_min)/freq_min))
            return np.linspace(freq_min, freq_max, n_bins)
        
        with fits.open(self.file) as hdul:
            bjdrefi = hdul[1].header['BJDREFI']
            bjdreff = hdul[1].header['BJDREFF']
        
        self.TIME = self.TIME[~np.isnan(self.LC)] # Time
        self.E_LC = self.LC[~np.isnan(self.LC)] # Lightcurve
        self.LC = self.LC[~np.isnan(self.LC)] # Lightcurve
        
        self.TIME = self.TIME + bjdrefi + bjdreff # Converts to Barycentric Julian Day
        mean = np.mean(self.LC)
        self.LC = (self.LC/mean - 1) * 10**6#/std
        # How to turn E_LC into ppm???
        
        self.FREQS = frequency_grid(self.TIME)
        P_LS = lomb_scargle(self.TIME, self.LC, self.E_LC, self.FREQS)
        self.A_LS = np.sqrt(4*P_LS / len(self.LC)) * 10 ** 6
    
    def writeCSV(self):
        directory = 'k2c'+ str(self.CAMPAIGN) + '/csv/'
        atts = tuple(self.__dict__.items())
        
        with open(directory + str(self.EPIC) + '.csv', 'w') as file:
            write = csv.writer(file, delimiter='|', quoting = csv.QUOTE_MINIMAL)
            for i in range(len(atts)):
                if i not in (range(4,9)):
                    write.writerow([atts[i][0], atts[i][1]])
        
        del atts
    
    def writeData(self):
        directory = 'k2c' + str(self.CAMPAIGN) + '/data/' # Sets string for directory according to campaign
        atts = tuple(self.__dict__.items()) # Creates a tuple of tuples, containing (Keyword, Value) of attributes
        
        comments = []
        with open('etc/fits-comments.txt', 'r') as txt:
            read = csv.reader(txt)
            for line in read:
                comments.append(line)
        
        head = fits.Header() # Defines Header for PrimaryHDU
        for i in range(1,len(atts)): # Iteration to create and assign Cards of attributes for Header (Except TIME, LC+E, FREQS and A_LS)
            if i not in (range(4,9)):
                c = fits.Card(atts[i][0], atts[i][1], comments[i])
                head.append(c)
        phdu = fits.PrimaryHDU(header = head) # Creates PrimaryHDU from defined Header. == Metadata Here ==
        
        # Define columns to be used in a BinTable
        colt = fits.Column(name = 'TIME', format = 'E', unit = 'd', array = self.TIME) # Time Column
        collc = fits.Column(name = 'LC', format = 'E', unit = 'ppm', array = self.LC) # LC Column
        colelc = fits.Column(name = 'E_LC', format = 'E', unit = 'ppm', array = self.E_LC) # LC Column
        colfreq = fits.Column(name = 'FREQS', format = 'E', unit = '1/d', array = self.FREQS) # LC Column
        colps = fits.Column(name = 'AMP_LOMBSCARG', format = 'E', unit = 'ppm', array = self.A_LS) # PS Column
        
        coldefsdata = fits.ColDefs([colt, collc, colelc]) # "Zips" the columns together
        binthdudata = fits.BinTableHDU.from_columns(coldefsdata) # Creates a BinTableHDU from the zipped columns
        binthdudata.name = 'DATA'
        
        coldefsamp = fits.ColDefs([colfreq, colps])
        binthduamp = fits.BinTableHDU.from_columns(coldefsamp)
        binthduamp.name = 'SPECTRUM'
        
        hdul = fits.HDUList([phdu, binthdudata, binthduamp]) # Creates an HDUList from the PrimaryHDU and BinTableHDU
        hdul.writeto(directory + str(self.EPIC) + '.fits') # Writes to assigned directory with object's EPIC ID

#test1 = ObjectID('k2c4/k2fits/testlc1.fits')
manager = CampaignManager()