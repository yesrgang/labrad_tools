import vxi11

from server_tools.device_server import Device

class N5181A(Device):
    vxi11_address = None
    
    state = None

    amplitude = None
    amplitude_range = None
    amplitude_units = 'dB'

    frequency = None
    frequency_range = None

    update_parameters = ['state', 'frequency', 'amplitude']

    def initialize(self):
        self.vxi11 = vxi11.Instrument(self.vxi11_address)
        self.do_update_parameters()

    def do_update_parameters(self):
        for parameter in self.update_parameters:
            getattr(self, 'get_{}'.format(parameter))()

    def set_state(self, state):
        command = 'OUTP:STAT {}'.format(int(bool(state)))
        self.vsi11.write(command)

    def get_state(self):
        ans = self.vxi11.ask('OUTP:STAT?')
        return bool(int(ans))
    
    def set_frequency(self, frequency):
        command = 'FREQ:CW {} Hz'.format(frequency)
        self.vxi11.write(command)

    def get_frequency(self):
        ans = self.vxi11.ask('FREQ:CW?')
        return float(ans) # keep things in MHz 

    def set_amplitude(self, amplitude):
        command = 'POW:AMPL {} {}'.format(amplitude, self.amplitude_units)
        self.vxi11.write(command)

    def get_amplitude(self):
        ans = self.vxi11.ask('POW:AMPL?')
        return float(ans)

