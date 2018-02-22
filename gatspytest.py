# Gatspy tests
import numpy as np
import matplotlib.pyplot as plt
from astroML.datasets import fetch_LINEAR_sample

#LINEAR_data = fetch_LINEAR_sample()
star_id = 10040133
t, mag, dmag = LINEAR_data.get_light_curve(star_id).T

fig, ax = plt.subplots()
ax.errorbar(t, mag, dmag, fmt='.k', ecolor='gray')
ax.set(xlabel='Time (days)', ylabel='magitude',
       title='LINEAR object {0}'.format(star_id))
ax.invert_yaxis();