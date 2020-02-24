from pathlib import Path
import logging
import OctoPrintCommunicator as opc
import pandas as pd
import json
import csv

'''
In this module, a list of IP addresses and API keys for Octoprint-connected 3D printers are read, then used to create 
instances of OctoPrintCommunicator clients. The OPCs handle communication between printers and different equipment.
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
    First row in the CSV must be "ipAddress,apiKey,username,password". The delimiter sign is automatically inferred.
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
    Read status from all available printers. Write desired data to one txt per printer to be parsed by PLC.
    '''
    for i, opc in enumerate(opcs):
        if opc.isPrinterConnected():
            r = opc.login()
        else:
            r = opc.connectToPrinter()
        opcStatus = opc.getPrinterStatus()
        opcSJ = json.loads(opcStatus)
        # Row structure: [printing] ; [ready] ; [operational] ; [pausing] ; [paused] ; [finishing] ; [nozzle temp] ; [bed temp]
        opcStatusNames = ("Printing;Ready;Operational;Pausing;Paused;Finishing;NozzleTemp;BedTemp\n")
        opcStatusString = (str(opcSJ['state']['flags']['printing']) + ';' +
                           str(opcSJ['state']['flags']['ready'])    + ';' +
                           str(opcSJ['state']['flags']['operational']) + ';' +
                           str(opcSJ['state']['flags']['pausing'])  + ';' +
                           str(opcSJ['state']['flags']['paused'])   + ';' +
                           str(opcSJ['state']['flags']['finishing']) + ";" +
                           str(opcSJ['temperature']['bed']['actual']) + ';' +
                           str(opcSJ['temperature']['tool0']['actual']))

        # Write status to txt for each OPC instance
        path_statusTxt = Path("PrinterStatus/" + "printer" + str(i) + ".txt")
        with open(path_statusTxt, "w+") as statusTextFile:
            statusTextFile.write(opcStatusNames + opcStatusString)

        # Print responses if the printResponses debugging variable is set to true
        if printDebug:
            print(opc.ipAddress + " login / connection response:\n" + r)
            print(opc.ipAddress + " printer status: " + opcStatus)


# Test code

importPrinterList()
updatePrinterStatus()

'''
i = 0; # Test using first printer in OPC list
print(opcs[i].selectPrintJob("/api/files/PATH TO GCODE IN OCTOPRINT"))
#print(opcs[i].startPrintJob())
#print(opcs[i].getCurrentPrintJob())
'''