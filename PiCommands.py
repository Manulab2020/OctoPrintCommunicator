'''
This class contains the necessary commands to extract information from Raspberry Pis running Octoprint,
as well as commands to start print jobs. Communication between the script and Pis are done through JSON objects.

Information about each printer's status is written to a csv that can be read by other programs.
'''
import sys
import time
import datetime
from pathlib import Path
import json
import requests
import csv
import pandas as pd


def writeErrorLog(errorMessage):
    '''
    Writes a timestamped error message to ErrorLog.txt.
    Argument: errorMessage to be written. If the message is "CLEARLOG", the log file will be cleared.
    '''
    path_ErrorLog = Path("ErrorLog.txt")
    currentTime = time.time()
    currentDatetime = datetime.datetime.fromtimestamp(currentTime).strftime(
        '%Y' + '.' + '%m' + '.' + '%d ' + '%H:%M:%S - ')
    if not path_ErrorLog.exists():
        open("ErrorLog.txt", 'a').close()
        print("Error log created")

    if errorMessage == "CLEARLOG":
        open(path_ErrorLog, 'w').close()
        print("Error log cleared")
    else:
        errorLog = open(path_ErrorLog, 'a')
        errorLog.write(currentDatetime + errorMessage + '\n')
        print("New error: " + errorMessage)

def login(ipAddress):
    '''
    Log into octoprint on the specified IP address
    Username: manulab, Password: propanautomat
    '''
    url = "http://" + ipAddress + "/api/login"
    payload = {"user": "manulab", "pass": "propanautomat"}
    r = requests.post(url, data=payload)
    print(r)

def isPrinterConnected(ipAddress, apiKey):
    '''
    Check if the specified Pi is connected to the Printer.
    Arguments: Octopi IP address, Octopi API Key
    Returns: True if connected, False if not
    '''
    url = "http://" + ipAddress + "/api/connection"
    headers = {"X-Api-Key": apiKey}
    try:
        r = requests.get(url, headers=headers)
        rJson = json.loads(r.text)

        if (rJson["current"]["state"]) == "Operational": # Can be Closed or Operational
            return True
        else:
            return False
    except Exception:
        e = sys.exc_info()[0]
        writeErrorLog(e)
        pass


def getPrinterStatus(ipAddress, apiKey):
    '''
    Returns a string (CSV row) containing data for the specified printer
    '''
    url = "http://" + ipAddress + "/api/printer"
    headers = {"X-Api-Key": apiKey}
    print("Accessing " + url + " using API Key " + apiKey)
    r = requests.get(url, headers=headers)
    rJson = json.loads(r.text)
    if r.text == "Printer is not operational":
        writeErrorLog(print("Printer " + ipAddress + " is not operational"))




def connectToPrinter(ipAddress, apiKey):
    '''
    Tell the specified Octoprint instance to connect to the printer
    Arguments: Octopi IP address, Octopi API key
    '''
    url = "http://" + ipAddress + "/api/connection"
    headers = {"Content-Type": "application/json", "X-Api-Key": apiKey}
    payload = {"command": "connect"}

    r = requests.post(url, headers=headers, data=payload)
    print(r)

'''
Tell the specified printer to start printing the specified G-code
G-code should be uploaded to the Manulab-folder in octoprint in advance.
Arguments: Octopi IP address, Octopi API key, path to g-code file on the pi
'''
