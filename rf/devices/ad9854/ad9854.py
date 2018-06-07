from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import Device
from lib.helpers import get_instruction_set
from lib.helpers import sleep

class AD9854(Device):
    serial_server_name = None
    serial_address = None
    serial_timeout = 0.5
    serial_baudrate = 4800
    
    address = None

    sysclk = 300e6
    freg = int(0x02)
    areg = int(0x08)
    
    state = True
    
    amplitude = None
    default_amplitude = 1
    amplitude_range = (0, 1)
    
    frequency = None
    default_frequency = 80e6
    frequency_range=(1e3, 140e6)

    update_parameters = ['state', 'frequency', 'amplitude']

    def make_ftw(self, frequency):
        ftw = hex(int(frequency * 2.**32 / self.sysclk))[2:].zfill(8) # 32-bit dac
        return [int('0x' + ftw[i:i+2], 0) for i in range(0, 8, 2)]

    def make_atw(self, amplitude):
        atw =  hex(int(amplitude * (2**12 - 1)))[2:].zfill(4)
        return [int('0x'+atw[i:i+2], 0) for i in range(0, 4, 2)] + [0, 0]

    @inlineCallbacks
    def initialize(self):
        yield self.connect_labrad()
        self.serial_server = yield self.cxn[self.serial_server_name]
        yield self.serial_server.select_interface(self.serial_address)
#        yield sleep(2)
        yield self.serial_server.timeout(self.serial_timeout)
        yield self.serial_server.baudrate(self.serial_baudrate)

        yield self.set_frequency(self.default_frequency)
        yield self.set_amplitude(self.default_amplitude)
    
    def set_state(self, state):
        pass

    def get_state(self):
        return True

    @inlineCallbacks
    def set_frequency(self, frequency):
        ftw = self.make_ftw(frequency)
        for b in get_instruction_set(self.subaddress, self.freg, ftw):
            yield self.serial_server.write(b)
        ans = yield self.serial_server.read_line()
        if ans != 'Roger that!':
            message = 'Error writing {} frequency'.format(self.name)
            #raise Exception(message)
            print ans
            print message
        else:
            print ans
        self.frequency = frequency

    def get_frequency(self):
        return self.frequency
        
    @inlineCallbacks
    def set_amplitude(self, amplitude):
        atw = self.make_atw(amplitude)
        for b in get_instruction_set(self.subaddress, self.areg, atw):
            yield self.serial_server.write(b)
        ans = yield self.serial_server.read_line()
        if ans != 'Roger that!':
            message = 'Error writing {} amplitude'.format(self.name)
#            raise Exception(message)
            print ans
            print message
        else:
            print ans
        self.amplitude = amplitude

    def get_amplitude(self):
        return self.amplitude

