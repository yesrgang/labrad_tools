import time

class ConductorConfig(object):
    def __init__(self):
        self.update_id = '689989'
        self.db_query_str = 'SELECT value FROM "experiment parameters" WHERE \
                "device" = \'sequence\' AND "parameter" = \'{}\' ORDER BY time \
                DESC LIMIT 1'
        self.data_directory = lambda: 'Z:\\SrQ\\data\\' + time.strftime('%Y%m%d') + '\\'
        
        self.default_parameters = {
                'clock_aom': {
                    'frequency': None,
                },
        }
