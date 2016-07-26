import time
import json
import numpy as np

from labrad.server import setting, Signal
from labrad.gpib import GPIBManagedServer, GPIBDeviceWrapper
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet import reactor


class RigolDSA815Wrapper(GPIBDeviceWrapper):
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
    def get_data(self, channel=1):
        """Channel 1 is alpha, channel 2 is beta"""
        if channel == 1:
            # alpha
            yield self.write(':SENS:FREQ:SPAN 20e6')
            yield self.write(':SENS:FREQ:CENT 100.96e6')
        else:
            # beta
            yield self.write(':SENS:FREQ:SPAN 20e6')
            yield self.write(':SENS:FREQ:CENT 1.36226e9')
            
        # Get data
        rawdata = yield self.query(':TRACe:DATA? TRACE1')
        data = [float(x) for x in rawdata[12:].split(',')]
        
        # Get frequency points from center and span
        center = yield self.query(':SENS:FREQ:CENT?')
        span = yield self.query(':SENS:FREQ:SPAN?')
        
        f = np.linspace(float(center) - 0.5*float(span),
                        float(center) + 0.5*float(span),
                        len(data)).tolist()
        
        returnValue ( (f, data) )
        

class RigolDSA815Server(GPIBManagedServer):
    """Control Rigol DSA815"""
    deviceWrapper = RigolDSA815Wrapper
    update = Signal(914526, "signal: update", 's')

    def __init__(self, configuration_filename):
        self.configuration_filename = configuration_filename
        self.load_configuration()
        # self.update = Signal(self.update_id, "signal: update", 's')
        GPIBManagedServer.__init__(self)
    
    def load_configuration(self):
        self.configuration = __import__(self.configuration_filename).RigolDSA815Config()
        for key, value in self.configuration.__dict__.items():
            setattr(self, key, value)
        return self.configuration

    @inlineCallbacks
    def initServer(self):
        yield GPIBManagedServer.initServer(self)

    @setting(9, 'select device by name', name='s', returns='s')    
    def select_device_by_name(self, c, name=None):
        if name is not None:
            conf = self.device_configurations[name]
            gpib_device_id = conf.gpib_device_id
            yield self.select_device(c, gpib_device_id)
            dev = self.selectedDevice(c)
            dev.set_configuration(conf)
            confd = self.device_configurations[name].__dict__
            returnValue(json.dumps(confd))
        else:
            returnValue(json.dumps(self.device_configurations.keys()))

    @setting(10, 'get data', returns='s')
    def get_data(self, c):
        dev = self.selectedDevice(c)
        f_alpha, data_alpha = yield dev.get_data(1)
        f_beta, data_beta = yield dev.get_data(2)
        json_string = json.dumps({'f_alpha': f_alpha,
                                  'data_alpha': data_alpha,
                                  'f_beta': f_beta,
                                  'data_beta': data_beta,
                                  })
        yield self.update(json_string)
        returnValue(json_string)
    
    @inlineCallbacks
    def get_data_forever(self, c, channel):
        # yield self.get_data(c, channex1l)
        
        reactor.callLater(self.update_period, self.get_data_forever, *[c, channel])
        
    @setting(11, 'start loop', channel='i', returns='s')
    def start_loop(self, c, channel):
        self.running_loop = yield self.get_data_forever(channel, c)
        
    # @setting(12, 'stop loop', channel='i', returns='s')
    # def stop_loop(self):
    #     running_loop.cancel()
        
    # @setting(12, 'send update')
    # def send_update(self, c):
    #     dev = self.selectedDevice(c)
    #     update_d = {}
    #     for param in dev.update_parameters:
    #         try:
    #             value = yield getattr(dev, 'get_'+param)()
    #             update_d[param] = value
    #         except AttributeError:
    #             print 'device has no attribute get_{}'.format(param)
    #     self.update(json.dumps(update_d))

    @setting(13, 'get system configuration')
    def get_system_configuration(self, c):
        conf =  self.load_configuration()
        return json.dumps(conf.__dict__)
    
    @setting(14, 'get device configuration', device_name='s')
    def get_device_configuration(self, c, device_name):
        conf = self.load_configuration()
	return json.dumps(conf.device_configurations(device_name).__dict__)

if __name__ == '__main__':
    configuration_name = 'rigoldsa815_configuration'
    __server__ = RigolDSA815Server(configuration_name)
    from labrad import util
    util.runServer(__server__)
