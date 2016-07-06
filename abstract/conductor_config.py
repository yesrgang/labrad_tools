import os
import time

SEP = os.path.sep

class ConductorConfig(object):
    def __init__(self):
        self.name = '%LABRADNODE%_conductor'
        self.update_id = '689989'
        self.db_write_period = 120 # [s]
        self.data_delay = 10
        self.db_query_str = 'SELECT value FROM "experiment parameters" WHERE \
                "device" = \'sequence\' AND "parameter" = \'{}\' ORDER BY time \
                DESC LIMIT 1'
        self.sequencers = [
                'yesr20_analog_sequencer', 
                'yesr20_digital_sequencer'
        ]
        self.default_sequence = {'digital@T': [1, 5, 1]}
        self.default_devices = {
            'Clock AOM': {
                'frequency': {
                    'init commands': ["self.client.ag33500b_stepper.select_device_by_name('clock steer')"], 
                    'update commands': ["lambda value, self=self: self.client.ag33500b_stepper.frequency(value)"],
                    'default value': 27.2572e6,
                },
            },
        }
        self.data_directory = lambda: 'Z:\\SrQ\\data\\' + time.strftime('%Y%m%d') + '\\'

