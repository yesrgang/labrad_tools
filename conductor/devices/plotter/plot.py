import json
import time

from twisted.internet.defer import inlineCallbacks

from conductor_device.conductor_parameter import ConductorParameter

class Plot(ConductorParameter):
#    data_dir = '/home/srgang/yesrdata/SrQ/new_data/{}/{}#{}/'
    data_dir = '/home/srgang/srqdata/data/{}/{}#{}/'
    priority = 1

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
    
    @inlineCallbacks
    def update(self):
        if self.value:
            settings = json.loads(self.value)
            date_str = time.strftime('%Y%m%d')
            exp_name = self.conductor.experiment_name
            exp_num = self.conductor.experiment_number
            exp_pt = self.conductor.point_number
            run_dir = self.data_dir.format(date_str, exp_name, exp_num)
            settings['data_path'] = run_dir

            yield self.cxn.plotter.plot(json.dumps(settings))
