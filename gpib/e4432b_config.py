class DeviceConfiguration(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class ServerConfig(object):
    def __init__(self):
        self.state_id = 698013 
	self.frequency_id = 698014
	self.amplitude_id = 698015
        self.name = '%LABRADNODE% E4432B'
        self.deviceName = 'Hewlett-Packard ESG-D3000B'
    	self.instruments = {
                            'alpha': DeviceConfiguration(
				                         gpib_device_id='yesr10 GPIB Bus - GPIB0::20',
                                                         def_state=True, 
                                                         def_frequency=1.3615e6,
                                                         def_amplitude=6,
                                                         frequency_range=(250e3, 3e9),
							 amplitude_range=(-20, 20),
                                                        )
                           }
                       
