import json
from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import returnValue

from devices.picoscope.picoscope import Picoscope


class BluePMT(Picoscope):
    picoscope_server_name = 'yesr10_picoscope'
    picoscope_serial_number = 'DU009/008'
    picoscope_duration = 20e-3
    picoscope_frequency = 2e6
    picoscope_n_capture = 3
    picoscope_trigger_threshold = 2# [V]
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
    
    @inlineCallbacks
    def retrive(self, record_name, process_name):
        if record_name == self.recording_name:
            self.record_names.append(record_name)
            while len(self.record_names) > self.max_records:
                rn = self.record_names.popleft()
                del self.records[rn]

            data_format = {"A": [None, None, None]}
            response_json = yield self.picoscope_server.get_data(json.dumps(data_format))
            response = json.loads(response_json)
            gnd = response["A"][0]
            exc = response["A"][1]
            bac = response["A"][2]
            self.records[record_name] = {
                "gnd": gnd,
                "exc": exc,
                "bac": bac,
                }
            self.recording_name = None
        
        record = self.records.get(record_name)
        if record is None:
            message = 'record ({}) is not available'.format(record_name)
            raise Exception(message)

        if process_name == 'full':
            returnValue(record)
        elif process_name == 'sum':
            data = {k: sum(v) for k, v in record.items()}
            data['tot'] = data['gnd'] + data['exc'] - 2 * data['bac']
            data['frac'] = (data['exc'] - data['bac']) / data['tot']
            returnValue(data)
        else:
            message = 'undefined process_name ({})'.format(process_name)
            raise Exception(message)

__device__ = BluePMT
