# -*- coding: utf-8 -*-
"""
Created on Wed May 18 15:04:22 2022

@author: allen
"""

from Instruments import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import time

date = '220609'

# Tunable laser
ProductID = 4106
DeviceKey = '6700 SN10173'

# OSA
OSA_address = 'GPIB0::1::INSTR'
ESA_address = 'GPIB0::21::INSTR'

#%% forward1
voltList = np.arange(9.7,11.21,0.01)
PiezoVoltage = list()
Wavelength = list()
path = os.path.join(date,'forward2')
with TLB6700(ProductID, DeviceKey) as tlb,\
     AQ3675(OSA_address) as osa,\
     R3465(ESA_address) as esa:
    tlb.query(f'SOUR:VOLT:PIEZ {0}')
    for v in voltList:
        tlb.query(f'SOUR:VOLT:PIEZ {v}')
        print(f'Voltage:{round(v,2)}%')
        PiezoVoltage.append(tlb.query('SOUR:VOLT:PIEZ?'))
        Wavelength.append(float(tlb.query('SENS:WAVE?')))
        # time.sleep(2)
        data = osa.fetchData()
        data.to_csv(os.path.join(path,f'osa{int(v*100)}.csv'),index=False)
        data = esa.fetchData()
        data.to_csv(os.path.join(path,f'esa{int(v*100)}.csv'),index=False)
    
df = pd.DataFrame({'Voltage':PiezoVoltage,
                    'Wavelength':Wavelength})
df.to_csv(os.path.join(path,'WavelengthTable.csv'),index=False)

#%% backward1
# voltList = np.arange(29,15.1,-0.1)
# PiezoVoltage = list()
# Wavelength = list()
# path = os.path.join(date,'backward1')
# with TLB6700(ProductID, DeviceKey) as tlb, AQ3675(OSA_address) as osa:
#     for v in voltList:
#         tlb.query(f'SOUR:VOLT:PIEZ {v}')
#         print(f'Voltage:{round(v,2)}%')
#         PiezoVoltage.append(tlb.query('SOUR:VOLT:PIEZ?'))
#         Wavelength.append(float(tlb.query('SENS:WAVE?')))
#         time.sleep(2)
#         data = osa.fetchData()
#         data.to_csv(os.path.join(path,f'data{int(v*100)}.csv'),index=False)
    
# df = pd.DataFrame({'Voltage':PiezoVoltage,
#                     'Wavelength':Wavelength})
# df.to_csv(os.path.join(path,'WavelengthTable.csv'),index=False)

# #%% forward2
# voltList = np.arange(15.2,17.01,0.01)
# PiezoVoltage = list()
# Wavelength = list()
# path = os.path.join(date,'forward2')
# with TLB6700(ProductID, DeviceKey) as tlb, AQ3675(OSA_address) as osa:
#     for v in voltList:
#         tlb.query(f'SOUR:VOLT:PIEZ {v}')
#         print(f'Voltage:{round(v,2)}%')
#         PiezoVoltage.append(tlb.query('SOUR:VOLT:PIEZ?'))
#         Wavelength.append(float(tlb.query('SENS:WAVE?')))
#         time.sleep(2)
#         data = osa.fetchData()
#         data.to_csv(os.path.join(path,f'data{int(v*100)}.csv'),index=False)
    
#     tlb.query('SOUR:VOLT:PIEZ 0')

# df = pd.DataFrame({'Voltage':PiezoVoltage,
#                     'Wavelength':Wavelength})
# df.to_csv(os.path.join(path,'WavelengthTable.csv'),index=False)