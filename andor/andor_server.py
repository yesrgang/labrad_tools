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
import json
import sys

from labrad.server import Signal, setting

from server_tools.device_server import DeviceServer

UPDATE_ID = 693334

class AndorServer(DeviceServer):
    """ Provides control of andor cameras """
    update = Signal(UPDATE_ID, 'signal: update', 's')
    name = '%LABRADNODE%_andor'

    @setting(10, record_path='ss', record_type='s', recorder_config='s', returns='b')
    def record(self, c, record_path, record_type, recorder_config='{}'):
        """ record 
        Args:
            record_path: list, first element is day's folder, second element is filename
            record_type: string, type of image to record
            recorder_config: json dumped dict, kwargs to be passed to recorder class' init
        Returns:
            bool, success
        """
        device = self.get_device(c)
        device.record(record_path, record_type, recorder_config)
        return True
    
    @setting(11, settings_json='s', returns='s')
    def get_sums(self, c, settings_json):
        """ sum atom numbers using defined regions
        Args:
            settings_json: json dumped dict e.g.
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
        settings = json.loads(settings_json)
        sums = device.process(settings)
        return json.dumps(sums)

if __name__ == "__main__":
    from labrad import util
    util.runServer(AndorServer())
