# -*- coding: utf-8 -*-
"""
Created on Thu Sep  1 10:42:13 2022

@author: allen
"""

from Instruments import *
import matplotlib.pyplot as plt
plt.close('all')

# Tunable laser
ProductID = 4106
DeviceKey = '6700 SN10173'

with TLB6700(ProductID, DeviceKey) as tlb:
    print(int(tlb.query('*OPC?'))==1)
    tlb.query(f'OUTP:SCAN:START')
    while(int(tlb.query('*OPC?')) == 0):
        pass
    print(tlb.query('*OPC?'))