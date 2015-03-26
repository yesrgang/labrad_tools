class PSUConfig(object):
    def __init__(self):
        self.name = 'psu0'
        self.server_name = 'yesr13_sorensen_psu'
        self.update_id = 461020
        
        self.current_decimals = 0
        self.voltage_decimals = 1

        self.update_time = 500 # [ms]
        self.spinbox_width = 80 # [pixels]
