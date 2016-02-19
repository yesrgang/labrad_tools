"""
### BEGIN NODE INFO
[info]
name = 33500b
version = 1.0
description = 
instancename = 33500b

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""
import os
import json
import numpy as np
from labrad.server import setting, Signal
from labrad.gpib import GPIBManagedServer, GPIBDeviceWrapper
from twisted.internet.defer import inlineCallbacks, returnValue
from influxdb import InfluxDBClient


class AG33500BWrapper(GPIBDeviceWrapper):
    def set_configuration(self, configuration):
        self.configuration = configuration
        for key, value in configuration.__dict__.items():
            setattr(self, key, value)
    
    @inlineCallbacks
    def set_defaults(self):
        for command in self.init_commands:
            yield self.write(command)

    @inlineCallbacks
    def get_state(self):
        ans = yield self.query('OUTP{}?'.format(self.source))
	self.state = bool(int(ans))
        returnValue(ans)

    @inlineCallbacks
    def set_state(self, state):
        yield self.write('OUTP{}:STAT {}'.format(self.source, int(bool(state))))

    @inlineCallbacks
    def get_frequency(self):
        ans = yield self.query('SOUR{}:FREQ?'.format(self.source))
	self.frequency = float(ans)
        returnValue(float(ans))

    @inlineCallbacks
    def set_frequency(self, frequency):
        yield self.write('SOUR{}:FREQ {}'.format(self.source, frequency))

    @inlineCallbacks
    def get_amplitude(self):
        ans = yield self.query('SOUR{}:VOLT?'.format(self.source))
	self.amplitude = float(ans)
        returnValue(float(ans))

    @inlineCallbacks
    def set_amplitude(self, amplitude):
        yield self.write('SOUR{}:VOLT {}'.format(self.cource, amplitude))


class AG33500BServer(GPIBManagedServer):
    """Provides basic control for HP signal generators"""
    deviceWrapper = AG33500BWrapper
    
    def __init__(self, configuration_filename):
        self.configuration_filename = configuration_filename
        self.configuration = self.load_configuration()
        self.update = Signal(self.update_id, "signal: update", 's')
	if self.configuration:
            GPIBManagedServer.__init__(self)
    
    def load_configuration(self):
        configuration = __import__(self.configuration_filename).ServerConfig()
        for key, value in configuration.__dict__.items():
            setattr(self, key, value)
        return configuration

    @inlineCallbacks 
    def initServer(self):
        yield GPIBManagedServer.initServer(self)
        for name, conf in self.device_confs.items():
            for key, gpib_device_id in self.list_devices(None):
                if conf.gpib_device_id == gpib_device_id:
                    dev = self.devices[key]
                    dev.set_configuration(conf)
                    dev.set_defaults()

    @setting(9, 'select device by name', name='s', returns='s')    
    def select_device_by_name(self, c, name):
	gpib_device_id = self.device_confs[name].gpib_device_id
        yield self.select_device(c, gpib_device_id)
        dev = self.selectedDevice(c)
	confd = self.device_confs[name].__dict__
        returnValue(json.dumps(confd))

    @setting(10, 'state', state='b', returns='b')
    def state(self, c, state=None):
        dev = self.selectedDevice(c)
        if state is not None:
            yield dev.set_state(state)
        state = yield dev.get_state()
        yield self.send_update(c)
        returnValue(state)

    @setting(11, 'frequency', frequency='v', returns='v')
    def frequency(self, c, frequency=None):
        dev = self.selectedDevice(c)
        if frequency is not None:
            yield dev.set_frequency(frequency)
        frequency = yield dev.get_frequency()
        yield self.send_update(c)
        returnValue(frequency)

    @setting(12, 'amplitude', amplitude='v', returns='v')
    def amplitude(self, c, amplitude=None):
        dev = self.selectedDevice(c)
        if amplitude is not None:
            yield dev.set_amplitude(amplitude)
        amplitude = yield dev.get_amplitude()
        yield self.send_update(c)
        returnValue(amplitude)

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

    @setting(15, 'get system configuration', returns='s')
    def get_system_configuration(self, c):
        conf = self.load_configuration()
        return str(conf)

if __name__ == '__main__':
    configuration_name = '33500b_config'
    __server__ = AG33500BServer(configuration_name)
    from labrad import util
    util.runServer(__server__)

