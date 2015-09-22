class SixDDSConfig(object):
    def __init__(self):
        self.name = 'dds0'
        self.server_name = 'yers20_6dds'
        self.update_id = 461017 

        self.frequency_stepsize = 1e-2
        self.frequency_units = 1e6 # [MHz]
        self.amplitude_stepsize = 0.01
        self.sweeprate_stepsize = 0.1 # [Hz/s]

        self.update_time = 10 # [ms]
        self.spinbox_width = 100 # [pixels]
