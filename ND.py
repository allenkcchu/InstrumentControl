#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 16:48:35 2022

@author: allenchu
"""

import numpy as np
import PyDAQmx as nidaq
import time
import matplotlib.pyplot as plt 

class AIParameters(object):
    limits = (0, 5)
    physicalChannel = ["/Dev4/ai0"]

    def __init__(self, sample_rate, sample_number, channels=None, limits=None):
        self.sampleRate = sample_rate
        self.sampleNumber = sample_number
        if limits is None:
            limits = self.limits
        self.limit_inf= limits[0]
        self.limit_sup= limits[1]
        if channels is not None:
            if type(channels) is str:
                physicalChannel = [channels]
            self.physicalChannel = channels

    @property
    def device_name(self):
        device_name = self.physicalChannel[0].split('/')[0]
        if device_name == '' :
            device_name = self.physicalChannel[0].split('/')[1]
        return device_name

class Trigger(object):
    def __init__(self, terminal):
        self.terminal = terminal
class RisingTrigger(Trigger):
    direction = nidaq.DAQmx_Val_Rising
class FallingTrigger(Trigger):
    direction = nidaq.DAQmx_Val_Falling

class AIVoltageChan(nidaq.Task):
    def __init__(self, ai_param, reset=True, terminalConfig=nidaq.DAQmx_Val_RSE, trigger=None):
        if reset:
            nidaq.DAQmxResetDevice(ai_param.device_name)
        super(AIVoltageChan, self).__init__()
        self.sampleNumber = ai_param.sampleNumber
        self.sampleRate = ai_param.sampleRate
        self.limit_inf = ai_param.limit_inf
        self.limit_sup = ai_param.limit_sup
        self.physicalChannel = ai_param.physicalChannel
        self.numberOfChannel = len(ai_param.physicalChannel)
        if isinstance(terminalConfig, str):
            terminalConfig = getattr(nidaq, terminalConfig)
        self.terminalConfig = terminalConfig
        self.trigger = trigger
        self.configure()
    def configure(self):
        channel_string = ','.join(self.physicalChannel)
        self.CreateAIVoltageChan(channel_string,"",self.terminalConfig,
                                 self.limit_inf,self.limit_sup,
                                 nidaq.DAQmx_Val_Volts,None)
    def start(self):
        n = self.sampleNumber
        sampleRate = self.sampleRate
        # self.CfgSampClkTiming("/Dev4/PFI2",sampleRate,nidaq.DAQmx_Val_Rising,nidaq.DAQmx_Val_FiniteSamps,n)
        self.CfgSampClkTiming("",sampleRate,nidaq.DAQmx_Val_Rising,nidaq.DAQmx_Val_FiniteSamps,n)
        if self.trigger is not None:
            self.CfgDigEdgeRefTrig(self.trigger.terminal,self.trigger.direction,10)
        self.StartTask()
    def read(self):
        n = self.sampleNumber
        data = np.zeros((self.numberOfChannel,n), dtype=np.float64)
        read = nidaq.int32()
        self.ReadAnalogF64(n,10.0, nidaq.DAQmx_Val_GroupByChannel,data,n*self.numberOfChannel,nidaq.byref(read),None)
        return data
    def stop(self):
        self.StopTask()
    def wait(self, timeout=10):
        self.WaitUntilTaskDone(timeout)

