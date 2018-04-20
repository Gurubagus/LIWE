#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 09:41:28 2017

@author: Zachary Taylor
"""

import VoltTemp
import Humidity
import Irradiance
import datetime
from time import sleep
import sys
sys.path.append('/home/pi/Desktop/O.T.E./GmailUpdater')
import upload_to_drive

precision = 2 #how many decimal places you want in the readings

#'time' and 'numberofreadings' mean it collects one reading every minute
#and averages 60 of them equalling one reading ever hour
timer = 60 #reading delay
numberofreadings = 60 #how many total readings to average

#All List for storage of chopped data to be written to data file
Cell1List = []
Cell2List = []
Cell3List = []
Cell4List = []
TempList  = []
HumList   = []
IrrList   = []
i = 0
Wattsum = 0

#    voltchop/humchop/irrchop methods take incoming data
#    from subscripts, timestamps it, and appends it to the 
#    appropriate Lists 

def voltchop():
    
    vt = VoltTemp.main()
    if len(vt) > 1:
        try:
            f = open('/home/pi/Desktop/O.T.E./GUI/Serread/Raw Data/VoltTempRAW', 'a+')
            time = '{:%y-%d-%m %H:%M:%S}'.format(datetime.datetime.now())  
            data = str(time+', '+vt)
            f.write(data+'\n')
            x, y, w, z, t= vt.split(',')
            Cell1List.append(float(x))
            Cell2List.append(float(y))
            Cell3List.append(float(w))
            Cell4List.append(float(z))
            TempList.append(float(t))
        except:
            voltchop()
                    
def humchop():

    hum = Humidity.main() 

    if len(hum) > 1:
        try:
            f = open('/home/pi/Desktop/O.T.E./GUI/Serread/Raw Data/HumidityRAW', 'a+')
            time = '{:%y-%d-%m %H:%M:%S}'.format(datetime.datetime.now())  
            data = str(time+', '+hum)
            f.write(data+'\n')
            x = hum[:-8]
            HumList.append(float(x))
        except:
            humchop()
        
def irrchop():
    
    irr = Irradiance.main()
    
    if len(irr)>1:
         try:
            f = open('/home/pi/Desktop/O.T.E./GUI/Serread/Raw Data/IrradianceRAW', 'a+')
            time = '{:%y-%d-%m %H:%M:%S}'.format(datetime.datetime.now())  
            data = str(time+', '+irr)
            f.write(data+'\n')
            irrchopped = irr[:-10]
            IrrList.append(float(irrchopped))       
         except:
            irrchop()
            

                
def main():
    #importing all necessary global variables
    global Cell1List
    global Cell2List
    global Cell3List
    global Cell4List
    global TempList
    global HumList
    global IrrList
    global i
    global Wattsum
    global numberofreadings
    
    #running the 3 data preparing methods
    voltchop()
    humchop()
    irrchop()
    
    
    # if loop counts to "i" then runs 
    if i >= numberofreadings:
   
        #creates averages of all readings for designed number of reads
        cell1ave = sum(Cell1List)/len(Cell1List)
        cell1ave = round(cell1ave,precision)
        cell2ave = sum(Cell2List)/len(Cell2List)
        cell2ave = round(cell2ave,precision)
        cell3ave = sum(Cell3List)/len(Cell3List)
        cell3ave = round(cell3ave,precision)
        cell4ave = sum(Cell4List)/len(Cell4List)
        cell4ave = round(cell4ave,precision)
        tempave = sum(TempList)/len(TempList)
        tempave = round(tempave,precision)
        humave = sum(HumList)/len(HumList)
        humave = round(humave,precision)
        irrave = sum(IrrList)/len(IrrList)
        irrave = round(irrave,precision)
        Wattsum+=irrave
        Wattsum = round(Wattsum,precision)
        
        #timestamp
        time = '{:%y-%d-%m %H:%M:%S}'.format(datetime.datetime.now())
        
        #Prepares then writes data to file
        c = str([cell1ave,cell2ave,cell3ave,cell4ave,tempave,humave,irrave,Wattsum])
        c = c[1:-1]
        f = open("/home/pi/Desktop/O.T.E./Data/Data.txt", 'a+')
        f.write(time+','+c+"\n")
        
        #resets all lists to zero
        Cell1List = []
        Cell2List = []
        Cell3List = []
        Cell4List = []
        TempList  = []
        HumList   = []
        IrrList   = []
        i = 0
        
        #script for uploading data file to gdrive
        upload_to_drive.main()
        
    else:
        i+=1

if __name__=="__main__":   
    while True:
        main()
        sleep(timer)
