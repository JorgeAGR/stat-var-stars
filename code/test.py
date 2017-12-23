import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from astropy.io import fits
from astropy.visualization import astropy_mpl_style
plt.style.use(astropy_mpl_style)
import matplotlib.image as mpimg

#PyKE Tools
from pyke import kepextract, kepdraw

class RawLightCurve(object):
    
    def __init__(self,file,title,colorscale,colorlabel):
        self.file = file
        self.title = title
        
        self.imgdata = fits.getdata(self.file)
        
        self.shape = np.shape(self.imgdata)
        self.dim = len(self.shape)

test = RawLightCurve('ktwo210359769-c04_llc.fits','test','gray','test')

#plt.plot(test.imgdata[1])
#plt.show()

kepextract('ktwo210359769-c04_llc.fits','test.fits')
#kepdraw('test.fits')

f = fits.open('ktwo210359769-c04_llc.fits')
plt.plot(f.data['TIME'], f.data['SAP_FLUX'])
plt.show()