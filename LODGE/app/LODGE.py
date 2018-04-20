#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 31 09:41:28 2017
Version published on Fri April 20th 2018

L.O.D.G.E
Liwe Opv Data G.u.i. Environment
(forgive the name, i'm a fool for acronyms)

This is a GUI for the visualization and management of data incoming from a private Google Drive account.
The account collects and stores multiple sensor readings from an testing environment for 4 organic
photovoltaic (solar panel) cells.

The initial data is collect and broadcast from a linux system reading multiple Arduino microcontrollers, which 
takes readings every minute and averages 60 of them giving one reading every hour.

The GUI allows the user to adjust the visualizations of this incoming data and export all
or any section of it as per the users needs.

@author: Zachary Taylor (zachary.mark.taylor@gmail.com)

REFERENCE!: The Google Sync code (labelled accordingly) was written by dtsvetkov1 - contact danilatsvet@gmail.com
Code can be found at https://github.com/dtsvetkov1/Google-Drive-sync
Big thank you to danilatsvet!!
"""
#start download_from_drive (Google Sync)
import datetime
import io
    # import mimetypes
import os
import shutil
import time
import hashlib
import httplib2

    # from os import path
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaIoBaseDownload
#End download_from_drive (Google Sync)

#Start GUI Imports            
import sys
sys.path.append(r'C:\Users\Zac\Desktop\app')
import threading
import sched
s = sched.scheduler(time.time, time.sleep)
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import pyqtgraph as pg
from pyqtgraph import QtCore, QtGui
#End GUI Imports 

#time = '{:%y-%d-%m %H:%M:%S}'.format(datetime.datetime.now())
file = ''
filename = ''
fileloc = ''
zipped = []

#data list for each sensor input
Cell1List = []
Cell2List = []
Cell3List = []
Cell4List = []
TempList  = []
HumList   = []
IrrList   = []
DateList  = []
selected = []
selectedlabels = []

# default y lims for graph
d = float(0.0)
volt_y_lim1 = 0
volt_y_lim2 = 12
temp_y_lim1 = -10
temp_y_lim2 = 40
hum_y_lim1 = 0
hum_y_lim2 = 40
irr_y_lim1 = 0
irr_y_lim2 = 1000
plotlength_end = 1
plotlength_start = 1

# initial plot length and title
plotlength = 10
xname ='Last 10 Hours'

# global variable for the kWh counter
Watt_total = 0   
    
# Main Widget, graphing window embedded here
class Main(QMainWindow):
    
    def __init__(self, parent=None, *args, **kwargs):
        
        super().__init__(parent)
        self.setWindowTitle("L.O.D.G.E.")
        self.main_window = Window(parent=self)
        self.setCentralWidget(self.main_window)
        
    # Menus
        bar = self.menuBar() 
        file_menu = bar.addMenu('XLim')
        ylim_menu = bar.addMenu('YLim')
        export_menu = bar.addMenu('Export Data')
     
    #allows user to keyboard shortcut exit the program
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

    #Creates 10 Hour graphing option on menubar
        lastten = QAction('&10 Hours', self)
        lastten.setStatusTip('Plot only 10 previous hours')
        lastten.triggered.connect(Window.plotlengthten)
        file_menu.addAction(lastten)
        
    #Creates 24 Hour graphing option on menubar
        lasttwentyfour = QAction('&24 Hours', self)
        lasttwentyfour.setStatusTip('Plot only 24 previous hours')
        lasttwentyfour.triggered.connect(Window.plotlengthday)
        file_menu.addAction(lasttwentyfour)
      
    #Creates 7 Days graphing option on menubar
        lastweek = QAction('&7 Days', self)
        lastweek.setStatusTip('Plot only 7 previous days')
        lastweek.triggered.connect(Window.plotlengthweek)
        file_menu.addAction(lastweek)
        
    #Creates 1 Month graphing option on menubar
        lastmonth = QAction('&30 Days', self)
        lastmonth.setStatusTip('Plot only 30 previous days')
        lastmonth.triggered.connect(Window.plotlengthmonth)
        file_menu.addAction(lastmonth)
       
    #Creates All graphing option on menubar
        lastall = QAction('&All', self)
        lastall.setStatusTip('Plot all available data')
        lastall.triggered.connect(Window.plotlengthall)
        file_menu.addAction(lastall)
        
    #Changes ylim on voltage graph
        vylim = QAction('Voltage', self)
        vylim.setStatusTip('Change Voltage Y lim')
        vylim.triggered.connect(volt_y_lim)
        ylim_menu.addAction(vylim)
        
    #Changes ylim on voltage graph
        irrylim = QAction('Irradiance', self)
        irrylim.setStatusTip('Change Irradiance Y lim')
        irrylim.triggered.connect(irr_y_lim)
        ylim_menu.addAction(irrylim)
 
    #Changes ylim on humidity graph       
        humylim = QAction('Humidity', self)
        humylim.setStatusTip('Change Humidity Y lim')
        humylim.triggered.connect(hum_y_lim)
        ylim_menu.addAction(humylim)

    #Changes ylim on temperature graph        
        tempylim = QAction('Temperature', self)
        tempylim.setStatusTip('Change Humidity Y lim')
        tempylim.triggered.connect(temp_y_lim)
        ylim_menu.addAction(tempylim)

    #Changes ylim on all graphs back to default settings    
        defaultylim = QAction('Default (ALL)', self)
        defaultylim.setStatusTip('Change all Y LIM to default')
        defaultylim.triggered.connect(self.default_y_lim)
        ylim_menu.addAction(defaultylim)
     
    #Changes xlim on all graphs to custom setting
        customxlim = QAction('Custom', self)
        customxlim.setStatusTip('Choose custom plot length')
        customxlim.triggered.connect(custom_x_lim)
        file_menu.addAction(customxlim)
        
    #exports  data
        export_func = QAction('Custom Export', self)
        export_func.setStatusTip('Exports data in customized format')
        export_func.triggered.connect(Main.callcheckbox)
        export_menu.addAction(export_func)   
        
    #calls data export checkbox widget    
    def callcheckbox(self):
        global window
        
        window = custom_export()
        window.show()
        return window
    
    #Y Lim changing code     
    def default_y_lim(self):
        
        global volt_y_lim1
        global volt_y_lim2
        global temp_y_lim1
        global temp_y_lim2
        global hum_y_lim1
        global hum_y_lim2
        global irr_y_lim1
        global irr_y_lim2
        
        volt_y_lim1 = 0
        volt_y_lim2 = 12
        temp_y_lim1 = -10
        temp_y_lim2 = 40
        hum_y_lim1 = 0
        hum_y_lim2 = 40
        irr_y_lim1 = 0
        irr_y_lim2 = 1000
        
    def default_x_lim(self):
        
        global volt_y_lim1
        global volt_y_lim2
        global temp_y_lim1
        global temp_y_lim2
        global hum_y_lim1
        global hum_y_lim2
        global irr_y_lim1
        global irr_y_lim2
        
        volt_y_lim1 = 0
        volt_y_lim2 = 12
        temp_y_lim1 = -10
        temp_y_lim2 = 40
        hum_y_lim1 = 0
        hum_y_lim2 = 40
        irr_y_lim1 = 0
        irr_y_lim2 = 1000

# The objects for the popup messages for choosing new Y Lims.
# Forgive my sloppy code, i know you should just create the one class and create seperate objects
# but i didn't have time to figure out how to edit the output variabel at the end of the IF statement 
# for each new object, so.....here we are.
        
class volt_y_lim (QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Input'
        self.left = 10
        self.top = 10
        self.width = 1640
        self.height = 480
        self.initUI()
     
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
     
        self.getInteger()
     
     
    def getInteger(self):
        
        global volt_y_lim2
        global volt_y_lim1
        
        j, okPressed = QInputDialog.getInt(self, "Voltage","Y LIM = MIN:", 0, -100, 100, 1)
        i, okPressed = QInputDialog.getInt(self, "Voltage","Y LIM = MAX:", 10, 0, 100, 1)
    
        if okPressed:
            volt_y_lim2 = i
            volt_y_lim1 = j

#Calls pop-up window to choose new Y LIM           
class irr_y_lim (QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Input'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
     
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
     
        self.getInteger()
     
     
    def getInteger(self):
        
        global irr_y_lim1
        global irr_y_lim2
        
        j, okPressed = QInputDialog.getInt(self, "Irradiance","Y LIM = MIN:", 0, -100, 100, 1)
        i, okPressed = QInputDialog.getInt(self, "Irradiance","Y LIM = MAX:", 10, 0, 100, 1)
    
        if okPressed:
            irr_y_lim2 = i
            irr_y_lim1 = j

#Calls pop-up window to choose new Y LIM               
class hum_y_lim (QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Input'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
        self.initUI()
     
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
     
        self.getInteger()
     
     
    def getInteger(self):
        
        global hum_y_lim2
        global hum_y_lim1
        
        j, okPressed = QInputDialog.getInt(self, "Humidity","Y LIM = MIN:", 0, -100, 100, 1)
        i, okPressed = QInputDialog.getInt(self, "Humidity","Y LIM = MAX:", 10, 0, 100, 1)
    
        if okPressed:
            hum_y_lim2 = i
            hum_y_lim1 = j

#Calls pop-up window to choose new Y LIM                
class temp_y_lim (QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Input'
        self.left = 10
        self.top = 10
        self.width = 1000
        self.height = 480
        self.initUI()
     
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
     
        self.getInteger()
     
     
    def getInteger(self):
        
        global temp_y_lim2
        global temp_y_lim1
        
        j, okPressed = QInputDialog.getInt(self, "Temperature","Y LIM = MIN", 0, -100, 100, 1)
        i, okPressed = QInputDialog.getInt(self, "Temperature","Y LIM = MAX:", 10, 0, 100, 1)
    
        if okPressed:
            temp_y_lim2 = i
            temp_y_lim1 = j

#Calls pop-up window to choose new Y LIM               
class custom_x_lim (QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Input'
        self.left = 10
        self.top = 10
        self.width = 1000
        self.height = 480
        self.initUI()
     
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
     
        self.getInteger()
     
     
    def getInteger(self):
        
        global plotlength
        global xname
     
        
        j, okPressed = QInputDialog.getInt(self, "Choose # of data points to graph backwards from most current reading","Value:", 0, -10000, 100000, 1)
    
        if okPressed:
            plotlength = j
            xname = str("Last %s Hours" % j)
 
#Calls pop-up window to choose length of data for exporting           
class data_length (QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Input'
        self.left = 400
        self.top = 400
        self.width = 600
        self.height = 100
        self.initUI()
     
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
     
        self.getlength()
     
     
    def getlength(self):

        global plotlength_start
        global plotlength_end
        global file
        
        i, okPressed = QInputDialog.getInt(self, "Data = Start ","Data points backward from newest: (MAX:"+str(len(Cell1List))+")", 0, -10000, 100000, 1)
        j, okPressed = QInputDialog.getInt(self, "Data = End","How many total data points: (default = all)", i, -10000, 100000, 1)
    
        if okPressed:
            plotlength_start = i
            plotlength_end   = j
        
    def centerOnScreen (self):

        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2))
            
            
#Calls pop-up window to choose save directory for exported data    
class choosedir(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Input'
        self.left = 10
        self.top = 10
        self.width = 1000
        self.height = 480
        self.initUI()
     
    def initUI(self):
        self.setWindowTitle(self.title)
        
        self.setGeometry(self.left, self.top, self.width, self.height)
     
        self.chosen()
     
     
    def chosen(self):
        
        global plotlength_start
        global plotlength_end
        global file
     
        
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory")) 
        
        
#Checkbox Widget (custom export menu option) 
class custom_export(QWidget):
    def __init__(self):
        
        super().__init__()
        self.title = 'Choose what data you would like to include:'
        self.left = 250
        self.top = 100
        self.width = 480
        self.height = 100

#All Checkbox options with initial setting to all checked
        layout = QGridLayout()
        self.setLayout(layout)

        self.checkbox1 = QCheckBox("Cell 1")
        self.checkbox1.setChecked(True)
        layout.addWidget(self.checkbox1, 0, 0)

        self.checkbox2 = QCheckBox("Cell 2")
        layout.addWidget(self.checkbox2, 1, 0)
        self.checkbox2.setChecked(True)

        self.checkbox3 = QCheckBox("Cell 3")
        layout.addWidget(self.checkbox3, 2, 0)
        self.checkbox3.setChecked(True)
        
        self.checkbox4 = QCheckBox("Cell 4")
        layout.addWidget(self.checkbox4, 3, 0)
        self.checkbox4.setChecked(True)

        self.checkbox5 = QCheckBox("Temperature")
        layout.addWidget(self.checkbox5, 0, 1)
        self.checkbox5.setChecked(True)

        self.checkbox6 = QCheckBox("Irradiance")
        layout.addWidget(self.checkbox6, 1, 1)
        self.checkbox6.setChecked(True)

        self.checkbox7 = QCheckBox("Humidity")
        layout.addWidget(self.checkbox7, 2, 1)
        self.checkbox7.setChecked(True)
        
        self.dirbutton = QPushButton("Choose: Save Location", self)
        self.dirbutton.clicked.connect(choosedir)
        layout.addWidget(self.dirbutton)
        
        self.nextbutton = QPushButton("Next", self)
        self.nextbutton.clicked.connect(self.Nextplease)
        layout.addWidget(self.nextbutton)
        
        self.initUI()
     
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(0, 0, self.width, self.height)
        self.centerOnScreen()
        self.isActiveWindow()

    def centerOnScreen (self):

        resolution = QtGui.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                  (resolution.height() / 2) - (self.frameSize().height() / 2)) 
   
    def Nextplease(self):
        
        global plotlength_start
        global plotlength_end
        
        custom_export.hide(self)
        self.getName()
        data_length()
        self.checkbox_toggled()
        self.savefile()
        
    def getName(self):
        
        global filename
        
        j, okPressed = QInputDialog.getText(self, "Filename","Enter your Filename:")
    
        if okPressed:
            
            filename = j
        
    def savefile(self):
        
        global file
        global filename
        global fileloc
        global selected
        global plotlength_start
        global plotlength_end
        
        if len(file) > 1:
            
            fileloc = str(file+"/"+filename+".txt")
            f = open(fileloc,'w+')
            zipped = zip(*selected)
            zipped = list(zipped)
            zipped = zipped[len(zipped)-plotlength_start:len(zipped)-plotlength_start+plotlength_end]
            f.write( ", ".join( str(e) for e in selectedlabels ) )
            f.write('\n')
            f.write("\n".join(map(str, zipped)))
            f.close()
            self.changedata()

        else:
            file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
            self.savefile()
            
 #removeds '(' and ')' from data file after creation by savefile method           
    def changedata(self):
        global fileloc
    
        original = open(fileloc, 'r').read()
        removed = original.replace("(","")
        removed = removed.replace(")","")
        open(fileloc, 'w+').write(removed)
        
 #checks which data user has selected and creates list for savefile method 'selected'
    def checkbox_toggled(self):
        global selected
        global selectedlabels
        global zipped
        global plotlength_start
        global plotlength_end
        
        selected = []
        selectedlabels = []
        selected.append(DateList)
        selectedlabels.append(' Date/Time')

        if self.checkbox1.isChecked():
            selected.append(Cell1List)
            selectedlabels.append('Cell 1')
            

        if self.checkbox2.isChecked():
            selected.append(Cell2List)
            selectedlabels.append('Cell 2')

        if self.checkbox3.isChecked():
            selected.append(Cell3List)
            selectedlabels.append('Cell 3')
            
        if self.checkbox4.isChecked():
            selected.append(Cell4List)
            selectedlabels.append('Cell 4')
            
        if self.checkbox5.isChecked():
            selected.append(TempList)
            selectedlabels.append('Temp')
            
        if self.checkbox6.isChecked():
            selected.append(IrrList)
            selectedlabels.append('W/m^2')
            
        if self.checkbox7.isChecked():
            selected.append(HumList)
            selectedlabels.append('Hum')
        
        selectedlabels.append('')      
        zipped = zip(selected)
   
#Graphing Widget set as central widget in Main     
class Window(QWidget):

    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        self.figure = plt.figure()
        
        #Watt counter
        self.lcd = QtGui.QLCDNumber(self)
        self.lcd.display(Watt_total)

        #general canvas creation
        self.canvas = FigureCanvas(self.figure)

#        self.toolbar = NavigationToolbar(self.canvas, self)
        self.label = QtGui.QLabel(self)
        self.label.setText("Total kWh Received")

        layout = QtGui.QGridLayout()
        self.setLayout(layout)

#        layout.addWidget(self.toolbar,0,0,1,1)
        layout.addWidget(self.canvas,1,0,4,4)
        layout.addWidget(self.lcd,0,3,1,1)
        layout.addWidget(self.label,0,2,1,1)

        self.plot()
        
        #all "plot..." methods are creating different plotting lengths
    def getInteger(self):
        i, okPressed = QInputDialog.getInt(self.Window, "Get integer","Percentage:", 28, 0, 100, 1)
        if okPressed:
            print(i)

#X Lim changing methods         
    def plotlengthten(self):
    
        global plotlength
        global xname
        plotlength = 10
        xname = 'Last 10 Hours'
        
    def plotlengthday(self):
        
        global plotlength
        global xname
        plotlength = 24
        xname = 'Last 24 Hours'
        
        
    def plotlengthweek(self):
        
        global plotlength
        global xname
        plotlength = 168
        xname = 'Last 7 Days'
        
        
    def plotlengthmonth(self):
        
        global plotlength
        global xname
        plotlength = 720
        xname = 'Last 30 Days'
        
        
    def plotlengthall(self):
        
        global plotlength
        global xname
        plotlength = len(Cell1List)
        xname = 'All Readings'
              
  #plotting method    
    def plot(self):

        global volt_y_lim
        global temp_y_lim
        global hum_y_lim
        global irr_y_lim
 
        #time between new plotting run, should never be lower than 5
        #or it won't have time to finish the data/plot before the next 
        #(depending on # of data points)
        
        t = threading.Timer(5.0,self.plot)
        t.setDaemon(True)
        t.start()

        # makes sure data set is reset then gathers new data
        self.clean()
        self.getdata()
        
        #divides plots into 4 seperate graphs
        ax = plt.subplot2grid((3,3),(0,0), colspan=3,rowspan=2)
        ax1 = plt.subplot2grid((3,3),(2,0))
        ax2 = plt.subplot2grid((3,3),(2,1))
        ax3 = plt.subplot2grid((3,3),(2,2))        
        
        #removes previous plot data
        ax.clear()
        ax1.clear()
        ax2.clear()
        ax3.clear()
        
        #plots new data set
        ax.plot(Cell1List[-int(plotlength):]) # to change looke -> '*-'
        ax.plot(Cell2List[-int(plotlength):])
        ax.plot(Cell3List[-int(plotlength):])
        ax.plot(Cell4List[-int(plotlength):])
        ax1.plot(TempList[-int(plotlength):])
        ax2.plot(HumList[-int(plotlength):])
        ax3.plot(IrrList[-int(plotlength):])
        
        #plot titles
        ax.legend("1234")
        ax.set_title('Cell Voltage')
        ax1.set_title('°C')
        ax2.set_title("Humidity")
        ax3.set_title("W/m^2")
        
        plt.tight_layout()
        
        #sets plot ranges for better data visualization
        ax.set_xlabel(xname)
        ax.set_xticklabels([])
        ax.set_ylim([volt_y_lim1,volt_y_lim2])
        ax1.set_ylim([temp_y_lim1,temp_y_lim2])
        ax2.set_ylim([hum_y_lim1,hum_y_lim2])
        ax3.set_ylim([irr_y_lim1,irr_y_lim2])
        
        
        self.canvas.draw()
        self.lcd.display(Watt_total/1000)
 
    # START OF Google Sync CODE by dtsvetkov1 - contact danilatsvet@gmail.com
    # code can be found at https://github.com/dtsvetkov1/Google-Drive-sync
    # Big thank you to danilatsvet!!
    
    def download_from_drive():
            # import initial_upload
        
        # If modifying these scopes, delete your previously saved credentials
        # at ~/.credentials/drive-python-quickstart.json
        SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly',
                  'https://www.googleapis.com/auth/drive.file',
                  'https://www.googleapis.com/auth/drive']
        CLIENT_SECRET_FILE = 'client_secret.json'
        APPLICATION_NAME = 'Drive Sync'
        
        # Declare full path to folder and folder name
        FULL_PATH = r'..\app\Data'
        DIR_NAME = 'Data'
        # Or simply
        #DIR_NAME = FULL_PATH.split('/')[-1]
        
        # Sample (reference) map of Google Docs MIME types to possible exports
        # (for more information check about().get() method with exportFormats field)
        GOOGLE_MIME_TYPES = {
            'application/vnd.google-apps.document':
            ['application/vnd.openxmlformats-officedocument.wordprocessingml.document',
             '.docx'],
            # 'application/vnd.google-apps.document':
            # 'application/vnd.oasis.opendocument.text',
            'application/vnd.google-apps.spreadsheet':
            ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
             '.xlsx'],
            # 'application/vnd.oasis.opendocument.spreadsheet',
            'application/vnd.google-apps.presentation':
            ['application/vnd.openxmlformats-officedocument.presentationml.presentation',
             '.pptx']
            # 'application/vnd.oasis.opendocument.presentation'
        }
        # 'application/vnd.google-apps.drawing': 'application/x-msmetafile'
        # 'application/vnd.google-apps.folder': '',
        # 'application/vnd.google-apps.form': 'application/pdf',
        # 'application/vnd.google-apps.fusiontable': '',
        # 'application/vnd.google-apps.map': 'application/pdf',
        # 'application/vnd.google-apps.photo': 'image/jpeg',
        # 'application/vnd.google-apps.file': '',
        # 'application/vnd.google-apps.sites': '',
        # 'application/vnd.google-apps.unknown': '',
        # 'application/vnd.google-apps.video': '',
        # 'application/vnd.google-apps.audio': '',
        # 'application/vnd.google-apps.drive-sdk': ''
        # 'application/octet-stream': 'text/plain'
        
        def folder_upload(service):
            '''Uploads folder and all it's content (if it doesnt exists)
            in root folder.
        
            Args:
                items: List of folders in root path on Google Drive.
                service: Google Drive service instance.
        
            Returns:
                Dictionary, where keys are folder's names
                and values are id's of these folders.
            '''
        
            parents_id = {}
        
            for root, _, files in os.walk(FULL_PATH, topdown=True):
                last_dir = root.split('/')[-1]
                pre_last_dir = root.split('/')[-2]
                if pre_last_dir not in parents_id.keys():
                    pre_last_dir = []
                else:
                    pre_last_dir = parents_id[pre_last_dir]
        
                folder_metadata = {'name': last_dir,
                                   'parents': [pre_last_dir],
                                   'mimeType': 'application/vnd.google-apps.folder'}
                create_folder = service.files().create(body=folder_metadata,
                                                       fields='id').execute()
                folder_id = create_folder.get('id', [])
        
                for name in files:
                    file_metadata = {'name': name, 'parents': [folder_id]}
                    media = MediaFileUpload(
                        os.path.join(root, name),
                        mimetype=mimetypes.MimeTypes().guess_type(name)[0])
                    service.files().create(body=file_metadata,
                                           media_body=media,
                                           fields='id').execute()
        
                parents_id[last_dir] = folder_id
        
            return parents_id
        
        
        def check_upload(service):
            """Checks if folder is already uploaded,
            and if it's not, uploads it.
        
            Args:
                service: Google Drive service instance.
        
            Returns:
                ID of uploaded folder, full path to this folder on computer.
        
            """
        
            results = service.files().list(
                pageSize=100,
                q="'root' in parents and trashed != True and \
                mimeType='application/vnd.google-apps.folder'").execute()
        
            items = results.get('files', [])
        
            # Check if folder exists, and then create it or get this folder's id.
            if DIR_NAME in [item['name'] for item in items]:
                folder_id = [item['id']for item in items
                             if item['name'] == DIR_NAME][0]
            else:
                parents_id = folder_upload(service)
                folder_id = parents_id[DIR_NAME]
        
            return folder_id, FULL_PATH
        
        
        def get_credentials():
            """Gets valid user credentials from storage.
        
            If nothing has been stored, or if the stored credentials are invalid,
            the OAuth2 flow is completed to obtain the new credentials.
        
            Returns:
                Credentials, the obtained credential.
            """
            home_dir = os.path.expanduser('~')
            credential_dir = os.path.join(home_dir, '.credentials')
            if not os.path.exists(credential_dir):
                os.makedirs(credential_dir)
            credential_path = os.path.join(credential_dir,
                                           'drive-python-sync.json')
        
            store = Storage(credential_path)
            credentials = store.get()
            if not credentials or credentials.invalid:
                flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
                flow.user_agent = APPLICATION_NAME
                # if flags:
                credentials = tools.run_flow(flow, store, flags=None)
                # else:  # Needed only for compatibility with Python 2.6
                # credentials = tools.run(flow, store)
                print('Storing credentials to ', credential_path)
            return credentials
        
        
        def get_tree(folder_name, tree_list, root, parents_id, service):
            """Gets folder tree relative paths.
        
            Recursively gets through subfolders, remembers their names ad ID's.
        
            Args:
                folder_name: Name of folder, initially
                name of parent folder string.
                folder_id: ID of folder, initially ID of parent folder.
                tree_list: List of relative folder paths, initially
                empy list.
                root: Current relative folder path, initially empty string.
                parents_id: Dictionary with pairs of {key:value} like
                {folder's name: folder's Drive ID}, initially empty dict.
                service: Google Drive service instance.
        
            Returns:
                List of folder tree relative folder paths.
        
            """
            folder_id = parents_id[folder_name]
        
            results = service.files().list(
                pageSize=100,
                q=("%r in parents and \
                mimeType = 'application/vnd.google-apps.folder'and \
                trashed != True" % folder_id)).execute()
        
            items = results.get('files', [])
            root += folder_name + os.path.sep
        
            for item in items:
                parents_id[item['name']] = item['id']
                tree_list.append(root + item['name'])
                folder_id = [i['id'] for i in items
                             if i['name'] == item['name']][0]
                folder_name = item['name']
                get_tree(folder_name, tree_list,
                         root, parents_id, service)
        
        
        def download_file_from_gdrive(file_path, drive_file, service):
            """Downloads file from Google Drive.
        
            If file is Google Doc's type, then it will be downloaded
            with the corresponding non-Google mimetype.
        
            Args:
                path: Directory string, where file will be saved.
                file: File information object (dictionary), including it's name, ID
                and mimeType.
                service: Google Drive service instance.
            """
            file_id = drive_file['id']
            file_name = drive_file['name']
            if drive_file['mimeType'] in GOOGLE_MIME_TYPES.keys():
                if file_name.endswith(GOOGLE_MIME_TYPES[drive_file['mimeType']][1]):
                    file_name = drive_file['name']
                else:
                    file_name = '{}{}'.format(
                        drive_file['name'],
                        GOOGLE_MIME_TYPES[drive_file['mimeType']][1])
                    service.files().update(fileId=file_id,
                                           body={'name': file_name}).execute()
        
        
                request = service.files().export(
                    fileId=file_id,
                    mimeType=(GOOGLE_MIME_TYPES[drive_file['mimeType']])[0]).execute()
                with io.FileIO(os.path.join(file_path, file_name), 'wb') as file_write:
                    file_write.write(request)
        
            else:
                request = service.files().get_media(fileId=file_id)
                file_io = io.FileIO(os.path.join(file_path, drive_file['name']), 'wb')
                downloader = MediaIoBaseDownload(file_io, request)
                done = False
                while done is False:
                    _, done = downloader.next_chunk()
        
        
        def by_lines(input_str):
            """Helps Sort items by the number of slashes in it.
        
            Returns:
                Number of slashes in string.
            """
            return input_str.count(os.path.sep)
        
        
        def main():
            """Shows basic usage of the Google Drive API.
        
            Creates a Google Drive API service object and outputs the names and IDs
            for up to 10 files.
            """
            # credentials = get_credentials()
            http = get_credentials().authorize(httplib2.Http())
            service = discovery.build('drive', 'v3', http=http)
        
            # Get id of Google Drive folder and it's path (from other script)
            # folder_id, full_path = initial_upload.check_upload(service)
            folder_id, full_path = check_upload(service)
            folder_name = full_path.split(os.path.sep)[-1]
            tree_list, root, parents_id = [], '', {}
        
            # About_drive = service.about().get(
            # fields='importFormats, exportFormats').execute()
            # print(About_drive)
            parents_id[folder_name] = folder_id
            get_tree(folder_name, tree_list, root, parents_id, service)
            os_tree_list = []
            root_len = len(full_path.split(os.path.sep)[0:-2])
        
            # Get list of folders three paths on computer
            for root, dirs, files in os.walk(full_path, topdown=True):
                for name in dirs:
                    var_path = (os.path.sep).join(
                        root.split(os.path.sep)[root_len + 1:])
                    os_tree_list.append(os.path.join(var_path, name))
        
            # old folders on computer
            download_folders = list(set(tree_list).difference(set(os_tree_list)))
            # new folders on computer, which you dont have(i suppose heh)
            remove_folders = list(set(os_tree_list).difference(set(tree_list)))
            # foldes that match
            exact_folders = list(set(os_tree_list).intersection(set(tree_list)))
        
            exact_folders.append(folder_name)
        
            var = (os.path.sep).join(full_path.split(os.path.sep)[0:-1]) + os.path.sep
        
            # Download folders from Drive
            download_folders = sorted(download_folders, key=by_lines)
        
            for folder_dir in download_folders:
                variable = var + folder_dir
                last_dir = folder_dir.split(os.path.sep)[-1]
        
                folder_id = parents_id[last_dir]
                results = service.files().list(
                    pageSize=20, q=('%r in parents' % folder_id)).execute()
        
                items = results.get('files', [])
                os.makedirs(variable)
                files = [f for f in items
                         if f['mimeType'] != 'application/vnd.google-apps.folder']
        
                for drive_file in files:
                    # file_id = f['id']
                    download_file_from_gdrive(variable, drive_file, service)
        
            # Check and refresh files in existing folders
            for folder_dir in exact_folders:
                # var = '/'.join(full_path.split('/')[0:-1]) + '/'
                variable = var + folder_dir
                last_dir = folder_dir.split(os.path.sep)[-1]
                os_files = [f for f in os.listdir(variable)
                            if os.path.isfile(os.path.join(variable, f))]
                folder_id = parents_id[last_dir]
        
                results = service.files().list(
                    pageSize=1000,
                    q=('%r in parents and \
                    mimeType!="application/vnd.google-apps.folder"' % folder_id),
                    fields="files(id, name, mimeType, \
                        modifiedTime, md5Checksum)").execute()
        
                items = results.get('files', [])
        
                refresh_files = [f for f in items if f['name'] in os_files]
                upload_files = [f for f in items if f['name'] not in os_files]
                remove_files = [f for f in os_files
                                if f not in [j['name']for j in items]]
        
                for drive_file in refresh_files:
                    file_dir = os.path.join(variable, drive_file['name'])
                    file_time = os.path.getmtime(file_dir)
                    # mtime = drive_file['modifiedTime']
                    mtime = datetime.datetime.strptime(drive_file['modifiedTime'][:-2],
                                                       "%Y-%m-%dT%H:%M:%S.%f")
                    drive_time = time.mktime(mtime.timetuple())
        
                    file_dir = os.path.join(variable, drive_file['name'])
                    os_file_md5 = hashlib.md5(open(file_dir, 'rb').read()).hexdigest()
                    if 'md5Checksum' in drive_file.keys():
                        # print(1, file['md5Checksum'])
                        drive_md5 = drive_file['md5Checksum']
                        # print(2, os_file_md5)
                    else:
                        drive_md5 = None
        
                    if (file_time < drive_time) or (drive_md5 != os_file_md5):
                        os.remove(os.path.join(variable, drive_file['name']))
                        download_file_from_gdrive(variable, drive_file, service)
        
                for os_file in remove_files:
                    os.remove(os.path.join(variable, os_file))
        
                for drive_file in upload_files:
                    download_file_from_gdrive(variable, drive_file, service)
        
            # Delete old and unwanted folders from computer
            remove_folders = sorted(remove_folders, key=by_lines, reverse=True)
        
            for folder_dir in remove_folders:
                # var = '/'.join(full_path.split('/')[0:-1]) + '/'
                variable = var + folder_dir
                last_dir = folder_dir.split(os.path.sep)[-1]
                shutil.rmtree(variable)     
            #method for gather data from data file
        main()
        
    # END OF Google Sync CODE by dtsvetkov1 - contact danilatsvet@gmail.com
    # code can be found at https://github.com/dtsvetkov1/Google-Drive-sync
    # Big thank you to danilatsvet!!      
    
 #Method for gathering and filtering data from Google Sync file
 #Places data into appropriate lists to be read by plot method   
    def getdata(self):
        global Watt_total
        Window.download_from_drive()
        pullData = open(r"..\app\Data\data.txt","r", encoding='utf-8').read()
        dataList = pullData.split('\n')
        
        for eachLine in dataList:
            if len(eachLine) > 1:
            
                data = eachLine.split(',')
                
                a, b = float(data[1]), float(data[2])
                c, d = float(data[3]), float(data[4])
                e, f = float(data[5]), float(data[6])
                g, h = float(data[7]), float(data[8])
    
                
                DateList.append(data[0])
                Cell1List.append(float(a))
                Cell2List.append(float(b))
                Cell3List.append(float(c))
                Cell4List.append(float(d))
                TempList.append(float(e))
                HumList.append(float(f))
                IrrList.append(float(g))  
                Watt_total = h
                
  #resets data lists to prevent multiple graph overlays              
    def clean(self):
    
        global Cell1List
        global Cell2List
        global Cell3List
        global Cell4List
        global TempList
        global HumList
        global IrrList
        global DateList
        
        Cell1List = []
        Cell2List = []
        Cell3List = []
        Cell4List = []
        TempList  = []
        HumList   = []
        IrrList   = []
        DateList  = [] 
        
if __name__ == '__main__':
    def run_app():
        
        app = QApplication(sys.argv)
        main = Main()
        main.show()
        app.exec_()
    
    run_app()
    input()
