import json
from twisted.internet.defer import inlineCallbacks
from labrad.wrappers import connectAsync
from conductor_device.conductor_parameter import ConductorParameter

class Recorder(ConductorParameter):
    priority = 2

    @inlineCallbacks
    def initialize(self):
#        self.cxn = yield connectAsync(name=self.name)
        yield self.connect()
        yield self.cxn.yesr10_andor.select_device('ikon')
    
    @inlineCallbacks
    def update(self):
        experiment_name = self.conductor.experiment_name
        experiment_number = self.conductor.experiment_number
        point_number = self.conductor.point_number
        if ((experiment_name is not None) and (experiment_number is not None) 
                and (point_number is not None)):
            record_name = '{}-images#{}-{}'.format(experiment_name, 
                    experiment_number, point_number)
        else:
            record_name = ''

        if self.value is not None:
            recorder_type = self.value.get('type', '')
            recorder_config = json.dumps(self.value.get('config', {}))
            yield self.cxn.yesr10_andor.record(record_name, recorder_type, 
                    recorder_config)

        else:
            print self.value
