"""
### BEGIN NODE INFO
[info]
name = spectrum_analyzer
version = 1.0
description = 
instancename = spectrum_analyzer

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

import sys

from labrad.server import Signal, setting

sys.path.append('../')
from server_tools.device_server import DeviceServer
from server_tools.decorators import quickSetting

UPDATE_ID = 6984523

class SpectrumAnalyzerServer(DeviceServer):
    """ Provides basic control for spectrum analyzers """
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'spectrum_analyzer'

    def stopServer(self):
        for device in self.devices:
            device.connection.close()

    @quickSetting(10, '*v')
    def trace(self, c, trace=1):
        """ Get data points from trace """
    
    @quickSetting(11, '*v')
    def frequency_range(self, c, frequency_range=None):
        """ Get and set frequency range """

    @quickSetting(12, 'v')
    def resolution_bandwidth(self, c, resolution_bandwidth=None):
        """ Get and set resolution bandwidth """

    @quickSetting(13, 'v')
    def amplitude_scale(self, c, amplitude_scale=None):
        """ Get and set amplitude scale """

    @quickSetting(14, 'v')
    def amplitude_offset(self, c, offset=None):
        """ Get and set amplitude offset"""


if __name__ == '__main__':
    from labrad import util
    util.runServer(SpectrumAnalyzerServer())
