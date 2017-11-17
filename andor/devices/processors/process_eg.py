from processor import Processor
from lib.helpers import *

class ProcessEg(Processor):
    name = 'process_eg'
    config_path = './devices/processors/process_eg.json'

    def get_counts(self):
        self.load()

        high_intensity_coefficient = 2 / (self.linewidth * self.pulse_length 
                * self.efficiency * self.gain)
        low_intensity_coefficient = self.pixel_size**2 / self.cross_section

        bright = (
            np.array(self.images['bright'], dtype='f') 
            - np.array(self.images['dark_bright'], dtype='f')
            )
        image_g = (
            np.array(self.images['image_g'], dtype='f') 
            - np.array(self.images['dark_g'], dtype='f')
            )
        image_e = (
            np.array(self.images['image_e'], dtype='f') 
            - np.array(self.images['dark_e'], dtype='f')
            )
        norm_indicies = get_norm_indicies(bright, self.norm)

        bright_g = bright * np.sum(image_g[norm_indicies]) / np.sum(bright[norm_indicies])
        image_g, bright_g = fix_image_gradient(image_g, bright_g, self.norm)
        
        i_g = (image_g > 0) & (bright_g > 0)
        n_g = np.zeros_like(bright_g)
        n_g[i_g] = (
            low_intensity_coefficient * np.log(bright_g[i_g] / image_g[i_g])
            + high_intensity_coefficient * (bright_g[i_g] - image_g[i_g])
            )
    
        bright_e = bright * np.sum(image_e[norm_indicies]) / np.sum(bright[norm_indicies])
        image_e, bright_e = fix_image_gradient(image_e, bright_e, self.norm)
        
        i_e = (image_e > 0) & (bright_e > 0)
        n_e = np.zeros_like(bright_e)
        n_e[i_e] = (
            low_intensity_coefficient * np.log(bright_e[i_e] / image_e[i_e])
            + high_intensity_coefficient * (bright_e[i_e] - image_e[i_e])
            )

        counts = {}
        for roi_name, roi in self.roi.items():
            roi_pts = region_pts(get_roi_corners(n_g, roi))
            g = np.sum(n_g[zip(*roi_pts)])
            e = np.sum(n_e[zip(*roi_pts)])
            counts[roi_name] = {
                'n_g': g,
                'n_e': e,
                'frac': e / (g + e),
                'tot': g + e,
                }

        return counts
