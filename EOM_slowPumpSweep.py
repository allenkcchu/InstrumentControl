# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 10:51:50 2022

@author: allen
"""

from Instruments import *
import matplotlib.pyplot as plt
import time
import os

path = '221002_2'

plt.close('all')

OSC_address = 'GPIB0::7::INSTR'
SG_address = 'GPIB0::27::INSTR'
# Tunable laser
ProductID = 4106
DeviceKey = '6700 SN10173'
ampList = np.arange(8,16.1,1)
freqList = np.arange(1200e6,2201e6,20e6)
totalCount = 10
total = len(ampList)*len(freqList)*totalCount
print(f'Total iteration conditions: {total}')
with TLB6700(ProductID, DeviceKey) as tlb,\
     SG384(SG_address) as sg,\
     HP54810A(OSC_address) as osc:
         N = 0
         for amp in ampList:
             for freq in freqList:    
                 for count in range(totalCount):
                     N = N+1
                     print(f'{N/total*100:.2f}%:count {count}, amp {amp} dBm, freq {int(freq*1e-6)} MHz')
                     sg.tuneAmp(amp)
                     sg.tuneFreq(freq)
                     tlb.query(f'OUTP:SCAN:START')
                     while(int(tlb.query('*OPC?')) == 0):
                         pass
                     data = osc.fetchData()
                     
                     data.to_csv(os.path.join(path,f'SlowPumpMod_amp{int(round(amp*10,0))}_freq{int(round(freq*1e-6,0))}_{count}.csv'),index=False)
                     time.sleep(0.2)