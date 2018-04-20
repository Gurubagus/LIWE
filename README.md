# LIWE
echo "# LIWE" >> README.md git init git add README.md git commit -m "first commit" git remote add origin https://github.com/Gurubagus/LIWE.git git push -u origin master

"""
This is a G.U.I. (Graphical User Interface) created for the purpose of visualizing and managing the data being collected and broadcast by a Linux and Microcontroller based system for the environmental stress testing of OPV (Organic Photovoltaic) cells, or more simply organic solar panels. 
This automatically syncs with the data broadcast to a private Google Drive account every 5 seconds, organizes and then visualizes it in 4 separate graphs.
LODGE allows the user to change X lim and Y lim variables on all graphs and provides a function to export the data in a variety of ways to better suit the users needs.

The LODGE folder contains everything needed to install the system on the users computer
EXCEPT the client json and credential files, these have been ommitted for security reasons. Please contact
author to submit a request for access.

The SERIAL folder contains the code necessary for the collecting, managing, and uploading of the data to the Google drive 

The MICROCONTROLLER folder contains the Arduino code for the sensors gathering the data
"""
