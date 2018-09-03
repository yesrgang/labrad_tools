from devices.dg1000z.dg1000z import DG1000Z

class AlphaSpinPolAOM(DG1000Z):
    vxi11_address = '192.168.1.37'
    source = 1

    frequency_range = (1, 100e6)
    amplitude_range = (-20, 11)
    amplitude_units = 'dBm'

    update_parameters = ['state', 'amplitude', 'frequency']

    def initialize(self):
        DG1000Z.initialize(self)
        self.vxi11.write('SOUR1:FREQ 80e6')
        self.vxi11.write('SOUR1:VOLT 10')
        self.vxi11.write('SOUR1:VOLT:OFFS 0')
        self.vxi11.write('OUTP1:LOAD 50')
        self.vxi11.write('OUTP1:STAT 1')

__device__ = AlphaSpinPolAOM
