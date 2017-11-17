from processor import Processor
from lib.helpers import *

class ProcessG(Processor):
    name = 'process_g'
    config_path = './devices/processors/process_g.json'

    def get_counts(self):
        self.load()
        high_intensity_coefficient = 2 / (self.linewidth * self.pulse_length 
                * self.efficiency * self.gain)
        low_intensity_coefficient = self.pixel_size**2 / self.cross_section

        bright = (
            np.array(self.images['bright'], dtype='f') 
            - np.array(self.images['dark'], dtype='f')
            )
        image = (
            np.array(self.images['image'], dtype='f') 
            - np.array(self.images['dark'], dtype='f')
            )

        norm_indicies = get_norm_indicies(bright, self.norm)
        
        bright = bright * np.sum(image[norm_indicies]) / np.sum(bright[norm_indicies])
        image, bright = fix_image_gradient(image, bright, self.norm)

        i = (image > 0) & (bright > 0)
        n = np.zeros_like(bright)
        n[i] = (
            low_intensity_coefficient * np.log(bright[i] / image[i])
            + high_intensity_coefficient * (bright[i] - image[i])
            )
        
        counts = {}
        for roi_name, roi in self.roi.items():
            roi_pts = region_pts(get_roi_corners(n, roi))
            counts[roi_name] = {
                'n': np.sum(n[zip(*roi_pts)]),
                }

        return counts
