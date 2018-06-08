import json
import h5py
import numpy as np
import os
from scipy.optimize import curve_fit
import time

from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import returnValue
from twisted.internet.reactor import callInThread

from devices.picoscope.picoscope import Picoscope

#def fit_function(x, a, b):
#    T0 = -2e1
#    TAU1 = 6.5e3
#    TAU2 = 9.5e1
#    return a * (np.exp(-(x-T0)/TAU1) - np.exp(-(x-T0)/TAU2)) + b
#

TAU = 2.3e4
def fit_function(x, a):
    return a * np.exp(-x / TAU)

class BluePMT(Picoscope):
    autostart = False
    picoscope_server_name = 'yesr10_picoscope'
    picoscope_serial_number = 'DU009/008'
    picoscope_duration = 2e-3
    picoscope_frequency = 100e6
    picoscope_n_capture = 3
    picoscope_trigger_threshold = 2 # [V]
    picoscope_timeout = -1 # [ms]

    picoscope_channel_settings = {
        'A': {
            'coupling': 'DC',
            'voltage_range': 10.0,
            'attenuation': 1,
            'enabled': True,
            },
        'B': {
            'coupling': 'DC',
            'voltage_range': 10.0,
            'attenuation': 1,
            'enabled': False,
            },
        'C': {
            'coupling': 'DC',
            'voltage_range': 10.0,
            'attenuation': 1,
            'enabled': False,
            },
        'D': {
            'coupling': 'DC',
            'voltage_range': 10.0,
            'attenuation': 1,
            'enabled': False,
            },
        }

    data_format = {
        'A': {
            'gnd': 0,
            'exc': 1,
            'bac': 2,
            },
        }

    p0 = [1]


    @inlineCallbacks
    def record(self, data_path):
        self.recording_name = data_path
        yield self.picoscope_server.run_block()
        callInThread(self.do_record_data, data_path)
#        yield self.do_record_data(data_path)
    
    @inlineCallbacks
    def do_record_data(self, data_path):
        raw_data_json = yield self.picoscope_server.get_data(json.dumps(self.data_format), True)
        raw_data = json.loads(raw_data_json)["A"]
        raw_sums = {label: sum(raw_counts) for label, raw_counts in raw_data.items()}
        raw_fits = {}

        b = np.mean(raw_data['bac'])
        for label, raw_counts in raw_data.items():
            counts = np.array(raw_counts)[500:] - b
            popt, pcov = curve_fit(fit_function, range(len(counts)), counts, p0=self.p0)
            raw_fits[label] = popt[0]

        tot_sum = raw_sums['gnd'] + raw_sums['exc'] - 2 * raw_sums['bac']
        frac_sum = (raw_sums['exc'] - raw_sums['bac']) / tot_sum
        tot_fit = raw_fits['gnd'] + raw_fits['exc'] - 2 * raw_fits['bac']
        frac_fit = (raw_fits['exc'] - raw_fits['bac']) / tot_fit

        processed_data = {
            'frac_sum': frac_sum,
            'tot_sum': tot_sum,
            'frac_fit': frac_fit,
            'tot_fit': tot_fit,
            }

        data_directory = os.path.dirname(data_path) 
        if not os.path.isdir(data_directory):
            os.makedirs(data_directory)
    
        print "saving processed data to {}".format(data_path)

        json_path = data_path + '.json'
        if os.path.exists(json_path):
            print 'not saving data to {}. file already exists'.format(json_path)
        else:
            with open(data_path + '.json', 'w') as outfile:
                json.dump(processed_data, outfile, default=lambda x: x.tolist())
        
        h5py_path = data_path + '.hdf5'
        if os.path.exists(h5py_path):
            print 'not saving data to {}. file already exists'.format(h5py_path)
        else:
            with h5py.File(h5py_path) as h5f:
                for k, v in raw_data.items():
                    h5f.create_dataset(k, data=np.array(v), compression='gzip')
        
        """ temporairly store data """
        if len(self.record_names) > self.max_records:
            oldest_name = self.record_names.popleft()
            if oldest_name not in self.record_names:
                _ = self.records.pop(oldest_name)
        self.record_names.append(data_path)
        self.records[data_path] = processed_data

        yield self.device_server.update(self.name)
    
    @inlineCallbacks
    def retrive(self, record_name):
        yield None
        if type(record_name).__name__ == 'int':
            record_name = self.record_names[record_name]
        if record_name not in self.records:
            message = 'cannot locate record: {}'.format(record_name)
            raise Exception(message)
        record = self.records[record_name]
        record['record_name'] = record_name
        returnValue(record)

__device__ = BluePMT
