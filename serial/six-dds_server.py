import labrad.types as T

class AD9854(object):
    def __init__(self, **kwargs): #address, frequency, amplitude=1, clock_multiplier=24):
        self.freg = int(0x02) #int(0x0b)
        self.areg = int(0x08) #int(0x0c)
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])
    
    def ftw(self):
        ftw = hex(int(self.frequency*2.**32/self.sysclk))[2:].zfill(8) # 32-bit dac
        return [int('0x'+ftw[i:i+2], 0) for i in range(0, 8, 2)]

    def atw(self):
        atw =  hex(int(self.amplitude*(2**12-1)))[2:].zfill(4)
        return [int('0x'+atw[i:i+2], 0) for i in range(0, 4, 2)] + [0, 0]

class DDSConfig(object):
    def __init__(self):
        self.name = '%LABRADNODE% 6DDS'
        self.serial_server_name = 'yesr20_serial_server'
        self.port = 'COM6'
        self.timeout = T.Value(1, 's')
        self.baudrate = 4800
        self.stopbits=1
        self.bytesize=8

        self.update_id = 698017
        self.dds = {
            '813 x AOM': AD9854(
                address=0,
                state=True,
                frequency=88.75e6, # [Hz]
                frequency_range=(1e3, 140e6), # [Hz]
                amplitude=1,
                amplitude_range=(0, 1),
                sysclk=300e6,
                update_parameters=['state', 'frequency', 'amplitude']
                ),
            
            '813 y AOM': AD9854(
                address=1,
                state=True,
                frequency=91.25e6, # [Hz]
                frequency_range=(1e3, 140e6), # [Hz]
                amplitude=1,
                amplitude_range=(0, 1),
                sysclk=300e6,
                update_parameters=['state', 'frequency', 'amplitude'],
		),
            
            '813 z AOM': AD9854(
                address=2,
                state=True,
                frequency=90e6, # [Hz]
                frequency_range=(1e3, 140e6), # [Hz]
                amplitude=1,
                amplitude_range=(0, 1),
                sysclk=300e6,
                update_parameters=['state', 'frequency', 'amplitude'],
                ),
            
            'HODT AOM': AD9854(
                address=3,
                state=True,
                frequency=30e6, # [Hz]
                frequency_range=(1e3, 140e6), # [Hz]
                amplitude=1,
                amplitude_range=(0, 1),
                sysclk=300e6,
                update_parameters=['state', 'frequency', 'amplitude'],
                ),
            
            'VODT AOM': AD9854(
                address=4,
                state=True,
                frequency=30.2e6, # [Hz]
                frequency_range=(1e3, 140e6), # [Hz]
                amplitude=1,
                amplitude_range=(0, 1),
                sysclk=300e6,
                update_parameters=['state', 'frequency', 'amplitude'],
                ),
            
            'dimple AOM': AD9854(
                address=5,
                state=True,
                frequency=25.6e6, # [Hz]
                frequency_range=(1e3, 140e6), # [Hz]
                amplitude=1,
                amplitude_range=(0, 1),
                sysclk=300e6,
                update_parameters=['state', 'frequency', 'amplitude'],
                ),
            }
