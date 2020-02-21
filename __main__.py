from pathlib import Path
import logging
import OctoPrintCommunicator as opc
import pandas as pd
import json
import csv

'''
In this module, a list of IP addresses and API keys for Octoprint-connected 3D printers are read, then used for
communication with other equipment. 
'''

# Set up necessary variables
opcs = list()                                       # For storing all initialized OctoPrintClient objects
path_ListOfPrinters = Path("ListOfPrinters.csv")    # System-independent path

# Set up logger
logging.basicConfig(
    filename='Log.txt', level=logging.DEBUG, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)


def importPrinterList():
    '''
    Import Octopi / printer IP addresses and API keys from the local ListOfPrinters.csv
    First row in the CSV must be "ipAddress,apiKey". The delimiter sign is automatically inferred.
    All valid rows are used to create OctoPrintClient objects, which are then stored in a list.
    '''
    global ipList
    global apiList
    try:

        # Infer CSV delimiter (comma or semicolon)
        with open(path_ListOfPrinters, 'r') as csvfile:
            dialect = csv.Sniffer().sniff(csvfile.read(1024))
            delimiter = dialect.delimiter

        # Read csv to Pandas dataframe using first row as headers
        df = pd.read_csv(path_ListOfPrinters, sep=delimiter, header=0)
        ipList = list(df.ipAddress)
        apiList = list(df.apiKey)

        # Create an OPC instance for every element in the List Of Printers
        for i in range(len(ipList)):
            opcs.append(opc.OctoPrintClient(ipList[i], apiList[i]))

    except Exception as e:
        logger.error(e)
        logger.error(print("ListOfPrinters.csv may be missing or of invalid format"))


def getJsonNameValuePair(jsonObj, name, value=None):
    '''
    TODO: Test this when relevant OPC methods are done
    What it says on the tin. Limited to simple structures with one name-value pair.
    '''
    return (str(jsonObj[name]) + str(jsonObj[name][value]))

# Test code:
i = 0

importPrinterList()
print(opcs[i].login("manulab", "propanautomat"))

opcStatus = opcs[i].getPrinterStatus()
print(opcStatus)
opcSJ = json.loads(opcStatus)
# Row structure: [printing] ; [ready] ; [operational] ; [pausing] ; [paused] ; [finishing] ; [nozzle temp] ; [bed temp]
opcStatusString = (str(opcSJ['state']['flags']['printing'])    + ';' + str(opcSJ['state']['flags']['ready'])      + ';' +
                str(opcSJ['state']['flags']['operational']) + ';' + str(opcSJ['state']['flags']['pausing'])    + ';' +
                str(opcSJ['state']['flags']['paused'])      + ';' + str(opcSJ['state']['flags']['finishing'])  + ";" +
                str(opcSJ['state']['flags']['paused'])      + ';' + str(opcSJ['temperature']['bed']['actual']) + ';' +
                str(opcSJ['temperature']['tool0']['actual']))

print(opcStatusString)
# opcs[i].startPrintJob() #TODO: find out why file and job posts receive HTTP response 400