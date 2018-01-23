from twisted.internet.defer import inlineCallbacks, returnValue
import vxi11

from server_tools.device_server import Device

class AG335xxx(Device):
    vxi11_address = None
    source = None
    
    state = None

    amplitude = None
    amplitude_range = None

    frequency = None
    frequency_range = None

    update_parameters = ['state', 'frequency', 'amplitude']

    def initialize(self):
        self.vxi11 = vxi11.Instrument(self.vxi11_address)
        self.do_update_parameters()

    def do_update_parameters(self):
        self.state = self.get_state()
        self.frequency = self.get_frequency()
        self.amplitude = self.get_amplitude()

    def set_state(self, state):
        command = 'OUTP{}:STAT {}'.format(self.source, int(bool(state)))
        self.vxi11.write(command)

    def get_state(self):
        command = 'OUTP{}?'.format(self.source)
        ans = self.vxi11.ask(command)
        return bool(int(ans))

    def set_frequency(self, frequency):
        frequency = sorted([min(self.frequency_range), 
            max(self.frequency_range), frequency])[1]
        command = 'SOUR{}:FREQ {}'.format(self.source, frequency)
        self.vxi11.write(command)

    def get_frequency(self):
        command = 'SOUR{}:FREQ?'.format(self.source)
        ans = self.vxi11.ask(command)
        return float(ans)

    def set_amplitude(self, amplitude):
        amplitude = sorted([min(self.amplitude_range), 
            max(self.amplitude_range), amplitude])[1]
        command = 'SOUR{}:VOLT {} dBm'.format(self.source, amplitude)
        self.vxi11.write(command)

    def get_amplitude(self):
        command = 'SOUR{}:VOLT?'.format(self.source)
        ans = self.vxi11.ask(command)
        return float(ans)
