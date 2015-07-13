"""
### BEGIN NODE INFO
[info]
name = PRO8000
version = 1.0
description = 
instancename = %LABRADNODE% PRO8000

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

STATE_ID = 698001
CURRENT_ID = 69800
POWER_ID = 698003

class PRO8000Wrapper(GPIBDeviceWrapper):
    def initialize(self):
        pass
#        self.load_configuration()

#    def load_configuration(self):
#        from pro8000config import PRO8000Config, LDC80xxConfig
#        self.sysconf = PRO8000Config()
#
#    def ctl_conf(self, controller_name):
#        conf = self.sysconf.controller[controller_name].get_dict()
#        return conf

    def set_configuration(self, configuration):
        self.configuration = configuration

    @inlineCallbacks
    def set_slot(self, controller_name):
        slot = self.configuration.controller[controller_name].slot
        yield self.write(':SLOT {}'.format(slot))
#        slot = self.ctl_conf(controller_name)['slot']
#        yield self.write(':SLOT {}'.format(self.ctl_conf(controller_name)['slot']))

    @inlineCallbacks
    def get_current(self, controller_name):
        yield self.set_slot(controller_name)
        ans = yield self.query(':ILD:SET?')
        current = float(ans[9:])
        returnValue(current)

    @inlineCallbacks
    def set_current(self, controller_name, current):
        yield self.set_slot(controller_name)
        max_current = self.configuration.controller[controller_name].max_current
        current = sorted([0, current, max_current])[1]
        yield self.write(':ILD:SET {}'.format(current))
        returnValue(current)

    @inlineCallbacks
    def get_power(self, controller_name):
        yield self.set_slot(controller_name)
        ans = yield self.query(':POPT:ACT?')
        power = float(ans[10:])
        returnValue(power)

    @inlineCallbacks
    def get_state(self, controller_name):
        yield self.set_slot(controller_name)
        ans = yield self.query(':LASER?')
        if ans == ':LASER ON':
            returnValue(True)
        elif ans == ':LASER OFF':
            returnValue(False)

    @inlineCallbacks
    def set_state(self, controller_name, state):
        yield self.set_slot(controller_name)
        if state is True:
            yield self.write(':LASER ON')
            time.sleep(1) # what's the rush, man? 
            stop_value = self.configuration.controller[controller_name].def_currnet
            yield self.dial_current(controller_name, stop_value)
        else:
            yield self.dial_current(controller_name, 0.)
            yield self.write(':LASER OFF')

    @inlineCallbacks
    def dial_current(self, controller_name, stop_value):
        yield self.set_slot(controller_name)
        start_value = yield self.get_current(controller_name)
        values = np.linspace(start_value, stop_value, 20)
        for v in values: 
            yield self.set_current(controller_name, v)
            time.sleep(.05)


class PRO8000Server(GPIBManagedServer):
    """Provides basic CW control for Thor Labs PRO 8000 laser diode controller"""
#    name = '%LABRADNODE% PRO8000'
#    deviceName = 'PROFILE PRO8000'
    deviceWrapper = PRO8000Wrapper

    update_state = Signal(STATE_ID, "signal: update_state", '(sb)')
    update_current = Signal(CURRENT_ID, "signal: update_current", '(sv)')
    update_power = Signal(POWER_ID, "signal: update_power", '(sv)')

    def __init__(self, configuration_filename):
        self.configuration_filename = configuration_filename
        self.load_configuration()
        GPIBManagedServer.__init__(self)
    
    def load_configuration(self):
        self.configuration = __import__(self.configuration_filename).PRO8000Config()
        for key, value in self.configuration.__dict__.items():
            setattr(self, key, value)
        return self.configuration

    @inlineCallbacks
    def initServer(self):
        yield GPIBManagedServer.initServer(self)

    @setting(2, 'select device', key=[': Select first device', 's: Select device by name',
                'w: Select device by ID'], returns='s: Name of the selected device')
    def select_device(self, c, key):
        dev = self.selectDevice(c, key=key)
        dev.set_configuration(self.configuration)
        return dev.name

    @setting(10, 'state', controller_name='s', state='b', returns='b')
    def state(self, c, controller_name, state=None):
        dev = self.selectedDevice(c)
        if state is not None:
            yield dev.set_state(controller_name, state)
            yield self.request_values(c, controller_name)
        state = yield dev.get_state(controller_name)
        yield self.update_state((controller_name, state))
        returnValue(state)

    @setting(11, 'current', controller_name='s', current='v', returns='v')
    def current(self, c, controller_name, current=None):
        dev = self.selectedDevice(c)
        if current is not None: 
            yield dev.set_current(controller_name, current)
            yield self.power(c, controller_name)
        else:
            current = yield dev.get_current(controller_name)
            yield self.update_current((controller_name, current))
        returnValue(current)

    @setting(12, 'power', controller_name='s', returns='v')
    def power(self, c, controller_name):
        dev = self.selectedDevice(c)
        power = yield dev.get_power(controller_name)
        yield self.update_power((controller_name, power))
        returnValue(power)

    @setting(13, 'system state', state='b', returns='*b')
    def system_state(self, c, state=None):
        state_list = []
        for controller_name in self.sysconf.controller_order:
           s = yield self.state(c, controller_name, state)
           state_list.append(s)
        returnValue(state_list)

    @setting(14, 'request values', controller_name='s')
    def request_values(self, c, controller_name):
        yield self.state(c, controller_name)
        yield self.current(c, controller_name)
        yield self.power(c, controller_name)

    @setting(15, 'get system configuration')
    def get_system_configuration(self, c):
        conf =  self.load_configuration()
	d = {k: v for k, v in conf.__dict__.items() if k is not 'controller'}
        return str(d)
#        from pro8000config import PRO8000Config, LDC80xxConfig
#        self.sysconf = PRO8000Config()
#        sysconf_str = str(self.sysconf.get_dict())
#        return sysconf_str
    @setting(16, 'get controller configuration', controller_name='s')
    def get_controller_configuration(self, c, controller_name):
        conf = self.load_configuration()
	return str(conf.__dict__['controller'][controller_name].__dict__)

#    @setting(16, 'get controller configuration', controller_name='s', returns='s')
#    def get_controller_configuration(self, c, controller_name):
#        from pro8000config import PRO8000Config, LDC80xxConfig
#        self.sysconf = PRO8000Config()
#        ctlconf_str = str(self.sysconf.controller[controller_name].get_dict())
#        return ctlconf_str
        

__server__ = PRO8000Server('pro8000_configuration')

if __name__ == '__main__':
    from labrad import util
    util.runServer(__server__)
