class DeviceConfiguration(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class ServerConfig(object):
    def __init__(self):
        self.state_id = 698016 
	self.frequency_id = 698017
	self.amplitude_id = 698018
        self.name = '%LABRADNODE% DS345'
        self.deviceName = 'StanfordResearchSystems DS345'
    	self.instruments = {
                            'Spin Pol. AOM': DeviceConfiguration(
				                         gpib_device_id='yesr10 GPIB Bus - GPIB0::21',
                                                         def_state=True, 
                                                         def_frequency=20.06e6,
                                                         def_amplitude=5,
                                                         frequency_range=(10e6, 30e6),
							 amplitude_range=(-36, 10),
                                                        )
                           }
                       
