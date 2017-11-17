import json
import numpy as np
import h5py
from time import strftime

from recorder import Recorder

class RecordG(Recorder):
    name = 'record_g'
    config_path = './devices/recorders/record_g.json'

    def record(self, device, record_name):
        if record_name:
            cam = device.cam
            cam.AbortAcquisition()
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
            images = {key: data[i] for i, key in enumerate(["image", "bright", "dark"])}
            
            self.save(images, record_name)
            self.send_update(device, record_name)
