# -*- coding: utf-8 -*-
"""
Created on Thu May 26 17:25:04 2022

@author: allen
"""

from Instruments import *
import matplotlib.pyplot as plt
plt.close('all')

# ESA
SG_address = 'GPIB0::27::INSTR'

with SG384(SG_address) as sg:
    sg.tuneAmp(6)
    print(sg.query('AMPR?'))
# plt.plot(data.Frequency,data.Intensity)