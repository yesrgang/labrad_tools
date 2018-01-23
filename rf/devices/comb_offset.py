from twisted.internet.defer import inlineCallbacks

from devices.mfg2160.mfg2160 import MFG2160

class CombOffset(MFG2160):
    serial_server_name = 'yesr5_serial'
    serial_address = "COM14"

    frequency_range = (10e6, 300e6)
    amplitude_range = (0, 1)
    
    @inlineCallbacks
    def initialize(self):
        yield MFG2160.initialize(self)
        yield self.serial_server.write_line('SOUR3RF:AMP MAX')
#        yield self.set_frequency(70e6)
#        yield self.do_update_parameters()

__device__ = CombOffset
