from twisted.internet.defer import inlineCallbacks, returnValue
import vxi11

from server_tools.device_server import Device

class AG53220A(Device):
    vxi11_address = None
    
    channel = None

    def initialize(self):
        self.vxi11 = vxi11.Instrument(self.vxi11_address)

    def get_frequency(self):
        command = 'MEAS:FREQ? DEF, DEF, (@{})'.format(self.channel)
        response = self.vxi11.ask(command)
        return float(response)
