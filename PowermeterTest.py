# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 17:43:54 2022

@author: allen
"""

import pyvisa as visa
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

rm = visa.ResourceManager()
PM100 = rm.open_resource('USB0::0x1313::0x8072::P2003189::INSTR')
print(PM100.query('*IDN?'))
PM100.write('CORR:WAV 1550')
print(PM100.query('CORR:WAV?'))
print(f'Power: {PM100.query("MEAS:POW?")}')
PM100.close()