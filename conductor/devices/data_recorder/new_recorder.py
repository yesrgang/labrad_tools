import os
import json
import time
import h5py

from twisted.internet.defer import inlineCallbacks

from conductor_device.conductor_parameter import ConductorParameter

class NewRecorder(ConductorParameter):
    priority = 2
    #data_dir = 'Z:\\SrQ\\new_data\\{}\\{}#{}\\'
    data_dir = '/home/srgang/yesrdata/SrQ/new_data/{}/{}#{}/'
    data_filename = '{}.conductor'

    @inlineCallbacks
    def update(self):
        date_str = time.strftime('%Y%m%d')
        exp_name = self.conductor.experiment_name
        exp_num = self.conductor.experiment_number
        exp_pt = self.conductor.point_number
        run_dir = self.data_dir.format(date_str, exp_name, exp_num)
        if not os.path.isdir(run_dir):
            os.makedirs(run_dir)
        
        pt_filename = self.data_filename.format(exp_pt)
        pt_path = run_dir + pt_filename

        pv_json = yield self.conductor.get_parameter_values(None)
        pv = json.loads(pv_json)
        if exp_name is not None:
            with open(pt_path + '.json', 'w') as outfile:
#                print 'saving {}.json'.format(pt_path)
                json.dump(pv, outfile, default=lambda x: None)
