class BetaRFConfig(object):
    def __init__(self):
        self.name = 'beta'
        self.server_name = 'yesr13_n5181a'
        self.state_id = 461013
        self.frequency_id = 461014
        self.power_id = 461015
        self.sweepstate_id = 461016
        self.sweeprate_id = 461017

        self.min_frequency = .25 # [MHz]
        self.max_frequency = 3e3
        self.frequency_stepsize = 1e-2
        self.min_power = -20. # [dBm]
        self.max_power = 0.
        self.power_stepsize = 0.1
        self.min_sweeprate = -1000
        self.max_sweeprate = 1000
        self.sweeprate_stepsize = 0.1 # [mHz/s]

        self.update_time = 10 # [ms]
        self.spinbox_width = 80 # [pixels]
        self.show_sweep = True
