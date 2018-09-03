import json
import numpy as np
import h5py

class Processor(object):
    """ process single image """
    
    data_directory = "/home/srgang/yesrdata/SrQ/data/{}/{}"
    pixel_size = 0.55793991
    cross_section = 0.1014
    linewidth = 201.06192983
    pulse_length = 5
    efficiency = 0.50348
    gain = 0.25
    
    def __init__(self, config={}):
        for key, value in config.items():
            setattr(self, key, value)

    def load(self):
        """ load images """
        camera_name = self.camera_name
        off_x, off_y = self.offset
        width, height = self.size

        image_path = self.data_directory.format(*self.image_path)
        
        sub_px = [off_x - width / 2, off_x + width / 2, off_y - height / 2, off_y + height / 2]
        
        self.images = {}
        images_hdf5 = h5py.File(image_path, 'r')
        for key, image in images_hdf5.items():
            image = np.array(image, dtype=np.uint16)
            image = np.fliplr(np.flipud(image))
            sub_image = image[sub_px[2]:sub_px[3],sub_px[0]:sub_px[1]]
            self.images[key] = sub_image
        images_hdf5.close()
