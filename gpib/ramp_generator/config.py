from device_configs import DS345, HPSignalGenerator

class ServerConfig(object):
    def __init__(self):
    	self.devices = {
            'clock drift': AG335XXXRamp(
                gpib_server_name='yesr20_gpib_bus',
                address='GPIB0::25::INSTR',
                source=1,
                amplitude_units='V',
                frequency_range=(20e3, 30e6),
                amplitude_range=(0, .5),
                counter_server_name='yesr20_gpib_bus',
                counter_address='GPIB0::23::INSTR',
                counter_channel='1',
                init_commands=[
                    "SOUR1:FUNC SIN",
                    "SOUR1:VOLT 500e-3",
                    "SOUR1:VOLT:OFFS 0",
                    "OUTP1 1",
                ],
            ),
        }
