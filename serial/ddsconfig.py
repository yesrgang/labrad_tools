import labrad.types as T

class DDS(object):
    def __init__(self, address, frequency, amplitude=1, clock_multiplier=15):
        self.address = address
        self.frequency = frequency
        self.amplitude = amplitude
        self.clock_multiplier = clock_multiplier



class DDSConfig(object):
    def __init__(self):
        self.serial_server_name = 'vagabond_serial_server'
        self.port = '/dev/ttyACM0'
        self.timeout = T.Value(1, 's')
        self.baudrate = 9600
        self.stopbits=1
        self.bytesize=8

        self.DDSs = {'dds0': DDS(0, 42e6),
                     'dds1': DDS(1, 20e6),
                     }
