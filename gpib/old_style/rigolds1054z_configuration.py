class RigolDS1054ZDeviceConfiguration(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class RigolDS1054ZConfig(object):
    def __init__(self):
        self.update_id = 686692
        self.name = 'RigolDS1054Z'
        self.deviceName = 'RIGOL TECHNOLOGIES DS1054Z'
    	self.device_configurations = {
            '813 Cavity': RigolDS1054ZDeviceConfiguration(
                gpib_device_id='yesr20 GPIB Bus - USB0::0x1AB1::0x04CE::DS1ZA175022846',
                update_period=1.,
                init_commands=[
                    ":WAV:POIN:MODE NOR",
                    ":WAV:FORM ASC",
                ],
            ),
        }
