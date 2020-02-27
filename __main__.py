from pathlib import Path
from time import sleep
import logging
import OctoPrintCommunicator as opc
import pandas as pd
import json
import csv

'''
In this module, a list of IP addresses and API keys for Octoprint-connected 3D printers are read, then used to create 
instances of OctoPrintCommunicator clients. The main program then handles communication between printer OPC clients 
and various equipment.
'''

# Set up necessary variables
opcs = list()                                       # For storing all initialized OctoPrintClient objects
path_ListOfPrinters = Path("ListOfPrinters.csv")    # System-independent path
printDebug = True;                                  # Toggle whether or not to print all responses to console

# Set up logger
logging.basicConfig(
    filename='Log.txt', level=logging.ERROR, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


def importPrinterList():
    '''
    Import Octopi / printer IP addresses and API keys from the local ListOfPrinters.csv
    Usernames and passwords for the Octoprint user on each Pi is included as well.
    Lists are read by parsing columns. The first row should contain the following fields:
        "ipAddress", "apiKey", "username", "password". The delimiter sign is automatically inferred (, or ;).
    All valid rows are used to create OctoPrintClient objects, which are then stored in a list.
    '''
    global ipList
    global apiList
    global usernameList
    global passwordList
    try:

        # Infer CSV delimiter (comma or semicolon)
        with open(path_ListOfPrinters, 'r') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            delimiter = dialect.delimiter

        # Read csv to Pandas dataframe using first row as headers
        df = pd.read_csv(path_ListOfPrinters, sep=delimiter, header=0)
        ipList = list(df.ipAddress)
        apiList = list(df.apiKey)
        usernameList = list(df.username)
        passwordList = list(df.password)

        # Create an OPC instance for every element in the List Of Printers
        for i in range(len(ipList)):
            opcs.append(opc.OctoPrintClient(ipList[i], apiList[i], usernameList[i], passwordList[i]))

    except Exception as e:
        logger.error(e)
        logger.error(print("ListOfPrinters.csv may be missing or of invalid format"))

def updatePrinterStatus():
    '''
    Read status from all available printers. Write each printer's status as a row in a CSV file.
    Also, for testing purposes, write each printer's status to a separate txt file.
    '''

    # Row structure: [IP]; [connected]; [printing] ; [ready] ; [operational] ; [pausing] ; [paused] ; [finishing] ; [nozzle temp] ; [bed temp]
    opcStatusFields = ("IP;Connected;Printing;Ready;Operational;Pausing;Paused;Finishing;NozzleTemp;BedTemp\n")

    # Set up status CSV & txt
    path_statusCsv = Path("PrinterStatus/PrinterStatus.csv")
    statusCsv = open(path_statusCsv, 'w+') # Clear file before writing
    statusCsv.write(opcStatusFields)

    # Create status string for each connected printer
    for i, opc in enumerate(opcs):
        printerIsConnected = opc.isPrinterConnected()
        if printerIsConnected:
            r_login = opc.login()
            r_connect = opc.connectToPrinter()
            sleep(0.5)
            opcStatus = opc.getPrinterStatus()
            opcSJ = json.loads(opcStatus)
            # Row structure: [IP]; [connected]; [printing] ; [ready] ; [operational] ; [pausing] ; [paused] ; [finishing] ; [nozzle temp] ; [bed temp]
            opcStatusString =   (
                                str(opc.ipAddress) + ";" +
                                str(printerIsConnected) + ";" +
                                str(opcSJ['state']['flags']['printing']) + ';' +
                                str(opcSJ['state']['flags']['ready'])    + ';' +
                                str(opcSJ['state']['flags']['operational']) + ';' +
                                str(opcSJ['state']['flags']['pausing'])  + ';' +
                                str(opcSJ['state']['flags']['paused'])   + ';' +
                                str(opcSJ['state']['flags']['finishing']) + ";" +
                                str(opcSJ['temperature']['bed']['actual']) + ';' +
                                str(opcSJ['temperature']['tool0']['actual'])
                                )
        else:
            r_login = "Not connected to Pi!"
            r_connect = "Not connected to Pi!"
            opcStatus = "Not connected to Pi!"
            opcStatusString =   (
                                str(opc.ipAddress) + ";" +
                                str(printerIsConnected) + ";" +
                                ';' +
                                ';' +
                                ';' +
                                ';' +
                                ';' +
                                ";" +
                                ';'
                                )
        # Append status string to CSV & txt
        statusCsv.write(opcStatusString + "\n")
        path_statusTxt = Path("PrinterStatus/" + "printer" + str(i) + ".txt")
        with open(path_statusTxt, 'w+') as statusTextFile:
            statusTextFile.write(opcStatusFields + opcStatusString)

        # Print responses if the printResponses debugging variable is set to true
        if printDebug:
            print(opc.ipAddress + " login response: " + r_login)
            print(opc.ipAddress + " printer connect response: " + r_connect)
            print(opc.ipAddress + " printer status: " + opcStatus)

    # Close CSV to avoid
    statusCsv.close()

def connectToPrinters():
    '''
    Autoconnect the Pis to their respective printers (over USB)

    '''
    for i, opc in enumerate(opcs):
        response = opc.connectToPrinter()
        print("HTTP " + str(response))

# Test code

importPrinterList() # Always run this first!
#connectToPrinters()
print(opcs[0].connectToPrinter())
#print(opcs[2].disconnectFromPrinter())
#updatePrinterStatus()

#i = 0; # Test using first printer in OPC list
#print(opcs[i].selectPrintJob("/api/files/local/test/home.gcode"))
#print(opcs[i].getCurrentPrintJob())