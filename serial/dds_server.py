from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.server import Signal
from labrad.types import Error
import labrad.types as T
from twisted.internet import reactor
from twisted.internet.defer import returnValue
from twisted.internet.task import LoopingCall
import json
import time


class DDSServer(SerialDeviceServer):
    name = '%LABRADNODE% DDS Server'

    def __init__(self, configuration):
        super(DDSServer, self).__init__()
        self.load_configuration(configuration)
        self.update = Signal(self.update_id, 'signal: update', '(s)')
    
    @inlineCallbacks
    def initServer(self):
        try:
            yield self.init_serial(self.serial_server_name, self.port)
#            self.sweeping = LoopingCall(self._sweep)
#            self.sweeping.start(self.sweep_dwell)
        except SerialConnectionError, e:
            self.serial_server = None
            if e.code == 0:
                print 'Could not find serial server for node: {}'.format(self.node_server)
                print 'Please start correct serial server'
            elif e.code == 1:
                print 'Error opening serial connection'
                print 'Check set up and restart serial server'
            else: 
                raise
    
    def load_configuration(self, configuration):
        #config = __import__(self.config_name).DDSConfig()
        for key, value in configuration.__dict__.items():
            setattr(self, key, value)
    
    @inlineCallbacks
    def notify_listeners(self, name):
        d = self.dds[name]
        values = dict([('name', name)] + [(param, getattr(d, param)) for param in d.update_parameters])
        yield self.update(json.dumps(values))

    @setting(1, 'select device by name', name='s')
    def select_device_by_name(self, c, name):
        return str(self.dds[name].__dict__)

    def checksum(self, ins):
        checksum = sum(ins[1:])
        checksum_bin = bin(checksum)[2:].zfill(8)
        checksum_lowestbyte = checksum_bin[-8:]
        return int('0b'+str(checksum_lowestbyte), 0)

    def instruction_set(self, address, register, data):
        ins = [58, address, len(data)+1, register] + data
        ins.append(self.checksum(ins))
        return [chr(i) for i in ins]

    @setting(2, 'state', name='s', state='b')
    def state(self, c, name, state=None):
        yield self.notify_listeners(name)
        returnValue(True)

    @setting(3, 'frequency', name='s', frequency='v', returns='v')
    def frequency(self, c, name, frequency=None):
        if frequency is None:
            frequency = self.dds[name].frequency
        else:
            self.dds[name].frequency = frequency
        for c in self.instruction_set(self.dds[name].address, self.dds[name].freg, self.dds[name].ftw()):
            yield self.serial_server.write(c)
        yield self.notify_listeners(name)
        returnValue(frequency)
    
    @setting(4, 'amplitude', name='s', amplitude='v', returns='v')
    def amplitude(self, c, name, amplitude=None):
        if amplitude is None:
            amplitude = self.dds[name].amplitude
        else:
            self.dds[name].amplitude = amplitude
        for c in self.instruction_set(self.dds[name].address, self.dds[name].areg, self.dds[name].atw()):
            self.serial_server.write(c)
        yield self.notify_listeners(name)
        returnValue(amplitude)

    @setting(7, 'request values', name='s')
    def request_values(self, c, name):
        yield self.notify_listeners(name)
