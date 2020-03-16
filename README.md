# OPC: OctoPrint Communicator
For establishing basic communication between Octoprint-connected 3D printers and various equipment.

All communication between the script and printers is carried out over HTTP by using the Requests library with the Octoprint REST API.

For those simply looking for a Python-based Octoprint client, there are probably better alternatives out there.

### Main idea
This script is a monument to laziness and flexibility. 
It is meant to run natively on an Omron NY-series IPC connected to industrial automation equipment, so as to save us the hardships of handling all communications using IEC 61131-3-compliant languages.
When initialized, a CSV containing IPs and API keys for each Octoprint instance are parsed and used to create client objects for each printer.
These clients then handle reading and writing data to the printers.

### How it works
The script is started by invoking it from a command shell on the controller. This can be done e.g. in SCADA software or Windows' own Command Prompt.

It reads the config.ini file for relevant file path names and settings, then imports printers from a CSV containing IP addresses & API keys.
A list of Octoprint Client objects are then initialised and used to represent each printer. 

Periodically, the printers' status are read to a CSV, and another one - containing commands written by the IPC - are read and parsed by the script. This file is written by the IPCs internal controller and cleared by the script after it has parsed the commands.

*Copyright © 2020 Fredrik Siem Taklo. MIT License.*
