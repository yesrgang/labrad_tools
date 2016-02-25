import numpy as np
import json
from labrad.server import setting, Signal
from labrad.gpib import GPIBManagedServer, GPIBDeviceWrapper
from twisted.internet.defer import inlineCallbacks, returnValue

class SRSSignalGeneratorWrapper(GPIBDeviceWrapper):
    def initialize(self):
        pass

    def set_configuration(self, configuration):
        self.configuration = configuration
        for key, value in configuration.__dict__.items():
            setattr(self, key, value)

    @inlineCallbacks
    def get_frequency(self):
        ans = yield self.query('FREQ?')
        self.frequency = float(ans)

    @inlineCallbacks
    def set_frequency(self, frequency):
        yield self.write('FREQ {}'.format(frequency))

    @inlineCallbacks
    def get_amplitude(self):
        ans = yield self.query('AMPL?')
        self.amplitude = float(ans[:-2])

    @inlineCallbacks
    def set_amplitude(self, amplitude):
        yield self.write('AMPL {}DB'.format(amplitude))


class SRSSignalGeneratorServer(GPIBManagedServer):
    """Provides basic control for SRS signal generators"""
    deviceWrapper = SRSSignalGeneratorWrapper
    
    def __init__(self, configuration_filename):
        self.configuration_filename = configuration_filename
        self.configuration = self.load_configuration()
        self.update_state = Signal(self.state_id, "signal: update_state", '(sb)')
        self.update_frequency = Signal(self.frequency_id, "signal: update_frequency", '(sv)')
        self.update_amplitude = Signal(self.amplitude_id, "signal: update_amplitude", '(sv)')
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
    def select_device_by_name(self, c, name=None):
        if not name:
            returnValue(json.dumps(self.instruments.keys()))
    	gpib_device_id = self.instruments[name].gpib_device_id
        yield self.select_device(c, gpib_device_id)
        dev = self.selectedDevice(c)
        dev.set_configuration(self.instruments[name])
        dev.instrument_name = name
        returnValue(str(self.instruments[name].__dict__))

    @setting(10, 'state', state='b', returns='b')
    def state(self, c, state=None):
        dev = self.selectedDevice(c)
	dev.state = True
        yield self.update_state((dev.instrument_name, dev.state))
        returnValue(dev.state)

    @setting(11, 'frequency', frequency='v', returns='v')
    def frequency(self, c, frequency=None):
        dev = self.selectedDevice(c)
        if frequency is not None:
            yield dev.set_frequency(frequency)
        yield dev.get_frequency()
        yield self.update_frequency((dev.instrument_name, dev.frequency))
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


#if __name__ == '__main__':
#    configuration_name = 'hpetc_signal_generator_config'
#    __server__ = SRSSignalGeneratorServer(configuration_name)
#    from labrad import util
#    util.runServer(__server__)
