import os

node = os.getenv('LABRADNODE')

class ControlConfig(object):
    def __init__(self):
        self.servername = '{}_conductor'.format(node)
        self.update_id = 461028
        self.updateTime = 100 # [ms]
        self.boxWidth = 80
        self.boxHeight = 20
        self.numRows = 10
        self.device = 'sequence'
