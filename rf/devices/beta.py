from devices.ag335xxx.ag335xxx import AG335xxx

class Beta(AG335xxx):
    vxi11_address = "192.168.1.3"
    source = 1
    
    amplitude_units = 'dBm'
    amplitude_range = (-20, 20)
    
    frequency_range = (250e3, 120e6)

    def initialize(self):
        AG335xxx.initialize(self)
        self.vxi11.write('SOUR1:VOLT:UNIT dBm')
        self.vxi11.write('SOUR1:FM:DEV 10e6')
        self.vxi11.write('SOUR1:FM:SOUR EXT')
        self.vxi11.write('INP:ATT ON')
        self.vxi11.write('SOUR1:FM:STAT ON')

__device__ = Beta
