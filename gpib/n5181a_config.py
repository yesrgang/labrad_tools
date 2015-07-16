class DeviceConfiguration(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class ServerConfig(object):
    def __init__(self):
        self.state_id = 698013 
	self.frequency_id = 698014
	self.amplitude_id = 698015
        self.name = '%LABRADNODE% N5181A'
        self.deviceName = 'Agilent Technologies N5181A'
    	self.instruments = {
                       'beta': DeviceConfiguration(gpib_device_id='yesr10 GPIB Bus - GPIB0::19',
                                            def_state=True, 
                                            def_frequency=101.5,
                                            def_amplitude=6.),
                       }
