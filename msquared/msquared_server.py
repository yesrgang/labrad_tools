"""
### BEGIN NODE INFO
[info]
name = msquared
version = 1.0
description = 
instancename = msquared

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

from labrad.server import LabradServer, setting
from lib.msquared_connection import MSquaredConnection
import os.path
import json

class MSquaredServer(LabradServer):
    """
    M-squared LabRAD server
    """
    name = 'msquared'

    def __init__(self, config_path='./config.json'):
        self.config = self.load_config(config_path)

        LabradServer.__init__(self)

    @staticmethod
    def load_config(path):
        if (not os.path.isfile(path)):
            raise Exception('MSquaredServer: Could not find configuration (%s).', config_path)

        f = open(path, 'r')
        json_data = f.read()
        f.close()

        return json.loads(json_data)

    def initServer(self):
        host = self.config['host']
        port = self.config['port']
        addr = (host, port)

        connection = MSquaredConnection(addr, debug=True)
        ok = connection.open()
        if (not ok):
            raise Exception('MSquaredServer: Could not connect to M-squared laser. Make '
                            'sure you enabled remote control in the laser control panel.')

        self.connection = connection

    def stopServer(self):
        self.connection.close()

    @setting(0, 'force_reconnect')
    def force_reconnect(self, c, returns='b'):
        """
        Close and open socket connection to M-squared ICE module
        """
        self.connection.close()
        return self.connection.open()

    @setting(1, 'get_system_status', returns='s')
    def get_system_status(self, c):
        """
        Obtain the system status (left panel).

        M-squared command name: get_status
        """
        response = self.connection.get('get_status')

        if (response):
            for key, value in response.iteritems():
                if (value == 'off'): response[key] = False
                if (value == 'on'): response[key] = True
            return json.dumps(response)
        else:
            return response

    @setting(2, 'set_etalon_lock', on='b', returns='b')
    def set_etalon_lock(self, c, on):
        """
        This command puts the etalon lock on or off.

        M-squared command name: etalon_lock
        """
        ok = self.connection.set('etalon_lock', 'on' if on else 'off', key_name='operation')
        return ok

    @setting(3, 'get_etalon_lock', returns='b')
    def get_etalon_lock(self, c):
        """
        This command gets the current status of the etalon lock.

        M-squared command name: etalon_lock_status
        """
        response = self.connection.get('etalon_lock_status')

        if (response):
            return response['condition'] == 'on'
        else:
            return response

    @setting(4, 'set_etalon_tune', percentage='v', returns='b')
    def set_etalon_tune(self, c, percentage):
        """
        This command adjusts the etalon tuning.

        M-squared command name: tune_etalon
        """
        percentage = float(percentage)
        self.assert_arg_range(percentage, (0, 100))

        ok = self.connection.set('tune_etalon', percentage)
        return ok

    @setting(5, 'set_resonator_tune', percentage='v', returns='b')
    def set_resonator_tune(self, c, percentage):
        """
        This command adjusts the resonator tuning.

        M-squared command name: tune_resonator
        """
        percentage = float(percentage)
        self.assert_arg_range(percentage, (0, 100))

        ok = self.connection.set('tune_resonator', percentage)
        return ok

    @setting(6, 'set_resonator_fine_tune', percentage='v', returns='b')
    def set_resonator_fine_tune(self, c, percentage):
        """
        This command adjusts the resonator fine tuning.

        M-squared command name: fine_tune_resonator
        """
        percentage = float(percentage)
        self.assert_arg_range(percentage, (0, 100))

        ok = self.connection.set('fine_tune_resonator', percentage)
        return ok

    @staticmethod
    def assert_arg_range(arg, rng):
        minimum, maximum = rng

        if (arg > maximum or arg < minimum):
            raise ValueError('Value must be between %s and %s' % (minimum, maximum))

if __name__ == '__main__':
    from labrad import util

    server = MSquaredServer()
    util.runServer(server)
