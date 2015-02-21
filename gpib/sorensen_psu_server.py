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


class SorensenPSUWrapper(GPIBDeviceWrapper):

    def load_configuration(self, config):
        for key, value in config.__dict__.items():
            setattr(self, key, value)
        return str(config.__dict__)
    
    @inlineCallbacks
    def get_state(self):
        ans = yield self.query(':OUTP:STAT?')
        if ans == '1':
            returnValue(True)
        elif ans == '0':
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
        current = sorted([self.current_range[0], current, self.current_range[1]])[1]
        yield self.write(':SOUR:CURR {}'.format(current))
        returnValue(current)

    @inlineCallbacks
    def get_voltage(self):
        ans = yield self.query(':MEAS:VOLT?')
        returnValue(ans)

    @inlineCallbacks
    def set_voltage(self, voltage):
        voltage = sorted([self.voltage_range[0], voltage, self.voltage_range[1]])[1]
        yield self.write('SOUR:VOLT {}'.format(voltage))
        returnValue(voltage)

    @inlineCallbacks
    def get_power(self):
        ans = yield self.query(':MEAS:POW?')
        returnValue(ans)

    @inlineCallbacks
    def set_power(self, power):
        power = sorted([self.power_range[0], power, self.power_range[1]])[1]
        yield self.write('SOUR:POW {}'.format(power))
        returnValue(power)

class SorensenPSUServer(GPIBManagedServer):
    """Provides basic control for Sorensen DHP series power supplies"""
    name = '%LABRADNODE% PSU'
    deviceName = 'Sorensen DHP60-330 M9D'
    deviceWrapper = SorensenPSUWrapper


    def __init__(self, config_name):
        self.config_name = config_name
        self._load_configuration()
        self.update_values = Signal(self.update_id, "signal: update_values", '(sbvv)')
        GPIBManagedServer.__init__(self)

    @setting(10, 'state', state='b', returns='b')
    def state(self, c, state=None):
        dev = self.selectedDevice(c)
        if state is not None:
            yield dev.set_state(state)
        state = yield dev.get_state()
        yield self.notify_listeners(c)
        returnValue(state)

    @setting(11, 'current', current='v', returns='v')
    def current(self, c, current=None):
        dev = self.selectedDevice(c)
        if current is not None: 
            yield dev.set_current(current)
        current = yield dev.get_current()
        yield self.notify_listeners(c)
        returnValue(current)

    @setting(12, 'voltage', voltage='v', returns='v')
    def voltage(self, c, voltage=None):
        dev = self.selectedDevice(c)
        if voltage is not None:
            yield dev.set_voltage(voltage)
        voltage = yield dev.get_voltage()
        yield self.notify_listeners(c)
        returnValue(voltage)

    @setting(13, 'power', power='v', returns='v')
    def power(self, c, power=None):
        dev = self.selectedDevice(c)
        if power is not None:
            yield dev.set_power(power)
        power = yield dev.get_power()
        yield self.notify_listeners(c)
        returnValue(power)
    
    @inlineCallbacks
    def notify_listeners(self, c):
        dev = self.selectedDevice(c)
        s = yield dev.get_state()
        c = yield dev.get_current()
        v = yield dev.get_voltage()
        self.update_values((dev.name, s,c,v))

    def _load_configuration(self):
        config = __import__(self.config_name).SorensenPSUConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    @setting(15, 'select device by name', name='s', returns='s')
    def select_device_by_name(self, c, name=None):
        self._load_configuration()
        if name is None:
            returnValue(str(self.psu.keys()))
        else:
            yield self.select_device(c, self.psu[name].gpib_device_id)
            dev = self.selectedDevice(c)
            conf_str = dev.load_configuration(self.psu[name])
            returnValue(conf_str)

if __name__ == '__main__':
    from labrad import util
    config_name = 'sorensen_psu_config'
    __server__ = SorensenPSUServer(config_name)
    util.runServer(__server__)
