import numpy as np

from recorder import Recorder

class RecordG(Recorder):
    name = 'record_g'

    number_kinetics = 3
    exposure_time = 1e-3
    acquisition_mode = 3

    compression =  "gzip"
    compression_level = 4

    def record(self, device, record_path):
        if record_path:
            cam = device.cam
            cam.AbortAcquisition()
            cam.SetAcquisitionMode(self.acquisition_mode)
            cam.SetNumberKinetics(self.number_kinetics)
            cam.SetExposureTime(self.exposure_time)
            cam.SetImage(1, 1, 1, cam.width, 1, cam.height)
            
            cam.StartAcquisition()
            cam.StartAcquisition()
            cam.StartAcquisition()
#            
            data = []
            cam.GetAcquiredData(data)
            data = np.array(data, dtype=np.uint16)
            data = np.reshape(data, (self.number_kinetics, cam.height, cam.width))
            images = {key: data[i] for i, key in enumerate(["image", "bright", "dark"])}
            
            self.save(images, record_path)
            self.send_update(device, record_path)

__recorder__ = RecordG
