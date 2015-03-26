from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.server import Signal
from labrad.types import Error
import labrad.types as T
from twisted.internet import reactor
from twisted.internet.defer import returnValue
import time

STATE_ID = 698007
FREQUENCY_ID = 698008
POWER_ID = 698009

CLKIN = 20e6 # [MHz]

class DDSServer(SerialDeviceServer):
    name = '%LABRADNODE% DDS'

    update_state = Signal(STATE_ID, 'signal: update_state', 'b')
    update_frequency = Signal(FREQUENCY_ID, 'signal: update_frequency', 'v')
    update_power = Signal(POWER_ID, 'signal: update_power', 'v')
    
    def initServer(self):
      	self.get_configuration(None)
        self.init_serial(self.serial_server_name, self.ports)
    
    @setting(1, 'get configuration', returns='s')
    def get_configuration(self, c):
        from ddsconfig import DDSConfig
        config = DDSConfig()
        for key, value in config.__dict__.items():
            setattr(self, key, value)
        return str(config.__dict__)

    def _check_sum(self, ins):
        checksum = sum(ins[1:])
        checksum_bin = bin(checksum)[2:].zfill(48)
        checksum_lowestbyte = checksum_bin[40:]
        return int('0b'+str(checksum_lowestbyte), 0)

    def instruction_set(self, address, register, data):
        ins = [58, address, len(data)+1, register] + data
        ins = ins + [self._check_sum(ins)]
        return [chr(i) for i in ins]


    def _ftw(self, frequency, clk=300e6):
        return hex(int(frequency*2**48/clk))[2:].zfill(12) #48-bit dac
    
    @setting(2, 'frequency', name='s', frequency='v', returns='v')
    def frequency(self, c, name, frequency=None):
        if frequency is None:
            frequency = self.DDSs[name].frequency
        else:
            data = [int('0x'+self._ftw(frequency, CLKIN*self.DDSs[name].clock_multiplier)[i:i+2], 0) for i in range(0, 12, 2)]
            for c in self.instruction_set(self.DDSs[name].address, 2, data):
                self.serial_server.write(c)
            self.DDSs[name].frequency = frequency
        return frequency

    def _atw(self, amplitude):
        return hex(int(amplitude*(2**12-1)))[2:].zfill(4)
    
    @setting(3, 'amplitude', name='s', amplitude='v', returns='v')
    def amplitude(self, c, name, amplitude=None):
        if amplitude is None:
            amplitude = self.DDSs[name].amplitude
        else:
            data = [int('0x'+self._atw(amplitude)[i:i+2], 0) for i in range(0, 4, 2)]
            for c in self.instruction_set(self.DDSs[name].address, 8, data):
                self.serial_server.write(c)
            self.DDSs[name].amplitude = amplitude
        return amplitude

    @setting(4, 'clock multiplier', name='s', multiplier='i', returns='i')
    def clock_multiplier(self, c, name, multiplier=None):
        if multiplier == None:
            multiplier = self.DDSs[name].clock_multiplier
        else:
            multiplier = sorted([4, multiplier, 20])[1]
            data = [16, multiplier, 0, 33]
            for c in self.instruction_set(self.DDSs[name].address, 7, data):
                self.serial_server.write(c)
            self.DDSs[name].clock_multiplier = multiplier
        return multiplier

    @setting(5, 'request values', name='s')
    def request_values(self, c, name):
        yield self.frequency(c, name)
        yield self.amplitude(c, name)

    @setting(6, 'state', name='s')
    def state(self, c, name):
        return True
#
#
#    
#if __name__ == "__main__":
#    from labrad import util
#    util.runServer(DDSServer())
