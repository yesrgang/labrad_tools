import labrad.types as T

from devices.ad9854 import AD9854

class ServerConfig(object):
    def __init__(self):
        self.name = 'dds'

        self.devices = {
            '813_x_aom': AD9854(
                serial_server_name = 'yesr20_serial',
                port = 'COM6',
                address=0,
                frequency=112.5e6, # [Hz]
                ),
            
            '813_y_aom': AD9854(
                serial_server_name = 'yesr20_serial',
                port = 'COM6',
                address=1,
                frequency=115e6, # [Hz]
		),
            
            '813_z_aom': AD9854(
                serial_server_name = 'yesr20_serial',
                port = 'COM6',
                address=2,
                frequency=113.75e6, # [Hz]
                ),
            
            'hodt_aom': AD9854(
                serial_server_name = 'yesr20_serial',
                port = 'COM6',
                address=3,
                frequency=30e6, # [Hz]
                ),
            
            'vodt_aom': AD9854(
                serial_server_name = 'yesr20_serial',
                port = 'COM6',
                address=4,
                frequency=30.2e6, # [Hz]
                ),
            
            'dimple_aom': AD9854(
                serial_server_name = 'yesr20_serial',
                port = 'COM6',
                address=5,
                frequency=25.6e6, # [Hz]
                ),
            }
