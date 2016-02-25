class ConductorConfig(object):
    def __init__(self):
        self.name = '%LABRADNODE%_conductor'
        self.update_id = '689989'
        self.save_to_db = True
        self.dbquerystr = 'SELECT value FROM "sequence parameters" WHERE "name" = \'{}\' ORDER BY time DESC LIMIT 1'
        self.sequencers = [
            'yesr20_analog_sequencer', 
            'yesr20_digital_sequencer'
        ]
        
