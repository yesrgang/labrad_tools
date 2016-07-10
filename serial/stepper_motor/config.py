from devices.silver_pack_17 import SilverPack17

class ServerConfig(object):
    def __init__(self):
        self.name = 'stepper_motor'

        self.devices = {
            'nd filter': SilverPack17(
                serial_server_name='yesr5_serial',
                port='COM6',
            ),
        }
