#make dirs

import os

dirs = os.listdir()

for i in dirs:
    if 'k2c' in i:
        if not os.path.isdir(i+'/flags'):
            os.mkdir(i+'/flags')