import struct
from twisted.internet.defer import inlineCallbacks, returnValue

from server_tools.device_server import Device
from lib.helpers import get_instruction_set


class AD9959(Device):
    serial_server_name = None
    serial_address = None
    serial_timeout = 0.05
    serial_baudrate = 9600
    
    board_num = None
    channel_num = None

    sysclk = 500e6

    csreg = int(0x00)
    cfreg = int(0x03)
    freg = int(0x04)
    areg = int(0x06)
    lsrr_reg = int(0x07)
    rdw_reg = int(0x08)
    fdw_reg = int(0x09)
    
    state = True
    
    amplitude = None
    default_amplitude = 1
    amplitude_range = [0, 1]
    
    frequency = None
    default_frequency = 0e6
    frequency_range = [0, sysclk / 2]

    update_parameters = ['state', 'frequency', 'amplitude']
    
    def make_csw(self):
        if self.channel > 3:
            message = 'channel {} is not in range [0, 3]'.format(self.channel)
            raise Exception(message)
        return [(2**int(self.channel) << 4) + 2]

    def make_cfw(self, mode):
        cfw = [None, None, None]
        if mode == 'frequency':
            afp = 0b10
            linear_sweep_no_dwell = 0b0
            linear_sweep_enable = 0b1
        elif mode == 'amplitude':
            afp = 0b01
            linear_sweep_no_dwell = 0b0
            linear_sweep_enable = 0b1
        elif mode == 'phase':
            afp = 0b11
            linear_sweep_no_dwell = 0b0
            linear_sweep_enable = 0b1
        else:
            afp = 0b00
            linear_sweep_no_dwell = 0b0
            linear_sweep_enable = 0b0

        cfw[0] = (afp << 6)
        cfw[1] = (linear_sweep_no_dwell << 7) + (linear_sweep_enable << 6) + 0x03
        cfw[2] = 0x0
        return cfw

    def make_ftw(self, frequency):
        ftw = hex(int(frequency * 2.**32 / self.sysclk))[2:].zfill(8) # 32-bit dac
        return [int('0x' + ftw[i:i+2], 0) for i in range(0, 8, 2)]

    def make_atw(self, amplitude):
        asf = bin(int(amplitude * (2**10 - 1)))[2:].zfill(10)
        part_1 = int(asf[:2], 2)
        part_2 = int(asf[2:], 2)
        return [0] + [16 + part_1] + [part_2]
    
    def make_lsrrw(self, rate):
        t_step = max(-rate, 1)
#        print t_step
        return [t_step, t_step]
#        return list(struct.unpack('4b', struct.pack('I', step_size))[::-1])
    
    def make_rdw(self, rate):
        step_size = max(rate, 1)
#        print 'rdw', list(struct.unpack('4b', struct.pack('I', step_size))[::-1])
        return list(struct.unpack('4b', struct.pack('I', step_size))[::-1])

    def make_fdw(self, rate):
        step_size = max(rate, 1)
        return list(struct.unpack('4b', struct.pack('I', step_size))[::-1])
    
    @inlineCallbacks
    def set_linear_ramp(self, start=None, stop=None, rate=None):
        csw = self.make_csw()
        if start is not None:
            cfw = self.make_cfw('frequency')
            ftw_start = self.make_ftw(start)
            ftw_stop = self.make_ftw(stop)
            instruction_set = (
                get_instruction_set(self.board_num, self.csreg, csw)
                + get_instruction_set(self.board_num, self.cfreg, cfw)
                + get_instruction_set(self.board_num, self.freg, ftw_start)
                + get_instruction_set(self.board_num, int(0x0A), ftw_stop)
                )
            yield self.serial_server.write(''.join(instruction_set))
#            print '({}, {}) upd freqs'.format(self.board_num, self.channel_num)

        if rate is not None: 
            lsrrw = self.make_lsrrw(rate)
            rdw = self.make_rdw(rate)
            fdw = self.make_fdw(rate)
        
            instruction_set = (
                get_instruction_set(self.board_num, self.csreg, csw)
                + get_instruction_set(self.board_num, self.lsrr_reg, lsrrw)
                + get_instruction_set(self.board_num, self.rdw_reg, rdw)
                + get_instruction_set(self.board_num, self.fdw_reg, fdw)
                )
        
            yield self.serial_server.write(''.join(instruction_set))

    @inlineCallbacks
    def initialize(self):
        yield self.connect_labrad()
        self.serial_server = yield self.cxn[self.serial_server_name]
        yield self.serial_server.select_interface(self.serial_address)
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
        csw = self.make_csw()
        ftw = self.make_ftw(frequency)
        instruction_set = (
            get_instruction_set(self.board_num, self.csreg, csw)
            + get_instruction_set(self.board_num, self.freg, ftw)
            )
        
        yield self.serial_server.write(''.join(instruction_set))
       
        self.frequency = frequency

    def get_frequency(self):
        return self.frequency
        
    @inlineCallbacks
    def set_amplitude(self, amplitude):
        csw = self.make_csw()
        atw = self.make_atw(amplitude)
        instruction_set = (
            get_instruction_set(self.board_num, self.csreg, csw)
            + get_instruction_set(self.board_num, self.areg, atw)
            )
        
        yield self.serial_server.write(''.join(instruction_set))

        self.amplitude = amplitude

    def get_amplitude(self):
        return self.amplitude
    
