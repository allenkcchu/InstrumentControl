# -*- coding: utf-8 -*-
"""
Created on Thu May 26 17:25:04 2022

@author: allen
"""

from Instruments import *
import matplotlib.pyplot as plt
import pyvisa as visa
import numpy as np
import os
plt.close('all')

rm = visa.ResourceManager()

# PSA
PSA_address = 'GPIB0::18::INSTR'

path = '221127'
with rm.open_resource(PSA_address) as psa:
    print(psa.query('*IDN?'))
    print(psa.query('SENSE:SWE:POIN?'))
    # print(psa.query(':FORM:TRAC:DATA?'))
    data = psa.query('TRAC:DATA? TRACE1')
    freqStart = float(psa.query('SENS:FREQ:STAR?'))
    freqStop = float(psa.query('SENS:FREQ:STOP?'))
    step = float(psa.query('SENS:FREQ:CENT:STEP:INCR?'))
intensity = np.array([float(i) for i in data.split(',')])
freq = np.linspace(freqStart,freqStop,len(intensity))


data = pd.DataFrame({'Frequency':freq,
                     'Intensity':intensity})
plt.plot(data.Frequency,data.Intensity)

data.to_csv(os.path.join(path,f'feom_bestcomb_3.csv'),index=False)