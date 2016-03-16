"""
### BEGIN NODE INFO
[info]
name = ldc340
version = 1.0
description = 
instancename = ldc340

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

import time
import json
import numpy as np

from labrad.server import setting, Signal
from labrad.gpib import GPIBManagedServer, GPIBDeviceWrapper
from twisted.internet.defer import inlineCallbacks, returnValue


class LDC340Wrapper(GPIBDeviceWrapper):
    def set_configuration(self, configuration):
        self.configuration = configuration
        for key, value in configuration.__dict__.items():
            setattr(self, key, value)

    @inlineCallbacks
    def set_defaults(self):
        if hasattr(self, 'init_commands'):
            for command in self.init_commands:
                yield self.write(command)

    @inlineCallbacks
    def get_current(self):
        ans = yield self.query(':ILD:SET?')
        current = float(ans[9:])
        returnValue(current)

    @inlineCallbacks
    def set_current(self, current):
        lo, hi = self.current_range
        current = sorted([lo, current, hi])[1]
        yield self.write(':ILD:SET {}'.format(current))
        returnValue(current)

    @inlineCallbacks
    def get_power(self):
        ans = yield self.query(':POPT:ACT?')
        power = float(ans[10:])
        returnValue(power)

    @inlineCallbacks
    def get_state(self):
        ans = yield self.query(':LASER?')
        if ans == ':LASER ON':
            returnValue(True)
        elif ans == ':LASER OFF':
            returnValue(False)

    @inlineCallbacks
    def set_state(self, state, dial):
        if state is True:
            yield self.write(':LASER ON')
            time.sleep(1) # what's the rush, man? 
            if dial:
                stop_value = self.def_current
                yield self.dial_current(stop_value)
        else:
            if dial:
                yield self.dial_current(0.)
            yield self.write(':LASER OFF')

    @inlineCallbacks
    def dial_current(self, stop_value):
        start_value = yield self.get_current()
        values = np.linspace(start_value, stop_value, self.dial_steps)
        for v in values: 
            yield self.set_current(v)
            time.sleep(.05)


class LDC340Server(GPIBManagedServer):
    """Control Thorlabs LDC340"""
    deviceWrapper = LDC340Wrapper

    def __init__(self, configuration_filename):
        self.configuration_filename = configuration_filename
        self.load_configuration()
        self.update = Signal(self.update_id, "signal: update", 's')
        GPIBManagedServer.__init__(self)
    
    def load_configuration(self):
        self.configuration = __import__(self.configuration_filename).LDC340Config()
        for key, value in self.configuration.__dict__.items():
            setattr(self, key, value)
        return self.configuration

    @inlineCallbacks
    def initServer(self):
        yield GPIBManagedServer.initServer(self)

    @setting(9, 'select device by name', name='s', returns='s')    
    def select_device_by_name(self, c, name=None):
        if name is not None:
	    gpib_device_id = self.device_configurations[name].gpib_device_id
            yield self.select_device(c, gpib_device_id)
            dev = self.selectedDevice(c)
	    confd = self.device_configurations[name].__dict__
            returnValue(json.dumps(confd))
        else:
            returnValue(json.dumps(self.device_configurations.keys()))

    @setting(10, 'state', state='b', dial='b', returns='b')
    def state(self, c, state=None, dial=True):
        dev = self.selectedDevice(c)
        if state is not None:
            yield dev.set_state(state, dial)
        state = yield dev.get_state()
        self.update(json.dumps({'state': state}))
        returnValue(state)

    @setting(11, 'current', current='v', returns='v')
    def current(self, c, current=None):
        dev = self.selectedDevice(c)
        if current is not None: 
            yield dev.set_current(current)
        current = yield dev.get_current()
        #power = yield self.power(c)
        self.update(json.dumps({'current': current}))
        returnValue(current)

    @setting(12, 'power', returns='v')
    def power(self, c):
        dev = self.selectedDevice(c)
        power = yield dev.get_power()
        yield self.update(json.dumps({'power': power}))
        returnValue(power)

    @setting(14, 'send update')
    def send_update(self, c):
        dev = self.selectedDevice(c)
        update_d = {}
        for param in dev.update_parameters:
            try: 
                value = yield getattr(dev, 'get_'+param)()
                update_d[param] = value
            except AttributeError:
                print 'device has no attribute get_{}'.format(param)
        self.update(json.dumps(update_d))

    @setting(15, 'get system configuration')
    def get_system_configuration(self, c):
        conf =  self.load_configuration()
        return json.dumps(conf.__dict__)
    
    @setting(16, 'get controller configuration', device_name='s')
    def get_controller_configuration(self, c, device_name):
        conf = self.load_configuration()
	return json.dumps(conf.device_configurations(device_name).__dict__)

if __name__ == '__main__':
    configuration_name = 'ldc340_configuration'
    __server__ = LDC340Server(configuration_name)
    from labrad import util
    util.runServer(__server__)
