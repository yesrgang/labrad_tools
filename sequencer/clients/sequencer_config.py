import sys
import time

sys.path.append('../../sequencer/devices/lib')
from analog_ramps import RampMaker

class SequencerConfig(object):
    def __init__(self):
        self.sequencer_servername = 'sequencer'
        self.conductor_servername = 'conductor'
        self.timing_channel = 'Trigger@D15'
        self.base_directory = 'Z:\\SrQ\\data\\'
        self.sequence_directory = lambda: self.base_directory + '{}\\sequences\\'.format(time.strftime('%Y%m%d'))
        self.sequencer_update_id = 689223
        self.conductor_update_id = 689222
        self.spacer_width = 65
        self.spacer_height = 15
        self.namecolumn_width = 130
        self.namelabel_width = 200
        self.durationrow_height = 20
        self.analog_height = 50
        self.max_columns = 100
        self.digital_colors = ['#ff0000', '#ff7700', '#ffff00', '#00ff00', '#0000ff', '#8a2be2']
        self.rampMaker = RampMaker
