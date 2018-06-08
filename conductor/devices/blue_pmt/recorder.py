import json
from twisted.internet.defer import inlineCallbacks
import time
import os

from conductor_device.conductor_parameter import ConductorParameter

class Recorder(ConductorParameter):
    priority = 2
    data_dir = '/home/srgang/yesrdata/SrQ/new_data/{}/{}#{}/'
    #data_filename = 'test_pmt-{}.json'
    data_filename = '{}.blue_pmt'

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.pmt.select_device('blue_pmt')
    
    @inlineCallbacks
    def update(self):
        date_str = time.strftime('%Y%m%d')
        exp_name = self.conductor.experiment_name
        exp_num = self.conductor.experiment_number
        exp_pt = self.conductor.point_number
        run_dir = self.data_dir.format(date_str, exp_name, exp_num)
        
        pt_filename = self.data_filename.format(exp_pt)
        pt_path = run_dir + pt_filename
        
        if exp_name:
            yield self.cxn.pmt.record(pt_path)
