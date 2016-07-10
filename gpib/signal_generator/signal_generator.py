"""
### BEGIN NODE INFO
[info]
name = gpib_signal_generator
version = 1.0
description = 
instancename = gpib_signal_generator

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""


import json
import sys

from labrad.server import Signal, setting
from twisted.internet.defer import inlineCallbacks, returnValue

sys.path.append('../')
from gpib_device_server import GPIBDeviceServer
sys.path.append('../../')
from extras.decorators import quickSetting

UPDATE_ID = 698034

class SignalGeneratorServer(GPIBDeviceServer):
    """ Provides basic control for signal generators"""
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = 'gpib_signal_generator'

    @quickSetting(10, 'b')
    def state(self, c, state=None):
        """ get or change output state """

    @quickSetting(11, 'v')
    def frequency(self, c, frequency=None):
        """ get or change output frequency """


    @quickSetting(12, 'v')
    def amplitude(self, c, amplitude=None):
        """ get or change output amplitude """

    
    @quickSetting(13, 'v')
    def ramprate(self, c, ramprate=None):
        """ get or change ramprate """


if __name__ == "__main__":
    from labrad import util
    util.runServer(SignalGeneratorServer())
