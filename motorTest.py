#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Aug 15 16:48:58 2022

@author: allenchu
"""

from APTmotor import APTMotor as APT
import time
motor = APT(SerialNum=83844125)
msg = motor.getHardwareInformation()
print(msg)
print(motor.getPos())

# motor.go_home()
motor.mAbs(0)
print(motor.getPos())
motor.cleanUpAPT()