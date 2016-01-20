class PSUConfig(object):
    def __init__(self):
        self.name = 'AH PSU' 
        self.server_name = 'sorensen_psu'
        self.update_id = 461020
        
        self.current_decimals = 0
        self.current_units = [(0, 'A')]
        self.voltage_decimals = 0
        self.voltage_units = [(0, 'V')]

        self.update_time = 500 # [ms]
        self.spinbox_width = 80 # [pixels]
