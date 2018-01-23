from devices.dg1000z.dg1000z import DG1000Z

class ClockDetune(DG1000Z):
    vxi11_address = '192.168.1.5'
    source = 2

    frequency_range = (1e0, 60e6)
    amplitude_range = (0.0, 1.0)
    default_amplitude = 0.5

    def initialize(self):
        DG1000Z.initialize(self)
        self.vxi11.write('OUTP2:LOAD 50')
        self.set_amplitude(self.default_amplitude)

__device__ = ClockDetune
