class LDC340DeviceConfiguration(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class LDC340Config(object):
    def __init__(self):
        self.update_id = 698024
        self.name = 'ldc340'
        self.deviceName = 'PROFILE LDC340'
    	self.device_configurations = {
            '707': LDC340DeviceConfiguration(
                gpib_device_id='yesr10 GPIB Bus - GPIB0::10',
                current_range=(0, .1),
                dial_steps=20,
                def_current=.08,
                update_parameters=['current', 'power', 'state'],
            ),
        }
