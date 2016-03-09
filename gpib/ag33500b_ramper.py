"""
### BEGIN NODE INFO
[info]
name = ag33500b_ramper
version = 1.0
description = 
instancename = ag33500b_ramper

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

class AG33500BConfiguration(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class ServerConfig(object):
    def __init__(self):
        self.update_id = 698016 
        self.name = 'ag33500b_ramper'
        self.deviceName = 'Agilent Technologies 33522B'
    	self.device_confs = {
            'clock drift': AG33500BConfiguration(
                source=1,
                gpib_device_id='yesr20 GPIB Bus - GPIB0::25',
                frequency_range=(20e6, 30e6),
                amplitude_range=(0, .5),
                delayed_call=None,
                t_ramp=8e3,
                get_counter_frequency=[
                    "self.client.yesr20_gpib_bus.address('GPIB0::23')",
                    "self.client.yesr20_gpib_bus.query('MEAS:FREQ? DEF, DEF, (@1)')"
                ],
                init_commands=[
                    "SOUR1:FUNC SIN",
                    "SOUR1:VOLT 500e-3",
                    "SOUR1:VOLT:OFFS 0",
                    "SOUR1:FREQ:MODE SWE",
                    "TRIG1:SOUR IMM",
                    "OUTP1 1",
                ]
            ),
        }
                       
if __name__ == '__main__':
    from ag33500b import *
    configuration_name = 'ag33500b_ramper'
    __server__ = AG33500BServer(configuration_name)
    from labrad import util
    util.runServer(__server__)
