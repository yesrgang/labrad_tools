class DeviceConfig(object):
#	def __init__(self, gpib_device_id, def_state, def_frequency, def_amplitude, sweep_rate, sweep_state):
#		self.gpib_device_id = gpib_device_id
#		self.def_state = def_state
#		self.def_frequency = def_frequency # [MHz]
#		self.def_amplitude = def_amplitude
#		self.sweep_rate = sweep_rate
#		self.sweep_state = sweep_state
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class ServerConfig(object):
    def __init__(self):
        self.name = '%LABRADNODE% N5181A'
        self.deviceName = 'Agilent Technologies N5181A'
    	self.devices = {
                       'beta': DeviceConfig(gpib_device_id='yesr10 GPIB Bus - GPIB0::19',
                                            def_state=True, 
                                            def_frequency=101.5,
                                            def_amplitude=6.),
                       }
