class LDC80xxConfig(object):
    def __init__(self, **kwargs):
        self.d = {kw: kwargs[kw] for kw in kwargs}

    def get_dict(self):
        return self.d

class PRO8000Config(object):
    def __init__(self):
        self.gpib_device_id = 'yesr13 GPIB Bus - GPIB1::10'
        self.device_name = 'PROFILE PRO8000'
        self.controller_order = ['ZS', 'MOT', 'TC']
        self.controller = {
                'ZS': LDC80xxConfig(slot=2, min_current=0.0, max_current=0.153, def_current=0.1480, step_size=1e-4),
                'MOT': LDC80xxConfig(slot=4, min_current=0.0, max_current=0.153, def_current=0.1480, step_size=1e-4),
                'TC': LDC80xxConfig(slot=6, min_current=0.0, max_current=0.153, def_current=0.1480, step_size=1e-4), 
                #'2.6': LDC80xxConfig(slot=8, min_current=0.0, max_current=0.100, def_current=0.0821, step_size=1e-6)
                }

    def get_dict(self):
        return {'gpib_device_id': self.gpib_device_id, 
                'controller_order': self.controller_order,
                'device_name': self.device_name
                }
