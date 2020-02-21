import sys
from pathlib import Path
import logging
import json
import requests
import pandas as pd

'''
This class contains the necessary commands to extract information from Raspberry Pis running Octoprint,
as well as commands to start print jobs. Communication between the script and Pis are done through parsing of
JSON objects. Methods primarily return JSON-formatted strings.
'''

class OctoPrintClient:

    def __init__(self, ipAddress, apiKey):
        '''
        Initialize a "client". Each client handles one connection to one printer.
        A logger object is initialized to write error logs as well.
        '''
        self.ipAddress = ipAddress
        self.apiKey = apiKey

        logging.basicConfig(filename='Log.txt', level=logging.DEBUG,
                            format='%(asctime)s %(levelname)s %(name)s %(message)s')
        self.logger = logging.getLogger(__name__)


    def login(self, username, password):
        '''
        Log into octoprint on the specified IP address
        '''
        url = "http://" + self.ipAddress + "/api/login"
        payload = {"user": username, "pass": password}
        r = requests.post(url, data=payload)
        return r.text


    def connectToPrinter(self):
        '''
        Connect to the 3D printer over USB. Default values are used.
        Arguments: Octopi IP address, Octopi API key
        '''
        url = "http://" + self.ipAddress + "/api/connection"
        headers = {"Content-Type": "application/json", "X-Api-Key": self.apiKey}
        payload = {"command": "connect"}
        r = requests.post(url, headers=headers, data=payload)
        print(r)


    def isPrinterConnected(self):
        '''
        Check if the specified Pi is connected to the Printer.
        Arguments: Octopi IP address, Octopi API Key
        Returns: True if connected, False if not
        '''
        url = "http://" + self.ipAddress + "/api/connection"
        headers = {"X-Api-Key": self.apiKey}
        try:
            r = requests.get(url, headers=headers)
            rJson = json.loads(r.text)

            if (rJson["current"]["state"]) == "Operational": # Can be Closed or Operational
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(e)


    def getPrinterStatus(self):
        '''
        Request the current status of the connected 3D printer.
        Returns the response (JSON object) as a string.
        '''
        url = "http://" + self.ipAddress + "/api/printer"
        headers = {"X-Api-Key": self.apiKey}
        print("Accessing " + url + " using API Key " + self.apiKey)
        r = requests.get(url, headers=headers)
        rJson = json.loads(r.text)
        if r.text == "Printer is not operational":
            self.logger.error(print("Printer " + self.ipAddress + " is not operational"))
        else:
            return r.text


    def startPrintJob(self):
        '''
        Tell the specified printer to start printing the selected G-code
        G-code should be uploaded to the Manulab-folder in octoprint in advance.
        Arguments: Octopi IP address, Octopi API key, path to g-code file on the pi
        '''
        url = "http://" + self.ipAddress + "/api/job"
        headers = {"Content-Type": "application/json", "X-Api-Key": self.apiKey}
        payload = {"command": "start"}
        r = requests.post(url, headers=headers, data=payload)
        print(r)