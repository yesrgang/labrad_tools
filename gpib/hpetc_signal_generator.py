"""
### BEGIN NODE INFO
[info]
name = HP Signal Generator
version = 1.0
description = 
instancename = %LABRADNODE% HP Signal Generator

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
from twisted.internet.task import LoopingCall

#STATE_ID = 698013
#FREQUENCY_ID = 698014
#POWER_ID = 698015
#
class HPSignalGeneratorWrapper(GPIBDeviceWrapper):
    def initialize(self):
        pass

#    def load_configuration(self, name):
#        """ name is from config file"""
#        from n5181aconfig import ServerConfig
#        self.config = ServerConfig().device_dict[name]

    def set_configuration(self, configuration):
        self.configuration = configuration
        for key, value in configuration.__dict__.items():
            setattr(self, key, value)

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


class HPSignalGeneratorServer(GPIBManagedServer):
    """Provides basic control for HP signal generators"""
#    name = '%LABRADNODE% HP Signal Generator'
#    deviceName = ''
    deviceWrapper = HPSignalGeneratorWrapper
#
#    update_state = Signal(STATE_ID, "signal: update_state", 'b')
#    update_frequency = Signal(FREQUENCY_ID, "signal: update_frequency", 'v')
#    update_power = Signal(POWER_ID, "signal: update_power", 'v')

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
        self.update_state = Signal(self.state_id, "signal: update_state", '(sb)')
        self.update_current = Signal(self.current_id, "signal: update_current", '(sv)')
        self.update_power = Signal(self.power_id, "signal: update_power", '(sv)')
        yield GPIBManagedServer.initServer(self)

    @setting(9, 'select device by name', name='s', returns='s')    
    def select_device_by_name(self, c, name):
        gpib_device_id = self.devices[name].gpib_device_id
        yield self.select_device(c, gpib_device_id)
        dev = self.selectedDevice(c)
        dev.load_configuration(self.devices[name])
        returnValue(name)

    @setting(10, 'state', state='b', returns='b')
    def state(self, c, state=None):
        dev = self.selectedDevice(c)
        if state is not None:
            yield dev.set_state(state)
        sate = yield dev.get_state()
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

    @setting(13, 'sweep', parameters='(vb)', returns='(vb)')
    def sweep(self, c, parameters=None):
        dev = self.selectedDevice(c)
        if parameters is not None:
            dev.config.sweep_rate = parameters[0]
            dev.config.sweep_state = parameters[1]
        return (dev.config.sweep_rate, dev.config.sweep_state)
    
    @inlineCallbacks
    def _sweep(self):
        for k  in self.devices.keys():
            dev = self.devices[k]
            if hasattr(dev, 'config'):
                if dev.config.sweep_state:
                    f = yield dev.get_frequency()
                    f += dev.config.sweep_rate*self.sweep_dwell
                    yield dev.set_frequency(f)
                    yield self.update_frequency(f)
    
    @setting(14, 'request values')
    def request_values(self, c):
        yield self.state(c)
        yield self.frequency(c)
        yield self.power(c)

    @setting(15, 'get configuration', returns='s')
    def get_configuration(self, c):
        from n5181aconfig import ServerConfig, N5181AConfig
        config = ServerConfig()
        # for name, obj in config.device_dict.items():
        #     if obj.gpib_device_id in self.devices.keys():
        #         self.devices[obj.gpib_device_id].load_configuration(name)

        for key, value in config.__dict__.items():
            setattr(self, key, value)
        return str(config.__dict__)


if __name__ == '__main__':
    configuration_name = 'hpetc_signal_generator_config.py'
    __server__ = HPSignalGeneratorServer()
    from labrad import util
    util.runServer(__server__)
