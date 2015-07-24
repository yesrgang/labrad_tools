"""
### BEGIN NODE INFO
[info]
name = 34980A
version = 1.0
description = 
instancename = %LABRADNODE% 34980A

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

import numpy as np
from labrad.server import setting, Signal
from labrad.gpib import GPIBManagedServer, GPIBDeviceWrapper
from twisted.internet.defer import inlineCallbacks, returnValue
from influxdb import InfluxDBClient


class Agilent34980AWrapper(GPIBDeviceWrapper):
    def initialize(self):
        pass

    def set_configuration(self, configuration):
        self.configuration = configuration
        for key, value in configuration.__dict__.items():
            setattr(self, key, value)
    
    @inlineCallbacks
    def read_active_channels(self):
#        active_channels = {k: c for k, c in self.channels.items() if c.is_active}
#        self.channels is {
        values = []
        for address, channel in self.channels.items():
            if channel.is_active: 
                ans = yield self.query(channel.query_string + '(@{})'.format(str(address)))
		value = channel.ans_to_value(ans)
                values.append((channel.name, value))
        returnValue(values)


#    @inlineCallbacks
#    def get_state(self):
#        ans = yield self.query('OUTP:STAT?')
#	self.state = bool(int(ans))
#        returnValue(ans)
#
#    @inlineCallbacks
#    def set_state(self, state):
#        yield self.write('OUTP:STAT {}'.format(int(bool(state))))
#
#    @inlineCallbacks
#    def get_frequency(self):
#        ans = yield self.query('FREQ:CW?')
#	self.frequency = float(ans)
##        returnValue(float(ans)*1e-6) # keep things in MHz 
#
#    @inlineCallbacks
#    def set_frequency(self, frequency):
#        yield self.write('FREQ:CW {} Hz'.format(frequency))
#
#    @inlineCallbacks
#    def get_amplitude(self):
#        ans = yield self.query('POW:AMPL?')
#	self.amplitude = float(ans)
##        returnValue(float(ans))
#
#    @inlineCallbacks
#    def set_amplitude(self, amplitude):
#        yield self.write('POW:AMPL {} DBM'.format(amplitude))


class Agilent34980AServer(GPIBManagedServer):
    """Provides basic control for Agilent 34980A Multimeter"""
    deviceWrapper = Agilent34980AWrapper
    
    def __init__(self, configuration_filename):
        self.configuration_filename = configuration_filename
        self.configuration = self.load_configuration()
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

    @setting(9, 'select device by name', name='s', returns='s')    
    def select_device_by_name(self, c, name):
	gpib_device_id = self.instruments[name].gpib_device_id
        yield self.select_device(c, gpib_device_id)
        dev = self.selectedDevice(c)
        dev.set_configuration(self.instruments[name])
	dev.instrument_name = name
        returnValue(str(self.instruments[name].__dict__))

    @setting(10, 'read active channels', returns='*(sv)')
    def read_active_channels(self, c):
        dev = self.selectedDevice(c)
        values = yield dev.read_active_channels()
        influx_client = InfluxDBClient(**self.db_parameters)
        points = [{"measurement": "DMM", "tags": {"channel": name}, "fields": {"value": value}} for name, value in values]
        influx_client.write_points(points)
        returnValue(values)

#    @setting(10, 'state', state='b', returns='b')
#    def state(self, c, state=None):
#        dev = self.selectedDevice(c)
#        if state is not None:
#            yield dev.set_state(state)
#        yield dev.get_state()
#        yield self.update_state((dev.instrument_name, dev.state))
#        returnValue(dev.state)
#
#    @setting(11, 'frequency', frequency='v', returns='v')
#    def frequency(self, c, frequency=None):
#        dev = self.selectedDevice(c)
#        if frequency is not None:
#            yield dev.set_frequency(frequency)
#        yield dev.get_frequency()
#        yield self.update_frequency((dev.instrument_name, dev.frequency))
#        returnValue(dev.frequency)
#
#    @setting(12, 'amplitude', amplitude='v', returns='v')
#    def amplitude(self, c, amplitude=None):
#        dev = self.selectedDevice(c)
#        if amplitude is not None:
#            yield dev.set_amplitude(amplitude)
#        yield dev.get_amplitude()
#        yield self.update_amplitude((dev.instrument_name, dev.amplitude))
#        returnValue(dev.amplitude)
#
#    @setting(14, 'request values')
#    def request_values(self, c):
#        yield self.state(c)
#        yield self.frequency(c)
#        yield self.amplitude(c)

    @setting(15, 'get system configuration', returns='s')
    def get_system_configuration(self, c):
        conf = self.load_configuration()
        return str(conf)


if __name__ == '__main__':
    configuration_name = '34980a_config'
    __server__ = Agilent34980AServer(configuration_name)
    from labrad import util
    util.runServer(__server__)
