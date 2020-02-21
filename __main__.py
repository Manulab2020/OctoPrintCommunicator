'''
In this module, a list of IP addresses and API keys for Octoprint-connected 3D printers are read and
used to send and receive data between them and other devices.
'''


from pathlib import Path
import PiCommands as pi
import pandas as pd
import sys
import csv

path_ListOfPrinters = Path("ListOfPrinters.csv")


def importPrinterList(pathName):
    '''
    Import Octopi / printer IP addresses and API keys from the local ListOfPrinters.csv
    '''
    global ipList
    global apiList
    try:
        df = pd.read_csv(pathName, sep=";", header=0) # Read first row as column names (ipAddress & apiKey)
        ipList = list(df.ipAddress)
        apiList = list(df.apiKey)
    except:
        pi.writeErrorLog("ListOfPrinters.csv is missing or of invalid format")

# Test code:
importPrinterList(path_ListOfPrinters)
#PiCommands.getPrinterStatus(ipList[0], apiList[0])
pi.login(ipList[0])
pi.connectToPrinter(ipList[0], apiList[0])
if pi.isPrinterConnected(ipList[0],apiList[0]):
    print(ipList[0] + " is connected")
else:
    print(ipList[0] + " is not connected")
