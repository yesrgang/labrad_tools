"""
### BEGIN NODE INFO
[info]
name = E4432B
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

import numpy as np
import time
from labrad.server import setting, Signal
from labrad.gpib import GPIBManagedServer, GPIBDeviceWrapper
from twisted.internet.defer import inlineCallbacks, returnValue

STATE_ID = 698013
FREQUENCY_ID = 698014
POWER_ID = 698015

class E4432BWrapper(GPIBDeviceWrapper):
    def initialize(self):
        self.load_configuration()

    def load_configuration(self):
        from  e4432bconfig import E4432BConfig
        self.sysconf = E4432BConfig()

    def ctl_conf(self, controller_name):
        conf = self.sysconf.controller[controller_name].get_dict()
        return conf

    @inlineCallbacks
    def get_state(self):
        ans = yield self.query('OUTP:STAT?')
        returnValue(bool(int(ans)))

    @inlineCallbacks
    def set_state(self, state):
        yield self.write('OUTP:STAT {}'.format(int(bool(state))))

    @inlineCallbacks
    def get_frequency(self):
        ans = yield self.query('FREQ:CW?')
        returnValue(float(ans)*1e-6) # keep things in MHz 

    @inlineCallbacks
    def set_frequency(self, frequency):
        yield self.write('FREQ:CW {} MHz'.format(frequency))

    @inlineCallbacks
    def get_power(self):
        ans = yield self.query('POW:AMPL?')
        returnValue(float(ans))

    @inlineCallbacks
    def set_power(self, power):
        yield self.write('POW:AMPL {} DBM'.format(power))


class E4432BServer(GPIBManagedServer):
    """Provides basic control for HP E4432B signal generator"""
    name = '%LABRADNODE% E4432B'
    deviceName = ''
    deviceWrapper = E4432BWrapper

    update_state = Signal(STATE_ID, "signal: update_state", 'b')
    update_frequency = Signal(FREQUENCY_ID, "signal: update_frequency", 'v')
    update_power = Signal(POWER_ID, "signal: update_power", 'v')

    @inlineCallbacks
    def initServer(self):
        yield self.get_configuration(None)
        self.deviceName = self.config.device_name

        yield GPIBManagedServer.initServer(self)
    
    @setting(00, 'set defaults', returns='')    
    def set_defaults(self):
        yield self.state(None, self.config.def_state)
        yield self.frequency(None, self.config.def_frequency)
        yield self.power(None, self.config.def_power)

    @setting(10, 'state', state='b', returns='b')
    def state(self, c, state=None):
        dev = self.selectedDevice(c)
        if state is not None:
            yield dev.set_state(state)
        state = yield dev.get_state()
        yield self.update_state(state)
        returnValue(state)

    @setting(11, 'frequency', frequency='v', returns='v')
    def frequency(self, c, frequency=None):
        dev = self.selectedDevice(c)
        if frequency is not None:
            yield dev.set_frequency(frequency)
        frequency = yield dev.get_frequency()
        yield self.update_frequency(frequency)
        returnValue(frequency)

    @setting(12, 'power', power='v', returns='v')
    def power(self, c, power=None):
        dev = self.selectedDevice(c)
        if power is not None:
            yield dev.set_power(power)
        power = yield dev.get_power()
        yield self.update_power(power)
        returnValue(power)
    
    @setting(14, 'request values')
    def request_values(self, c):
        yield self.state(c)
        yield self.frequency(c)
        yield self.power(c)

    @setting(15, 'get configuration', returns='s')
    def get_configuration(self, c):
        from e4432bconfig import E4432BConfig
        self.config = E4432BConfig()
        return str(self.config.__dict__)

__server__ = E4432BServer()

if __name__ == '__main__':
    from labrad import util
    util.runServer(__server__)
