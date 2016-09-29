import time

class ConductorConfig(object):
    def __init__(self):
        self.data_directory = lambda: 'Z:\\SrQ\\data\\' + time.strftime('%Y%m%d') + '\\'
        self.default_parameters = {
#                'clock_aom': {
#                    'frequency': None,
#                },
                'sequencer': {
                    'sequence': None,
                },
        }
