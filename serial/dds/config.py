import labrad.types as T

class AD9854(object):
    def __init__(self, **kwargs):
        self.timeout = T.Value(1, 's')
        self.baudrate = 4800
        self.stopbits=1
        self.bytesize=8
        self.init_commands = []
        
        self.freg = int(0x02)
        self.areg = int(0x08)
        self.amplitude_range = (0, 1)
        self.amplitude = 1
        self.state = True
        self.frequency_range=(1e3, 140e6)
        self.sysclk=300e6
        self.update_parameters = ['state', 'frequency', 'amplitude']

        for kw in kwargs:
            setattr(self, kw, kwargs[kw])
    
    def ftw(self):
        ftw = hex(int(self.frequency*2.**32/self.sysclk))[2:].zfill(8) # 32-bit dac
        return [int('0x'+ftw[i:i+2], 0) for i in range(0, 8, 2)]

    def atw(self):
        atw =  hex(int(self.amplitude*(2**12-1)))[2:].zfill(4)
        return [int('0x'+atw[i:i+2], 0) for i in range(0, 4, 2)] + [0, 0]

class ServerConfig(object):
    def __init__(self):
        self.name = 'dds'

        self.devices = {
            '813 x AOM': AD9854(
                serial_server_name = 'yesr20_serial_server',
                port = 'COM6',
                address=0,
                frequency=112.5e6, # [Hz]
                ),
            
            '813 y AOM': AD9854(
                serial_server_name = 'yesr20_serial_server',
                port = 'COM6',
                address=1,
                frequency=115e6, # [Hz]
		),
            
            '813 z AOM': AD9854(
                serial_server_name = 'yesr20_serial_server',
                port = 'COM6',
                address=2,
                frequency=113.75e6, # [Hz]
                ),
            
            'HODT AOM': AD9854(
                serial_server_name = 'yesr20_serial_server',
                port = 'COM6',
                address=3,
                frequency=30e6, # [Hz]
                ),
            
            'VODT AOM': AD9854(
                serial_server_name = 'yesr20_serial_server',
                port = 'COM6',
                address=4,
                frequency=30.2e6, # [Hz]
                ),
            
            'dimple AOM': AD9854(
                serial_server_name = 'yesr20_serial_server',
                port = 'COM6',
                address=5,
                frequency=25.6e6, # [Hz]
                ),
            }
