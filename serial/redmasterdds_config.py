import labrad.types as T

class AD9915(object):
    def __init__(self, **kwargs): #address, frequency, amplitude=1, clock_multiplier=24):
        self.freg = int(0x0b)
        self.areg = int(0x0c)
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])
    
    def ftw(self):
        ftw = hex(int(self.frequency*2**32/self.sysclk))[2:].zfill(8) # 32-bit dac
        return [int('0x'+ftw[i:i+2], 0) for i in range(0, 8, 2)]

    def atw(self):
        atw =  hex(int(self.amplitude*(2**12-1)))[2:].zfill(4)
        return [int('0x'+atw[i:i+2], 0) for i in range(0, 4, 2)] + [0, 0]


class DDSConfig(object):
    def __init__(self):
        self.name = '%LABRADNODE% Red Master DDS'
        self.serial_server_name = 'yesr20_serial_server'
        self.port = 'COM7'
        self.timeout = T.Value(1, 's')
        self.baudrate = 9600
        self.stopbits=1
        self.bytesize=8

        self.update_id = 698017
        self.sweep_updateperiod = 60 # [s]

        self.dds = {
                     'red master': AD9915(address=0,
                                          state=True,
                                          frequency=300e6, # [Hz]
                                          frequency_range=(1e3, 1e9), # [Hz]
                                          amplitude=1,
                                          amplitude_range=(0, 1),
                                          sysclk=2.4e9),
                     }
