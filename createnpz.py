import numpy as np
import os
from astropy.io import fits

class Object(object):
    
    def __init__(self, file, flagdir):
        self.file = file  #String of name of the file
        self.flagdir = flagdir
        
        self.titles = []
        self.values = []
        
        with fits.open(self.file) as hdul:
            for i in range(len(hdul)):
                for title in hdul[i].header:
                    if title not in ('SIMPLE', 'BITPIX', 'NAXIS', 'EXTEND', 'EXTNAME'):
                        if i == 0:
                            self.titles.append(title)
                            if title in ('KEPLERID', 'EPIC','CAMPAIGN','MODULE','CHANNEL'):
                                self.values.append(int(hdul[i].header[title]))
                            else:
                                if hdul[i].header[title] == '':
                                    self.values.append(np.nan)
                                else:
                                    try:
                                        self.values.append(round(float(hdul[i].header[title]), 3))
                                    except:
                                        self.values.append(hdul[i].header[title])
                        elif i == 3:
                            if title in ('TTYPE1'):
                                self.titles.append(hdul[i].header[title])
                                self.values.append(hdul[i].data[hdul[i].header[title]][-1])
                        else:
                            if title in ('TTYPE1', 'TTYPE2', 'TTYPE3'):
                                self.titles.append(hdul[i].header[title])
                                self.values.append(hdul[i].data[hdul[i].header[title]])
                            if title in ('TUNIT1', 'TUNIT2', 'TUNIT3'):
                                self.titles.append(hdul[i].header['TTYPE'+title[-1]]+' UNIT')
                                self.values.append(hdul[i].header[title])
        
        self.cards = dict(zip(self.titles,self.values))
        
        self.FLAGS = []
        with open(self.flagdir) as file:
            for line in file:
                self.FLAGS.append(line)


def stardic():
    
    print('Updating Starlist...')
    
    campaigns = []
    for d in os.listdir():
            if 'k2c' in d:
                campaigns.append(int(d.lstrip('k2c')))
    campaigns = np.sort(campaigns)
    #campaigns = [4, 5, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16]
    
    stars = np.array([])
    teff = np.array([])
    logg = np.array([])
    flag = np.array([])
    for i in campaigns:
        directory = 'k2c' + str(i) + '/data/'
        f = os.listdir(directory)
        print(str(len(f)) + ' files in Campaign ' + str(i))
        for file in f:
            filedir = 'k2c'+ str(i) + '/data/' + file
            flagdir = 'k2c' + str(i) + '/flags/' + file[0:9] + '.txt'
            obj = Object(filedir, flagdir)
            stars = np.append(stars, file.rstrip('.fits'))
            teff = np.append(teff, obj.cards['TEFF'])
            logg = np.append(logg, obj.cards['LOGG'])
            flag = np.append(flag, int(obj.FLAGS[-1]))
    
    np.savez('etc/tnldict.npz', stars = stars, teff = teff, logg = logg, flag = flag)
    
    print('Starlist updated!')