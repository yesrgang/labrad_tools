"""
### BEGIN NODE INFO
[info]
name = plotter
version = 1.0
description = 
instancename = plotter

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

import json
import os

from labrad.server import LabradServer, setting, Signal

class PlotterServer(LabradServer):
    name = 'plotter'

    @setting(0, json_data='s')
    def plot(self, c, json_data):
        print json_data
        with open('../../figure.json', 'w') as outfile:
            json.dump(json.loads(json_data), outfile)

if __name__ == "__main__":
    from labrad import util
    server = PlotterServer()
    util.runServer(server)
