import json
from labrad.wrappers import connectAsync
from time import strftime
from twisted.internet.defer import inlineCallbacks

from conductor_device.conductor_parameter import ConductorParameter

class Recorder(ConductorParameter):
    priority = 2
    recorders = {
        'image': 'record_g',
        'image_3P1_excitation': 'record_g',
        'image_v2': 'record_g',
        'image_clock': 'record_eg',
        'image_ft': 'record_eg',
        }

    data_dir = '/home/srgang/yesrdata/SrQ/new_data/{}/{}#{}/'
    data_filename = '{}.ikon'

    image_settings = {}

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.yesr10_andor.select_device('hr_ikon')
    
    @inlineCallbacks
    def update(self):
        date_str = strftime('%Y%m%d')
        exp_name = self.conductor.experiment_name
        exp_num = self.conductor.experiment_number
        exp_pt = self.conductor.point_number
        run_dir = self.data_dir.format(date_str, exp_name, exp_num)
        
        pt_filename = self.data_filename.format(exp_pt)
        pt_path = run_dir + pt_filename
        
        recorder_type = ''
        try:
            sequence = self.conductor.parameters['sequencer']['sequence'].value
            for subsequence in self.recorders:
                if subsequence in sequence:
                    recorder_type = self.recorders[subsequence]
        except:
            print "conductor's andor ikon unable to determine sequence"

        if recorder_type:
            image_settings_json = json.dumps(self.image_settings)
            yield self.cxn.yesr10_andor.record(pt_path, recorder_type, image_settings_json)
