# -*- coding: utf-8 -*-
"""
Created on Sat Jul  9 15:09:59 2022

@author: allen
"""
from Instruments import *
import matplotlib.pyplot as plt
import os
plt.close('all')

# OSC
OSC_address = 'GPIB0::7::INSTR'

path = '220709'
with HP54810A(OSC_address) as osc:
    data = osc.fetchData()
    
    
plt.plot(data.Time,data.Volts)
# data.to_csv(os.path.join(path,'Osc_ch2.csv'),index=False)


