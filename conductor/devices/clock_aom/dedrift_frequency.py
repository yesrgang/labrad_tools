from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync

from conductor_device.conductor_parameter import ConductorParameter

class DedriftFrequency(ConductorParameter):
    priority = 1

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.yesr11_vxi11.select_interface("192.168.1.13")
    
    @inlineCallbacks
    def update(self):
        message = 'MEAS:FREQ? DEF, DEF, (@1)'
        response = yield self.cxn.yesr11_vxi11.query(message)
#        response = yield self.cxn.yesr20_gpib.query(message)
        try:
            self.value = float(response)
        except:
            self.value = None
