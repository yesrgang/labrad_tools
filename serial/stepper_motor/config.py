import labrad.types as T

class SilverPack17(object):
    def __init__(self, **kwargs):
        self.timeout = T.Value(1, 's')
        self.baudrate = 9600
        self.stopbits=1
        self.bytesize=8
        self.serial_connection = None
        
        self.init_commands = [
            '/1m30h10R\r' # current
            '/1V1000L500R\r' # velocity and acceleration
            '/1j256o1500R\r' # step resolution
        ]
        
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])

    def move_absolute_str(self, position):
        return '/1A{}R\r'.format(position)


class ServerConfig(object):
    def __init__(self):
        self.name = '%LABRADNODE%_stepper_motor'

        self.devices = {
            'nd filter': SilverPack17(
                serial_server_name='yesr5_serial_server',
                port='COM6',
            ),
        }
