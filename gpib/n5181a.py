"""
### BEGIN NODE INFO
[info]
name = n5181a
version = 1.0
description = 
instancename = n5181a

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

from hpetc_signal_generator import HPSignalGeneratorServer

class DeviceConfiguration(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class ServerConfig(object):
    def __init__(self):
        self.state_id = 698013 
	self.frequency_id = 698014
	self.amplitude_id = 698015
        self.name = 'n5181a'
        self.deviceName = 'Agilent Technologies N5181A'
    	self.instruments = {
        'beta': DeviceConfiguration(
            gpib_device_id='yesr10 GPIB Bus - GPIB0::19::INSTR',
            def_state=True, 
            def_frequency=101.5e6,
            def_amplitude=6.,
            frequency_range=(10e3, 200e6),
            amplitude_range=(-20, 20),
            measurement='red MOT detunings',
            detuning='beta phase lock offset',
            )
        }
        
        for inst in self.instruments.values():
            if hasattr(inst, 'measurement'):
                inst.dbpoint = lambda f: [{"measurement": inst.measurement, 
                    "tags": {'detuning': inst.detuning}, 
                    "fields": {"value": f}}]

if __name__ == '__main__':
    configuration_name = 'n5181a'
    __server__ = HPSignalGeneratorServer(configuration_name)
    from labrad import util
    util.runServer(__server__)
