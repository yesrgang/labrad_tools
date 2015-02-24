from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.server import Signal
from labrad.types import Error
import labrad.types as T
from twisted.internet import reactor
from twisted.internet.defer import returnValue
import time


class DDSServer(SerialDeviceServer):
    name = '%LABRADNODE% DDS Server'

    update_state = Signal(self.state_id, 'signal: update_state', '(sb)')
    update_frequency = Signal(self.frequency_id, 'signal: update_frequency', '(sv)')
    update_power = Signal(self.power_id, 'signal: update_power', '(sv)')

    def __init__(self, config_name):
        self.config_name = config_name
        self.load_configuration()
        super(DDSServer,  self).__init__()
    
    @inlineCallbacks
    def initServer(self):
        try:
            yield self.init_serial(self.serial_server_name, self.port)
            self.sweeping = LoopingCall(self._sweep)
            self.sweeping.start(self.sweep_dwell)
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
    
    def load_configuration(self):
        config = __import__(self.config_name).DDSConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)

    @setting(1, 'select device by name', name='s')
    def select_device_by_name(self, c, name):
        return str(self.dds[name].__dict__)

    def checksum(self, ins):
        checksum = sum(ins[1:])
        checksum_bin = bin(checksum)[2:].zfill(32)
        checksum_lowestbyte = checksum_bin[-8:]
        return int('0b'+str(checksum_lowestbyte), 0)

    def instruction_set(self, address, register, data):
        ins = [58, address, len(data)+1, register] + data
        ins.append(self.checksum(ins))
        return [chr(i) for i in ins]

    @setting(2, 'state', name='s', state='b')
    def state(self, c, name, state=None):
        return True

    @setting(3, 'frequency', name='s', frequency='v', returns='v')
    def frequency(self, c, name, frequency=None):
        if frequency is None:
            frequency = self.dds[name].frequency
        else:
            self.dds[name].frequency = frequency
        for c in self.instruction_set(self.dds[name].address, int(0x0b), self.dds[name].ftw()):
            yield self.serial_server.write(c)
        yield self.update_frequency((name, frequency))
        returnValue(frequency)
    
    @setting(4, 'amplitude', name='s', amplitude='v', returns='v')
    def amplitude(self, c, name, amplitude=None):
        if amplitude is None:
            amplitude = self.dds[name].amplitude
        else:
            self.dds[name].amplitude = amplitude
        for c in self.instruction_set(self.dds[name].address, int(0x0c), self.dds[name].atw()):
            self.serial_server.write(c)
        yield self.update_amplitude((name, amplitude))
        returnValue(amplitude)

    @setting(5, 'sweep state', name='s', state'b', returns='b')
    def sweep_state(self, c, name, state):
        if state is None:
            state = self.dds[name].sweep_state
        else:
            self.dds[name].sweep_state = state
        yield self.update_sweepstate((name, state))
        returnValue(state)

    @setting(6, 'sweep rate', name='s', rate='v', returns='v')
    def sweep_rate(self, c, name, rate):
        if rate is None
            rate = self.dds[name].sweep_rate
        else:
            self.dds[name].sweep_rate = rate
        yield self.update_sweeprate((name, rate))
        returnValue(rate)

    @inlineCallbacks
    def _sweep(self):
        for name in self.dds.keys():
            if self.dds[name].sweep_state:
                f = yield self.frequency(None, name)
                f += self.dds[name].sweep_rate*self.sweep_dwell
                yield self.frequency(None, name, f)

#    @setting(7, 'request values', name='s')
#    def request_values(self, c, name):
#        yield self.frequency(c, name)
#        yield self.amplitude(c, name)
#        yield self.state(c, name)

