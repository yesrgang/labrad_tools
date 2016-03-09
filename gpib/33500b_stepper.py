class AG33500BConfiguration(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class ServerConfig(object):
    def __init__(self):
        self.update_id = 698016 
        self.name = '33500B'
        self.deviceName = 'Agilent Technologies 33522B'
    	self.device_confs = {
#            'clock drift': AG33500BConfiguration(
#                source=1,
#                gpib_device_id='yesr20 GPIB Bus - GPIB0::25',
#                frequency_range=(20e6, 30e6),
#                amplitude_range=(0, .5),
#                delayed_call=None,
#                t_ramp=8e3,
##                get_counter_frequency=[
##                    "self.client.53220a.select_device_by_name('drift counter')",
##                    "self.client.53220a.get_frequency()"
##                ]
#                get_counter_frequency=[
#                    "self.client.yesr20_gpib_bus.address('GPIB0::23')",
#                    "self.client.yesr20_gpib_bus.query('MEAS:FREQ? DEF, DEF, (@1)')"
#                ],
#                init_commands=[
#                    "SOUR1:FUNC SIN",
#                    "SOUR1:VOLT 500e-3",
#                    "SOUR1:VOLT:OFFS 0",
#                    "SOUR1:FREQ:MODE SWE",
#                    "TRIG1:SOUR IMM",
#                    "OUTP1 1",
#                ]
#            ),
            'clock steer': AG33500BConfiguration(
                gpib_device_id='yesr20 GPIB Bus - GPIB0::25',
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
