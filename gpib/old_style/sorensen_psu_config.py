import labrad.types as T

class DHP(object):
    def __init__(self, **kwargs):
        for kw in kwargs:
            setattr(self, kw, kwargs[kw])
    
class SorensenPSUConfig(object):
    def __init__(self):
        self.name = 'sorensen_psu'

        self.update_id = 698020

        self.psu = {
                     'AH PSU': DHP(name='AH PSU',
                               voltage_range=(0, 10), # [V]
                               current_range=(0, 100), # [A]
                               power_range=(0, 1000),
                               def_state=False,
                               def_current=100,
                               def_voltage=0,
                               def_power=500,
                               gpib_device_id='yesr20 GPIB Bus - GPIB1::5::6'),
                    }
