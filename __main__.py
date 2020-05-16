from octoprintcommunication import OctoPrintClient
from pathlib import Path
from time import sleep
import configparser
import logging
import pandas
import json
import csv
import sys

'''
In this module, a list of IP addresses and API keys for Octoprint-connected 3D printers are read, then used to create 
instances of OctoPrintCommunicator clients. The main program then handles communication between printer OPC clients 
and various equipment.
'''


# First we need to set up the necessary variables to make the script run.
# Settings and file paths are read from config.ini
config = configparser.ConfigParser()
config.read('config.ini')

opcs = list()                                                   # For storing all initialized OctoPrintClient objects
path_ListOfPrinters = Path(config['Paths']['ListOfPrinters'])   # Path to the list of printer IPs / API keys
path_PrinterStatus = Path(config['Paths']['PrinterStatus'])     # Path to where to export the printer status
path_PrinterCommands = Path(config['Paths']['PrinterCommands']) # Path to printer commands from the IPC
path_Log = Path(config['Paths']['Log'])                         # Where to write the error log
verbose = config['Settings'].getboolean('Verbose')              # Toggle whether to print all responses to console
timeoutThreshold = int(config['Settings']['HTTP_timeout'])      # HTTP timeout threshold in seconds
cycleTime = int(config['Settings']['CycleTime'])                #
startupAutoConnect = config['Settings'].getboolean('StartupAutoConnect') # Autoconnect to printers when starting script

# Set up logger
logging.basicConfig(filename=path_Log, level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s %(message)s')
logger = logging.getLogger(__name__)

def inferCsvFormat(path_csv):
    '''
    Find the delimiter/separation string used in a CSV, then set the data/column header position.
    Returns: delimiter sign (string), which row number to read headers from (int)
    '''
    with open(path_csv, 'r') as csvfile:

        # Infer delimiter data automatically based on first line
        dialect = csv.Sniffer().sniff(csvfile.readline(), [',', ';'])
        csvfile.seek(0) # Return to first line of file for next read operation.
        delimiter = dialect.delimiter
        header = 0

        csvData = csv.reader(csvfile)
        csvDataList = list(csvData)
        if verbose:
            print("Opening " + str(path_csv) + " with delimiter=" + delimiter)

        # If the first line contains Excel separator data, use that instead, then use next line as header
        if csvDataList[0][0] == "sep=;":
            delimiter = ";"
            header = 1
        elif csvDataList[0][0] == "sep=,":
            delimiter = ","
            header = 1

        return (delimiter, header)

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

        delimiter, header = inferCsvFormat(path_ListOfPrinters)

        # Read csv to Pandas dataframe using first row as headers
        dataframe = pandas.read_csv(path_ListOfPrinters, sep=delimiter, header=header)
        ipList = list(dataframe.ipAddress)
        apiList = list(dataframe.apiKey)
        usernameList = list(dataframe.username)
        passwordList = list(dataframe.password)
        rackIDlist = list(dataframe.rackID)
        xPosList = list(dataframe.xPos)
        yPosList = list(dataframe.yPos)

        # Create an OPC instance for every element in the List Of Printers
        for i in range(len(ipList)):
            opcs.append(OctoPrintClient(ipList[i], apiList[i], usernameList[i], passwordList[i],
                                        rackIDlist[i], xPosList[i], yPosList[i],
                                        path_log=path_Log, timeout=timeoutThreshold, verbose=True))

    except Exception as e:
        logger.error(e)
        if verbose:
            print("ListOfPrinters.csv may be missing or of invalid format")

def connectToPrinters():
    '''
    Autoconnect the Pis to their respective printers (over USB)

    '''
    for i, opc in enumerate(opcs):
        if verbose:
            print("Attempting to connect to " + opc.ipAddress)
        if not opc.isPrinterConnected():
            response = opc.connectToPrinter()
            if verbose:
                print("HTTP " + str(response))
        else:
            if verbose:
                print("Already connected.")

def updatePrinterStatus():
    '''
    Read status from all available printers. Write each printer's status as a row in a CSV file.
    Also, for testing purposes, write each printer's status to a separate txt file.
    '''

    try:
        # Row header structure:
        # [IP]; [connected]; [printing]; [ready]; [operational]; [pausing]; [paused]; [finished]; [nozzle temp]; [bed temp]; [print job]; [rack ID]; [X pos]; [Y pos]
        opcStatusFields = ("IP;Connected;Printing;Ready;Operational;Pausing;Paused;Finished;NozzleTemp;BedTemp;PrintJob;RackID;Xpos;Ypos\n")

        # Set up status CSV & txt
        statusCsv = open(path_PrinterStatus, 'w+')  # Clear file before writing
        statusCsv.write(opcStatusFields)            # Add headers

        # Create status string for each connected printer
        for i, opc in enumerate(opcs):
            printerIsConnected = opc.isPrinterConnected()
            if printerIsConnected:
                opcStatus = opc.getPrinterStatus()
                opcSJ = json.loads(opcStatus)
                opcCurrentPrintJob = json.loads(opcs[0].getCurrentPrintJob())

                # The "finished"-status is a local variable in the client object.
                # It is only set when "finishing" is true, at the end of each print job.
                # It is reset by the printer command [printerIP , currentPrint, retrieved]
                if "true" in str(opcSJ['state']['flags']['finishing']):
                    opc.printFinished = "true"

                opcStatusString =   (
                                    str(opc.ipAddress)                              + ';' +
                                    str(printerIsConnected)                         + ';' +
                                    str(opcSJ['state']['flags']['printing'])        + ';' +
                                    str(opcSJ['state']['flags']['ready'])           + ';' +
                                    str(opcSJ['state']['flags']['operational'])     + ';' +
                                    str(opcSJ['state']['flags']['pausing'])         + ';' +
                                    str(opcSJ['state']['flags']['paused'])          + ';' +
                                    opc.printFinished                               + ';' +
                                    str(opcSJ['temperature']['bed']['actual'])      + ';' +
                                    str(opcSJ['temperature']['tool0']['actual'])    + ';' +
                                    str(opcCurrentPrintJob['job']['file']['name'])  + ';' +
                                    str(opc.rackID)                                 + ';' +
                                    str(opc.xPos)                                   + ';' +
                                    str(opc.yPos)
                                    )
            else:
                opcStatus = "Not connected to Pi!"
                opcStatusString =   (
                                    str(opc.ipAddress) + ";" +
                                    str(printerIsConnected) + ";" +
                                    ';' +
                                    ';' +
                                    ';' +
                                    ';' +
                                    ';' +
                                    ';' +
                                    ';' +
                                    ';' +
                                    ';' +
                                    ';' +
                                    ';' +
                                    ';'
                                    )

            # Append status string to CSV & txt
            statusCsv.write(opcStatusString + "\n")
            # Print responses if the verbose debugging variable is set to true
            if verbose:
                print(opc.ipAddress + " printer status: " + opcStatusString)

        # Close CSV to avoid access issues
        statusCsv.close()

    except Exception as e:
        logger.error(e)
        if verbose:
            print(e)

def getCommandList():
    '''
    Read and sort CSV containing commands for the printer. The CSV is intended to be written by an IPC.
    Returns the commands as lists of IP addresses, commands and arguments.
    '''

    delimiter, header = inferCsvFormat(path_PrinterCommands)

    # Read csv to Pandas dataframe using the first relevant row as headers
    dataframe = pandas.read_csv(path_PrinterCommands, sep=delimiter, header=header)
    ipList = list(dataframe.IP_Address)
    commandList = list(dataframe.Command)
    argumentList = list(dataframe.Argument)

    # Create a 2D list of command data.
    outputList = [ipList, commandList, argumentList]

    open(path_PrinterCommands, 'w').close() # Clear file after parsing it

    return outputList



'''
MAIN SCRIPT STARTS HERE

From the PrinterCommands.csv, each column (IP, command, argument) is parsed and stored in a list.
For every cycle, the program checks if there is an IP address matching that of a registered OctoPrint client.
If there is, the command is read and carried out, using arguments if applicable.
'''
if __name__ == "__main__":
    # Upon calling the script, printers are connected to Pis, then ran until the script / shell is closed.
    importPrinterList()  # Must be run first. Otherwise there won't be any OPCs to work with.

    # Connection time varies between hardware and network configurations.
    # Printers will usually take around 10 seconds to establish connection to OctoPrint.
    if startupAutoConnect:
        connectToPrinters()
        sleep(10)

    while True:
        updatePrinterStatus()
        commandList = getCommandList()

        # Parse and run commands
        for i, opc in enumerate(opcs):
            ipAddress = commandList[0][i]
            command = commandList[1][i]
            argument = commandList[2][i]

            # # # If printer is connected, run commands # # #
            if opc.isPrinterConnected:
                if ipAddress == opc.ipAddress:

                    if command.lower() == "print":
                        selectedFile = argument
                        # Check if the string actually points to the files directory
                        if "api/files" in str(selectedFile):
                            opc.selectPrintJob(selectedFile)
                            opc.startPrintJob()
                            print(ipAddress + ": attempting to print: " + selectedFile)

                    # For external applications,
                    if command == "printRetrieved":
                        opc.printFinished = "false"

            #Administrative commands (shutdown, settings, connections, debug)

            # Terminate script remotely
            if "shutdown" or "exit" in ipAddress.lower():
                msg = "Script shut down by external command"
                logger.info(msg)
                if verbose:
                    print(msg)
                sys.exit()

            # (Re)connect Pi to printer
            if command.lower == "connect":
                if ipAddress == opc.ipAddress:
                    opc.connectToPrinter()
                if argument.lower == "all":
                    connectToPrinters()

        sleep(cycleTime) # Slow down cycle time to reduce congestion, as tasks are not really time sensitive.
