import json
import numpy as np
import h5py
from time import strftime

from recorder import Recorder

class RecordEg(Recorder):
    name = 'record_eg'
    config_path = './devices/recorders/record_eg.json'

    def record(self, device, record_name):
        if record_name:
            cam = device.cam
            cam.AbortAcquisition()
            cam.SetShutter(1, 1, 0, 0)

            cam.SetAcquisitionMode(self.acquisition_mode)

            sub_height = int(cam.height / self.number_sub_frames)
            offset_height = cam.height - sub_height
            cam.SetFastKineticsEx(sub_height, self.number_sub_frames, 
                    self.exposure_time, 4, 1, 1, offset_height)

            cam.StartAcquisition()
            data = []
            cam.GetAcquiredData(data)
            data = np.array(data, dtype=np.uint16)
            data = np.reshape(data, (self.number_sub_frames, sub_height, cam.width))
            images = {key: data[i] for i, key in enumerate(["dark_g", "dark_e", "bright"])}
            
            cam.StartAcquisition()
            data = []
            cam.GetAcquiredData(data)
            data = np.array(data, dtype=np.uint16)
            data = np.reshape(data, (self.number_sub_frames, sub_height, cam.width))
            background_images = {key: data[i] for i, key in 
                    enumerate(["g_background", "e_background", "bright_background"])}

            images.update(background_images)
            
            self.save(images, record_name)
            self.send_update(device, record_name)
