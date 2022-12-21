# -*- coding: utf-8 -*-
"""
Created on Thu Jul 14 16:11:58 2022

@author: allen
"""


import pyvisa as visa
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

plt.close('all')

path = '220627'
exp = 'PhaseMod_Amp_14p73G_7dBm_noMod'
V = 0


rm = visa.ResourceManager()
visaObj = rm.open_resource('GPIB0::7::INSTR')
visaObj.timeout = 2000
# visaObj.values_format.is_binary = True
print(visaObj.query('*IDN?'))

# fprintf(visaObj,'*RST; :AUTOSCALE'); 
# fprintf(visaObj,':STOP');
# % Specify data from Channel 1
visaObj.write(':WAVEFORM:SOURCE CHAN1') 
# % Set timebase to main
visaObj.write(':TIMEBASE:MODE MAIN')
# % Set up acquisition type and count. 
visaObj.write(':ACQUIRE:TYPE NORMAL')
visaObj.write(':ACQUIRE:COUNT 1')
visaObj.write(':ACQUIRE:POINTS 5000')
# % Specify 5000 points at a time by :WAV:DATA?
visaObj.write(':WAV:POINTS:MODE RAW')
visaObj.write(':WAV:POINTS 5000')
# % Now tell the instrument to digitize channel1
# visaObj.write(':DIGITIZE CHAN1')
# % Wait till complete
# operationComplete = int(visaObj.query('*OPC?'))
# while not operationComplete:
#     operationComplete = int(visaObj.query('*OPC?'))

# % Get the data back as a WORD (i.e., INT16), other options are ASCII and BYTE
visaObj.write(':WAVEFORM:FORMAT ASCii')
# % Set the byte order on the instrument as well
# visaObj.write(':WAVEFORM:BYTEORDER LSBFirst')
# % Get the preamble block
preambleBlock = visaObj.query(':WAVEFORM:PREAMBLE?')
# % The preamble block contains all of the current WAVEFORM settings.  
# % It is returned in the form <preamble_block><NL> where <preamble_block> is:
# %    FORMAT        : int16 - 0 = BYTE, 1 = WORD, 2 = ASCII.
# %    TYPE          : int16 - 0 = NORMAL, 1 = PEAK DETECT, 2 = AVERAGE
# %    POINTS        : int32 - number of data points transferred.
# %    COUNT         : int32 - 1 and is always 1.
# %    XINCREMENT    : float64 - time difference between data points.
# %    XORIGIN       : float64 - always the first data point in memory.
# %    XREFERENCE    : int32 - specifies the data point associated with
# %                            x-origin.
# %    YINCREMENT    : float32 - voltage diff between data points.
# %    YORIGIN       : float32 - value is the voltage at center screen.
# %    YREFERENCE    : int32 - specifies the data point where y-origin
# %                            occurs.
# % Now send commmand to read data
RawData = visaObj.query(':WAV:DATA?')
# RawData = visaObj.read_raw()
# % read back the BINBLOCK with the data in specified format and store it in
# % the waveform structure. FREAD removes the extra terminator in the buffer
# waveform.RawData = binblockread(visaObj,'uint16'); fread(visaObj,1);
# % Read back the error queue on the instrument
# instrumentError = query(visaObj,':SYSTEM:ERR?');
# while ~isequal(instrumentError,['+0,"No error"' char(10)])
#     disp(['Instrument Error: ' instrumentError]);
#     instrumentError = query(visaObj,':SYSTEM:ERR?');
# end
# % Close the VISA connection.
visaObj.close()
# RawData = [RawData[N] for N in range(len(RawData[:-1]))]
# RawData = np.array(RawData)
# plt.plot(RawData)

RawData = RawData.replace('\r\n\x00','')
RawData = RawData.split('\n')[0]
RawData = [float(i) for i in RawData.split(',')]
RawData = np.array(RawData)

# %% Data processing: Post process the data retreived from the scope
# % Extract the X, Y data and plot it 

# % Maximum value storable in a INT16
maxVal = 2**16; 

# %  split the preambleBlock into individual pieces of info
preambleBlock = preambleBlock.split(',');

# % store all this information into a waveform structure for later use
Format = int(preambleBlock[0])     # This should be 1, since we're specifying INT16 output
Type = int(preambleBlock[1])
Points = int(preambleBlock[2])
Count = int(preambleBlock[3])      # This is always 1
XIncrement = float(preambleBlock[4]) # in seconds
XOrigin = float(preambleBlock[5])    # in seconds
XReference = float(preambleBlock[6])
YIncrement = float(preambleBlock[7]) # V
YOrigin = float(preambleBlock[8])
YReference = float(preambleBlock[9])
VoltsPerDiv = (maxVal * YIncrement / 8)      # V
Offset = ((maxVal/2 - YReference) * YIncrement + YOrigin)         # V
SecPerDiv = Points * XIncrement/10  # seconds
Delay = ((Points/2 - XReference) * XIncrement + XOrigin) # seconds
# 
# % Generate X & Y Data
XData = (XIncrement*(np.arange(len(RawData)))) - XIncrement;
YData = RawData

# % Plot it
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(XData,YData);
ax.set_xlabel('Time (s)');
ax.set_ylabel('Volts (V)');
ax.set_title('Oscilloscope Data');
ax.grid(True);

# %% Now let's also get the screenshot of the instrument and display it in MATLAB

# % Grab the screen from the instrument and display it
# % Set the buffer size to a large value sinze the BMP could be large
# visaObj.InputBufferSize = 10000000;
# % reopen the connection
# fopen(visaObj);
# % send command and get BMP.
# fprintf(visaObj,':DISPLAY:DATA? BMP, SCREEN, GRAYSCALE');
# screenBMP = binblockread(visaObj,'uint8'); fread(visaObj,1);
# % save as a BMP  file
# fid = fopen('test1.bmp','w');
# fwrite(fid,screenBMP,'uint8');
# fclose(fid);
# % Read the BMP and display image
# figure; colormap(gray(256)); 
# imageMatrix = imread('test1.bmp','bmp');
# image(imageMatrix); 
# % Adjust the figure so it shows accurately
# sizeImg = size(imageMatrix);
# set(gca,'Position',[0 0 1 1],'XTick' ,[],'YTick',[]); set(gcf,'Position',[50 50 sizeImg(2) sizeImg(1)]);
# axis off; axis image;

# % Delete objects and clear them.
# delete(visaObj); clear visaObj;
