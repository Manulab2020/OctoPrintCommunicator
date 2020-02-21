# OPC: OctoPrint Communicator
For establishing basic communication between Octoprint-connected 3D printers and various equipment.
For those simply looking for a python-based Octoprint client, there are probably better alternatives out there.

### Main idea
This program is our monument to laziness and flexibility. 
It is meant to run natively on an IPC connected to industrial automation equipment, so as to save us the hardships of handling all communications using IEC 61131-3-compliant languages.
When initialized, it parses a CSV containing IP addresses and API keys of any number of Octoprint-running Raspberry Pis, then connects to them. Printer data of interest is then exported to another CSV.

### Down the line
Current plans are to include the ability to request a print job externally. This will probably be done by parsing strings received over UDP.

*Copyright © 2020 Fredrik Siem Taklo. MIT License.*
