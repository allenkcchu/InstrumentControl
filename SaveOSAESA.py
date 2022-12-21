# -*- coding: utf-8 -*-
"""
Created on Wed Sep 14 19:40:14 2022

@author: allen
"""
from Instruments import *
import matplotlib.pyplot as plt
import os

plt.close('all')
filename = 'SolitonStep_1200MHz_12dBm.csv'
# ESA
ESA_address = 'GPIB0::21::INSTR'
# OSA
OSA_address = 'GPIB0::1::INSTR'

path = '221103'
with AQ3675(OSA_address) as osa,\
     R3465(ESA_address) as esa:
    dataOSA = osa.fetchData()
    dataESA = esa.fetchData(startFreq=10e6,stopFreq=1e9,Navg=1)
        
fig, ax = plt.subplots(ncols=2)
ax[0].plot(dataOSA.Wavelength,dataOSA.Intensity)
ax[1].plot(dataESA.Frequency,dataESA.Intensity)
dataOSA.to_csv(os.path.join(path,f'OSA_{filename}.csv'),index=False)
dataESA.to_csv(os.path.join(path,f'ESA_{filename}.csv'),index=False)    
