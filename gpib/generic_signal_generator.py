
"""
### BEGIN NODE INFO
[info]
name = Generic Signal Generator
version = 1.0
description = 
instancename = %LABRADNODE% Generic Signal Generator

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""
import os
import numpy as np
from labrad.server import setting, Signal
from labrad.gpib import GPIBManagedServer, GPIBDeviceWrapper
from twisted.internet.defer import inlineCallbacks, returnValue
from influxdb import InfluxDBClient

class GenericSignalGeneratorWrapper(GPIBDeviceWrapper):
    def initialize(self):
        pass

    def set_configuration(self, configuration):
        self.configuration = configuration
        for key, value in configuration.__dict__.items():
            setattr(self, key, value)

    @inlineCallbacks
    def get_state(self):
        if hasattr(self, 'state_query'):
            ans = yield self.query(self.state_query)
            self.state = bool(int(ans))

    @inlineCallbacks
    def set_state(self, state):
        if hasattr(self, 'state_write'):
        	yield self.write(self.state_write.format(int(bool(state))))

    @inlineCallbacks
    def get_frequency(self):
        if hasattr(self, 'freq_query'):
            ans = yield self.query(self.freq_query)
            self.frequency = float(ans)

    @inlineCallbacks
    def set_frequency(self, frequency):
        if hasattr(self, 'freq_write'):
            yield self.write(self.freq_write.format(frequency))

    @inlineCallbacks
    def get_amplitude(self):
	if hasattr(self, 'ampl_query'):
            ans = yield self.query(self.ampl_query)
            self.amplitude = float(ans)

    @inlineCallbacks
    def set_amplitude(self, amplitude):
        if hasattr(self, 'ampl_write'):
            yield self.write(self.ampl_write.format(amplitude))


class GenericSignalGeneratorServer(GPIBManagedServer):
    """Provides basic control for Generic signal generators"""
    deviceWrapper = GenericSignalGeneratorWrapper
    
    def __init__(self, configuration_filename):
        self.configuration_filename = configuration_filename
        self.configuration = self.load_configuration()
        self.update_state = Signal(self.state_id, "signal: update_state", '(sb)')
        self.update_frequency = Signal(self.frequency_id, "signal: update_frequency", '(sv)')
        self.update_amplitude = Signal(self.amplitude_id, "signal: update_amplitude", '(sv)')
	dsn = os.getenv('INFLUXDBDSN')
	#self.dbclient = InfluxDBClient.from_DSN(dsn)
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
#	self.load_configuration()

    @setting(9, 'select device by name', name='s', returns='s')    
    def select_device_by_name(self, c, name):
	gpib_device_id = self.instruments[name].gpib_device_id
        yield self.select_device(c, gpib_device_id)
        dev = self.selectedDevice(c)
        dev.set_configuration(self.instruments[name])
	dev.instrument_name = name
	confd = self.instruments[name].__dict__
	if confd.has_key('dbpoint'):
            confd['dbpoint'] = None
        returnValue(str(confd))

    @setting(10, 'state', state='b', returns='b')
    def state(self, c, state=None):
        dev = self.selectedDevice(c)
        if state is not None:
            yield dev.set_state(state)
        yield dev.get_state()
        yield self.update_state((dev.instrument_name, dev.state))
        returnValue(dev.state)

    @setting(11, 'frequency', frequency='v', returns='v')
    def frequency(self, c, frequency=None):
        dev = self.selectedDevice(c)
        if frequency is not None:
            yield dev.set_frequency(frequency)
        yield dev.get_frequency()
        yield self.update_frequency((dev.instrument_name, dev.frequency))
	#self.dbclient.write_points(dev.dbpoint(dev.frequency))
        returnValue(dev.frequency)

    @setting(12, 'amplitude', amplitude='v', returns='v')
    def amplitude(self, c, amplitude=None):
        dev = self.selectedDevice(c)
        if amplitude is not None:
            yield dev.set_amplitude(amplitude)
        yield dev.get_amplitude()
        yield self.update_amplitude((dev.instrument_name, dev.amplitude))
        returnValue(dev.amplitude)

    @setting(14, 'request values')
    def request_values(self, c):
        yield self.state(c)
        yield self.frequency(c)
        yield self.amplitude(c)

    @setting(15, 'get system configuration', returns='s')
    def get_system_configuration(self, c):
        conf = self.load_configuration()
        return str(conf)
