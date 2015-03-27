"""
### BEGIN NODE INFO
[info]
name = Red Master DDS
version = 1.0
description = 
instancename = %LABRADNODE% Red Master DDS

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""
from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.server import Signal
from labrad.types import Error
import labrad.types as T
from twisted.internet import reactor
from twisted.internet.defer import returnValue
from twisted.internet.task import LoopingCall
import time


class DDSServer(SerialDeviceServer):
    name = '%LABRADNODE% DDS Server'

#    update_state = Signal(self.state_id, 'signal: update_state', '(sb)')
#    update_frequency = Signal(self.frequency_id, 'signal: update_frequency', '(sv)')
#    update_power = Signal(self.power_id, 'signal: update_power', '(sv)')
#    update_sweepstate = Signal(self.sweepstate_id, 'signal: update_sweepstate', '(sb)')
#    update_sweeprate = Signal(self.sweeprate_id, 'signal: update_sweeprate', '(sv)')

    def __init__(self, config_name):
        SerialDeviceServer.__init__(self)
        self.config_name = config_name
        self.load_configuration()
        self.update_values = Signal(self.update_id, 'signal: update values', '(sbvvbv)')
    
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
    
    @inlineCallbacks
    def notify_listeners(self, name):
        d = self.dds[name]
        yield self.update_values((name, d.state, d.frequency, d.amplitude, d.sweepstate, d.sweeprate))

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
        return True

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

    @setting(5, 'sweepstate', name='s', state='b', returns='b')
    def sweepstate(self, c, name, state=None):
        if state is None:
            state = self.dds[name].sweepstate
        else:
            self.dds[name].sweepstate = state
        yield self.notify_listeners(name)
        returnValue(state)

    @setting(6, 'sweeprate', name='s', rate='v', returns='v')
    def sweeprate(self, c, name, rate=None):
        if rate is None:
            rate = self.dds[name].sweeprate
        else:
            self.dds[name].sweeprate = rate
            f = open(self.name.replace(' ', '_') + '_sweeps.txt', 'a')
            f.write(str({name: [dds.frequency, dds.sweeprate, time.time()] for name, dds in self.dds.items()})+'\n')
        yield self.notify_listeners(name)
        returnValue(rate)

    @inlineCallbacks
    def _sweep(self):
        for name in self.dds.keys():
            if self.dds[name].sweepstate:
                f = yield self.frequency(None, name)
                f += self.dds[name].sweeprate*self.sweep_dwell
                yield self.frequency(None, name, f)

    @setting(7, 'request values', name='s')
    def request_values(self, c, name):
        yield self.notify_listeners(name)

config_name = 'redmasterdds_config'
__server__ = DDSServer(config_name)

if __name__ == "__main__":
    from labrad import util
    util.runServer(__server__)
