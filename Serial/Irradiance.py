#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 30 13:35:45 2017

@author: Zachary Taylor
"""


import serial

serialPort = '/dev/ttyACM2'#Serial Port where the USB is plugged in
baudRate = 9600
ser = serial.Serial(serialPort , baudRate, timeout=0, writeTimeout=0) #ensure non-blocking
c = ""

def main():
    
    c = ser.readline() # attempt to read a character from Serial
    c = str(c.decode('utf-8')) #changes reading to standard format
   
    return c
