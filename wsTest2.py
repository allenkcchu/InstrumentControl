# -*- coding: utf-8 -*-
"""
Created on Wed Aug 17 14:46:16 2022

@author: allen
"""

#import wsapi python wrapper 
from wsapi import * 
import matplotlib.pyplot as plt 
import numpy as np

#Create the WSP vector Data 
wsFreq = np.arange(191.25, 196.275, 0.001) 
wsAttn = 10*np.sin(50*(wsFreq-191.25)/2/np.pi)+10 
wsPhase = 2*np.pi*np.cos(5*(wsFreq-191.25)) 
wsPort = np.ones(np.size(wsFreq))

#Create the WSP file 
WSPfile = open('TrigProfile.wsp', 'w') 
for x in range(np.size(wsFreq)):
    WSPfile.write("%0.3f\t%0.3f\t%0.3f\t%0.3f\n" % (wsFreq[x], wsAttn[x], wsPhase[x], wsPort[x])) WSPfile.close()

#Read Profile from WSP file 
WSPfile = open('TrigProfile.wsp', 'r') 
profiletext = WSPfile.read() WSPfile.close()

#create waveshaper instance and name it "ws1" 
rc = ws_create_waveshaper("ws1", "SN024187.wsconfig") 
print "ws_create_waveshaper rc="+ws_get_result_description(rc)

#compute filter profile from profile text, then load to Waveshaper device rc = ws_load_profile("ws1", profiletext) print "ws_load_profile rc="+ws_get_result_description(rc)

#delete the waveshaper instance rc = ws_delete_waveshaper("ws1") print "ws_delete_waveshaper rc="+ws_get_result_description(rc)