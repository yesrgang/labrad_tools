"""
### BEGIN NODE INFO
[info]
name = DS345 Server
version = 1.0
description = 

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

from labrad.server import setting
from labrad.gpib import GPIBManagedServer, GPIBDeviceWrapper
from twisted.internet.defer import inlineCallbacks, returnValue

class DS345Wrapper(GPIBDeviceWrapper):
    amplitude_units = 'DB'

    @inlineCallbacks
    def initialize(self):
        yield None
    
    @inlineCallbacks
    def frequency(self, new_frequency):
        if new_frequency is not None:
            yield self.write('FREQ {}'.format(new_frequency))
        updated_frequency = yield self.query('FREQ?')
        returnValue(float(updated_frequency))
    
    @inlineCallbacks
    def amplitude(self, new_amplitude):
        if new_amplitude is not None:
            yield self.write('AMPL {}{}'.format(new_amplitude, amplitude_units)
        updated_amplitude = yield self.query('AMPL?')
        returnValue(float(updated_amplitude[:-2]))

class DS345Server(GPIBManagedServer):
    """Provides basic control for SRS DS345"""
    name = 'DS345'
    deviceName = 'StanfordResearchSystems DS345'
    deviceWrapper = DS345Wrapper

    @setting(10, 'frequency', new_frequency='v', returns='v')
    def frequency(self, c, new_frequency=None):
        dev = self.selectDevice(c)
        updated_frequency = yield dev.frequency(new_frequency)
        returnValue(updated_frequency)
    
    @setting(11, 'amplitude', new_amplitude='v', returns='v')
    def amplitude(self, c, new_amplitude=None):
        dev = self.selectDevice(c)
        updated_amplitude = yield dev.amplitude(new_amplitude)
        returnValue(updated_amplitude)

__server__ = PRO8000Server()

if __name__ == '__main__':
    from labrad import util
    util.runServer(__server__)
