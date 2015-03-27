import labrad.types as T

class V18(object):
    def __init__(self, **kwargs):
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])


class VerdiConfig(object):
    def __init__(self):
        self.serial_server_name = 'yesr12_serial_server'
        self.port = '/dev/ttyUSB0'
        self.timeout = T.Value(1, 's')
        self.baudrate = 19200
        self.stopbits=1
        self.bytesize=8

        self.update_id = 698005

        self.verdi = {
                      'SolsTiS Pump': V18(state=None,
                                          shutter_state=None,
                                          power=None,
                                          power_range=(0, 18), # [W]
                                          current=None)
                      }
