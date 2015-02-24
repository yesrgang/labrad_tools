class BetaRFConfig(object):
    def __init__(self):
        self.name = 'dds0'
        self.server_name = 'vagabond_dds_server'
        self.state_id = 461013
        self.frequency_id = 461014
        self.power_id = 461015
        self.sweepstate_id = 461016
        self.sweeprate_id = 461017

        self.min_frequency = .1 # [MHz]
        self.max_frequency = 120.
        self.frequency_stepsize = 1e-2
        self.min_power = 0 # rel
        self.max_power = 1
        self.power_stepsize = 0.01

        self.update_time = 10 # [ms]
        self.spinbox_width = 80 # [pixels]
        self.show_sweep = True
