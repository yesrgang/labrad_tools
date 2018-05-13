import json
from scipy.optimize import curve_fit
from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import returnValue

from devices.picoscope.picoscope import Picoscope


class BluePMT(Picoscope):
    picoscope_server_name = 'yesr10_picoscope'
    picoscope_serial_number = 'DU009/008'
    picoscope_duration = 10e-3
    picoscope_frequency = 25e6
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

    p0 = [1, 3e-2]

    def fit_function(x, a, b):
        T0 = -2e1
        TAU1 = 6.5e3
        TAU2 = 9.5e1
        return a * (np.exp(-(x-T0)/TAU1) - np.exp(-(x-T0)/TAU2)) + b

    @inlineCallbacks
    def record(self, data_path):
        self.recording_name = data_path
        yield self.picoscope_server.run_block()
        callInThread(self.do_save_data, data_path)

    def do_record_data(self, data_path):
        raw_data_json = yield self.save_data(data_path, json.dumps(self.data_format))
        raw_data = json.loads(raw_data_json)["A"]
        raw_sums = {label: sum(raw_counts) for label, raw_counts in raw_data.items()}
        raw_fits = {}
        for label, raw_counts in raw_data.items():
            popt, pcov = curve_fit(fit_function, range(len(raw_counts)), raw_counts, p0=self.p0)
            raw_fits[label] = popt[0]

        tot_sum = raw_sums['gnd'] + raw_sums['exc'] - 2 * raw_sums['bac']
        frac_sum = (raw_sums['exc'] - raw_sums['bac']) / tot_sum
        tot_fit = raw_fits['gnd'] + raw_fits['exc'] - 2 * raw_fits['bac']
        frac_fit = (raw_fits['exc'] - raw_fits['bac']) / tot_fit

        data = {
            'gnd': raw_data['gnd'],
            'exc': raw_data['exc'],
            'bac': raw_data['bac'],
            'frac_sum': frac_sum,
            'tot_sum': tot_sum,
            'frac_fit': frac_fit,
            'tot_fit': tot_fit,
            }

        data_directory = os.path.dirname(data_path) 
        if not os.path.isdir(directory):
            os.makedirs(directory)

        with open(data_path, 'w') as outfile:
            json.dump(data, outfile, default=lambda x: x.tolist())
    
#    @inlineCallbacks
#    def retrive(self, record_name, process_name):
#        if record_name == self.recording_name:
#            self.record_names.append(record_name)
#            while len(self.record_names) > self.max_records:
#                rn = self.record_names.popleft()
#                del self.records[rn]
#
#            data_format = {"A": [None, None, None]}
#            response_json = yield self.picoscope_server.get_data(json.dumps(data_format))
#            response = json.loads(response_json)
#            gnd = response["A"][0]
#            exc = response["A"][1]
#            bac = response["A"][2]
#            self.records[record_name] = {
#                "gnd": gnd,
#                "exc": exc,
#                "bac": bac,
#                }
#            self.recording_name = None
#        
#        record = self.records.get(record_name)
#        if record is None:
#            message = 'record ({}) is not available'.format(record_name)
#            raise Exception(message)
#
#        if process_name == 'full':
#            returnValue(record)
#        elif process_name == 'sum':
#            data = {k: sum(v) for k, v in record.items()}
#            data['tot'] = data['gnd'] + data['exc'] - 2 * data['bac']
#            data['frac'] = (data['exc'] - data['bac']) / data['tot']
#            returnValue(data)
#        else:
#            message = 'undefined process_name ({})'.format(process_name)
#            raise Exception(message)

__device__ = BluePMT
