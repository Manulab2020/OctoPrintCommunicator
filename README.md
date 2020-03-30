# OPC: OctoPrint Communicator

A Python 3 script for establishing basic communication between Octoprint-connected 3D printers and various equipment. 

Communication between the script and printers is carried out over HTTP using the Requests library with the Octoprint REST API. To and from the IPC, CSV-files are used.

For those simply looking for a Python-based Octoprint client, there are probably better alternatives out there.

### Main idea
This script is meant to run natively on an Omron NY-series IPC connected to industrial automation equipment, so as to save us the hardships of handling all communications using IEC 61131-3-compliant languages.
When initialized, a CSV containing IPs and API keys for each Octoprint instance are parsed and used to create client objects for each printer.
These clients then handle reading and writing data to the printers.

### How to use it
First of all, edit ```config.ini``` and ```ListOfPrinters.csv``` to suit your needs. Set IP addresses, Octoprint API keys, where to write status messages, logs, verbosity, HTTP timeout thresholds and more. The script is invoked from a command shell on the controller. This can be done e.g. in SCADA software or Windows' own Command Prompt: 

```python /path/to/script/__main__.py```

Based on the entries in *ListOfPrinters.csv*, a list of Octoprint Client objects are initialised and used to represent each printer. 

Periodically, the printers' status are written to a CSV, and another one - containing commands from the IPC - are read and parsed by the script. This file is written by the IPCs internal controller and cleared by the script after it has parsed the commands.

*Copyright © 2020 Fredrik Siem Taklo. MIT License.*
