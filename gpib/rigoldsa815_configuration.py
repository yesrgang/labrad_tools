class RigolDSA815DeviceConfiguration(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class RigolDSA815Config(object):
    def __init__(self):
        self.update_id = 584272
        self.name = 'RigolDSA815'
        self.deviceName = 'Rigol Technologies DSA815'
    	self.device_configurations = {
            'Alpha Beta Beatnote': RigolDSA815DeviceConfiguration(
                gpib_device_id='yesr10 GPIB Bus - USB0::0x1AB1::0x0960::DSA8B175300897',
                update_period=1.,
                init_commands=[
                    ":SENS:FREQ:SPAN 20e6",
                ],
            ),
        }
