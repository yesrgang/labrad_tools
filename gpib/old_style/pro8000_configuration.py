class LDC80xxConfig(object):
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

class PRO8000Config(object):
    def __init__(self):
        self.name = 'pro8000'
        self.deviceName = 'PROFILE PRO8000'
        self.gpib_device_id = 'yesr20 GPIB Bus - GPIB0::9::INSTR'
        self.controller_order = ['3D', 'ZS', '2D']
        self.state_id = 698001
        self.current_id = 698002
        self.power_id = 698003
        self.controller = {
            '3D': LDC80xxConfig(slot=2, min_current=0.0, max_current=0.153, def_current=0.1498, step_size=1e-4),
            '2D': LDC80xxConfig(slot=4, min_current=0.0, max_current=0.153, def_current=0.1511, step_size=1e-4),
            'ZS': LDC80xxConfig(slot=6, min_current=0.0, max_current=0.153, def_current=0.1490, step_size=1e-4), 
        }
