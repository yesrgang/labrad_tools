"""
### BEGIN NODE INFO
[info]
name = DHP
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

from labrad.server import setting, Signal
from labrad.gpib import GPIBManagedServer, GPIBDeviceWrapper
from twisted.internet.defer import inlineCallbacks, returnValue

STATE_ID = 698004
CURRENT_ID = 698005
VOLTAGE_ID = 698006

class DHPWrapper(GPIBDeviceWrapper):
    def initialize(self):
        self.load_configuratoin()

    def load_configuratoin(self):
        from dhppsuconfig import DHPConfig
        self.conf = DHPConfig()

    def conf_str(self):
        conf_str = str(self.conf.get_dict())
        returnValue(conf_str)
    
    @inlineCallbacks
    def get_state(self):
        ans = yield self.query(':OUTP:STAT?')
        if ans == ':ON':
            returnValue(True)
        elif ans == ':OFF':
            returnValue(False)

    @inlineCallbacks
    def set_state(self, state):
        if state is True:
            yield self.write(':OUTP:STAT ON')
        else:
            yield self.write(':OUTP:STAT OFF')

    @inlineCallbacks
    def get_current(self):
        ans = yield self.query(':MEAS:CURR?')
        returnValue(ans)

    @inlineCallbacks
    def set_current(self, current):
        current = sorted([self.conf.min_current, current, self.conf.max_current])[1]
        yield self.write(':SOUR:CURR {}'.format(current))
        returnValue(current)

    @inlineCallbacks
    def get_voltage(self):
        ans = yield self.query(':MEAS:VOLT?')
        returnValue(ans)

    @inlineCallbacks
    def set_voltage(self, voltage):
        voltage = sorted([self.conf.min_voltage, voltage, self.conf.max_voltage])[1]
        yield self.write('SOUR:VOLT {}'.format(voltage))
        returnValue(voltage)

    @inlineCallbacks
    def get_power(self):
        ans = yield self.query(':MEAS:POW?')
        returnValue(ans)

    @inlineCallbacks
    def set_power(self, power):
        power = sorted([self.conf.min_power, power, self.conf.max_power])[1]
        yield self.write('SOUR:POW {}'.format(power))
        returnValue(power)

class PRO8000Server(GPIBManagedServer):
    """Provides basic control for Sorensen DHP series power supplies"""
    name = 'DHP'
    deviceName = '' #output of query('*IDN?')[:1]
    deviceWrapper = DHPWrapper

    #signals
    emit_state = Signal(STATE_ID, "signal: update_state", 'b')
    emit_current = Signal(CURRENT_ID, "signal: update_current", 'v')
    emit_voltage = Signal(VOLTAGE_ID, "signal: update_voltage", 'v')

    @setting(10, 'state', state='b', returns='b')
    def state(self, c, state=None):
        dev = self.selectedDevice(c)
        if state is not None:
            yield dev.set_state(state)
        state = yield dev.get_state()
        yield self.emit_state(state)
        returnValue(state)

    @setting(11, 'current', current='v', returns='v')
    def current(self, c, current=None):
        dev = self.selectedDevice(c)
        if current is not None: 
            yield dev.set_current(current)
        current = yield dev.get_current()
        yield self.emit_current(current)
        returnValue(current)

    @setting(12, 'voltage', voltage='s', returns='v')
    def power(self, c, voltage=None):
        dev = self.selectedDevice(c)
        if voltage is not None:
            yield dev.set_voltage(voltage)
        voltage = yield dev.get_voltage()
        yield self.emit_voltage(voltage)
        returnValue(voltage)

    @setting(14, 'request values')
    def requestValues(self, c):
        yield self.state(c)
        yield self.current(c)
        yield self.voltage(c)

    @setting(15, 'get configuration', returns='s')
    def getConfiguration(self, c):
        from dhppsuconfig import DHPConfig
        conf = DHPConfig()
        conf_str = str(conf.get_dict())
        return conf_str

__server__ = DHPServer()

if __name__ == '__main__':
    from labrad import util
    util.runServer(__server__)
