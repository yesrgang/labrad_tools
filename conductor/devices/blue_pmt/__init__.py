import json
from labrad.wrappers import connectAsync
from time import strftime
from twisted.internet.defer import inlineCallbacks

from conductor_device.conductor_parameter import ConductorParameter

class Recorder(ConductorParameter):
    priority = 1
    recorders = {
        'image': 'record_g',
        'image_clock': 'record_eg',
        'image_ft': 'record_eg',
        }

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.yesr10_andor.select_device('ikon')
    
    @inlineCallbacks
    def update(self):
        recorder_type = ''
        sequence = self.conductor.parameters['sequencer']['sequence'].value
        for subsequence, recorder in self.recorders.items():
            if subsequence in sequence:
                recorder_type = recorder

        experiment_name = self.conductor.experiment_name
        experiment_number = self.conductor.experiment_number
        point_number = self.conductor.point_number
        if experiment_name is not None:
            record_name = '{}#{}-image#{}.hdf5'.format(experiment_name, 
                    experiment_number, point_number)
        else:
            record_name = 'current-image.hdf5'
        record_path = [strftime('%Y%m%d'), record_name]

        if self.value is None:
            self.value = {}
        if recorder_type:
#            recorder_type = self.value.get('type', recorder_type)
            recorder_config = json.dumps(self.value.get('config', {}))
            yield self.cxn.yesr10_andor.record(record_path, recorder_type, 
                    recorder_config)

        yield self.conductor.set_parameter_value('andor', 'image_path', 
                record_path, True)

