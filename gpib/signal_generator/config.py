from device_configs import DS345, HPSignalGenerator, AG335XXX

class ServerConfig(object):
    def __init__(self):
    	self.devices = {
            'Spin Pol. AOM': DS345(
                gpib_server_name='yesr10_gpib_bus',
                address='GPIB0::21::INSTR',
                state=True, 
                frequency=20.07e6,
                amplitude=6,
                amplitude_units='DB',
                frequency_range=(1, 30e6),
                amplitude_range=(-36, 20),
            ),
            'beta': HPSignalGenerator(
                gpib_server_name='yesr10_gpib_bus',
                address='GPIB0::19::INSTR',
                state=True, 
                frequency=100.28e6,
                amplitude=6,
                amplitude_units='DB',
                frequency_range=(10e3, 200e6),
                amplitude_range=(-20, 20),
            ),
            'alpha': HPSignalGenerator(
                gpib_server_name='yesr10_gpib_bus',
                address='GPIB0::20::INSTR',
                state=True, 
                frequency=1.3629e9,
                amplitude=6,
                amplitude_units='DB',
                frequency_range=(250e3, 3e9),
                amplitude_range=(-20, 20),
            ),
            'clock steer': AG335XXX(
                gpib_server_name='yesr20_gpib_bus',
                address='GPIB0::25::INSTR',
                source=2,
                state=True, 
                frequency=27.33e6,
                amplitude=.5,
                amplitude_units='V',
                frequency_range=(20e3, 30e6),
                amplitude_range=(0, .5),
                init_commands=[
                    "SOUR2:FUNC SIN",
                    "SOUR2:FREQ:MODE CW",
                    "SOUR2:VOLT 500e-3",
                    "SOUR2:VOLT:OFFS 0",
                    "OUTP2 1",
                ],
            ),
        }
