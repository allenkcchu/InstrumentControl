# -*- coding: utf-8 -*-
"""
Created on Wed May 18 14:52:52 2022

@author: allen
"""

import os
import sys
# import ipdb
import pandas as pd
import numpy as np
import pyvisa
# import clr
from time import sleep
from APTMotor import APTMotor
from ctypes import cdll,c_long, c_ulong, c_uint32,byref,create_string_buffer,c_bool,c_char_p,c_int, c_uint8, c_int16, c_uint16, c_double, sizeof, c_voidp
import TLBP2 
# from clr import System
# from System.Text import StringBuilder
# from System import Int32
# from System.Reflection import Assembly
# sys.path.append('C:\\Program Files\\New Focus\\New Focus Tunable Laser Application\\Bin\\')
# clr.AddReference('UsbDllWrap')
# import Newport
# from struct import unpack

def print_error_msg(bp2, errorCode):
    messageBuffer = create_string_buffer(1024)
    bp2.error_message(errorCode, messageBuffer)

    if((errorCode & TLBP2._VI_ERROR) == 0):
        print("Beam Profiler Warning:", messageBuffer.value)
    else:
        print("Beam Profiler Error:", messageBuffer.value)

        bp2.close()

# class TLB6700:
#     def __init__(self, ProductID, DeviceKey):
#         self.ProductID = ProductID
#         self.DeviceKey = DeviceKey
#     def __enter__(self):
#         self.answer = StringBuilder(64)
#         self.tlb = Newport.USBComm.USB()
#         self.tlb.OpenDevices(self.ProductID, True)
#         return self
#     def query(self, msg):
#         self.answer.Clear()
#         self.tlb.Query(self.DeviceKey, msg, self.answer)
#         return self.answer.ToString()

#     def __exit__(self, exc_type, exc_value, traceback):
#         self.tlb.CloseDevices()

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


class Keithley2401:
    def __init__(self, COM_address):
        self.address = COM_address
        self.rm = pyvisa.ResourceManager()
    def __enter__(self):
        self.smu = self.rm.open_resource(self.address)
        self.smu.baud_rate = 57600
        self.smu.read_termination = '\n'
        self.smu.write_termination = '\n'
        self.smu.write(':FORM:ELEM VOLT,CURR,RES')
        return self
    def fetchData(self):
        return [float(i) for i in self.smu.query(':READ?').split(',')]
    def currLimit(self, CurrLim=10e-3):
        self.smu.write(f':SENS:CURR:PROT {CurrLim}')
    def voltLimit(self, VoltLim = 1):
        self.smu.write(f':SENS:VOLT:PROT {VoltLim}')
    def setVolt(self, Voltage=1):
        self.smu.write(f':SOUR:VOLT:LEV {Voltage}')
    def setCurr(self, Current=1e-6):
        self.smu.write(f':SOUR:CURR:LEV {Current}')
    def send(self, command):
        self.smu.write(command)
    def get(self):
        msg = self.smu.read()
        return msg
    def request(self, command):
        msg = self.smu.query(command)
        return msg
    def __exit__(self, exc_type, exc_value, traceback):
        self.smu.write(':OUTP:STAT 0')
        self.smu.close()
        
class PM100USB:
    def __init__(self, COM_address):
        self.address = COM_address
        self.rm = pyvisa.ResourceManager()
    def __enter__(self):
        self.pm = self.rm.open_resource(self.address)
        self.pm.write(':PRES')
        self.pm.write('AVER:COUN 5')
        self.pm.write('CORR:WAV 1550')
        self.pm.write('MEAS:POW')
        return self
    def getPower(self):
        return float(self.pm.query('READ?'))
    def setWavelength(self, wavelength):
        self.pm.write(f'CORR:WAV {wavelength}')
    def send(self, command):
        self.pm.write(command)
    def get(self):
        msg = self.pm.read()
        return msg
    def request(self, command):
        msg = self.pm.query(command)
        return msg
    def __exit__(self, exc_type, exc_value, traceback):
        self.pm.close()
        
class PAX1000IR2:
    def __init__(self, COM_address):
        self.address = COM_address
        self.rm = pyvisa.ResourceManager()
    def __enter__(self):
        self.pax = self.rm.open_resource(self.address)
        self.pax.write('SENS:CALC:MOD 5')
        self.pax.write('INP:ROT:STAT 1')
        return self
    def getPolarization(self):
        return [float(i) for i in self.pax.query('SENS:DATA:LAT?').split(',')]
    def send(self, command):
        self.pax.write(command)
    def get(self):
        msg = self.pax.read()
        return msg
    def request(self, command):
        msg = self.pax.query(command)
        return msg
    def __exit__(self, exc_type, exc_value, traceback):
        self.pax.write('INP:ROT:STAT 0')
        self.pax.close()
        
class APT:
    def __init__(self, SerialNum=67856069, HWTYPE=29, dllname=os.path.join(os.getcwd(),'APT.dll')):
        self.address = SerialNum
        self.hwtype = HWTYPE
        self.dll = dllname
    def __enter__(self):
        self.apt = APTMotor(SerialNum=self.address, HWTYPE=self.hwtype, dllname=self.dll)
        hwInfo = self.apt.getHardwareInformation()
        hwInfo = [i.decode("utf-8") for i in hwInfo]
        self.hwInfo = f"{hwInfo[0]}, {hwInfo[1]}, {hwInfo[2]}"
        print(f"{hwInfo[0]}, {hwInfo[1]}, {hwInfo[2]}")
        return self
    
    def zero(self):
        self.apt.go_home()
    
    def moveAbs(self, location):
        self.apt.mAbs(location)
        
    def getPos(self):
        return float(self.apt.getPos())
    
    def close(self):
        self.apt.cleanUpAPT()
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

class BP209:
    def __init__(self, drumSpeed = 10):
        self.drumSpeed = drumSpeed

        self.bp2 = TLBP2.TLBP2()
        deviceCount = c_uint32()
        self.res = self.bp2.get_connected_devices(None, byref(deviceCount))
        if(self.res != 0):
            print_error_msg(self.bp2, self.res)
        if(deviceCount.value == 0):
            print("No device connected")
        print("Found devices: ", deviceCount.value)

        self.resStr = (TLBP2.BP2_DEVICE * deviceCount.value)()
        self.res = self.bp2.get_connected_devices(self.resStr, byref(deviceCount))
        if(self.res != 0):
            print_error_msg(self.bp2, self.res)
        self.bp2.close()
        print("Openning device: ", self.resStr[0].resourceString)

        return self
        
    def __enter__(self):
        self.bp2 = TLBP2.TLBP2()
        try:
            self.res = self.bp2.open(self.resStr[0].resourceString, c_bool(True), c_bool(True))
            if(self.res != 0):
                print_error_msg(self.bp2, self.res) 

            instrName = create_string_buffer(1024)
            self.res = self.bp2.get_instrument_name(instrName)
            instrName = instrName.raw.decode("utf8").strip("\x00")
            
            serialNum = create_string_buffer(1024)    
            self.res = self.bp2.get_serial_number(serialNum)
            serialNum = serialNum.raw.decode("utf8").strip("\x00")
            print(f"{instrName}, {serialNum}")
            
            device_status = c_uint16(0)
            self.res = 0
            while (self.res == 0 and (device_status.value & TLBP2.BP2_STATUS_SCAN_AVAILABLE) == 0):
                self.res = self.bp2.get_device_status(byref(device_status))
            
            sampleCount = c_uint16()
            resolution = c_double()

            self.res = self.bp2.set_drum_speed_ex(c_double(self.drumSpeed), byref(sampleCount), byref(resolution))
            if(self.res != 0):
                print_error_msg(self.bp2, self.res)

            gain_buffer = (c_uint8 * 5)()
            gain_buffer[0] = c_uint8(12)
            gain_buffer[1] = c_uint8(12)
            gain_buffer[2] = c_uint8(12)
            gain_buffer[3] = c_uint8(12)
            gain_buffer[4] = c_uint8(12)
            self.bp2.set_gains(gain_buffer, gain_buffer[4])
            self.res = self.bp2.set_auto_gain(c_bool(True))
            if(self.res != 0):
                print_error_msg(self.bp2, self.res)
            

            bw_buffer = (c_double * 4)()
            bw_buffer[0] = c_double(125.0)
            bw_buffer[1] = c_double(125.0)
            bw_buffer[2] = c_double(125.0)
            bw_buffer[3] = c_double(125.0) 
            self.res = self.bp2.set_bandwidths(bw_buffer)
            if(self.res != 0):
                print_error_msg(self.bp2, self.res)

            min_wavelength = c_uint16()
            max_wavelength = c_uint16()
            self.res = self.bp2.get_wavelength_range(byref(min_wavelength), byref(max_wavelength))
            if(self.res != 0):
                print_error_msg(self.bp2, self.res)

            self.res = self.bp2.set_wavelength(c_double(min_wavelength.value + (max_wavelength.value - min_wavelength.value)/2))
            if(self.res != 0):
                print_error_msg(self.bp2, self.res)

            self.res = self.bp2.set_position_correction(c_int16(TLBP2.VI_ON))
            if(self.res != 0):
                print_error_msg(self.bp2, self.res)
        except NameError as inst:
            print("Name Error: ", inst)
        except ValueError as inst:
            print("Value Error: ", inst)

        return self
    
    def getProfile(self):
        data = list
        if(self.res == 0):
            slit_data = (TLBP2.BP2_SLIT_DATA * 4)()
            calculation_result = (TLBP2.BP2_CALCULATIONS * 4)()
            power = c_double()
            powerSaturation = c_double()
            power_intensities = (c_double * 7500)()
            print("Calling get_slit_scan_data")
            if(self.res == 0):
                for count in range(10):
                    self.res = self.bp2.get_slit_scan_data(slit_data, calculation_result, byref(power), byref(powerSaturation), power_intensities)
                data.append(list(slit_data[0].slit_samples_positions))
                data.append(list(slit_data[0].slit_samples_intensities))
                data.append(list(slit_data[1].slit_samples_positions))
                data.append(list(slit_data[1].slit_samples_intensities))
            else:
                print("The scan returned the error:", self.res)
        else:
            print("The device status returned the error:", self.res)
        df = pd.DataFrame(data,columns = ['axis0_position','axis0_intensity','axis1_position','axis1_intensity'])
        return df
    
    def close(self):
        self.bp2.close()
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
