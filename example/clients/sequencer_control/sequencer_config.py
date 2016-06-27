import time
import os
from analog_ramps import RampMaker

node = os.getenv('LABRADNODE')
sep = os.path.sep

class SequencerConfig(object):
    def __init__(self):
        self.digital_servername = '{}_digital_sequencer'.format(node)
        self.analog_servername = '{}_analog_sequencer'.format(node)
        self.conductor_servername = '{}_conductor'.format(node)
        self.base_directory = '..{}..{}data{}'.format(sep, sep, sep)
        self.sequence_directory = lambda: self.base_directory + '{}{}sequences{}'.format(time.strftime('%Y%m%d'), sep, sep)
        self.conductor_update_id = 689222
        self.digital_update_id = 689223
        self.spacer_width = 65
        self.spacer_height = 15
        self.namecolumn_width = 130
        self.namelabel_width = 200
        self.durationrow_height = 20
        self.analog_height = 50
        self.max_columns = 100
        self.digital_colors = ['#ff0000', '#ff7700', '#ffff00', '#00ff00', '#0000ff', '#8a2be2']
        self.rampMaker = RampMaker
