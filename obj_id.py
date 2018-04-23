'''
== Object Identifier ==
+ Goes through FITS files, digs up some metadata
and lightcurves. Searches for more meta data
and writes a new FITS file with everything
+ Look for C14 and C15
'''
from astropy.io import fits
import numpy as np
#from astroML.time_series import lomb_scargle
from scipy.signal import lombscargle
import csv
import os
import subprocess
import createnpz

class CampaignManager(object):
     
    def __init__(self):
        with open('etc/config.txt', 'r') as config:
            opts = tuple(csv.reader(config, delimiter = ',', quoting = csv.QUOTE_MINIMAL))
            opts = dict( zip( [opts[i][0] for i in range(len(opts))] , [opts[i][1:] for i in range(len(opts))] ))

        for c in opts['campaigns']:
            folder = 'k2c' + c
            if not os.path.isdir(folder):
                print('Making directories for Campaign ' + c)
                subprocess.call(['mkdir', 'k2c' + c])
                subprocess.call(['mkdir', 'k2c' + c + '/csv'])
                subprocess.call(['mkdir', 'k2c' + c + '/data'])
                subprocess.call(['mkdir', 'k2c' + c + '/flags'])
                subprocess.call(['mkdir', 'k2c' + c + '/k2fits'])
                
        for c in opts['catalogs']:
            catalog = 'epic-catalog/epic_' + c + '_27Feb2018.txt'
            if not os.path.isfile(catalog):
                print('Downloading EPIC Catalog...')
                subprocess.run('epic-catalog/epic_ctlg_dl')
        
        print('\nDeveloped by: Jorge A. Garcia @ New Mexico State University')
        
        self.main()
    
    def main(self):
        
        main = '\n= Menu =\n1) Download\n2) Process\n3) Exit\n\nSelect an option: '
        while True:
            option = input(main)
            
            if option in ('1', 'download', 'Download', 'DOWNLOAD'):
                dtext =  '''\n= Download =
Possible arguments:
- If a single campaign is to be downloaded, enter the number of that campaign.
- If inputing multiple campaigns, seperate the numbers with only a space.
  (eg: 1 4 10 12)
- To download all campaigns, enter "all". (Will take a long time!)

Enter campaign(s) to be downloaded: '''
                
                campaign = input(dtext)
                
                if campaign in ('all', 'All', 'ALL'):
                    for c in os.listdir():
                        if 'k2c' in c:
                            if os.listdir(c + '/k2fits/') == []:
                                print('Downloading Campaign ' + campaign.lstrip('k2c') + '...')
                                subprocess.run('epic-catalog/'+ campaign)
                            else:
                                print('Campaign ' + campaign.lstrip('k2c') + ' already downloaded!')
                elif len(campaign) > 2:
                    campaign = campaign.split()
                    for c in campaign:
                        if os.listdir('k2c' + c + '/k2fits/') == []:
                            print('Downloading Campaign ' + c + '...')
                            subprocess.run('epic-catalog'+'/k2c' + c)
                        else:
                            print('Campaign ' + c + ' already downloaded!')
                else:
                    if os.listdir('k2c' + campaign + '/k2fits/') == []:
                        print('Downloading Campaign ' + campaign + '...')
                        subprocess.run('epic-catalog'+'/k2c' + campaign)
                    else:
                        print('Campaign ' + campaign + ' already downloaded!')
            
            elif option in ('2', 'process', 'Process', 'PROCESS'):
                ptext = '''\n= Process =
Possible arguments:
- If a single campaign is to be processed, enter the number of that campaign.
- If inputing multiple campaigns, seperate the numbers with only a space.
  (eg: 1 4 10 12)
- To process all campaigns, enter "all".(Will take a long time!)

Enter campaign(s) to be processed: '''
                campaign = input(ptext)
                
                if campaign in ('all', 'All', 'ALL'):
                    for c in os.listdir():
                        if 'k2c' in c:
                            self.process(c.lstrip('k2c'))
                elif len(campaign) > 2:
                    campaign = campaign.split()
                    for c in campaign:
                        self.process(c)
                else:
                    self.process(campaign)
                createnpz.stardic()
                
            else:
                print('Exiting...\nBye!')
                break
    
    def process(self, campaign):
        if os.listdir('k2c' + str(campaign) + '/k2fits/') == []:
            print('Must download FITS files for Campaign ' + str(campaign) +' first!')
        elif os.listdir('k2c' + str(campaign) + '/data/') == []:
                filelist = os.listdir('k2c' + str(campaign) + '/k2fits')
                print('Processing Campaign ' + str(campaign) + '...')
                for f in filelist:
                    print('k2c' + str(campaign) + '/k2fits/' + f)
                    ObjectID('k2c' + str(campaign) + '/k2fits/' + f)
                print('Finished Campaign ' + str(campaign))
        else:
            print('Campaign ' + str(campaign) + ' already processed!')
        

class ObjectID(object):
    
    def __init__(self, file):
        self.file = file  #String of name of the file
        
        with fits.open(self.file) as hdul:
            self.KEPLERID = int(hdul[0].header['KEPLERID']) #  Kepler ID
            self.EPIC = int(hdul[0].header['OBJECT'].strip('EPIC')) # EPIC ID.
                # Removes the 'EPIC' prefix from the ID.
            self.CAMPAIGN = str(hdul[0].header['CAMPAIGN']) # Campaign Number
            
            if self.CAMPAIGN in ['101', '102', '111', '112']:
                self.CAMPAIGN = self.CAMPAIGN[:-1]
            
            self.LC = hdul[1].data['PDCSAP_FLUX'] # Lightcurve w/ NaNs
            self.E_LC = hdul[1].data['PDCSAP_FLUX_ERR'] # Lightcurve Error w/ NaNs
            self.TIME = hdul[1].data['TIME'] # Time w/ NaNs
            
            self.processData()
            
            # Flag determines interest in data. 0 - Unprocessed.
            # 0 - Unprocessed. 1 - Priority. 2 - Good. 3 -Trash
            #self.FLAG = np.array([0])
            self.FLAG = 0
            
            self.MODULE = hdul[0].header['MODULE'] # CCD Module Number
            self.CHANNEL = hdul[0].header['CHANNEL'] # CCD Channel Number
            #self.OUTPUT = hdul[0].header['OUTPUT'] # CCD Output - Do we need this?
            
            self.RA = hdul[0].header['RA_OBJ'] # RA
            self.DEC = hdul[0].header['DEC_OBJ'] # Declination
            #self.PARALLAX = str(hdul[0].header['PARALLAX']) # Parallax. Left out due to buggy behavior
            
            self.CADENCE = hdul[0].header['OBSMODE'] # Long/short cadence observation
            
            self.searchEpic()
            self.writeCSV()
            self.createFlags()
            self.writeData()
    
    def searchEpic(self):
        if 210000000 >= self.EPIC >= 201000001:
            filename = 'epic_1_27Feb2018.txt'
        elif 220000000 >= self.EPIC >= 210000001:
            filename = 'epic_2_27Feb2018.txt'
        elif 230000000 >= self.EPIC >= 220000001:
            filename = 'epic_3_27Feb2018.txt'
        elif 240000000 >= self.EPIC >= 230000001:
            filename = 'epic_4_27Feb2018.txt'
        elif 250000000 >= self.EPIC >= 240000001:
            filename = 'epic_5_27Feb2018.txt'
        elif 251809654 >= self.EPIC >= 250000001:
            filename = 'epic_6_27Feb2018.txt'
        
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
        def frequency_grid(time, oversampling):
            period = time[-1] - time[0]
            dt = period / len(time)
            df = 1/period/oversampling
            fmax = 1/(2*dt)
            fmin = df
            freqs = np.arange(fmin, fmax, df)
            omegas = 2*np.pi*freqs
            return freqs, omegas
        
        with fits.open(self.file) as hdul:
            bjdrefi = hdul[1].header['BJDREFI']
            bjdreff = hdul[1].header['BJDREFF']
        
        self.TIME = self.TIME[~np.isnan(self.LC)] # Time
        self.E_LC = self.LC[~np.isnan(self.LC)] # Lightcurve
        self.LC = self.LC[~np.isnan(self.LC)] # Lightcurve
        
                #Jackiewicz  2011
        bad = np.where(np.std(np.diff(self.LC))*5 < np.abs(np.diff(self.LC)))
        mean = np.mean(self.LC)
        indy = []
        for b in bad[0]:
            if (self.LC[b] > (mean + 8*np.std(self.LC))) or (self.LC[b] < (mean - 8*np.std(self.LC))):
                indy.append(b)
        if indy:
            self.TIME = np.delete(self.TIME, indy)
            self.E_LC = np.delete(self.E_LC, indy)
            self.LC = np.delete(self.LC, indy)
        
        self.TIME = self.TIME + bjdrefi + bjdreff # Converts to Barycentric Julian Day
        mean = np.mean(self.LC)
        self.LC = (self.LC/mean - 1) * 10**6
        # How to turn E_LC into ppm???
        
        self.FREQS, omegas = frequency_grid(self.TIME, 1)
        #P_LS = lomb_scargle(self.TIME, self.LC, self.E_LC, omegas)
        P_LS = lombscargle(self.TIME, self.LC, omegas)
        self.A_LS = np.sqrt(4*P_LS / len(self.LC))
    
    def writeCSV(self):
        directory = 'k2c'+ str(self.CAMPAIGN) + '/csv/'
        atts = tuple(self.__dict__.items())
        
        with open(directory + str(self.EPIC) + '.csv', 'w+') as file:
            write = csv.writer(file, delimiter='|', quoting = csv.QUOTE_MINIMAL)
            for i in range(len(atts)):
                if i not in (range(4,10)):
                    write.writerow([atts[i][0], atts[i][1]])
        del atts
    
    def createFlags(self):
        directory = 'k2c'+ str(self.CAMPAIGN) + '/flags/'
        
        with open(directory + str(self.EPIC) + '.txt', 'w+') as file:
            file.write(str(self.FLAG))
    
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
            if i not in (range(4,10)):
                c = fits.Card(atts[i][0], atts[i][1], comments[i-1])
                head.append(c)
        phdu = fits.PrimaryHDU(header = head) # Creates PrimaryHDU from defined Header. == Metadata Here ==
        
        # Define columns to be used in a BinTable
        colt = fits.Column(name = 'TIME', format = 'E', unit = 'Days (d)', array = self.TIME) # Time Column
        collc = fits.Column(name = 'LC', format = 'E', unit = 'Amplitude (ppm)', array = self.LC) # LC Column
        colelc = fits.Column(name = 'E_LC', format = 'E', unit = 'Amplitude (ppm)', array = self.E_LC) # LC Column
        colfreq = fits.Column(name = 'FREQS', format = 'E', unit = 'Cycles per Day (1/d)', array = self.FREQS) # LC Column
        colps = fits.Column(name = 'AMP_LOMBSCARG', format = 'E', unit = 'Amplitude (ppm)', array = self.A_LS) # PS Column
        #colflag = fits.Column(name = 'FLAGS', format = 'I', array = self.FLAG)
        
        coldefsdata = fits.ColDefs([colt, collc, colelc]) # "Zips" the columns together
        binthdudata = fits.BinTableHDU.from_columns(coldefsdata) # Creates a BinTableHDU from the zipped columns
        binthdudata.name = 'DATA'
        
        coldefsamp = fits.ColDefs([colfreq, colps])
        binthduamp = fits.BinTableHDU.from_columns(coldefsamp)
        binthduamp.name = 'SPECTRUM'
        
        hdul = fits.HDUList([phdu, binthdudata, binthduamp])#, binthduflag]) # Creates an HDUList from the PrimaryHDU and BinTableHDU
        hdul.writeto(directory + str(self.EPIC) + '.fits') # Writes to assigned directory with object's EPIC ID

CampaignManager()