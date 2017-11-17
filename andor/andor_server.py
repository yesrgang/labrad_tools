"""
### BEGIN NODE INFO
[info]
name = andor
version = 1.0
description = 
instancename = %LABRADNODE%_andor

[startup]
cmdline = %PYTHON% %FILE%
timeout = 60

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""
import sys

from labrad.server import Signal, setting

from server_tools.device_server import DeviceServer

UPDATE_ID = 693334

class AndorServer(DeviceServer):
    """ Provides control of andor cameras """
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = '%LABRADNODE%_andor'

    @setting(10, 'record', record_name="s", record_type="s", recorder_config="s", returns='b')
    def record(self, c, record_name="", record_type="", recorder_config='{}'):
        """ record 
        Args:
            record_name: string
            record_type: string
            recorder_config: json dumped dict
        Returns:
            bool
        """
        device = self.get_device(c)
        device.record(record_name, record_type, recorder_config)
        return True
    
    @setting(11, 'get_sums', settings='s', returns='s')
    def get_sums(self, c, settings):
        """ sum atom numbers using defined regions
        Args:
            settings: json dumped dict e.g.
                {
                    'name': 'andor',
                    'offset': (525, 192),
                    'size': (200, 200),
                    'roi': {
                        'all': [30, 30, 0, 0],
                        'center': [7, 7, 0, 0],        
                        },
                    'norm': (0, 0, 60, 80),
                } 
        Returns:
            json dumped dict of summed counts in each roi
            {
                'all': {
                    'n_g': x,
                    'n_e': y,
                    'frac': z,
                    }
            }
        """
        device = self.get_device(c)
        device.process(settings)
        return True

if __name__ == "__main__":
    from labrad import util
    util.runServer(AndorServer())
