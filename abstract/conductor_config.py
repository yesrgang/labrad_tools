class ConductorConfig(object):
    def __init__(self):
        self.name = '%LABRADNODE%_conductor'
        self.update_id = '689989'
        self.save_to_db = True
        self.sequencers = [
            'yesr20_analog_sequencer', 
            'yesr20_digital_sequencer'
        ]
        
