import h5py
import json
import numpy as np
import os


class Recorder(object):
    name = None

    number_kinetics = None
    exposure_time = 1e-3

    # 1 = single scan, 2 = accumulate, 3 = kinetics mode, 4 = fast kinetics mode, 5 = run until abort
    acquisition_mode = 3
    compression = "gzip"
    compression_level = 4

    def __init__(self, config={}):
        print config
        for key, value in config.items():
            setattr(self, key, value)

    def record(self, cam, record_name):
        pass
    
    def save(self, images, record_path):
        record_directory = os.path.dirname(record_path) 
        if not os.path.isdir(record_directory):
            os.makedirs(record_directory)
        print "saving processed data to {}".format(record_path)


#        json_path = record_path + '.json'
#        if os.path.exists(json_path):
#            print 'not saving data to {}. file already exists'.format(json_path)
#        else:
#            with open(record_path + '.json', 'w') as outfile:
#                json.dump(processed_data, outfile, default=lambda x: x.tolist())
        
        h5py_path = record_path + '.hdf5'
        if os.path.exists(h5py_path):
            os.remove(h5py_path)
        with h5py.File(h5py_path) as h5f:
            for k, v in images.items():
                h5f.create_dataset(k, data=np.array(v), compression='gzip')

        if hasattr(self, 'offset') and hasattr(self, 'size'):
            print 'recording small images'
            off_x, off_y = self.offset
            width, height = self.size
            sub_px = [off_x - width / 2, off_x + width / 2, off_y - height / 2, off_y + height / 2]

            h5py_path = record_path + '.small.hdf5'
            if os.path.exists(h5py_path):
                os.remove(h5py_path)
            with h5py.File(h5py_path) as h5f:
                for k, v in images.items():
                    v_small = v[sub_px[2]:sub_px[3],sub_px[0]:sub_px[1]]
                    h5f.create_dataset(k, data=np.array(v_small), compression='gzip')

#        """ temporairly store data """
#        if len(self.record_names) > self.max_records:
#            oldest_name = self.record_names.popleft()
#            if oldest_name not in self.record_names:
#                _ = self.records.pop(oldest_name)
#        self.record_names.append(record_path)
#        self.records[data_path] = processed_data

    def send_update(self, device, record_path):
        signal = {
            device.name: {
                'record_path': record_path,
                'record_type': self.name,
                },
            }
        signal_json = json.dumps(signal)
        device.device_server.update(signal_json)
