from devices.v18 import V18

class ServerConfig(object):
    def __init__(self):
        self.devices = {
            'm2 pump': V18(
                serial_server_name='yesr20_serial',
                port='COM8',
                power_range=(0, 18), # [W]
                init_power=16, # [W]
                full_power=18, # [W]
                shutter_delay=5*60, # [s]
                full_power_delay=30*60, # [s]
                )
        }
