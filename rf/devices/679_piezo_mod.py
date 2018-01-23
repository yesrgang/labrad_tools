from devices.dg1000z.dg1000z import DG1000Z

class PiezoMod679(DG1000Z):
    vxi11_address = '192.168.1.19'
    source = 2

    frequency_range = (1e-6, 5e3)
    amplitude_range = (0.0, 5.0)
    offset_range = (-10, 10)

    def initialize(self):
        DG1000Z.initialize(self)
        self.vxi11.write('SOUR2:FREQ 5e2')
        self.vxi11.write('SOUR2:VOLT 0.15')
        self.vxi11.write('SOUR2:VOLT:OFFS 0')
        self.vxi11.write('SOUR2:FUNC:RAMP:SYMM 50')
        self.vxi11.write('SOUR2:APPL:RAMP')
        self.vxi11.write('OUTP2:LOAD INF')
        self.vxi11.write('OUTP2:STAT 1')

__device__ = PiezoMod679
