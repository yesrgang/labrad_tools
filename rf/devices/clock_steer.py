from devices.ag335xxx.ag335xxx import AG335xxx

class ClockSteer(AG335xxx):
    vxi11_address = "192.168.1.18"
    source = 2
    
    amplitude_units = 'V'
    amplitude_range = (0, 0.5)
    
    frequency_range = (20e3, 30e6)

    def initialize(self):
        AG335xxx.initialize(self)
        self.vxi11.write('SOUR2:FUNC SIN')
        self.vxi11.write('SOUR2:FREQ:MODE CW')
        self.vxi11.write('SOUR2:VOLT 500e-3')
        self.vxi11.write('SOUR2:VOLT:OFFS 0')
        self.vxi11.write('OUTP2 1')

__device__ = ClockSteer
