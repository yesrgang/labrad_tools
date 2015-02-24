class N5181AConfig(object):
	def __init__(self, gpib_device_id, def_state, def_frequency, def_amplitude, sweep_rate, sweep_state):
		self.gpib_device_id = gpib_device_id
		self.def_state = def_state
		self.def_frequency = def_frequency # [MHz]
		self.def_amplitude = def_amplitude
		self.sweep_rate = sweep_rate
		self.sweep_state = sweep_state

class ServerConfig(object):
    def __init__(self):
    	self.device_name = 'Agilent Technologies N5181A'
    	self.device_dict = {
    						'beta': N5181AConfig('yesr13 GPIB Bus - GPIB0::2', True, 101.98, -13.0, 0.0, False),
    						}

        self.sweep_dwell = 1 # [s]
