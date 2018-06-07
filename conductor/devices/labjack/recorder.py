import json
from labrad.wrappers import connectAsync
from time import strftime
from twisted.internet.defer import inlineCallbacks

from conductor_device.conductor_parameter import ConductorParameter

class Recorder(ConductorParameter):
    priority = 1

    channels = [0, 2]
    sample_rate = 1000

    do_debug = True
    value = None

    @inlineCallbacks
    def initialize(self):
        yield self.connect()
        yield self.cxn.yesr13_labjack.select_interface('470016914')
    
    @inlineCallbacks
    def update(self):
        experiment_name = self.conductor.experiment_name
        experiment_number = self.conductor.experiment_number
        point_number = self.conductor.point_number
        if experiment_name is not None:
            record_name = '{}#{}.{}-labjack.hdf5'.format(experiment_name, 
                    experiment_number, point_number)
        else:
            record_name = 'tmp-data.hdf5'
       
        record_path = [strftime('%Y%m%d'), '{}#{}'.format(experiment_name, experiment_number), record_name]

        cycle_time = self.conductor.parameters['sequencer']['cycle_time'].value - 200e-3
        yield self.cxn.yesr13_labjack.stream(self.channels, cycle_time, self.sample_rate, record_name)

        self.value = record_name

