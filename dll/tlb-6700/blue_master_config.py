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

        self.digital_lock_period = 1 # [s]
        self.get_dmm_str = "self.client._34980a.measure_channel('Blue Spec. Err.')"
        self.init_dmm_str = "self.client._34980a.select_device_by_name('srq monitor')"
        self.pid_sampling_interval = self.digital_lock_period
        self.pid_prop_gain = 1e-7
        self.pid_int_gain = 1e-7
        self.pid_min_max = (65, 90)



