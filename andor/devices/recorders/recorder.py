import h5py
import json
import numpy as np
import os
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
    
    def save(self, images, record_path):
        data_directory = self.data_directory.format(record_path[0])
        if not os.path.isdir(data_directory):
            os.makedirs(data_directory)
        data_path = data_directory + record_path[1]
        h5f = h5py.File(data_path, "w")
        for image in images:
            h5f.create_dataset(image, data=images[image], 
                    compression=self.compression, 
                    compression_opts=self.compression_level)
        h5f.close()

    def send_update(self, device, record_path):
        signal = {
            device.name: {
                'record_path': record_path,
                'record_type': self.name,
                },
            }
        device.server.update(json.dumps(signal))
