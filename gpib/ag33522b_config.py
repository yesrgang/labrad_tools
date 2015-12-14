class AG33522BConfiguration(object):
    def __init__(self, **kwargs):
        self.state_query = 'OUTP:STAT?'
	self.state_write = 'OUTP:STAT {}'
	self.freq_query = 'FREQ:CW?'
	self.freq_write = 'FREQ:CW {} Hz'
	self.ampl_query = 'VOLT?'
	self.ampl_write = 'VOLT {} DBM'
        for key, value in kwargs.items():
            setattr(self, key, value)

class ServerConfig(object):
    def __init__(self):
        self.state_id = 698016 
	self.frequency_id = 698017
	self.amplitude_id = 698018
        self.name = 'ag33522b'
        self.deviceName = 'Agilent Technologies 33522B'
    	self.instruments = {
                            'red probe': AG33522BConfiguration(
                                                        gpib_device_id='yesr10 GPIB Bus - GPIB0::18',
                                                        def_state=True, 
                                                        def_frequency=101.5e6,
                                                        def_amplitude=6.,
                                                        frequency_range=(10e3, 200e6),
							amplitude_range=(-20, 20),
                                                        measurement='red MOT detunings',
							detuning='red probe',
							
							)
			    }
        
	for inst in self.instruments.values():
            if hasattr(inst, 'measurement'):
		    inst.dbpoint = lambda f: [{"measurement": inst.measurement, 
                                                "tags": {'detuning': inst.detuning}, 
                                                "fields": {"value": f}}]
