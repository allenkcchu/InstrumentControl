#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 16:57:39 2022

@author: allenchu
"""

import PyDAQmx as nidaq
from ND import AIVoltageChan, AIParameters
from APTmotor import APTMotor as APT
import matplotlib.pyplot as plt
import numpy as np

N = 1000
rate = 1e5

mode = nidaq.DAQmx_Val_Diff
sampling_type = nidaq.DAQmx_Val_FiniteSamps #nidaq.DAQmx_ContSamps for continuous - must stop the task and also update N to be the buffer size
timeout = 5

ai = AIVoltageChan(ai_param=AIParameters(rate, ['/Dev1/ai0','/Dev1/ai1']))

motor = APT(SerialNum=83844125)
print(motor.getPos())
ai.start()
ai.wait()
motor.mAbs(19)
data = ai.read()
ai.stop()
motor.mAbs(0)
# data inspection
print(data.shape)
print(data[0,:])
# print(data[1,:])
plt.plot(np.arange(N), data[0,:])
plt.show()
#daq = NIDAQmxInstrument(device_name='Dev4')  # hardware specified by model number
#print(daq)