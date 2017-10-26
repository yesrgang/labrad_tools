import json
import numpy as np
import h5py

class RecordG(object):
    def __init__(self, config_json):
        config_updates = json.loads(config_json) 
        with open('./devices/recorders/record_g.json', 'r') as infile:
            default_config = json.load(infile)
        config = default_config.update(config_updates)
        for key, value in config.items():
            setattr(self, key, value)

    def record(self, cam, record_name):
        cam.SetNumberKinetics(self.number_kinetics)
        cam.SetExposureTime(self.exposure_time)
        cam.SetAcquisitionMode(self.acquisition_mode)
        cam.SetImage(1, 1, 1, cam.width, 1, cam.height)
        
        cam.StartAcquisition()
        cam.StartAcquisition()
        cam.StartAcquisition()
        
        data = []
        cam.GetAcquiredData(data)
        data = np.array(data, dtype=np.uint16)
        data = np.reshape(data, (self.number_kinetics, cam.height, cam.width))
        images = {key: data[i] for i, key in enumerate(["dark", "bright", "background"])}
        
        data_path = self.data_directory + record_name + ".hdf5"
        h5f = h5py.File(data_path, "w")
        for image in images:
            h5f.create_dataset(image, data=images[image])
        h5f.close()
