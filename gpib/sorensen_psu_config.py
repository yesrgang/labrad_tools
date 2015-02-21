import labrad.types as T

class DHP(object):
    def __init__(self, **kwargs): #address, frequency, amplitude=1, clock_multiplier=24):
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])
    
class SorensenPSUConfig(object):
    def __init__(self):
        self.name = '%LABRADNODE% Sorensen PSU'

        self.update_id = 698020

        self.psu = {
                     'psu0': DHP(name='psu0',
                                 voltage_range=(0, 30), # [V]
                                 current_range=(0, 100), # [A]
                                 power_range=(0, 3000),
                                 state=False,
                                 gpib_device_id='yesr13 GPIB Bus - GPIB0::1'),
                    }
