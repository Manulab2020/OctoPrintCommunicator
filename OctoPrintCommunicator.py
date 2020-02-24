import sys
from pathlib import Path
import logging
import json
import requests

'''
This class contains the necessary commands to extract information from Raspberry Pis running Octoprint,
as well as commands to start print jobs. Communication between the script and Pis are done through parsing of
JSON objects. Methods primarily return JSON-formatted strings.
'''

class OctoPrintClient:

    def __init__(self, ipAddress, apiKey, username, password):
        '''
        Initialize a "client". Each client handles one connection to one printer.
        A logger object is initialized to write error logs as well.
        '''
        self.ipAddress = ipAddress
        self.apiKey = apiKey
        self.username = username
        self.password = password

        logging.basicConfig(filename='Log.txt', level=logging.ERROR,
                            format='%(asctime)s %(levelname)s %(name)s %(message)s')
        self.logger = logging.getLogger(__name__)


    def printDebugInfo(self):
        '''
        Print relevant info about this object for debugging purposes
        '''
        print("IP: " + self.ipAddress + ", ")
        print("API key: " + self.apiKey + ", ")
        print("Username: " + self.username + ", ")
        print("Password: " + self.password + ", ")

    def login(self):
        '''
        Log into Octoprint on the specified IP address
        Returns response as string.
        '''
        url = "http://" + self.ipAddress + "/api/login"
        payload = {"user": self.username, "pass": self.password}
        r = requests.post(url, json=payload)
        return r.text

    def logout(self):
        '''
        Log out from Octoprint on the specified IP address.
        You probably do not need to use this for this program.
        Returns response as string.
        '''
        url = "http://" + self.ipAddress + "/api/logout"
        r = requests.post(url)
        return r.text

    def connectToPrinter(self):
        '''
        Connect to the 3D printer over USB. Default values are used.
        Returns response as string.
        '''
        url = "http://" + self.ipAddress + "/api/connection"
        headers = {"Content-Type": "application/json", "X-Api-Key": self.apiKey}
        payload = {"command": "connect"}
        r = requests.post(url, headers=headers, json=payload)
        return r.text

    def disconnectFromPrinter(self):
        '''
        Disconnect from the 3D printer if connected.
        Returns response as string.
        '''
        url = "http://" + self.ipAddress + "/api/connection"
        headers = {"Content-Type": "application/json", "X-Api-Key": self.apiKey}
        payload = {"command": "connect"}
        r = requests.post(url, headers=headers, json=payload)
        return r.text

    def isPrinterConnected(self):
        '''
        Check if the specified Pi is connected to the Printer.
        Returns: True if connected, False if not
        '''
        url = "http://" + self.ipAddress + "/api/connection"
        headers = {"X-Api-Key": self.apiKey}

        r = requests.get(url, headers=headers)
        rJson = json.loads(r.text)

        if (rJson["current"]["state"]) == "Operational": # Can be Closed or Operational
            return True
        else:
            return False


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

    def getCurrentPrintJob(self):
        '''
        Check to see what is currently printing, if anything at all.
        Return JSON string containing job info.
        '''
        url = "http://" + self.ipAddress + "/api/job"
        headers = {"X-Api-Key": self.apiKey}
        r = requests.get(url, headers=headers)
        return r.text

    def selectPrintJob(self, gcodePath):
        '''
        Select gcode stored on the Pi.
        Argument: path to the gcode
        Returns the response as JSON string
        '''
        url = "http://" + self.ipAddress + gcodePath
        headers = {"Content-Type": "application/json", "X-Api-Key": self.apiKey}
        payload = {"command": "select"}
        r = requests.post(url, headers=headers, json=payload)
        return r.text

    def startPrintJob(self):
        '''
        Tell the specified printer to start printing the selected G-code
        G-code should be uploaded to the Manulab-folder in octoprint in advance.
        Arguments: Octopi IP address, Octopi API key, path to g-code file on the pi
        Returns: response as JSON string
        '''
        url = "http://" + self.ipAddress + "/api/job"
        headers = {"Content-Type": "application/json", "X-Api-Key": self.apiKey}
        payload = {"command": "start"}
        r = requests.post(url, headers=headers, json=payload)
        return r.text