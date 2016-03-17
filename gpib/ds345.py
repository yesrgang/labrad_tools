"""
### BEGIN NODE INFO
[info]
name = ds345
version = 1.0
description = 
instancename = ds345

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

from srs_signal_generator import SRSSignalGeneratorServer

class DeviceConfiguration(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class ServerConfig(object):
    def __init__(self):
        self.state_id = 698016 
        self.frequency_id = 698017
        self.amplitude_id = 698018
        self.name = 'ds345'
        self.deviceName = 'StanfordResearchSystems DS345'
    	self.instruments = {
            'Spin Pol. AOM': DeviceConfiguration(
                gpib_device_id='yesr10 GPIB Bus - GPIB0::21',
                def_state=True, 
                def_frequency=20.06e6,
                def_amplitude=5,
                frequency_range=(10e6, 30e6),
                amplitude_range=(-36, 10),
            ),
                            
            'Clock AOM Kill': DeviceConfiguration(
                gpib_device_id='yesr20 GPIB Bus - GPIB0::21',
                def_state=True, 
                def_frequency=27.15e6,
                def_amplitude=-2,
                frequency_range=(1, 30e6),
                amplitude_range=(-36, 20),
            ),
        }
if __name__ == '__main__':
    configuration_name = 'ds345'
    __server__ = SRSSignalGeneratorServer(configuration_name)
    from labrad import util
    util.runServer(__server__)  
