from twisted.internet.defer import inlineCallbacks

from hp_signal_generator.hp_signal_generator import HPSignalGenerator


class Alpha(HPSignalGenerator):
    gpib_server_name = 'yesr9_gpib'
    gpib_address = 'GPIB0::19::INSTR'

    frequency_range = (250e3, 3e9)
    amplitude_range = (-20, 20)

    @inlineCallbacks
    def initialize(self):
        yield HPSignalGenerator.initialize(self)
        yield self.gpib_server.write('FM1:DEV 2e6')
        yield self.set_amplitude(10)
        yield self.set_state(True)

__device__ = Alpha
