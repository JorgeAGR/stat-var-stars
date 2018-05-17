import pandas as pd
import numpy as np

parameters = np.load('etc/tnldict.npz')
flags = np.load('etc/flagarray.npy')

starlist = pd.DataFrame({'Star': parameters['stars'], 
                         'T_Eff': parameters['teff'],
                         'log_g': parameters['logg'],
                         'Flag': flags
                         })