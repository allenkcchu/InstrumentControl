# -*- coding: utf-8 -*-
"""
Created on Wed May 18 14:52:52 2022

@author: allen
"""

import os
import sys
import ipdb
import pandas as pd
import numpy as np
import pyvisa
import clr
from time import sleep
from clr import System
from System.Text import StringBuilder
from System import Int32
from System.Reflection import Assembly
sys.path.append('C:\\Program Files\\New Focus\\New Focus Tunable Laser Application\\Bin\\')
clr.AddReference('UsbDllWrap')
import Newport
from struct import unpack

class TLB6700:
    def __init__(self, ProductID, DeviceKey):
        self.ProductID = ProductID
        self.DeviceKey = DeviceKey
    def __enter__(self):
        self.answer = StringBuilder(64)
        self.tlb = Newport.USBComm.USB()
        self.tlb.OpenDevices(self.ProductID, True)
        return self
    def query(self, msg):
        self.answer.Clear()
        self.tlb.Query(self.DeviceKey, msg, self.answer)
        return self.answer.ToString()

    def __exit__(self, exc_type, exc_value, traceback):
        self.tlb.CloseDevices()

class AQ3675:
    def __init__(self, GPIB_address):
        self.address = GPIB_address
        self.rm = pyvisa.ResourceManager()
    def __enter__(self):
        self.osa = self.rm.open_resource(self.address)
        self.osa.timeout = 10e3
        
        return self
    def fetchData(self):
        x = self.osa.query(':TRAC:DATA:X? TRA')
        y = self.osa.query(':TRAC:DATA:Y? TRA')
        df = pd.DataFrame({'Wavelength':x.split(','),
                           'Intensity':y.split(',')})
        df = df.apply(pd.to_numeric,errors='coerce')
        
        return df
    def __exit__(self, exc_type, exc_value, traceback):
        self.osa.close()

class R3465:
    def __init__(self, GPIB_address, samples=1001):
        self.address = GPIB_address
        self.rm = pyvisa.ResourceManager()
        self.samples = samples
        self.maxLevel = 14592
        self.minLevel = 1792
    def __enter__(self):
        self.esa = self.rm.open_resource(self.address)
        return self
    def fetchData(self,startFreq=0,stopFreq=3e9,dbpdiv=10,reflevel=10,Navg=3):
        self.esa.write(f'FA {startFreq}')
        self.esa.write(f'FB {stopFreq}')
        self.esa.write(f'DD {dbpdiv}')
        self.esa.write(f'RL {reflevel}')
        freq = np.linspace(startFreq,stopFreq,self.samples)
        DivOut = int(self.esa.query('DD?'))
        if DivOut == 0:
            Div = 10
        elif DivOut == 1:
            Div = 5
        elif DivOut == 2:
            Div = 2
        elif DivOut == 3:
            Div = 1
        elif DivOut == 4:
            Div = 0.5
        Ref = float(self.esa.query('RL?'))
        
        data = list()
        for N in range(Navg):
            self.esa.write('TAA?')
            dataTmp = list()
            for i in range(1001):
                tmp = self.esa.read()
                tmp = ((float(tmp)-self.minLevel)/(self.maxLevel-self.minLevel)-1)*10*Div+Ref
                dataTmp.append(10**(tmp*0.1))
            data.append(dataTmp)
        data = 10*np.log10(np.mean(np.array(data),axis=0))
        df = pd.DataFrame({'Frequency':freq,
                           'Intensity':data})
        
        
        return df
    def __exit__(self, exc_type, exc_value, traceback):
        self.esa.close()
        
class SG384:
    def __init__(self, GPIB_address):
        self.address = GPIB_address
        self.rm = pyvisa.ResourceManager()
    def __enter__(self):
        self.sg = self.rm.open_resource(self.address)
        self.sg.write('ENBR 1')
        self.sg.write('AMPR 1 vpp')
        return self
    def tuneFreq(self,freq):
        self.sg.write(f'FREQ {freq}')
    def tuneAmp(self,amp):
        self.sg.write(f'AMPR {amp}')
    def query(self,command):
        msg = self.sg.query(command)
        return msg
    def send(self,command):
        self.sg.write(command)
    def __exit__(self, exc_type, exc_value, traceback):
        self.sg.write('ENBR 0')
        self.sg.close()

class E5052A:
    def __init__(self, GPIB_address):
        self.address = GPIB_address
        self.rm = pyvisa.ResourceManager()
    def __enter__(self):
        self.ssa = self.rm.open_resource(self.address)
        return self
    def fetchData(self):
        x = self.ssa.query('CALC:PN1:DATA:XDAT?').split(',')
        y = self.ssa.query('CALC:PN1:DATA:RDAT?').split(',')
        df = pd.DataFrame({'Frequency':x,
                           'PN':y})
        df = df.apply(pd.to_numeric,errors='coerce')
        return df
    def getCarrier(self):
        carrier = self.ssa.query('CALC:PN1:DATA:CARR?')
        fc = float(carrier.split(',')[0])*1e-9
        power = float(carrier.split(',')[1])
        return (fc,power)
    def send(self, command):
        self.ssa.write(command)
    def get(self, command):
        msg = self.ssa.read(command)
        return msg
    def __exit__(self, exc_type, exc_value, traceback):
        self.ssa.close()
        
class N9010A:
    def __init__(self, GPIB_address):
        self.address = GPIB_address
        self.rm = pyvisa.ResourceManager()
    def __enter__(self):
        self.exa = self.rm.open_resource(self.address)
        return self
    def fetchData(self):
        data = self.exa.query('CALC:DATA?').split(',')
        data = np.array(data)
        data = data.reshape((-1,2))
        df = pd.DataFrame(data,columns=['Frequency','Intensity'])
        df = df.apply(pd.to_numeric,errors='coerce')
        return df
    def send(self, command):
        self.exa.write(command)
    def get(self, command):
        msg = self.exa.read(command)
        return msg
    def __exit__(self, exc_type, exc_value, traceback):
        self.exa.close()
        
        
class TDS7404:
    def __init__(self, GPIB_address):
        self.address = GPIB_address
        self.rm = pyvisa.ResourceManager()
    def __enter__(self):
        self.scope = self.rm.open_resource(self.address)
        return self
    def fetchData(self, channel):
        self.scope.write(f"DATA:SOU CH{channel}")
        self.scope.write('DATA:WIDTH 1')
        self.scope.write('DATA:ENC RPB')
        ymult = float(self.scope.query('WFMPRE:YMULT?'))
        yzero = float(self.scope.query('WFMPRE:YZERO?'))
        yoff = float(self.scope.query('WFMPRE:YOFF?'))
        xincr = float(self.scope.query('WFMPRE:XINCR?'))
        xdelay = float(self.scope.query('HORizontal:POSition?'))
        self.scope.write('CURVE?')
        data = self.scope.read_raw()
        headerlen = 2 + int(data[1])
        header = data[:headerlen]
        ADC_wave = data[headerlen:-1]
        ADC_wave = np.array(unpack('%sB' % len(ADC_wave),ADC_wave))
        Volts = (ADC_wave - yoff) * ymult  + yzero
        Time = np.arange(0, (xincr * len(Volts)), xincr)-((xincr * len(Volts))/2-xdelay)
        df = pd.DataFrame({'Time':Time-np.min(Time),
                           'Volts':Volts})
        return df
    def send(self, command):
        self.scope.write(command)
    def get(self, command):
        msg = self.scope.read(command)
        return msg
    def __exit__(self, exc_type, exc_value, traceback):
        self.scope.close()

class HP54810A:
    def __init__(self, GPIB_address):
        self.address = GPIB_address
        self.rm = pyvisa.ResourceManager()
    def __enter__(self):
        self.scope = self.rm.open_resource(self.address)
        self.scope.timeout = 2000
        self.scope.write(':WAVEFORM:SOURCE CHAN1') 
        self.scope.write(':TIMEBASE:MODE MAIN')
        self.scope.write(':ACQUIRE:TYPE NORMAL')
        self.scope.write(':ACQUIRE:COUNT 1')
        self.scope.write(':ACQUIRE:POINTS 5000')
        self.scope.write(':WAV:POINTS:MODE RAW')
        self.scope.write(':WAV:POINTS 5000')
        self.scope.write(':WAVEFORM:FORMAT ASCii')
        return self
    def fetchData(self):
        preambleBlock = self.scope.query(':WAVEFORM:PREAMBLE?')
        RawData = self.scope.query(':WAV:DATA?')
        RawData = RawData.replace('\r\n\x00','')
        RawData = RawData.split('\n')[0]
        RawData = [float(i) for i in RawData.split(',')]
        RawData = np.array(RawData)
        preambleBlock = preambleBlock.split(',');
        XIncrement = float(preambleBlock[4]) # in seconds
        XData = (XIncrement*(np.arange(len(RawData)))) - XIncrement;
        YData = RawData

        df = pd.DataFrame({'Time':XData,
                           'Volts':YData})
        return df
    def send(self, command):
        self.scope.write(command)
    def get(self):
        msg = self.scope.read()
        return msg
    def __exit__(self, exc_type, exc_value, traceback):
        self.scope.close()
