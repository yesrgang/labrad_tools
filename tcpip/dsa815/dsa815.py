"""
### BEGIN NODE INFO
[info]
name = dsa815
version = 1.0
description = 
instancename = dsa815

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""


from labrad.server import LabradServer, setting
from vxi11 import Instrument
import os.path, json, re

class DSA815Server(LabradServer):
    """
    DSA815 (Rigol 1.5 GHz spectrum analyzer) LabRAD server
    """
    name = 'dsa815'

    def __init__(self, config_path='./config.json'):
        self.config = self.load_config(config_path)
        LabradServer.__init__(self)

    def initServer(self):
        host = self.config['host']
        instrument = Instrument(host)
        self.instrument = instrument

    def stopServer(self):
        self.instrument.close()

    @setting(0, 'reset', returns='b')
    def reset(self, c):
        """
        Reset the device
        """
        self.instrument.write('*RST')
        return True

    @setting(1, 'get_trace', trace='i', returns='*v[]')
    def get_trace(self, c, trace=1):
        """
        Get data points of trace <n>
        """
        self.assert_arg_range(trace, (1, 4))

        raw_data = self.instrument.ask(':TRACe:DATA? TRACE%i' % trace)
        values_str = re.compile('^#[0-9]+\s(.+)$').match(raw_data).group(1)
        raw_values = values_str.split(', ')

        return [float(s) for s in raw_values]

    @setting(2, 'get_range', returns='*v[]')
    def get_range(self, c):
        """
        Get start and stop frequency
        """
        start = float(self.instrument.ask(':SENSe:FREQuency:STARt?'))
        stop = float(self.instrument.ask(':SENSe:FREQuency:STOP?'))

        return [start, stop]

    @setting(3, 'set_range', rng='*v[]', returns='b')
    def set_range(self, c, rng):
        """
        Set start and stop frequency given by <rng>
        """
        self.assert_arg_length(rng, 2)

        start, stop = rng
        self.instrument.write(':SENSe:FREQuency:STARt %i' % start)
        self.instrument.write(':SENSe:FREQuency:STOP %i' % stop)

        return True

    @setting(4, 'get_rbw', returns='v')
    def get_rbw(self, c):
        """
        Get the resolution bandwidth
        """
        rbw = self.instrument.ask(':SENSe:BANDwidth:RESolution?')

        return float(rbw)

    @setting(5, 'set_rbw', rbw='v', returns='b')
    def set_rbw(self, c, rbw):
        """
        Set the resolutin bandwidth
        """
        self.instrument.write(':SENSe:BANDwidth:RESolution %i' % rbw)

        return True

    @staticmethod
    def load_config(path):
        if (not os.path.isfile(path)):
            raise Exception('DSA815Server: Could not find configuration (%s).', config_path)

        f = open(path, 'r')
        json_data = f.read()
        f.close()

        return json.loads(json_data)

    @staticmethod
    def assert_arg_range(arg, rng):
        minimum, maximum = rng

        if (arg > maximum or arg < minimum):
            raise ValueError('Value must be between %i and %i' % (minimum, maximum))

    @staticmethod
    def assert_arg_length(arg, length):
        if (len(arg) > length):
            raise ValueError('Value must be of length %i' % length)


if __name__ == '__main__':
    from labrad import util

    server = DSA815Server()
    util.runServer(server)
