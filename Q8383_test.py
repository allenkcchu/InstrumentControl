# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 12:37:30 2022

@author: allen
"""

import pyvisa as visa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

plt.close('all')

path = '221122'
exp = 'EOcomb'
DUTID = '1um_200GHz'


rm = visa.ResourceManager()
osa = rm.open_resource('GPIB0::9::INSTR')
datay = osa.query('OSD0?')
datax = osa.query('OSD1?')
osa.close()

df = pd.DataFrame({'Wavelength':np.array(datax.split(',')).astype(np.float64),
                   'Intensity':np.array(datay.split(',')).astype(np.float64)
})
plt.plot(df.Wavelength*1e9,df.Intensity)

df.to_csv(os.path.join(path,f'{exp}_{DUTID}.csv'),index=False)