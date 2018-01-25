from twisted.internet.defer import inlineCallbacks, returnValue
import vxi11

from server_tools.device_server import Device

class AG335xxx(Device):
    vxi11_address = None
    source = None

    waveforms = None

    update_parameters = []

    def initialize(self):
        self.vxi11 = vxi11.Instrument(self.vxi11_address)
        command = 'SOUR{}:DATA:VOL:CLE'.format(self.source)
        self.vxi11.write(command)
        for waveform in self.waveforms:
            command = 'MMEM:LOAD:DATA{} "{}"'.format(self.source, waveform)
            self.vxi11.write(command)
            command = 'SOUR{}:FUNC:ARB "{}"'.format(self.source, waveform)
            self.vxi11.write(command)

    def set_waveform(self, waveform):
        if waveform not in self.waveforms:
            message = 'waveform "{}" not configured'.format(waveform)
            raise Exception(message)
        command = 'SOUR{}:FUNC:ARB "{}"'.format(self.source, waveform)
        self.vxi11.write(command)

    def get_waveform(self):
        command = 'SOUR{}:FUNC:ARB?'.format(self.source)
        ans = self.vxi11.ask(command)
        return ans
