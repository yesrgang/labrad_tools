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
import json

from labrad.server import setting, Signal
from labrad.gpib import GPIBManagedServer, GPIBDeviceWrapper
from twisted.internet.defer import inlineCallbacks, returnValue
from time import sleep


class SorensenPSUWrapper(GPIBDeviceWrapper):

    def load_configuration(self, config):
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    @inlineCallbacks
    def set_defaults(self):
        yield self.set_state(self.def_state)
        yield self.set_current(self.def_current)
        yield self.set_voltage(self.def_voltage)
        yield self.set_power(self.def_power)
    
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

class fake_c(object):
    ID = 0
    def __init__(self):
        self.ID = 0

    def __iter__(self):
        return self

    def next(self):
        raise StopIteration

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class SorensenPSUServer(GPIBManagedServer):
    """Provides basic control for Sorensen DHP series power supplies"""
    deviceName = 'Sorensen DHP60-330 M9D'
    deviceWrapper = SorensenPSUWrapper

    def __init__(self, config_name):
        self.config_name = config_name
        self._load_configuration()
        self.update_values = Signal(self.update_id, "signal: update_values", '(sbvvv)')
        GPIBManagedServer.__init__(self)
    
    @inlineCallbacks
    def initServer(self):
        yield GPIBManagedServer.initServer(self)
        for name, conf in self.psu.items():
            for key, gpib_device_id in self.list_devices(None):
                if conf.gpib_device_id == gpib_device_id:
                    dev = self.devices[key]
                    dev.load_configuration(conf)
                    dev.set_defaults()

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
            sleep(.5)
        current = yield dev.get_current()
        yield self.notify_listeners(c)
        returnValue(current)

    @setting(12, 'voltage', voltage='v', returns='v')
    def voltage(self, c, voltage=None):
        dev = self.selectedDevice(c)
        if voltage is not None:
            yield dev.set_voltage(voltage)
            sleep(.5)
        voltage = yield dev.get_voltage()
        yield self.notify_listeners(c)
        returnValue(voltage)

    @setting(13, 'power', power='v', returns='v')
    def power(self, c, power=None):
        dev = self.selectedDevice(c)
        if power is not None:
            yield dev.set_power(power)
            sleep(.5)
        power = yield dev.get_power()
        yield self.notify_listeners(c)
        returnValue(power)
    
    @inlineCallbacks
    def notify_listeners(self, c):
        dev = self.selectedDevice(c)
        s = yield dev.get_state()
        c = yield dev.get_current()
        v = yield dev.get_voltage()
        p = yield dev.get_power()
        print s,c,v,p
        yield self.update_values((dev.name, s, c, v, p))

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
            dev.load_configuration(self.psu[name])
            returnValue(json.dumps(self.psu[name].__dict__))

if __name__ == '__main__':
    from labrad import util
    config_name = 'sorensen_psu_config'
    __server__ = SorensenPSUServer(config_name)
    util.runServer(__server__)
