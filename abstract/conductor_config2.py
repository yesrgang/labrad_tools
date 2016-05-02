class ConductorConfig(object):
    def __init__(self):
        self.name = '%LABRADNODE%_conductor'
        self.update_id = '689989'
        self.db_write_period = 120 # [s]
        self.db_query_str = 'SELECT value FROM "experiment parameters" WHERE "device" = \'sequence\' AND "parameter" = \'{}\' ORDER BY time DESC LIMIT 1'
        self.sequencers = [
            'yesr20_analog_sequencer', 
            'yesr20_digital_sequencer'
        ]

        self.default_sequence = {'digital@T': [1, 5, 1]}
