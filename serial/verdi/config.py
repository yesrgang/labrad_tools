import labrad.types as T

class V18(object):
    def __init__(self, **kwargs):
        self.timeout = T.Value(1, 's')
        self.baudrate = 19200
        self.stopbits=1
        self.bytesize=8
        self.delayed_calls = []
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])


class VerdiConfig(object):
    def __init__(self):
        self.verdi = {
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
