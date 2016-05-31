"""
### BEGIN NODE INFO
[info]
name = ag33500b_stepper
version = 1.0
description = 
instancename = ag33500b_stepper

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
        self.name = 'ag33500b_stepper'
        self.deviceName = 'Agilent Technologies 33522B'
    	self.device_confs = {
            'clock steer': AG33500BConfiguration(
                gpib_device_id='yesr20 GPIB Bus - GPIB0::25::INSTR',
                source=2,
                frequency_range=(20e6, 30e6),
                amplitude_range=(0, .5),
                update_parameters=['frequency'],
                init_commands=[
                    "SOUR2:FUNC SIN",
                    "SOUR2:FREQ:MODE CW",
                    "SOUR2:FREQ 27.1792e6",
                    "SOUR2:VOLT 500e-3",
                    "SOUR2:VOLT:OFFS 0",
                    "OUTP2 1",
                ]

            ),
        }
                       
if __name__ == '__main__':
    from ag33500b import *
    configuration_name = 'ag33500b_stepper'
    __server__ = AG33500BServer(configuration_name)
    from labrad import util
    util.runServer(__server__)
