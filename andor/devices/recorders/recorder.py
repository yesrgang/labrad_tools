import json
import numpy as np
import h5py
from time import strftime

class Recorder(object):
    config_path = None
    def __init__(self, config_json='{}'):
        with open(self.config_path, 'r') as infile:
            config = json.load(infile)
        config_updates = json.loads(config_json) 
        config.update(config_updates)
        for key, value in config.items():
            setattr(self, key, value)

    def record(self, cam, record_name):
        pass
    
    def save(self, images, record_name):
        data_directory = self.data_directory.format(strftime("%Y%m%d"))
        data_path = data_directory + record_name + ".hdf5"
        h5f = h5py.File(data_path, "w")
        for image in images:
            h5f.create_dataset(image, data=images[image], 
                    compression=self.compression, 
                    compression_opts=self.compression_level)
        h5f.close()

    def send_update(self, device, record_name):
        signal = {
            device.name: {
                'record_name': record_name+'.hdf5',
                'record_type': self.name,
                },
            }
        device.server.update(json.dumps(signal))
