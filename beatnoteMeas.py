# -*- coding: utf-8 -*-
"""
Created on Thu May 26 19:59:04 2022

@author: allen
"""

from Instruments import *
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
import time
plt.close('all')

SG_address = 'GPIB0::27::INSTR'
ESA_address = 'GPIB0::21::INSTR'

path = '220526'
with R3465(ESA_address) as esa, SG384(SG_address) as sg:
    # freqList = np.arange(600e6,4001e6,400e6)
    # for N, freq in enumerate(freqList):
    #     sg.tuneFreq(freq)
    #     time.sleep(0.1)
        
    #     I = list()
    #     for N in range(20):
    #         print(f'Frequency: {int(freq*1e-6)}MHz, avg {N}')
    #         data = esa.fetchData()
    #         if N == 0:
    #             I = 10**(data.Intensity.values/10)
    #         else:
    #             I = I+10**(data.Intensity.values/10)
    #     I = I/(N+1)
    #     data.Intensity = 10*np.log10(I)
    #     plt.plot(data.Frequency,data.Intensity)
    #     data.to_csv(os.path.join(path,f'fmod_{int(freq*1e-6)}.csv'),index=False)
    
    sg.send('ENBR 0')
    print(sg.query('ENBR?'))
    freq=0
    time.sleep(0.1)
    for N in range(20):
        print(f'Frequency: {int(freq*1e-6)}MHz, avg {N}')
        data = esa.fetchData()
        if N == 0:
            I = 10**(data.Intensity.values/10)
        else:
            I = I+10**(data.Intensity.values/10)
    I = I/(N+1)
    data.Intensity = 10*np.log10(I)
    plt.plot(data.Frequency,data.Intensity)
    data.to_csv(os.path.join(path,f'fmod_{int(freq*1e-6)}.csv'),index=False)