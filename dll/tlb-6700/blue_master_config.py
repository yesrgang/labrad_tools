class ServerConfig(object):
    def __init__(self):
        self.name = '%LABRADNODE% TLB-6700'
        self.update_id = 698022
        self.dll_filename = 'usbdll.dll'
        self.max_buffer_length = 64
	
	self.current_range = (0., 160.)
	self.default_current = 157.0
	self.ramp_duration = 3.0
	self.ramp_points = 30
	
	self.voltage_range = (0., 100.)

